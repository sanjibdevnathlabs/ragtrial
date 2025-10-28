#!/usr/bin/env python3
"""
Interactive RAG CLI - Terminal-based interface for RAG queries

Usage:
    python examples/interactive_rag_cli.py
    
    Or with environment variables:
    APP_ENV=dev GEMINI_API_KEY=your_key python examples/interactive_rag_cli.py
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.chain_rag.chain import RAGChain
from config import Config
import constants


def print_banner():
    """Print welcome banner."""
    print("\n" + "=" * 70)
    print("   🤖 RAG SYSTEM - Interactive Terminal Interface")
    print("=" * 70)
    print()


def print_separator():
    """Print section separator."""
    print("-" * 70)


def format_sources(sources: list) -> str:
    """Format source documents for display."""
    if not sources:
        return "  No sources found"
    
    output = []
    for i, source in enumerate(sources, 1):
        metadata = source.get("metadata", {})
        source_path = metadata.get(constants.META_SOURCE, "unknown")
        filename = Path(source_path).name if source_path != "unknown" else "unknown"
        
        content_preview = source.get("content", "")[:150]
        if len(source.get("content", "")) > 150:
            content_preview += "..."
        
        output.append(f"  [{i}] {filename}")
        output.append(f"      {content_preview}")
        output.append("")
    
    return "\n".join(output)


def display_result(result: dict):
    """Display query result in a formatted way."""
    print()
    print_separator()
    
    # Display answer
    print("📝 ANSWER:")
    print()
    answer = result.get(constants.RESPONSE_KEY_ANSWER, "No answer generated")
    
    # Word wrap the answer for better readability
    words = answer.split()
    line = ""
    for word in words:
        if len(line) + len(word) + 1 <= 70:
            line += word + " "
        else:
            print("  " + line.strip())
            line = word + " "
    if line:
        print("  " + line.strip())
    
    print()
    
    # Display has_answer status
    has_answer = result.get(constants.RESPONSE_KEY_HAS_ANSWER, False)
    status_icon = "✅" if has_answer else "❌"
    print(f"{status_icon} Answer Found: {has_answer}")
    
    print()
    print_separator()
    
    # Display sources
    sources = result.get(constants.RESPONSE_KEY_SOURCES, [])
    print(f"📚 SOURCES ({len(sources)} documents):")
    print()
    print(format_sources(sources))
    
    print_separator()
    print()


def interactive_mode(rag_chain: RAGChain):
    """Run interactive query loop."""
    print("💡 Tips:")
    print("  - Type your question and press Enter")
    print("  - Type 'quit', 'exit', or 'q' to exit")
    print("  - Type 'help' for more information")
    print()
    print_separator()
    
    while True:
        try:
            # Get user input
            print()
            question = input("🔍 Your Question: ").strip()
            
            if not question:
                print("⚠️  Please enter a question")
                continue
            
            # Check for exit commands
            if question.lower() in ['quit', 'exit', 'q']:
                print("\n👋 Goodbye!\n")
                break
            
            # Check for help command
            if question.lower() == 'help':
                print()
                print("📖 HELP:")
                print("  - Ask any question about your indexed documents")
                print("  - The system will retrieve relevant chunks and generate an answer")
                print("  - Sources are shown with each answer")
                print("  - Type 'quit' or 'exit' to leave")
                print()
                continue
            
            # Process query
            print("\n⏳ Processing query...")
            result = rag_chain.query(question)
            
            # Display result
            display_result(result)
            
        except KeyboardInterrupt:
            print("\n\n👋 Interrupted by user. Goodbye!\n")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}\n")
            continue


def main():
    """Main entry point."""
    print_banner()
    
    try:
        # Initialize config
        print("🔧 Initializing configuration...")
        config = Config()
        
        # Display config info
        print(f"   Provider: {config.rag.provider}")
        if config.rag.provider == constants.LLM_PROVIDER_GOOGLE:
            print(f"   Model: {config.rag.google.model}")
        elif config.rag.provider == constants.LLM_PROVIDER_OPENAI:
            print(f"   Model: {config.rag.openai.model}")
        elif config.rag.provider == constants.LLM_PROVIDER_ANTHROPIC:
            print(f"   Model: {config.rag.anthropic.model}")
        
        print(f"   Vector Store: {config.vectorstore.provider}")
        print()
        
        # Initialize RAG chain
        print("🚀 Initializing RAG chain...")
        rag_chain = RAGChain(config=config)
        print("✅ RAG chain initialized successfully!")
        print()
        
        # Start interactive mode
        interactive_mode(rag_chain)
        
    except Exception as e:
        print(f"\n❌ Initialization Error: {e}")
        print("\nTroubleshooting:")
        print("  1. Make sure APP_ENV is set (e.g., APP_ENV=dev)")
        print("  2. Check that your API key is set (e.g., GEMINI_API_KEY=xxx)")
        print("  3. Ensure documents are indexed in the vector store")
        print()
        sys.exit(1)


if __name__ == "__main__":
    main()

