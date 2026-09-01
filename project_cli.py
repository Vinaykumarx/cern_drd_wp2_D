#!/usr/bin/env python3
from core.bootstrap import require_bootstrap; require_bootstrap()
"""
🎯 PROJECT MANAGEMENT CLI
Interactive command-line interface for managing project tasks and status

Usage:
    python project_cli.py status          # Show quick status
    python project_cli.py report          # Generate full report
    python project_cli.py kanban          # Show kanban board
    python project_cli.py add             # Add new task
    python project_cli.py assign <id>     # Assign task to engineer
    python project_cli.py allocate        # Show resource recommendations
    python project_cli.py menu            # Interactive menu
"""

import sys
from pathlib import Path
from project_agent import (
    ProjectStatusAgent, TaskStatus, Priority, TaskCategory,
    Task, KanbanBoard
)


class ProjectCLI:
    """Interactive CLI for project management"""

    def __init__(self):
        self.agent = ProjectStatusAgent()
        self.kanban = self.agent.kanban

    def show_quick_status(self):
        """Show quick project status"""
        report = self.agent.run_full_assessment()
        health = report['project_health']
        stats = report['kanban_stats']

        print("\n" + "="*80)
        print(f"🎯 PROJECT STATUS: {health['status']}")
        print("="*80)
        print(f"Health Score: {health['health_score']:.1f}/100")
        print(f"\nTasks:")
        for status, count in stats['by_status'].items():
            print(f"  {status}: {count}")
        print(f"\nEstimated Effort: {stats['total_estimated_hours']:.0f} hours")
        print("="*80 + "\n")

    def show_kanban_board(self):
        """Display kanban board"""
        print(self.kanban.get_kanban_view())

    def show_allocations(self):
        """Show resource allocation recommendations"""
        report = self.agent.run_full_assessment()
        recs = report['resource_recommendations']

        print("\n" + "="*80)
        print("👥 ENGINEER ALLOCATION RECOMMENDATIONS")
        print("="*80 + "\n")

        for rec in recs['recommendations'][:10]:
            print(f"📌 {rec['task_id']}: {rec['task_title']}")
            print(f"   ✓ Recommend: {rec['recommended_engineer']}")
            print(f"   ✓ Level: {rec['level']}")
            if rec['skills_match']:
                print(f"   ✓ Skills: {', '.join(rec['skills_match'])}")
            print()

        print("="*80 + "\n")

    def show_full_report(self):
        """Generate full report"""
        print(self.agent.generate_detailed_report())

    def add_task_interactive(self):
        """Interactively add new task"""
        print("\n" + "="*80)
        print("➕ ADD NEW TASK")
        print("="*80 + "\n")

        title = input("Task Title: ").strip()
        if not title:
            print("❌ Title is required")
            return

        description = input("Description: ").strip()
        
        print("\nCategory:")
        for i, cat in enumerate(TaskCategory, 1):
            print(f"  {i}. {cat.value}")
        cat_choice = input("Select (1-6): ").strip()
        try:
            category = list(TaskCategory)[int(cat_choice) - 1]
        except (ValueError, IndexError):
            print("❌ Invalid category")
            return

        print("\nPriority:")
        for i, pri in enumerate(Priority, 1):
            print(f"  {i}. {pri.value}")
        pri_choice = input("Select (1-4): ").strip()
        try:
            priority = list(Priority)[int(pri_choice) - 1]
        except (ValueError, IndexError):
            print("❌ Invalid priority")
            return

        try:
            hours = float(input("Estimated Hours (0 if unknown): ") or 0)
        except ValueError:
            hours = 0

        task = self.kanban.add_task(
            title=title,
            description=description,
            category=category,
            priority=priority,
            estimated_hours=hours,
        )

        print(f"\n✅ Task created: {task.id}")
        print("="*80 + "\n")

    def assign_task_interactive(self):
        """Interactively assign task"""
        print("\n" + "="*80)
        print("👤 ASSIGN TASK TO ENGINEER")
        print("="*80 + "\n")

        # Show unassigned tasks
        unassigned = [t for t in self.kanban.tasks.values() if not t.assigned_to]
        if not unassigned:
            print("✅ All tasks are assigned!")
            return

        print("Unassigned Tasks:")
        for i, task in enumerate(unassigned[:10], 1):
            print(f"  {i}. [{task.id}] {task.title[:50]}")

        try:
            choice = int(input("\nSelect task (1-10): ")) - 1
            if choice < 0 or choice >= len(unassigned):
                raise ValueError
            selected_task = unassigned[choice]
        except (ValueError, IndexError):
            print("❌ Invalid selection")
            return

        # Show engineers
        engineers = self.agent.allocator.engineers
        print(f"\nAvailable Engineers ({len(engineers)}):")
        for i, eng in enumerate(engineers, 1):
            print(f"  {i}. {eng.engineer_name} ({eng.level.value})")

        try:
            eng_choice = int(input("Select engineer (1-10): ")) - 1
            if eng_choice < 0 or eng_choice >= len(engineers):
                raise ValueError
            engineer = engineers[eng_choice]
        except (ValueError, IndexError):
            print("❌ Invalid selection")
            return

        self.kanban.assign_task(selected_task.id, engineer.engineer_name)
        engineer.current_load += 1

        print(f"\n✅ Assigned {selected_task.id} to {engineer.engineer_name}")
        print("="*80 + "\n")

    def update_task_status(self):
        """Update task status"""
        print("\n" + "="*80)
        print("📋 UPDATE TASK STATUS")
        print("="*80 + "\n")

        # Show tasks in progress
        in_progress = [t for t in self.kanban.tasks.values() 
                      if t.status in [TaskStatus.TODO, TaskStatus.IN_PROGRESS]]
        if not in_progress:
            print("ℹ️ No tasks to update")
            return

        print("Active Tasks:")
        for i, task in enumerate(in_progress[:15], 1):
            print(f"  {i}. [{task.id}] {task.title[:50]}")

        try:
            choice = int(input(f"\nSelect task (1-{len(in_progress)}): ")) - 1
            if choice < 0 or choice >= len(in_progress):
                raise ValueError
            selected_task = in_progress[choice]
        except (ValueError, IndexError):
            print("❌ Invalid selection")
            return

        print("\nNew Status:")
        for i, status in enumerate(TaskStatus, 1):
            print(f"  {i}. {status.value}")

        try:
            status_choice = int(input("Select (1-6): ")) - 1
            if status_choice < 0 or status_choice >= len(TaskStatus):
                raise ValueError
            new_status = list(TaskStatus)[status_choice]
        except (ValueError, IndexError):
            print("❌ Invalid selection")
            return

        self.kanban.update_task_status(selected_task.id, new_status)
        print(f"\n✅ Updated {selected_task.id} to {new_status.value}")
        print("="*80 + "\n")

    def show_menu(self):
        """Show interactive menu"""
        while True:
            print("\n" + "="*80)
            print("🤖 PROJECT STATUS AGENT - MAIN MENU")
            print("="*80)
            print("""
1. Quick Status           Show project health & task counts
2. Kanban Board          Display full kanban board
3. Resource Allocation   Show engineer allocation recommendations
4. Full Report           Generate detailed analysis report
5. Add Task              Create new task
6. Assign Task           Assign task to engineer
7. Update Status         Change task status
8. Exit                  Quit
            """)
            print("="*80)

            choice = input("Select option (1-8): ").strip()

            if choice == '1':
                self.show_quick_status()
            elif choice == '2':
                self.show_kanban_board()
            elif choice == '3':
                self.show_allocations()
            elif choice == '4':
                self.show_full_report()
            elif choice == '5':
                self.add_task_interactive()
            elif choice == '6':
                self.assign_task_interactive()
            elif choice == '7':
                self.update_task_status()
            elif choice == '8':
                print("\n👋 Goodbye!\n")
                break
            else:
                print("❌ Invalid option")

    def run(self, args: list = None):
        """Run CLI with arguments"""
        if not args or not args:
            self.show_menu()
            return

        command = args[0].lower()

        if command == 'status':
            self.show_quick_status()
        elif command == 'kanban':
            self.show_kanban_board()
        elif command == 'allocate':
            self.show_allocations()
        elif command == 'report':
            self.show_full_report()
        elif command == 'add':
            self.add_task_interactive()
        elif command == 'assign' and len(args) > 1:
            task_id = args[1]
            # Quick assign
            print(f"Assigning {task_id}...")
        elif command == 'menu':
            self.show_menu()
        elif command == 'help':
            print(__doc__)
        else:
            print(f"Unknown command: {command}")
            print(__doc__)


def main():
    """Main entry point"""
    cli = ProjectCLI()
    cli.run(sys.argv[1:])


if __name__ == '__main__':
    main()
