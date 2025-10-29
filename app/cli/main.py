#!/usr/bin/env python3
"""
Interactive RAG CLI - Terminal-based interface for RAG queries

Usage:
    python -m app.cli.main

    Or with environment variables:
    APP_ENV=dev GEMINI_API_KEY=your_key python -m app.cli.main
"""

import sys
from pathlib import Path
from typing import Any, Dict

import constants
from app.chain_rag.chain import RAGChain
from config import Config
from logger import get_logger

logger = get_logger(__name__)

# CLI Constants
CLI_BANNER_WIDTH = 70
CLI_SEPARATOR = "-" * CLI_BANNER_WIDTH
CLI_DOUBLE_SEPARATOR = "=" * CLI_BANNER_WIDTH
CLI_ANSWER_MAX_LINE_LENGTH = 70

# CLI Commands
CMD_QUIT = "quit"
CMD_EXIT = "exit"
CMD_Q = "q"
CMD_HELP = "help"

# CLI Messages
MSG_WELCOME_BANNER = "🤖 RAG SYSTEM - Interactive Terminal Interface"
MSG_TIPS_HEADER = "💡 Tips:"
MSG_TIP_QUESTION = "  - Type your question and press Enter"
MSG_TIP_EXIT = "  - Type 'quit', 'exit', or 'q' to exit"
MSG_TIP_HELP = "  - Type 'help' for more information"
MSG_GOODBYE = "\n👋 Goodbye!\n"
MSG_INTERRUPTED = "\n\n👋 Interrupted by user. Goodbye!\n"
MSG_EMPTY_QUESTION = "⚠️  Please enter a question"
MSG_PROCESSING = "\n⏳ Processing query..."
MSG_INITIALIZING_CONFIG = "🔧 Initializing configuration..."
MSG_INITIALIZING_RAG = "🚀 Initializing RAG chain..."
MSG_RAG_INITIALIZED = "✅ RAG chain initialized successfully!"
MSG_INIT_ERROR = "\n❌ Initialization Error: {}"
MSG_QUERY_ERROR = "\n❌ Error: {}\n"
MSG_PROMPT = "\n🔍 Your Question: "

# Help Messages
MSG_HELP_HEADER = "\n📖 HELP:"
MSG_HELP_ASK = "  - Ask any question about your indexed documents"
MSG_HELP_RETRIEVAL = (
    "  - The system will retrieve relevant chunks and generate an answer"
)
MSG_HELP_SOURCES = "  - Sources are shown with each answer"
MSG_HELP_EXIT = "  - Type 'quit' or 'exit' to leave\n"

# Troubleshooting Messages
MSG_TROUBLESHOOTING_HEADER = "\nTroubleshooting:"
MSG_TROUBLESHOOTING_ENV = "  1. Make sure APP_ENV is set (e.g., APP_ENV=dev)"
MSG_TROUBLESHOOTING_KEY = (
    "  2. Check that your API key is set (e.g., GEMINI_API_KEY=xxx)"
)
MSG_TROUBLESHOOTING_DOCS = "  3. Ensure documents are indexed in the vector store\n"

# Result Display
MSG_ANSWER_HEADER = "📝 ANSWER:"
MSG_SOURCES_HEADER = "📚 SOURCES ({} documents):"
MSG_NO_SOURCES = "  No sources found"
MSG_ANSWER_FOUND = "Answer Found: {}"


def print_banner():
    """Print welcome banner."""
    print(f"\n{CLI_DOUBLE_SEPARATOR}")
    print(f"   {MSG_WELCOME_BANNER}")
    print(CLI_DOUBLE_SEPARATOR)
    print()


def print_separator():
    """Print section separator."""
    print(CLI_SEPARATOR)


def print_tips():
    """Print usage tips."""
    print(MSG_TIPS_HEADER)
    print(MSG_TIP_QUESTION)
    print(MSG_TIP_EXIT)
    print(MSG_TIP_HELP)
    print()
    print_separator()


def print_help():
    """Print help information."""
    print(MSG_HELP_HEADER)
    print(MSG_HELP_ASK)
    print(MSG_HELP_RETRIEVAL)
    print(MSG_HELP_SOURCES)
    print(MSG_HELP_EXIT)


def print_troubleshooting():
    """Print troubleshooting tips."""
    print(MSG_TROUBLESHOOTING_HEADER)
    print(MSG_TROUBLESHOOTING_ENV)
    print(MSG_TROUBLESHOOTING_KEY)
    print(MSG_TROUBLESHOOTING_DOCS)


def get_model_name(config: Config) -> str:
    """
    Get the configured LLM model name based on provider.

    Args:
        config: Configuration instance

    Returns:
        Model name string
    """
    provider = config.rag.provider.lower()

    if provider == constants.LLM_PROVIDER_GOOGLE:
        return config.rag.google.model

    if provider == constants.LLM_PROVIDER_OPENAI:
        return config.rag.openai.model

    if provider == constants.LLM_PROVIDER_ANTHROPIC:
        return config.rag.anthropic.model

    return "unknown"


