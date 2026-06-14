import os
import re

import streamlit as st
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain_core.prompts import PromptTemplate
from pinecone import Pinecone
from rank_bm25 import BM25Okapi

load_dotenv()

MODEL = "gpt-4.1-mini"
EMBEDDING_MODEL = "text-embedding-3-small"
EMBEDDING_DIMENSIONS = 512
PINECONE_NAMESPACE = "enterprise-company-policies"
SCORE_THRESHOLD = 0.45
RETRIEVAL_K = 10
RERANK_TOP_N = 5
VECTOR_WEIGHT = 0.6

RAG_TEMPLATE = """You are an enterprise-support assistant that helps EMPLOYEES with questions about INTERNAL COMPANY POLICIES (HR, IT, Finance, Legal, Facilities, Marketing, and Sales operations).

You do NOT have any information about external customers' orders, shipments, deliveries, tracking, charges, refunds, or returns of the company's products. If the issue is about an external customer's order, shipping, delivery, billing, or return, OR if the context below does not directly and clearly address the issue, respond with exactly:
"I don't have that information about this."

Do not guess, do not state a "likely cause", and do not try to relate unrelated policy topics to the issue.

If the context is relevant, be concise and practical: state the relevant policy and the next step the agent should take.

Context:
{context}

employee issue: {question}

Support guidance:"""

st.set_page_config(page_title="EnterPrise TLDR", page_icon="📘", layout="wide")

