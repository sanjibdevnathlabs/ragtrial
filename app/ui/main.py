"""
Streamlit UI for RAG Chat Application.

Features:
- Chat interface with streaming responses
- File upload and document management
- Multi-tab interface (Chat, Analytics, About)
- Source citations
- Chat history export
- Session analytics
"""

import time
from pathlib import Path
from typing import Any, Dict

import streamlit as st

import constants
import trace.codes as codes
from app.chain_rag.chain import RAGChain
from config import Config
from logger import get_logger

logger = get_logger(__name__)


# Page configuration
st.set_page_config(
    page_title=constants.UI_PAGE_TITLE,
    page_icon=constants.UI_PAGE_ICON,
    layout=constants.UI_LAYOUT,
    initial_sidebar_state=constants.UI_SIDEBAR_STATE,
)


@st.cache_resource
def get_rag_chain() -> RAGChain:
    """
    Initialize RAG chain (cached to avoid re-initialization).

    Returns:
        Initialized RAG chain
    """
    config = Config()
    logger.info(codes.UI_INITIALIZING_SERVICES)
    return RAGChain(config)


def initialize_session_state() -> None:
    """Initialize Streamlit session state variables."""
    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "rag_chain" not in st.session_state:
        with st.spinner(constants.UI_MSG_INITIALIZING_SERVICES):
            st.session_state.rag_chain = get_rag_chain()
            logger.info(codes.UI_SERVICES_INITIALIZED)


def display_sidebar() -> None:
    """Display sidebar with document management and settings."""
    with st.sidebar:
        st.title(constants.UI_TITLE_DOCUMENT_MANAGEMENT)

        # File upload section
        st.subheader(constants.UI_TITLE_UPLOAD_DOCUMENTS)
        uploaded_file = st.file_uploader(
            constants.UI_FILE_UPLOAD_LABEL,
            type=constants.UI_FILE_TYPES,
            help=constants.UI_FILE_UPLOAD_HELP,
        )

        if uploaded_file:
            if st.button(constants.UI_BUTTON_UPLOAD_INDEX, use_container_width=True):
                with st.spinner(f"{constants.UI_MSG_UPLOADING} {uploaded_file.name}..."):
                    try:
                        logger.info(
                            codes.UI_FILE_UPLOAD_STARTED,
                            filename=uploaded_file.name,
                        )

                        # Save file
                        file_bytes = uploaded_file.read()
                        file_path = Path("source_docs") / uploaded_file.name
                        file_path.parent.mkdir(exist_ok=True)
                        file_path.write_bytes(file_bytes)

                        st.success(f"{constants.UI_MSG_UPLOAD_SUCCESS}: {uploaded_file.name}")
                        st.info(constants.UI_MSG_UPLOAD_HINT)

                        logger.info(
                            codes.UI_FILE_UPLOAD_COMPLETED,
                            filename=uploaded_file.name,
                        )

                    except Exception as e:
                        logger.error(
                            codes.UI_FILE_UPLOAD_FAILED,
                            filename=uploaded_file.name,
                            error=str(e),
                            exc_info=True,
                        )
                        st.error(f"{constants.UI_MSG_UPLOAD_FAILED}: {str(e)}")

        st.divider()

        # Document list
        st.subheader(constants.UI_TITLE_INDEXED_DOCUMENTS)
        try:
            files = list(Path("source_docs").glob("*.*"))

            if files:
                st.metric(constants.UI_METRIC_TOTAL_DOCUMENTS, len(files))

                with st.expander("View All Documents"):
                    for file in files[:10]:  # Show first 10
                        st.text(f"• {file.name}")

                    if len(files) > 10:
                        st.caption(f"... and {len(files) - 10} more")
            else:
                st.info(constants.UI_MSG_NO_DOCUMENTS)

        except Exception:
            st.warning(constants.UI_MSG_COULD_NOT_LIST_DOCUMENTS)

        st.divider()

        # RAG configuration
        st.subheader(constants.UI_TITLE_CONFIGURATION)
        config = Config()
        st.code(
            f"""
LLM: {config.rag.provider}
Model: {config.rag.get_provider_config().model}
Embeddings: {config.embeddings.provider}
Vector Store: {config.vectorstore.provider}
        """,
            language="yaml",
        )

        st.divider()

        # Session statistics
        st.subheader(constants.UI_TITLE_STATISTICS)
        user_messages = len(
            [m for m in st.session_state.messages if m["role"] == constants.UI_CHAT_ROLE_USER]
        )
        st.metric(constants.UI_METRIC_QUESTIONS_ASKED, user_messages)

        st.divider()

        # Actions
        st.subheader(constants.UI_TITLE_ACTIONS)

        col1, col2 = st.columns(2)

        with col1:
            if st.button(constants.UI_BUTTON_CLEAR_CHAT, use_container_width=True):
                st.session_state.messages = []
                st.rerun()

        with col2:
            if st.button(constants.UI_BUTTON_EXPORT_CHAT, use_container_width=True):
                export_chat_history()


