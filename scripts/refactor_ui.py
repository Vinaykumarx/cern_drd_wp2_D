import sys

def main():
    with open("app/streamlit_app_DEPRECATED.py", "r") as f:
        content = f.read()

    split_target = "    # --------------- RENDER CHAT -----------------"
    if split_target not in content:
        print("Could not find split target!")
        sys.exit(1)

    top_part, render_part = content.split(split_target)

    # Dedent the render part
    render_lines = render_part.split('\n')
    new_render_lines = []
    
    clean_render_lines = []
    for line in render_lines:
        if "if __name__ == \"__main__\":" in line:
            break
        clean_render_lines.append(line)

    for line in clean_render_lines:
        if line.startswith("    "):
            new_render_lines.append(line[4:])
        else:
            new_render_lines.append(line)

    render_func_str = "\ndef render_chat_messages(doc_mgr):\n"
    for line in new_render_lines:
        render_func_str += "    " + line + "\n"

    new_run_layout = """    # --------------- RENDER CHAT & DASHBOARD -----------------
    if "agent_logs" not in st.session_state:
        st.session_state.agent_logs = ["> System initialized.", "> Agent Orchestrator Online. Waiting for commands."]

    col_chat, col_dash = st.columns([2.5, 1.0])
    
    with col_dash:
        st.subheader("🖥️ Swarm Intelligence Feed")
        log_container = st.container(height=600)
        for log in st.session_state.agent_logs:
            log_container.code(log, language="bash")
        st.markdown("---")
        st.selectbox("Active Brain (Orchestrator)", ["Groq Llama 3.1 8B (Fast)", "OpenAI GPT-4", "Claude 3.5 Sonnet"], key="model_selectbox")
        st.button("Force Agent Sync")

    with col_chat:
        render_chat_messages(doc_mgr)

if __name__ == "__main__":
    run()
"""

    final_content = top_part + new_run_layout + render_func_str

    with open("app/streamlit_app_DEPRECATED.py", "w") as f:
        f.write(final_content)
        
    print("Refactor complete.")

if __name__ == "__main__":
    main()