st.markdown(
    """
    <style>
    .block-container { padding-top: 2.5rem; }

    .app-title {
        text-align: center;
        font-size: 2.75rem;
        font-weight: 800;
        margin-bottom: 0.1rem;
        letter-spacing: 0.5px;
    }
    .app-subtitle {
        text-align: center;
        color: #8b8f99;
        font-size: 1.05rem;
        margin-bottom: 1.5rem;
    }

    /* "New chat" pill button */
    .st-key-new_chat_btn button {
        font-size: 1.05rem;
        font-weight: 600;
        height: 3.2rem;
        padding: 0 1.4rem;
        border-radius: 2rem;
        line-height: 1;
        gap: 0.5rem;
        background: linear-gradient(135deg, #6f7bf7, #4f5fe0);
        border: none;
        color: #ffffff;
        box-shadow: 0 4px 14px rgba(79, 95, 224, 0.4);
        transition: transform 0.15s ease, box-shadow 0.15s ease;
        white-space: nowrap;
    }
    .st-key-new_chat_btn button:hover {
        background: linear-gradient(135deg, #7c87f9, #5a69e8);
        transform: scale(1.04);
        box-shadow: 0 6px 18px rgba(79, 95, 224, 0.5);
        color: #ffffff;
    }
    .st-key-new_chat_btn button:active {
        transform: scale(0.97);
    }

    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background-color: var(--background-color);
        border-right: 1px solid #e6e8f0;
    }
    section[data-testid="stSidebar"] .block-container {
        padding-top: 1.5rem;
    }

    /* Past-query history items */
    section[data-testid="stSidebar"] button {
        text-align: left;
        justify-content: flex-start;
        border-radius: 10px;
        padding: 0.65rem 0.9rem;
        margin-bottom: 0.5rem;
        border: 1px solid #dadff2;
        background-color: #e8eaf6;
        color: #3b3f47;
        font-size: 0.92rem;
        line-height: 1.3;
        white-space: normal;
        transition: background-color 0.15s ease, border-color 0.15s ease, transform 0.1s ease;
    }
    section[data-testid="stSidebar"] button:hover {
        background-color: #d8defa;
        border-color: #c7d0f5;
        color: #3b3f47;
        transform: translateX(2px);
    }
    section[data-testid="stSidebar"] button[kind="primary"] {
        background-color: #4f5fe0;
        border-color: #4f5fe0;
        color: #ffffff;
        font-weight: 600;
    }
    section[data-testid="stSidebar"] button[kind="primary"]:hover {
        background-color: #4350c4;
        border-color: #4350c4;
    }

    /* Response area card */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        border-radius: 16px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_resource
def get_rag_pipeline():
    embeddings = OpenAIEmbeddings(model=EMBEDDING_MODEL, dimensions=EMBEDDING_DIMENSIONS)
    pc = Pinecone(api_key=os.environ["PINECONE_API_KEY"])
    index = pc.Index(os.environ["PINECONE_INDEX_NAME"])
    vector_store = PineconeVectorStore(
        index=index, embedding=embeddings, namespace=PINECONE_NAMESPACE
    )
    llm = ChatOpenAI(model=MODEL)
    prompt_template = PromptTemplate.from_template(RAG_TEMPLATE)
    return vector_store, llm, prompt_template


def _tokenize(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", text.lower())


def rerank_documents(question: str, retrieved: list, top_n: int = RERANK_TOP_N) -> list:
    """Hybrid rerank: combine vector similarity with BM25 keyword overlap."""
    docs = [doc for doc, _ in retrieved]
    vector_scores = [score for _, score in retrieved]

    bm25 = BM25Okapi([_tokenize(doc.page_content) for doc in docs])
    bm25_scores = bm25.get_scores(_tokenize(question))

    def normalize(values):
        lo, hi = min(values), max(values)
        if hi == lo:
            return [0.0 for _ in values]
        return [(v - lo) / (hi - lo) for v in values]

    norm_vector = normalize(vector_scores)
    norm_bm25 = normalize(bm25_scores)

    combined = [
        VECTOR_WEIGHT * v + (1 - VECTOR_WEIGHT) * b
        for v, b in zip(norm_vector, norm_bm25)
    ]

    ranked = sorted(zip(docs, combined), key=lambda pair: pair[1], reverse=True)
    return [doc for doc, _ in ranked[:top_n]]


def get_answer(question: str) -> str:
    if not os.environ.get("OPENAI_API_KEY"):
        return (
            "No OPENAI_API_KEY found. Set it as an environment variable "
            "(or in a .env file) to enable answers."
        )
    if not os.environ.get("PINECONE_API_KEY") or not os.environ.get("PINECONE_INDEX_NAME"):
        return (
            "No PINECONE_API_KEY / PINECONE_INDEX_NAME found. Set them as "
            "environment variables (or in a .env file) to enable answers."
        )

    vector_store, llm, prompt_template = get_rag_pipeline()

    retrieved = vector_store.similarity_search_with_score(question, k=RETRIEVAL_K)

    if not retrieved or retrieved[0][1] < SCORE_THRESHOLD:
        return "I don't have that information about this."

    relevant_docs = rerank_documents(question, retrieved)

    docs_content = "\n\n".join(doc.page_content for doc in relevant_docs)
    prompt = prompt_template.invoke({"question": question, "context": docs_content})
    response = llm.invoke(prompt)

    sources = list(dict.fromkeys(doc.metadata["title"] for doc in relevant_docs))
    answer = response.content
    if sources:
        answer += f"\n\n*Source(s): {', '.join(sources)}*"
    return answer


def summarize_conversation(messages: list[dict]) -> str:
    first_question = next((m["content"] for m in messages if m["role"] == "user"), "Conversation")
    summary = first_question.strip().replace("\n", " ")
    return summary[:60] + ("..." if len(summary) > 60 else "")


def start_new_chat():
    st.session_state.messages = []
    st.session_state.current_history_idx = None
    st.session_state.viewing_history_idx = None


if "messages" not in st.session_state:
    st.session_state.messages = []
if "history" not in st.session_state:
    st.session_state.history = []
if "viewing_history_idx" not in st.session_state:
    st.session_state.viewing_history_idx = None
if "current_history_idx" not in st.session_state:
    st.session_state.current_history_idx = None

# ---- Left sidebar: Past Queries ----
with st.sidebar:
    st.markdown("### 🗂️ Past Queries")
    if not st.session_state.history:
        st.caption("No past conversations yet. Your chat history will appear here.")
    else:
        st.caption(f"{len(st.session_state.history)} saved conversation(s)")
        st.write("")
        for idx, conv in enumerate(st.session_state.history):
            is_selected = st.session_state.viewing_history_idx == idx
            label = f"💬 {conv['summary']}"
            if st.button(
                label,
                key=f"history_{idx}",
                use_container_width=True,
                type="primary" if is_selected else "secondary",
            ):
                st.session_state.viewing_history_idx = idx

# ---- Main area ----
header_left, header_center, header_right = st.columns([1, 5, 1])
with header_center:
    st.markdown("<div class='app-title'>📘 EnterPrise TLDR</div>", unsafe_allow_html=True)
    st.markdown(
        "<div class='app-subtitle'>Welcome to the Enterprise policies one-stop-shop Q&A chatbot.</div>",
        unsafe_allow_html=True,
    )
with header_right:
    st.write("")
    if st.button("✨ New Chat", key="new_chat_btn", help="Start a new chat", use_container_width=True):
        start_new_chat()
        st.rerun()

# ---- Question input ----
with st.form("question_form", clear_on_submit=True, border=False):
    input_col, ask_col = st.columns([10, 1])
    with input_col:
        question = st.text_input(
            "Question",
            placeholder="How can I help you?",
            label_visibility="collapsed",
        )
    with ask_col:
        submitted = st.form_submit_button("Ask", use_container_width=True, type="primary")

# ---- Handle a new question ----
if submitted and question.strip():
    if st.session_state.viewing_history_idx is not None:
        st.session_state.viewing_history_idx = None

    st.session_state.messages.append({"role": "user", "content": question.strip()})
    with st.spinner("Looking through policies..."):
        answer = get_answer(question.strip())
    st.session_state.messages.append({"role": "assistant", "content": answer})

    if st.session_state.current_history_idx is None:
        st.session_state.history.insert(
            0,
            {
                "summary": summarize_conversation(st.session_state.messages),
                "messages": st.session_state.messages,
            },
        )
        st.session_state.current_history_idx = 0

AVATARS = {"user": "🧑‍💼", "assistant": "📘"}

# ---- Main response area ----
st.write("")
with st.container(border=True, height=600):
    if st.session_state.viewing_history_idx is not None:
        conv = st.session_state.history[st.session_state.viewing_history_idx]
        st.markdown(f"📄 **Past conversation:** {conv['summary']}")
        st.divider()
        for m in conv["messages"]:
            with st.chat_message(m["role"], avatar=AVATARS.get(m["role"])):
                st.markdown(m["content"])
    elif not st.session_state.messages:
        st.markdown(
            "<div style='text-align:center; color:#9aa0ab; margin-top: 220px;'>"
            "💬 Ask a question above to get started — e.g. "
            "<i>\"How many sick days do I get per year?\"</i></div>",
            unsafe_allow_html=True,
        )
    else:
        for m in st.session_state.messages:
            with st.chat_message(m["role"], avatar=AVATARS.get(m["role"])):
                st.markdown(m["content"])
