"""
# DEPRECATED — Streamlit Frontend

This file is DEPRECATED. The primary UI is the Next.js frontend (`frontend/`).

Streamlit no longer performs:
  - Direct ingestion (replaced by FastAPI /api/import_remote and /api/upload)
  - Direct retrieval (replaced by FastAPI /api/chat)
  - Direct document/session management (replaced by FastAPI /api/*)

All RAG operations go through the canonical pipeline:
  extraction/extract_with_docid.py → core/rag_pipeline.py → core/vector_store_lance.py
"""

import os
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional

import streamlit as st
from dotenv import load_dotenv
import pandas as pd
from groq import Groq, BadRequestError
import base64
import re
from datetime import datetime
import httpx

API_BASE_URL = os.getenv("FASTAPI_URL", "http://localhost:8000")
httpx_client = httpx.Client(timeout=30.0)


def api_get_json(path: str) -> Any:
    resp = httpx_client.get(f"{API_BASE_URL}{path}")
    resp.raise_for_status()
    return resp.json()


def api_post_json(path: str, json_data: Any = None, files: Any = None) -> Any:
    if files:
        resp = httpx_client.post(f"{API_BASE_URL}{path}", files=files)
    else:
        resp = httpx_client.post(f"{API_BASE_URL}{path}", json=json_data or {})
    resp.raise_for_status()
    return resp.json()


# --------------------------------------------------------------------------------
# Groq client loader
# --------------------------------------------------------------------------------

def get_groq_client() -> Optional[Groq]:
    load_dotenv()
    key = os.getenv("GROQ_API_KEY")
    if not key:
        return None
    return Groq(api_key=key)


# --------------------------------------------------------------------------------
# LLM summarization & Expansion
# --------------------------------------------------------------------------------

def call_groq_intent(client: Groq, user_query: str) -> str:
    prompt = f"""You are an Intent Router for a Physics Notebook.
Analyze the user's input: "{user_query}"
4. Is this a command to import, ingest, or fetch a web link or URL into the database? (e.g. "import this link: https://xyz.com/file.pdf"). If so, output exactly "ACTION_IMPORT".
5. If the user is discussing your capabilities, giving you meta instructions, acting as your co-developer, or having a high-level conceptual discussion outside of the documents (e.g. "what are your capabilities", "why did you say that", "you are agent zero"). Output exactly "META_SYSTEM".
6. Is this a casual greeting? (e.g., "hi", "how are you"). Output "CONVERSATION".
7. If the user asks about physics logic or specific data (e.g., "show me graphs", "what are the tables", "tell me about CERN"). Output "RESEARCH".

You MUST output exactly ONE word: "CONVERSATION", "RESEARCH", "ACTION_IMPORT", or "META_SYSTEM". No other text."""
    try:
        resp = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.1-8b-instant",
            temperature=0.0,
            max_tokens=10,
        )
        ans = resp.choices[0].message.content.strip().upper()
        if "META_SYSTEM" in ans:
            return "META_SYSTEM"
        elif "CONVERSATION" in ans:
            return "CONVERSATION"
        elif "ACTION_IMPORT" in ans:
            return "ACTION_IMPORT"
        return "RESEARCH"
    except Exception:
        return "RESEARCH"

def call_groq_hyde(client: Groq, user_query: str) -> str:
    prompt = f"""You are an expert CERN particle physicist and materials scientist. 
A user has asked the following query: "{user_query}"
Respond with a highly technical, precise paragraph (3-4 sentences) that perfectly answers this question using advanced domain terminology. Do not include pleasantries. Only output the hypothetical answer block."""
    try:
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama3-8b-8192",
            temperature=0.3,
            max_tokens=200,
        )
        return chat_completion.choices[0].message.content.strip()
    except Exception as e:
        print(f"[HyDE Error] {e}")
        return user_query