def print_config_info(config: Config):
    """
    Print configuration information.

    Args:
        config: Configuration instance
    """
    print(f"   Provider: {config.rag.provider}")
    print(f"   Model: {get_model_name(config)}")
    print(f"   Vector Store: {config.vectorstore.provider}")
    print()


def wrap_text(text: str, max_length: int = CLI_ANSWER_MAX_LINE_LENGTH) -> None:
    """
    Print text with word wrapping.

    Args:
        text: Text to wrap and print
        max_length: Maximum line length
    """
    words = text.split()
    line = ""

    for word in words:
        if len(line) + len(word) + 1 <= max_length:
            line += word + " "
            continue

        print("  " + line.strip())
        line = word + " "

    if line:
        print("  " + line.strip())


def format_source(source: Dict[str, Any], index: int) -> str:
    """
    Format a single source document.

    Args:
        source: Source document dictionary
        index: Source index number

    Returns:
        Formatted source string
    """
    metadata = source.get("metadata", {})
    source_path = metadata.get(constants.META_SOURCE, "unknown")

    filename = Path(source_path).name if source_path != "unknown" else "unknown"

    content_preview = source.get("content", "")[:150]
    if len(source.get("content", "")) > 150:
        content_preview += "..."

    lines = [f"  [{index}] {filename}", f"      {content_preview}", ""]

    return "\n".join(lines)


def format_sources(sources: list) -> str:
    """
    Format source documents for display.

    Args:
        sources: List of source documents

    Returns:
        Formatted sources string
    """
    if not sources:
        return MSG_NO_SOURCES

    formatted = []
    for i, source in enumerate(sources, 1):
        formatted.append(format_source(source, i))

    return "\n".join(formatted)


def display_result(result: Dict[str, Any]):
    """
    Display query result in a formatted way.

    Args:
        result: Query result dictionary
    """
    print()
    print_separator()

    # Display answer
    print(MSG_ANSWER_HEADER)
    print()

    answer = result.get(constants.RESPONSE_KEY_ANSWER, "No answer generated")
    wrap_text(answer)

    print()

    # Display has_answer status
    has_answer = result.get(constants.RESPONSE_KEY_HAS_ANSWER, False)
    status_icon = "✅" if has_answer else "❌"
    print(f"{status_icon} {MSG_ANSWER_FOUND.format(has_answer)}")

    print()
    print_separator()

    # Display sources
    sources = result.get(constants.RESPONSE_KEY_SOURCES, [])
    print(MSG_SOURCES_HEADER.format(len(sources)))
    print()
    print(format_sources(sources))

    print_separator()
    print()


def is_exit_command(question: str) -> bool:
    """
    Check if the question is an exit command.

    Args:
        question: User input

    Returns:
        True if exit command, False otherwise
    """
    return question.lower() in [CMD_QUIT, CMD_EXIT, CMD_Q]


def is_help_command(question: str) -> bool:
    """
    Check if the question is a help command.

    Args:
        question: User input

    Returns:
        True if help command, False otherwise
    """
    return question.lower() == CMD_HELP


def process_user_input(question: str, rag_chain: RAGChain) -> bool:
    """
    Process user input and return whether to continue.

    Args:
        question: User input
        rag_chain: RAG chain instance

    Returns:
        True to continue loop, False to exit
    """
    # Guard: Empty question
    if not question:
        print(MSG_EMPTY_QUESTION)
        return True

    # Guard: Exit command
    if is_exit_command(question):
        print(MSG_GOODBYE)
        return False

    # Guard: Help command
    if is_help_command(question):
        print_help()
        return True

    # Process query
    try:
        print(MSG_PROCESSING)
        result = rag_chain.query(question)
        display_result(result)
    except Exception as e:
        print(MSG_QUERY_ERROR.format(e))

    return True


def run_interactive_loop(rag_chain: RAGChain):
    """
    Run interactive query loop.

    Args:
        rag_chain: Initialized RAG chain instance
    """
    print_tips()

    while True:
        try:
            question = input(MSG_PROMPT).strip()
            should_continue = process_user_input(question, rag_chain)

            if not should_continue:
                break

        except KeyboardInterrupt:
            print(MSG_INTERRUPTED)
            break


def initialize_config() -> Config:
    """
    Initialize configuration.

    Returns:
        Initialized Config instance
    """
    print(MSG_INITIALIZING_CONFIG)
    config = Config()
    print_config_info(config)
    return config


def initialize_rag_chain(config: Config) -> RAGChain:
    """
    Initialize RAG chain.

    Args:
        config: Configuration instance

    Returns:
        Initialized RAG chain instance
    """
    print(MSG_INITIALIZING_RAG)
    rag_chain = RAGChain(config=config)
    print(MSG_RAG_INITIALIZED)
    print()
    return rag_chain


def run_cli():
    """Main CLI entry point."""
    print_banner()

    try:
        config = initialize_config()
        rag_chain = initialize_rag_chain(config)
        run_interactive_loop(rag_chain)

    except Exception as e:
        print(MSG_INIT_ERROR.format(e))
        print_troubleshooting()
        sys.exit(1)


if __name__ == "__main__":
    run_cli()
