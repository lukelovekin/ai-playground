"""Load data/ markdown files + resume PDF into ChromaDB. Run once, re-run after any changes."""
from pathlib import Path
import chromadb
from chromadb.utils import embedding_functions
from pdfminer.high_level import extract_text
from dotenv import load_dotenv

load_dotenv()

DATA_DIR = Path(__file__).parent.parent / "data"
RESUME_PDF = Path(__file__).parent.parent / "lukelovekin.pdf"
CHROMA_DIR = Path(__file__).parent.parent / "chroma_db"

CHUNK_SIZE = 300
CHUNK_OVERLAP = 50


def chunk_text(text: str, size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    words = text.split()
    chunks, i = [], 0
    while i < len(words):
        chunk = " ".join(words[i : i + size])
        if chunk.strip():
            chunks.append(chunk)
        i += size - overlap
    return chunks


def ingest():
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")

    try:
        client.delete_collection("portfolio")
    except Exception:
        pass
    collection = client.create_collection("portfolio", embedding_function=ef)

    docs, ids, metas = [], [], []
    doc_id = 0

    # Resume PDF — primary source for work history, education, certs
    if RESUME_PDF.exists():
        text = extract_text(str(RESUME_PDF))
        for chunk in chunk_text(text):
            docs.append(chunk)
            ids.append(f"resume_{doc_id}")
            metas.append({"source": "resume"})
            doc_id += 1
        print(f"  ✓  {RESUME_PDF.name} ({doc_id} chunks)")
    else:
        print(f"  ⚠  Resume not found: {RESUME_PDF.name}")

    # Markdown files — personal info, AI skills, project deep-dives
    for md_file in sorted(DATA_DIR.glob("*.md")):
        before = doc_id
        source = md_file.stem
        text = md_file.read_text(encoding="utf-8")
        for chunk in chunk_text(text):
            docs.append(chunk)
            ids.append(f"{source}_{doc_id}")
            metas.append({"source": source})
            doc_id += 1
        print(f"  ✓  {md_file.name} ({doc_id - before} chunks)")

    collection.add(documents=docs, ids=ids, metadatas=metas)
    print(f"\nTotal: {len(docs)} chunks → {CHROMA_DIR}")


if __name__ == "__main__":
    ingest()