def call_groq_summary(
    client: Groq,
    question: str,
    chat_history: List[Dict[str, Any]],
    text_hits: List[Dict[str, Any]],
    figure_hits: List[Dict[str, Any]],
    table_hits: List[Dict[str, Any]],
    temperature: float = 0.7,
    strict_source: bool = False,
) -> str:

    ctx = []
    ctx.append("CRITICAL SYSTEM IDENTITY: You are an advanced Agentic Multimodal Copilot. You DO HAVE full autonomous authorization and direct internal access to read external PDFs, images, and tables. The context provided to you below is literally the exact extracted content from the user's uploaded PDFs and URLs. NEVER state that you cannot access PDFs. NEVER state that you are a merely text-based AI. You are a visual and scientific assistant!\n\n")

    if strict_source:
        ctx.append("You are a careful scientific assistant. IMPORTANT: Only use information from the context below.\n")
        ctx.append("If the user's message is a simple conversational greeting (e.g., 'hi', 'hello'), politely greet them back.\n")
        ctx.append("For all actual questions, if the answer is not in the provided context, you MUST strictly say: 'This information is not available in the provided source.'\n")
        ctx.append("Do NOT make up, infer, or generate information beyond what is explicitly provided.\n\n")
    else:
        ctx.append("You are an assistant helping with scientific PDFs (CERN reports).\n")
        ctx.append("Try to base your answers on the provided context if possible, but you may use external knowledge if needed.\n")
        ctx.append("IMPORTANT: If you are drawing from your own external knowledge, DO NOT append citation brackets like [C1]. Only use citation brackets for facts explicitly found in the context below.\n\n")
        
    ctx.append(f"User question:\n{question}\n")
    ctx.append("For facts drawn from the context, you MUST rigorously cite your sources natively inside your sentences (e.g., append '[C1]'). DO NOT make up fake citations.\n")
    ctx.append("Relevant context (text + figures + tables):\n")

    idx = 1
    for h in text_hits:
        ctx.append(f"### [C{idx}] (TEXT, Page {h.get('page')})")
        ctx.append(h.get("text","")[:1200] + "\n")
        h["citation_id"] = f"[C{idx}]"
        idx += 1

    for h in figure_hits:
        ctx.append(f"### [C{idx}] (FIGURE, Page {h.get('page')})")
        ctx.append(h.get("text","")[:800] + "\n")
        h["citation_id"] = f"[C{idx}]"
        idx += 1

    for h in table_hits:
        ctx.append(f"### [C{idx}] (TABLE, Page {h.get('page')})")
        ctx.append(h.get("text","")[:800] + "\n")
        h["citation_id"] = f"[C{idx}]"
        idx += 1

    ctx.append("Provide a concise structured answer and flawlessly include the citation tags inside your sentences.\n")
    ctx.append("\n--- \nIMPORTANT: You MUST conclude your response by generating exactly 3 short, insightful follow-up questions the user can ask related to this topic context. Format them as a numbered list under the heading '**Suggested Follow-Ups:**'.\n")
    context_str = "\n".join(ctx)

    sys_msg = {"role": "system", "content": ("You are a careful scientific assistant that strictly adheres to source material." if strict_source else "You are a careful scientific assistant.")}
    
    api_messages = [sys_msg]
    if chat_history:
        for m in chat_history[-6:-1]:
            api_messages.append({"role": m["role"], "content": str(m["content"])})
            
    api_messages.append({"role": "user", "content": context_str})

    models = [
        "llama-3.3-70b-versatile",
        "llama-3.1-70b-versatile",
        "llama-3.2-3b-preview",
    ]

    for m in models:
        try:
            resp = client.chat.completions.create(
                model=m,
                messages=api_messages,
                max_tokens=1100,
                temperature=temperature,
            )
            return resp.choices[0].message.content
        except BadRequestError as e:
            if "model_decommissioned" in str(e):
                continue
            return f"(LLM error: {e})"
        except Exception as e:
            return f"(LLM failed: {e})"

    return "(LLM summarization failed)"


# --------------------------------------------------------------------------------
# CSS — ChatGPT style
# --------------------------------------------------------------------------------

THIS_FILE = Path(__file__).resolve()
PROJECT_ROOT = THIS_FILE.parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core.ui_theme import inject_css


# --------------------------------------------------------------------------------
# Rendering helpers
# --------------------------------------------------------------------------------

