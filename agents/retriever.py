import os
import chromadb
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction
from agents.state import AgentState


def retriever_node(state: AgentState) -> AgentState:
    """Embed the company + context query and retrieve relevant docs from ChromaDB."""
    query = f"{state['company_name']} {state['meeting_context']}"

    client = chromadb.PersistentClient(path="./chroma_db")
    embedding_fn = OpenAIEmbeddingFunction(
        api_key=os.environ["OPENAI_API_KEY"],
        model_name="text-embedding-3-small",
    )
    collection = client.get_or_create_collection(
        name="sales_knowledge",
        embedding_function=embedding_fn,
    )

    results = collection.query(query_texts=[query], n_results=4)
    docs = results["documents"][0] if results["documents"] else []

    log = state.get("status_log", [])
    log.append(f"📂 Retriever: found {len(docs)} relevant documents from knowledge base.")

    return {**state, "retrieved_docs": docs, "status_log": log}
