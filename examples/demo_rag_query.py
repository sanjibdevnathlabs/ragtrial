#!/usr/bin/env python3
"""
Demo: RAG Query with LangChain

This script demonstrates how to use the RAG (Retrieval-Augmented Generation) chain
to query documents and get answers with source citations.

Prerequisites:
1. Documents must be ingested into vectorstore first
2. GEMINI_API_KEY must be set in environment

Usage:
    python examples/demo_rag_query.py
"""

from app import RAGChain
from config import Config
from logger import get_logger

logger = get_logger(__name__)


def main():
    """
    Demonstrate RAG query functionality.
    """
    print("=" * 80)
    print("RAG QUERY DEMO".center(80))
    print("=" * 80)
    print()

    # Initialize configuration
    print("📝 Loading configuration...")
    config = Config()
    print("✅ Configuration loaded")
    print(f"   - Embeddings: {config.embeddings.provider}")
    print(f"   - Vectorstore: {config.vectorstore.provider}")
    # Get model based on provider
    provider = config.rag.provider
    if provider == "google":
        model = config.rag.google.model
    elif provider == "openai":
        model = config.rag.openai.model
    else:
        model = config.rag.anthropic.model
    print(f"   - LLM: {provider}/{model}")
    print()

    # Initialize RAG chain
    print("🔗 Initializing RAG chain...")
    try:
        rag_chain = RAGChain(config)
        print("✅ RAG chain initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize RAG chain: {e}")
        return

    print()
    print("=" * 80)
    print()

    # Example queries
    queries = [
        "What is retrieval-augmented generation?",
        "How do embeddings work?",
        "What are the benefits of vector databases?",
    ]

    for i, question in enumerate(queries, 1):
        print(f"QUERY {i}: {question}")
        print("-" * 80)

        try:
            response = rag_chain.query(question)

            # Display answer
            print("\n📋 ANSWER:")
            print(f"{response['answer']}")
            print()

            # Display metadata
            print("📊 METADATA:")
            print(f"   - Retrieved: {response['retrieval_count']} documents")
            print(f"   - Has Answer: {response['has_answer']}")
            print()

            # Display sources
            if response["sources"]:
                print("📚 SOURCES:")
                for j, source in enumerate(response["sources"], 1):
                    source_name = source["metadata"].get("source", "Unknown")
                    content_preview = source["content"][:100] + "..."
                    print(f"   [{j}] {source_name}")
                    print(f"       {content_preview}")
                print()

        except Exception as e:
            print(f"❌ Query failed: {e}")
            print()

        print("=" * 80)
        print()


if __name__ == "__main__":
    main()