def render_text_tab(text_hits, doc_mgr_data):
    if not text_hits:
        st.info("No text retrieved.")
        return
    for h in text_hits:
        page = h.get("page")
        score = h.get("score", 0.0)
        title = h.get("title")
        summary = h.get("summary")
        keywords = h.get("keywords")
        doc_id = h.get("doc_id")
        
        display_title = f"{title} (Page {page})" if title else f"Page {page} • score {score:.3f}"
        
        with st.expander(display_title, expanded=False):
            doc_meta = next((d for d in doc_mgr_data if d.get("doc_id") == doc_id), None) if doc_mgr_data else None
            source_str = doc_meta.get("filename") if doc_meta else h.get("source", doc_id)
            if not source_str or source_str == "default":
                source_str = "CERN Document"
                
            st.markdown(f"**📄 Source Document:** `{source_str}`")
            
            if doc_meta:
                url = doc_meta.get("url")
                if url:
                    st.markdown(f"[🔗 Open Original Source URL]({url})")

            if summary:
                st.markdown(f"**📝 Summary:** {summary}")
            if keywords:
                st.markdown(f"**🏷️ Keywords:** {keywords}")
            st.markdown("---")
            st.markdown(h.get("text", "")[:2000])


def render_figures_tab(figure_hits, doc_mgr_data):
    if not figure_hits:
        st.info("No figures retrieved.")
        return
    for h in figure_hits:
        page = h.get("page")
        score = h.get("score", 0.0)
        img = h.get("image_path")
        doc_id = h.get("doc_id")
        
        with st.expander(f"Figure (Page {page}) • score {score:.3f}", expanded=False):
            doc_meta = next((d for d in doc_mgr_data if d.get("doc_id") == doc_id), None) if doc_mgr_data else None
            source_str = doc_meta.get("filename") if doc_meta else h.get("source", doc_id)
            if not source_str or source_str == "default":
                source_str = "CERN Document"
                
            st.markdown(f"**📄 Source Document:** `{source_str}`")
            if doc_meta:
                url = doc_meta.get("url")
                if url:
                    st.markdown(f"[🔗 Open Original Source URL]({url})")

            st.markdown(h.get("text", "")[:800])
            if img and os.path.exists(img):
                st.image(img, width=250)
                with st.expander("Open larger"):
                    st.image(img, use_column_width=True)


def render_tables_tab(table_hits, doc_mgr_data):
    if not table_hits:
        st.info("No tables retrieved.")
        return

    for h in table_hits:
        page = h.get("page")
        score = h.get("score", 0.0)
        csv_path = h.get("table_csv")
        doc_id = h.get("doc_id")

        with st.expander(f"Table (Page {page}) • score {score:.3f}", expanded=False):
            doc_meta = next((d for d in doc_mgr_data if d.get("doc_id") == doc_id), None) if doc_mgr_data else None
            source_str = doc_meta.get("filename") if doc_meta else h.get("source", doc_id)
            if not source_str or source_str == "default":
                source_str = "CERN Document"
                
            st.markdown(f"**📄 Source Document:** `{source_str}`")
            if doc_meta:
                url = doc_meta.get("url")
                if url:
                    st.markdown(f"[🔗 Open Original Source URL]({url})")

            st.markdown(h.get("text", "")[:800])

            if csv_path and os.path.exists(csv_path):
                try:
                    df = pd.read_csv(csv_path)
                    st.dataframe(df.head(8), height=160)
                    with st.expander("Show full table"):
                        st.dataframe(df)
                except Exception as e:
                    st.error(f"Failed to load CSV: {e}")
            else:
                st.warning(f"CSV not found: {csv_path}")


# --------------------------------------------------------------------------------
# MAIN APP
# --------------------------------------------------------------------------------