def export_chat_history() -> None:
    """Export chat history to markdown file."""
    if not st.session_state.messages:
        st.warning(constants.UI_MSG_NO_MESSAGES_TO_EXPORT)
        return

    logger.info(codes.UI_CHAT_EXPORT_STARTED)

    # Create export content
    export_content = f"{constants.UI_EXPORT_HEADER}\n\n"
    export_content += f"{constants.UI_EXPORT_TIMESTAMP_LABEL} {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n"

    for msg in st.session_state.messages:
        role = msg["role"].title()
        content = msg["content"]
        export_content += f"## {role}\n\n{content}\n\n"

        if msg.get("sources"):
            export_content += f"{constants.UI_EXPORT_SOURCES_LABEL}\n"
            for idx, source in enumerate(msg["sources"], 1):
                filename = source.get("filename", constants.UI_SOURCE_FILENAME_UNKNOWN)
                export_content += f"{idx}. {filename}\n"
            export_content += "\n"

    # Offer download
    st.download_button(
        label=constants.UI_EXPORT_DOWNLOAD_LABEL,
        data=export_content,
        file_name=f"{constants.UI_EXPORT_FILENAME_PREFIX}{int(time.time())}{constants.UI_EXPORT_FILENAME_SUFFIX}",
        mime=constants.UI_EXPORT_MIME_TYPE,
    )

    logger.info(codes.UI_CHAT_EXPORT_COMPLETED)


def display_chat_message(role: str, content: str, sources: list = None) -> None:
    """
    Display a chat message with optional sources.

    Args:
        role: Message role (user/assistant)
        content: Message content
        sources: Optional list of source documents
    """
    with st.chat_message(role):
        st.markdown(content)

        if sources:
            source_count = len(sources)
            label = constants.UI_VIEW_N_SOURCES_LABEL.format(source_count)

            with st.expander(label):
                for idx, source in enumerate(sources, 1):
                    col1, col2 = st.columns([1, 3])

                    with col1:
                        st.markdown(f"**{constants.UI_SOURCE_LABEL_PREFIX} {idx}**")
                        filename = source.get("filename", constants.UI_SOURCE_FILENAME_UNKNOWN)
                        st.caption(filename)

                    with col2:
                        content_preview = source.get("content", "")[:300] + "..."
                        st.text_area(
                            label=f"{constants.UI_SOURCE_CONTENT_LABEL} {idx}",
                            value=content_preview,
                            height=100,
                            disabled=True,
                            label_visibility="collapsed",
                        )

                    if idx < len(sources):
                        st.divider()


def process_user_query(question: str) -> Dict[str, Any]:
    """
    Process user query through RAG chain.

    Args:
        question: User's question

    Returns:
        Response dictionary with answer and sources
    """
    try:
        logger.info(codes.UI_QUERY_PROCESSING, question=question[:100])
        response = st.session_state.rag_chain.query(question)
        logger.info(codes.UI_QUERY_COMPLETED)
        return response

    except ValueError as e:
        # Validation or security error
        logger.warning(codes.UI_QUERY_FAILED, error=str(e))
        return {
            "success": False,
            "answer": f"⚠️ **Error:** {str(e)}",
            "sources": [],
            "has_answer": False,
        }

    except Exception as e:
        # Unexpected error
        logger.error(codes.UI_QUERY_FAILED, error=str(e), exc_info=True)
        return {
            "success": False,
            "answer": "❌ **Error:** An unexpected error occurred. Please try again.",
            "sources": [],
            "has_answer": False,
        }


