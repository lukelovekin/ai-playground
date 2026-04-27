# notebooks

Standalone reference notebooks covering LangChain fundamentals, prompt engineering, similarity search, data wrangling, and LangGraph.

## Notebooks

### `langchain_fundamentals.ipynb`

End-to-end walkthrough of the LangChain stack: models and chat messages, prompt templates, output parsers, document loaders, text splitters, embeddings, vector stores, retrievers, memory, chains (LLMChain and LCEL), and agents using the ReAct framework.

### `prompt_engineering_and_templates.ipynb`

Covers zero-shot, one-shot, few-shot, chain-of-thought, and self-consistency prompting techniques. Applies LangChain prompt templates to summarisation, QA, classification, code generation, and role-playing tasks.

### `similarity_search.ipynb`

Manual and library implementations of L2 distance, dot product, and cosine similarity over sentence embeddings. Step-by-step comparisons using numpy, scipy, and PyTorch.

### `semantic_similarity_faiss.ipynb`

FAISS-based semantic similarity search — embedding text into vectors and querying the index for nearest neighbours.

### `langgraph_101.ipynb`

Introduction to LangGraph's core primitives: typed state dictionaries, nodes, edges, routers, and conditional branching. Two worked examples:
- A user authentication workflow with success/failure routing.
- A QA workflow that validates input, retrieves context, and calls IBM WatsonX to generate an answer.

### `data_wrangling.ipynb`

End-to-end data cleaning pipeline on a used car dataset: missing value handling (mean imputation, frequency replacement, row dropping), type correction, unit standardisation (mpg → L/100km), min-max normalisation, equal-width binning, and one-hot encoding.

### `llm_agents_with_tools.ipynb`

LLM agents that call Python functions as tools — covers tool definition, schema generation, and multi-turn agent loops.

### `langchain_tool_calling.ipynb`

Tool calling patterns with LangChain — defining tools, binding them to models, and handling tool call results.

### `dalle_image_generation.ipynb`

Image generation with DALL-E via the OpenAI API.

### `text_to_chart_agent.ipynb`

An agent that takes a natural language description and generates matplotlib chart code, then renders it.

## Tools

**LangChain**, **LangGraph**, **FAISS**, **IBM WatsonX**, **OpenAI**, **pandas**, **NumPy**, **matplotlib**, **PyTorch**