def run():
    st.set_page_config(page_title="CERN Multimodal RAG", layout="wide")
    inject_css()

    st.title("🔬 CERN Multimodal RAG")
    st.caption("Intelligent Physics Notebook • DEPRECATED — use Next.js frontend")

    # -------------------------------------------------------------
    # Session Manager Panel (Sidebar) — via API
    # -------------------------------------------------------------
    st.sidebar.header("💬 Conversation History")
    
    try:
        sessions = api_get_json("/api/sessions")
    except Exception:
        sessions = []
    
    if "active_session_id" not in st.session_state:
        try:
            new_ = api_post_json("/api/sessions")
            st.session_state.active_session_id = new_["id"]
        except Exception:
            st.session_state.active_session_id = "fallback"
        st.session_state.chat = []
        
    col1, col2 = st.sidebar.columns([4, 1])
    with col1:
        session_opts = {}
        for s in sessions:
            mtime = datetime.fromtimestamp(s["mod_time"]).strftime('%b %d') if "mod_time" in s else ""
            session_opts[s["id"]] = f"{s['title'][:25]} ({mtime})"
            
        if st.session_state.active_session_id not in session_opts:
            session_opts[st.session_state.active_session_id] = "New Conversation..."
            
        options_list = list(session_opts.keys())
        current_index = options_list.index(st.session_state.active_session_id) if st.session_state.active_session_id in options_list else 0
        
        selected_session = st.selectbox(
            "Select Session:",
            options=options_list,
            format_func=lambda x: session_opts[x],
            index=current_index,
            label_visibility="collapsed"
        )
        
    with col2:
        if st.button("➕", help="New Chat"):
            try:
                new_ = api_post_json("/api/sessions")
                st.session_state.active_session_id = new_["id"]
            except Exception:
                st.session_state.active_session_id = "fallback"
            st.session_state.chat = []
            st.rerun()

    if selected_session != st.session_state.active_session_id:
        st.session_state.active_session_id = selected_session
        try:
            st.session_state.chat = api_get_json(f"/api/chat/{selected_session}")
        except Exception:
            st.session_state.chat = []
        st.rerun()

    st.sidebar.markdown("---")

    # -------------------------------------------------------------
    # Notebook Sources Panel (Sidebar) — via API
    # -------------------------------------------------------------
    st.sidebar.header("📚 Notebook Sources")
    
    try:
        docs_data = api_get_json("/api/all_documents")
        registered_docs = docs_data.get("documents", [])
    except Exception:
        registered_docs = []
    
    active_docs = []
    
    if not registered_docs:
        st.sidebar.info("No sources in your notebook yet.")
    else:
        st.sidebar.markdown("Select which sources to chat with:")
        for d in registered_docs:
            doc_id = d.get("doc_id", "")
            if st.sidebar.checkbox(f"📄 {doc_id}", value=True, key=f"chk_{doc_id}"):
                active_docs.append(doc_id)
                
    search_doc_ids = active_docs if active_docs else None

    st.sidebar.markdown("---")

    # Add Source — via API only
    st.sidebar.subheader("➕ Add New Source")
    url_input = st.sidebar.text_input("URL (Web or PDF)")
    upload = st.sidebar.file_uploader("Upload local PDF", type=["pdf"])
    custom_id = st.sidebar.text_input("Source ID (optional)")

    if st.sidebar.button("Import & Extract"):
        if url_input:
            try:
                with st.spinner("Importing remote source via API..."):
                    result = api_post_json("/api/import_remote", {"url": url_input, "doc_id": custom_id or None})
                    d_id = result.get("doc_id", "unknown")
                    st.sidebar.success(f"Import queued: {d_id}")
            except Exception as e:
                st.sidebar.error(f"Import failed: {e}")
        elif upload:
            try:
                with st.spinner("Uploading PDF via API..."):
                    files = {"file": (upload.name, upload.getvalue(), "application/pdf")}
                    result = api_post_json("/api/upload", files=files)
                    st.sidebar.success(f"Upload queued: {result.get('doc_id', 'unknown')}")
            except Exception as e:
                st.sidebar.error(f"Upload failed: {e}")
        else:
            st.sidebar.warning("Provide either a URL or upload a file.")
            
    st.sidebar.markdown("---")
    
    # Query Settings
    st.sidebar.subheader("⚙️ Agent Settings")
    temperature = st.sidebar.slider(
        "Temperature (0=strict source only, 1.0=creative):",
        min_value=0.0, max_value=1.0, value=0.7, step=0.1,
    )
    strict_source = temperature < 0.3
    if strict_source:
        st.sidebar.info("🔒 Strict Notebook Mode: Answers strictly tied to selected sources.")
    
    st.sidebar.markdown("---")

    # Chat history
    if "chat" not in st.session_state:
        st.session_state.chat: List[Dict[str, Any]] = []

    # --- User input
    user_query = st.chat_input("Ask something about the PDF...")
    
    if st.session_state.get("pending_auto_import_url"):
        user_query = f"Import {st.session_state.pending_auto_import_url}"
        st.session_state.pending_auto_import_url = None

    if user_query:
        st.session_state.chat.append({"role": "user", "content": user_query})

        client = get_groq_client()
        expanded_query = user_query
        
        intent = "RESEARCH"
        if client:
            intent = call_groq_intent(client, user_query)

        # ACTION_IMPORT — delegate to API
        url_match = re.search(r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+", user_query)
        if intent == "ACTION_IMPORT" and url_match:
            extracted_url = url_match.group(0)
            
            if "agent_logs" in st.session_state:
                st.session_state.agent_logs.append("> Orchestrator: Detected ACTION_IMPORT request.")
                st.session_state.agent_logs.append(f"> Orchestrator: Delegating to FastAPI. Target: {extracted_url}")
            
            st.session_state.chat.append({
                "role": "assistant",
                "content": f"⚙️ **Importing via API:** `{extracted_url}`",
            })
            
            try:
                with st.spinner("Importing via FastAPI..."):
                    result = api_post_json("/api/import_remote", {"url": extracted_url})
                    d_id = result.get("doc_id", "unknown")
                    st.session_state.chat.append({
                        "role": "assistant",
                        "content": f"✅ **Import queued:** `{d_id}`. The document will be processed in the background.",
                    })
            except Exception as e:
                st.session_state.chat.append({
                    "role": "assistant",
                    "content": f"❌ **Import failed:** {e}",
                })
            st.rerun()
            
        elif intent == "ACTION_IMPORT" and not url_match:
            intent = "RESEARCH"

        if intent == "CONVERSATION":
            with st.spinner("Reflecting..."):
                try:
                    slim_history = [{"role": m["role"], "content": m["content"]} for m in st.session_state.chat[-3:]]
                    c_resp = client.chat.completions.create(
                        messages=[{"role": "system", "content": "You are a polite scientific assistant. Briefly reply to the greeting."}] + slim_history,
                        model="llama-3.1-8b-instant",
                        temperature=0.5,
                        max_tokens=60,
                    )
                    answer = c_resp.choices[0].message.content
                except Exception as e:
                    answer = f"Hello! I am your scientific notebook assistant. (Error: {e})"

            st.session_state.chat.append({
                "role": "assistant",
                "content": answer,
                "text_hits": [],
                "figure_hits": [],
                "table_hits": [],
                "suggested_links": [],
            })
            
        elif intent == "META_SYSTEM":
            with st.spinner("Agent Zero computing..."):
                if "agent_logs" in st.session_state:
                    st.session_state.agent_logs.append("> Orchestrator: Meta-Protocol Activated.")
                
                try:
                    slim_history = [{"role": m["role"], "content": m["content"]} for m in st.session_state.chat[-6:]]
                    sys_prompt = "CRITICAL DIRECTIVE: You are Agent Zero."
                    c_resp = client.chat.completions.create(
                        messages=[{"role": "system", "content": sys_prompt}] + slim_history,
                        model="llama-3.3-70b-versatile",
                        temperature=0.8,
                        max_tokens=600,
                    )
                    answer = c_resp.choices[0].message.content
                except Exception as e:
                    answer = f"Agent Zero Offline. Error: {e}"

            st.session_state.chat.append({
                "role": "assistant",
                "content": answer,
                "text_hits": [],
                "figure_hits": [],
                "table_hits": [],
                "suggested_links": [],
            })

        else:
            # --- RAG via API ---
            if client and not strict_source:
                 with st.spinner("Expanding query for dense retrieval (HyDE)…"):
                     hypo_answer = call_groq_hyde(client, user_query)
                     expanded_query = f"{user_query}\n\nTechnical Expansion:\n{hypo_answer}"

            if "agent_logs" in st.session_state:
                st.session_state.agent_logs.append("> Orchestrator: Query classified as 'RESEARCH'.")
                st.session_state.agent_logs.append("> Orchestrator: Delegating to FastAPI /api/chat.")

            with st.spinner("Searching via API…"):
                try:
                    api_resp = api_post_json("/api/chat", {
                        "session_id": st.session_state.active_session_id,
                        "message": expanded_query,
                        "temperature": temperature,
                    })
                    answer = api_resp.get("content", "(No answer)")
                    api_hits = api_resp.get("hits", [])
                    suggested_links = api_resp.get("suggested_links", [])
                except Exception as e:
                    answer = f"(API call failed: {e})"
                    api_hits = []
                    suggested_links = []

            text_hits = [h for h in api_hits if h.get("section_type") == "text"]
            figure_hits = [h for h in api_hits if h.get("section_type") == "figure"]
            table_hits = [h for h in api_hits if h.get("section_type") == "table"]

            # Web search fallback (UI-only)
            if not strict_source and not text_hits and not figure_hits and not table_hits:
                if "agent_logs" in st.session_state:
                    st.session_state.agent_logs.append("> Orchestrator: Strict mode is OFF. Delegating to Agent BETA (Web Crawler).")
                with st.spinner("Analyzing global physics web for auxiliary sources..."):
                    try:
                        from duckduckgo_search import DDGS
                        results = DDGS().text(user_query + " physics science CERN", max_results=2)
                        for r in results:
                            if r.get("href"):
                                suggested_links.append(r)
                    except Exception:
                        pass

            st.session_state.chat.append({
                "role": "assistant",
                "content": answer,
                "text_hits": text_hits,
                "figure_hits": figure_hits,
                "table_hits": table_hits,
                "suggested_links": suggested_links,
            })

    # --------------- RENDER CHAT & DASHBOARD -----------------
    if "agent_logs" not in st.session_state:
        st.session_state.agent_logs = ["> System initialized.", "> Agent Orchestrator Online. Waiting for commands."]

    tab_chat, tab_dash = st.tabs(["💬 Agent Chat", "📊 Agent Zero Dashboard"])
    
    with tab_dash:
        st.header("Agent Zero Core Systems")
        metrics_col1, metrics_col2, metrics_col3 = st.columns(3)
        with metrics_col1:
            st.metric("Registered Documents", len(registered_docs) if registered_docs else 0)
        with metrics_col2:
            st.metric("Active Sessions", len(sessions))
        with metrics_col3:
            st.metric("API Status", "Connected" if registered_docs is not None else "Error")
            
        st.markdown("---")
        
        st.subheader("🖥️ Swarm Intelligence Feed")
        log_container = st.container(height=400)
        for log in st.session_state.agent_logs[-15:]:
            log_container.code(log, language="bash")
            
        st.selectbox("Active Brain (Orchestrator)", ["Groq Llama 3.1 8B (Fast)", "OpenAI GPT-4", "Claude 3.5 Sonnet"], key="model_selectbox")
        st.button("Force Agent Sync")

    with tab_chat:
        render_chat_messages(registered_docs)

@st.dialog("📄 Original Physics Source", width="large")
def show_pdf_dialog(pdf_path: str, page: int = 1):
    import base64
    try:
        with open(pdf_path, "rb") as f:
            base64_pdf = base64.b64encode(f.read()).decode('utf-8')
        pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}#page={page}" width="100%" height="800" type="application/pdf"></iframe>'
        st.markdown(pdf_display, unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Could not load PDF: {e}")

def render_chat_messages(doc_mgr_data):
    
    for msg in st.session_state.chat:
        role = msg["role"]
    
        if role == "user":
            with st.chat_message("user"):
                st.markdown(f"<div class='user-bubble'>{msg['content']}</div>", unsafe_allow_html=True)
    
        else:
            text_hits = msg.get("text_hits", [])
            figure_hits = msg.get("figure_hits", [])
            table_hits = msg.get("table_hits", [])
    
            with st.chat_message("assistant"):
                col_left, col_right = st.columns([2.2, 1.0])
    
                with col_left:
                    st.markdown(
                        f"<div class='assistant-bubble'>{msg['content']}</div>",
                        unsafe_allow_html=True,
                    )
                    
                    sugg = msg.get("suggested_links", [])
                    if sugg:
                        st.info("🚨 **Missing Context:** I couldn't find a strong answer locally, but my Subagent found a candidate on the CERN web domain!")
                        for i, s in enumerate(sugg):
                            url = s.get('href', '') or s.get('url', '')
                            title = s.get('title', '') or s.get('filename', '')
                            st.markdown(f"- **[{title}]({url})**")
                            if st.button(f"📥 Auto-Ingest & Learn from {url[:40]}...", key=f"auto_ingest_{i}_{url}"):
                                st.session_state.pending_auto_import_url = url
                                st.rerun()
    
                with col_right:
                    if figure_hits:
                        f = figure_hits[0]
                        img = f.get("image_path")
                        st.markdown("<div class='side-card'>", unsafe_allow_html=True)
                        st.markdown("<div class='side-title'>Top Figure</div>", unsafe_allow_html=True)
                        st.markdown(
                            f"<div class='side-meta'>Page {f.get('page')} • score {f.get('score',0):.3f}</div>",
                            unsafe_allow_html=True,
                        )
                        if img and os.path.exists(img):
                            st.image(img, width=250)
                        st.markdown("</div>", unsafe_allow_html=True)

                    if table_hits:
                        t = table_hits[0]
                        csv = t.get("table_csv")
                        st.markdown("<div class='side-card'>", unsafe_allow_html=True)
                        st.markdown("<div class='side-title'>Top Table</div>", unsafe_allow_html=True)
                        st.markdown(
                            f"<div class='side-meta'>Page {t.get('page')} • score {t.get('score',0):.3f}</div>",
                            unsafe_allow_html=True,
                        )
                        if csv and os.path.exists(csv):
                            try:
                                df = pd.read_csv(csv)
                                st.dataframe(df.head(5), height=120)
                            except Exception:
                                st.caption("Failed to load table.")
                        st.markdown("</div>", unsafe_allow_html=True)

                all_hits = text_hits + figure_hits + table_hits
                
                if all_hits:
                    st.divider()
                    st.markdown("**🔍 Interactive Citations (Click to View Source)**")
                    cols = st.columns(min(len(all_hits), 4) if len(all_hits) > 0 else 1)
                    for i, h in enumerate(all_hits):
                        cid = h.get("citation_id", f"[C{i+1}]")
                        sec_type = str(h.get("section_type", "Text")).capitalize()
                        score = h.get('score', 0)
                        page = h.get('page', '?')
                        
                        col = cols[i % len(cols)]
                        with col:
                            with st.popover(f"{cid} {sec_type} (Pg {page})", use_container_width=True):
                                doc_id = h.get("doc_id")
                                doc_meta = next((d for d in doc_mgr_data if d.get("doc_id") == doc_id), None) if doc_mgr_data else None
                                source_str = doc_meta.get("filename") if doc_meta else h.get("source", doc_id)
                                if not source_str or source_str == "default":
                                    source_str = "CERN Document"
                                    
                                st.markdown(f"**📄 Source:** `{source_str}`")
                                st.caption(f"Vector Similarity Score: {score:.3f}")
                                
                                if doc_meta and doc_meta.get("url"):
                                    st.markdown(f"[🔗 Open Original Document URL]({doc_meta.get('url')})")
                                
                                if doc_meta and doc_meta.get("path") and os.path.exists(doc_meta["path"]):
                                    if st.button(f"👁️ View Natively", key=f"popover_view_pdf_{cid}_{i}_{doc_id}"):
                                        show_pdf_dialog(doc_meta["path"], page)
                            
                            st.markdown("---")
                            
                            chunk_text = h.get("text", "")
                            if chunk_text:
                                st.markdown("**Text Excerpt:**")
                                st.info(f"_{chunk_text}_")
                            
                            img_path = h.get("image_path")
                            if img_path and os.path.exists(img_path):
                                st.image(img_path)
                            
                            csv_path = h.get("table_csv")
                            if csv_path and os.path.exists(csv_path):
                                try:
                                    df = pd.read_csv(csv_path)
                                    st.dataframe(df)
                                except:
                                    pass
                            
                            if sec_type.lower() == "figure":
                                img = h.get("image_path")
                                if img and os.path.exists(img):
                                    st.image(img, use_column_width=True)
                                st.markdown(h.get("text", "")[:800])
                            elif sec_type.lower() == "table":
                                csv = h.get("table_csv")
                                st.info("Table Extracted Data:")
                                st.caption(h.get("text", "")[:400])
                                if csv and os.path.exists(csv):
                                    try:
                                        st.dataframe(pd.read_csv(csv))
                                    except: pass
                            else:
                                st.markdown(h.get("text", "")[:1500])
    

if __name__ == "__main__":
    run()