def render_chat_tab() -> None:
    """Render the chat interface tab."""
    # Display chat history
    for message in st.session_state.messages:
        display_chat_message(
            role=message["role"],
            content=message["content"],
            sources=message.get("sources"),
        )

    # Chat input
    if question := st.chat_input(constants.UI_CHAT_INPUT_PLACEHOLDER):
        # Add user message to chat
        st.session_state.messages.append(
            {
                "role": constants.UI_CHAT_ROLE_USER,
                "content": question,
            }
        )

        # Display user message
        display_chat_message(constants.UI_CHAT_ROLE_USER, question)

        # Process query with progress indicator
        with st.spinner(constants.UI_MSG_THINKING):
            response = process_user_query(question)

        # Add assistant response to chat
        assistant_message = {
            "role": constants.UI_CHAT_ROLE_ASSISTANT,
            "content": response.get("answer", "I couldn't generate an answer."),
            "sources": response.get("sources", []),
        }
        st.session_state.messages.append(assistant_message)

        # Display assistant response
        display_chat_message(
            role=constants.UI_CHAT_ROLE_ASSISTANT,
            content=assistant_message["content"],
            sources=assistant_message["sources"],
        )


def render_analytics_tab() -> None:
    """Render the analytics dashboard tab."""
    st.subheader(constants.UI_TITLE_ANALYTICS)

    if st.session_state.messages:
        col1, col2, col3 = st.columns(3)

        user_msgs = [
            m
            for m in st.session_state.messages
            if m["role"] == constants.UI_CHAT_ROLE_USER
        ]
        assistant_msgs = [
            m
            for m in st.session_state.messages
            if m["role"] == constants.UI_CHAT_ROLE_ASSISTANT
        ]

        with col1:
            st.metric(constants.UI_METRIC_TOTAL_MESSAGES, len(st.session_state.messages))

        with col2:
            st.metric(constants.UI_METRIC_QUESTIONS_ASKED, len(user_msgs))

        with col3:
            avg_sources = (
                sum(len(m.get("sources", [])) for m in assistant_msgs)
                / max(len(assistant_msgs), 1)
            )
            st.metric(constants.UI_METRIC_AVG_SOURCES, f"{avg_sources:.1f}")

        # Recent questions
        st.subheader("Recent Questions")
        for msg in user_msgs[-5:]:
            st.text(f"• {msg['content']}")
    else:
        st.info("Start chatting to see analytics")


def render_about_tab() -> None:
    """Render the about/information tab."""
    st.subheader(constants.UI_TITLE_ABOUT)
    st.markdown(
        """
    This is a **RAG (Retrieval-Augmented Generation)** application that lets you:

    - 📤 **Upload documents** (PDF, TXT, MD, DOCX, CSV, JSON)
    - 🔍 **Ask questions** about your documents
    - 🤖 **Get AI-powered answers** with source citations
    - 💬 **Chat naturally** with context awareness

    ### How It Works

    1. **Upload** your documents using the sidebar
    2. **Index** them by running ingestion (`python ingestion/ingest.py`)
    3. **Ask questions** in the chat interface
    4. **Get answers** with source citations

    ### Technology Stack

    - **Frontend:** Streamlit
    - **Backend:** FastAPI
    - **RAG Framework:** LangChain
    - **Vector Store:** ChromaDB (configurable)
    - **LLM:** Google Gemini (configurable)

    ### Architecture

    This application uses a **unified architecture** where:
    - FastAPI serves as the main server (port 8000)
    - Streamlit UI is embedded and accessible at `/langchain/chat`
    - API endpoints are available at `/api/v1/*`
    - API documentation is at `/docs`

    ### Need Help?

    - [API Docs](http://localhost:8000/docs)
    - [GitHub Repository](#)
    - [User Guide](#)
    """
    )


def main() -> None:
    """Main Streamlit application."""
    initialize_session_state()

    # Header
    st.title(constants.UI_PAGE_TITLE)
    st.caption("Upload documents, ask questions, and get AI-powered answers")

    # Sidebar
    display_sidebar()

    # Main content area with tabs
    tab1, tab2, tab3 = st.tabs(
        [
            constants.UI_TAB_CHAT,
            constants.UI_TAB_ANALYTICS,
            constants.UI_TAB_ABOUT,
        ]
    )

    with tab1:
        render_chat_tab()

    with tab2:
        render_analytics_tab()

    with tab3:
        render_about_tab()


if __name__ == "__main__":
    main()
