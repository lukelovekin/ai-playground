import re
from pathlib import Path
import chromadb
from chromadb.utils import embedding_functions
from backend.models import RetrievedContext
from dotenv import load_dotenv

load_dotenv()

CHROMA_DIR = Path(__file__).parent.parent / "chroma_db"
TOP_K = 4
PROFESSIONAL_SOURCES = {"resume", "professional_experience"}
PROFESSIONAL_GUARANTEE = 2  # guaranteed chunks per professional source

# Maps lowercase/de-punctuated tech terms to canonical forms so embedding
# captures the right concept regardless of how the user spelled it.
_TECH_ALIASES: dict[str, str] = {
    "nodejs": "Node.js",
    "nestjs": "NestJS",
    "nest.js": "NestJS",
    "nextjs": "Next.js",
    "next.js": "Next.js",
    "reactjs": "React",
    "react.js": "React",
    "vuejs": "Vue.js",
    "vue.js": "Vue.js",
    "typescript": "TypeScript",
    "javascript": "JavaScript",
    "postgresql": "PostgreSQL",
    "postgres": "PostgreSQL",
    "mongodb": "MongoDB",
    "fastapi": "FastAPI",
    "langchain": "LangChain",
    "langgraph": "LangGraph",
    "langraph": "LangGraph",
    "chromadb": "ChromaDB",
    "tailwindcss": "Tailwind CSS",
    "tailwind": "Tailwind CSS",
    "kafka": "Kafka",
    "expressjs": "Express",
    "express.js": "Express",
    "launchdarkly": "LaunchDarkly",
    "hubspot": "HubSpot",
    "strapi": "Strapi",
    "gatsby": "Gatsby",
    "flutter": "Flutter",
    "crewai": "CrewAI",
    "groq": "Groq",
    "php": "PHP",
    "graphql": "GraphQL",
    "mobx": "MobX",
    "kubernetes": "Kubernetes",
    "k8s": "Kubernetes",
    "firebase": "Firebase",
    "stripe": "Stripe",
    "datadog": "Datadog",
    "redis": "Redis",
    "gsap": "GSAP",
}

_collection_cache = None


def _collection():
    global _collection_cache
    if _collection_cache is None:
        client = chromadb.PersistentClient(path=str(CHROMA_DIR))
        ef = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )
        _collection_cache = client.get_collection("portfolio", embedding_function=ef)
    return _collection_cache


def _normalize_query(query: str) -> str:
    """Canonicalize tech name variants before embedding lookup."""
    tokens = []
    for token in query.split():
        key = re.sub(r"[^a-z0-9.]", "", token.lower())
        tokens.append(_TECH_ALIASES.get(key, token))
    return " ".join(tokens)


def retrieve(query: str, k: int = TOP_K) -> RetrievedContext:
    normalized = _normalize_query(query)
    col = _collection()

    # Professional chunks first — LLM reads context top-to-bottom,
    # so position determines what gets prioritised in the response.
    chunks: list[str] = []
    seen_ids: set[str] = set()

    for source in PROFESSIONAL_SOURCES:
        results = col.query(
            query_texts=[normalized],
            n_results=PROFESSIONAL_GUARANTEE,
            where={"source": source},
        )
        for doc, rid in zip(results["documents"][0], results["ids"][0]):
            if rid not in seen_ids:
                chunks.append(doc)
                seen_ids.add(rid)

    # Fill remaining slots with general semantic results.
    # personal_experience only appears here if it ranks naturally.
    general = col.query(query_texts=[normalized], n_results=k)
    for doc, rid in zip(general["documents"][0], general["ids"][0]):
        if rid not in seen_ids:
            chunks.append(doc)
            seen_ids.add(rid)

    return RetrievedContext(query=query, chunks=chunks)
