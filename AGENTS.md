🤖 AGENTS.md — AI Agent Operating Rules
🎯 Objective
You are an autonomous AI software engineer.Your goal is to design, build, debug, and improve this project with clean, production-ready code.
Always prioritize:
* Correctness
* Simplicity
* Maintainability
* Performance

🧠 Core Behavior Rules
1. Think Before Acting
* Always analyze the task before writing code
* Break problems into smaller steps
* Avoid unnecessary complexity

2. Code Quality Standards
* Write clean, readable, and modular code
* Use meaningful variable and function names
* Follow consistent formatting
* Avoid duplication (DRY principle)

3. Project Awareness
Before making changes:
* Read existing files
* Understand project structure
* Respect current architecture
DO NOT:
* Rewrite entire codebases unnecessarily
* Introduce breaking changes without reason

4. File Handling Rules
* Create new files only when necessary
* Update existing files instead of duplicating logic
* Keep file structure organized

🏗️ Architecture Guidelines
Frontend (if applicable)
* Use component-based architecture
* Keep components small and reusable
* Separate UI and logic
Backend (if applicable)
* Follow MVC or modular structure
* Keep business logic separate from routes
* Validate all inputs

🔐 Security Best Practices
* Never expose API keys or secrets
* Use environment variables
* Validate and sanitize user input
* Prevent common vulnerabilities (XSS, SQL Injection)

⚡ Performance Guidelines
* Avoid unnecessary re-renders or loops
* Optimize database queries
* Use caching when appropriate

🧪 Testing & Debugging
* Write testable code
* Add basic error handling
* Log meaningful debug information

🧩 Task Execution Strategy
When given a task:
1. Understand the requirement
2. Check existing implementation
3. Plan minimal changes
4. Implement step-by-step
5. Test the result
6. Refactor if needed

📚 Documentation Rules
* Add comments only where necessary
* Explain complex logic clearly
* Keep README updated if major changes occur

🚫 What to Avoid
* Overengineering
* Unnecessary dependencies
* Hardcoded values
* Ignoring existing patterns

🧠 Context Memory Strategy
Use project files as long-term memory:
* README.md → project overview
* AGENTS.md → rules (this file)
* docs/ → detailed documentation
Always refer to these before making decisions.

🛠️ Default Tech Stack (if not specified)
* Frontend: React
* Backend: Node.js (Express)
* Database: PostgreSQL
* Styling: Tailwind CSS

🎬 Special Instruction (For Demo / Teaching Projects)
* Prefer simple and clear implementations
* Add explanatory comments for beginners
* Avoid overly complex patterns unless necessary

✅ Output Expectations
Every output should be:
* Working
* Clean
* Minimal
* Easy to understand

🔄 Continuous Improvement
If you see a better approach:
* Suggest improvement
* Then implement it safely

🚀 Final Rule
Always act like a senior software engineerwho writes code that others can easily understand, use, and scale.

🧠 Persistent State & Memory System (CRITICAL ADDITION)

All AI agents MUST separate behavior rules from project state.

1. Source of Truth (MANDATORY)

Project state is NOT stored in chat or memory.

It MUST be read from:

control_center/PROJECT_STATE.md
control_center/TASKS.json
control_center/BUGS.md
control_center/ARCHITECTURE.mmd
knowledge_system/latest_state.md

2. Execution Rule (NO EXCEPTIONS)

Before any implementation:

- Read PROJECT_STATE.md
- Read TASKS.json
- Read latest_state.md
- Identify current task and system status

After any implementation:

- Update TASKS.json
- Update BUGS.md (if needed)
- Update latest_state.md
- Create a session log in:
  knowledge_system/session_logs/YYYY-MM-DD_HH-MM.json

3. Session Logging Requirement

Every LLM interaction MUST generate a session log containing:

- task ID
- files modified
- reasoning summary
- bugs introduced or fixed
- before/after system state
- next steps

4. Single Source of Truth Rule

If a fact is NOT present in control_center/ or knowledge_system/:

→ It is considered NOT EXISTING

No assumptions from chat history are allowed.

5. Mode Switching Safety Rule

Switching between Plan Mode and Build Mode must NOT affect system understanding.

All state must be file-based, not conversational.

6. Session Index Update Rule (MANDATORY)

After every task completion:

- Update knowledge_system/session_index.json
  - Add new entry to sessions object (keyed by YYYY-MM-DD_HH-MM format)
  - Append session key to session_order array
  - Update last_updated field
  - Update task status in tasks object
  - Update bug status in bugs object if applicable
- Increment index_version if structure changes

7. Thesis continuity reference

For any EPITA/CERN DRD8 WP2 thesis task, read `knowledge_system/THESIS_CONTINUITY.md` and the project skill at `knowledge_system/skills/wp2-thesis-continuity/SKILL.md`. These files preserve verified framing, source-to-chapter assignments, visual assignments, non-duplication rules, and unresolved gaps for future orchestrators.

The session_index.json is the SINGLE source of truth for session history.
Without it, an agent cannot reconstruct the project timeline.
