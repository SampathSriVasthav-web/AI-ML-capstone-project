import os
from typing import TypedDict, List, Dict, Any

import chromadb
from sentence_transformers import SentenceTransformer
from langgraph.graph import StateGraph, START, END

from support_assistant.models import SupportResponse


# ============================================================
# CONFIGURATION
# ============================================================

MOCK_LLM = os.getenv("MOCK_LLM", "1")

CHROMA_DIR = "support_assistant/chroma_db"
COLLECTION_NAME = "zepto_policies"


# ============================================================
# EMBEDDING MODEL
# ============================================================

model = SentenceTransformer("all-MiniLM-L6-v2")


# ============================================================
# CHROMADB
# ============================================================

client = chromadb.PersistentClient(
    path=CHROMA_DIR
)

collection = client.get_collection(
    name=COLLECTION_NAME
)


# ============================================================
# LANGGRAPH STATE
# ============================================================

class SupportState(TypedDict, total=False):
    query: str
    intent: str
    retrieved_chunks: List[Dict[str, Any]]
    answer: str
    sources: List[str]
    confidence: float


# ============================================================
# NODE 1: CLASSIFY INTENT
# ============================================================

def classify_intent(state: SupportState) -> SupportState:

    query = state["query"].lower()

    policy_keywords = [
        "delivery",
        "return",
        "refund",
        "membership",
        "tracking",
        "cancel",
        "gift card",
        "support hours"
    ]

    if MOCK_LLM != "0":

        if any(keyword in query for keyword in policy_keywords):
            intent = "policy_question"
        else:
            intent = "general_question"

    else:

        # Optional real LLM extension
        intent = "general_question"

    return {
        **state,
        "intent": intent
    }


# ============================================================
# NODE 2: RETRIEVE AND ANSWER
# ============================================================

def retrieve_and_answer(state: SupportState) -> SupportState:

    query = state["query"]

    # --------------------------------------------------------
    # Create embedding for the query
    # --------------------------------------------------------

    query_embedding = model.encode(query).tolist()

    # --------------------------------------------------------
    # Retrieve top 3 similar chunks
    # --------------------------------------------------------

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=3
    )

    documents = results.get("documents", [[]])[0]
    ids = results.get("ids", [[]])[0]

    retrieved_chunks = []

    for doc_id, document in zip(ids, documents):

        retrieved_chunks.append({
            "id": doc_id,
            "content": document
        })

    # --------------------------------------------------------
    # MOCK LLM BASELINE
    # --------------------------------------------------------

    if MOCK_LLM != "0":

        if len(retrieved_chunks) > 0:

            top_chunk = retrieved_chunks[0]["content"]

            # Assignment asks for a short excerpt
            top_chunk_snippet = top_chunk[:200]

            answer = (
                "Based on the retrieved context: "
                + top_chunk_snippet
            )

        else:

            answer = (
                "No relevant Zepto policy information was found."
            )

    else:

        # Optional real LLM extension
        answer = (
            "Real LLM mode can be implemented here."
        )

    # --------------------------------------------------------
    # Source document IDs
    # --------------------------------------------------------

    sources = [
        chunk["id"]
        for chunk in retrieved_chunks
    ]

    # --------------------------------------------------------
    # Pydantic validation
    # --------------------------------------------------------

    response = SupportResponse(
        answer=answer,
        sources=sources,
        confidence=1.0
    )

    return {
        **state,
        "retrieved_chunks": retrieved_chunks,
        "answer": response.answer,
        "sources": response.sources,
        "confidence": response.confidence
    }


# ============================================================
# NODE 3: DIRECT ANSWER
# ============================================================

def direct_answer(state: SupportState) -> SupportState:

    if MOCK_LLM != "0":

        answer = (
            "I can only answer questions about Zepto policies right now."
        )

    else:

        # Optional real LLM extension
        answer = (
            "Real LLM mode can be implemented here."
        )

    response = SupportResponse(
        answer=answer,
        sources=[],
        confidence=1.0
    )

    return {
        **state,
        "answer": response.answer,
        "sources": response.sources,
        "confidence": response.confidence
    }


# ============================================================
# ROUTER
# ============================================================

def route_intent(state: SupportState) -> str:

    if state["intent"] == "policy_question":
        return "retrieve_and_answer"

    return "direct_answer"


# ============================================================
# BUILD GRAPH
# ============================================================

builder = StateGraph(SupportState)


# Add nodes

builder.add_node(
    "classify_intent",
    classify_intent
)

builder.add_node(
    "retrieve_and_answer",
    retrieve_and_answer
)

builder.add_node(
    "direct_answer",
    direct_answer
)


# START → classify_intent

builder.add_edge(
    START,
    "classify_intent"
)


# Conditional routing

builder.add_conditional_edges(
    "classify_intent",
    route_intent,
    {
        "retrieve_and_answer": "retrieve_and_answer",
        "direct_answer": "direct_answer"
    }
)


# Both branches → END

builder.add_edge(
    "retrieve_and_answer",
    END
)

builder.add_edge(
    "direct_answer",
    END
)


# Compile

graph = builder.compile()


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    print()
    print("==============================")
    print("TEST 1: POLICY QUESTION")
    print("==============================")

    result = graph.invoke({
        "query": "What is Zepto's delivery policy?"
    })

    print("Intent:", result["intent"])
    print("Answer:", result["answer"])
    print("Sources:", result["sources"])
    print("Confidence:", result["confidence"])


    print()
    print("==============================")
    print("TEST 2: GENERAL QUESTION")
    print("==============================")

    result = graph.invoke({
        "query": "What is the capital of India?"
    })

    print("Intent:", result["intent"])
    print("Answer:", result["answer"])
    print("Sources:", result["sources"])
    print("Confidence:", result["confidence"])