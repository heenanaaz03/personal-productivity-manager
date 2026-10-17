import csv
from datetime import date, datetime, timedelta
from pathlib import Path


class Task:
    def __init__(self, task_no, title, desc, deadline, priority, is_done=False):
        self.task_no = task_no
        self.title = title
        self.desc = desc
        self.deadline = deadline
        self.priority = priority
        self.is_done = is_done

    def __str__(self):
        status = "Completed" if self.is_done else "Ongoing"

        return (
            f"\nTask No: {self.task_no}\n"
            f"Title: {self.title}\n"
            f"Description: {self.desc}\n"
            f"Deadline: {self.deadline}\n"
            f"Priority: {self.priority}\n"
            f"Status: {status}\n"
        )


class TaskManager:
    def __init__(self):
        self.tasks = []

    def find_task(self, task_no):
        for task in self.tasks:
            if task.task_no == task_no:
                return task
        return None

    def add_task(self):
        while True:
            try:
                task_no = int(input("Enter task number: "))
                if task_no < 1:
                    print("Task number must be positive.")
                elif self.find_task(task_no):
                    print("That task number already exists.")
                else:
                    break
            except ValueError:
                print("Enter a valid whole number.")

        while True:
            title = input("Enter title: ").strip()
            if title:
                break
            print("Title cannot be empty.")

        desc = input("Enter description: ").strip()

        while True:
            deadline = input("Enter deadline (YYYY-MM-DD): ").strip()
            try:
                datetime.strptime(deadline, "%Y-%m-%d")
                break
            except ValueError:
                print("Invalid date. Use YYYY-MM-DD, e.g. 2026-10-20.")

        while True:
            priority = input("Enter priority (High/Medium/Low): ").strip().capitalize()
            if priority in ("High", "Medium", "Low"):
                break
            print("Priority must be High, Medium, or Low.")

        task = Task(task_no, title, desc, deadline, priority)
        self.tasks.append(task)
        print("Task added successfully!")

    def show_tasks(self):
        if not self.tasks:
            print("No tasks found.")
            return

        for task in self.tasks:
            print(task)

    def task_done(self, task_no):
        task = self.find_task(task_no)

        if task is None:
            print("Task not found.")
        elif task.is_done:
            print("Task is already completed.")
        else:
            task.is_done = True
            print("Task marked as completed!")

    def filter_by_status(self, status):
        matching_tasks = [
            task for task in self.tasks
            if (status == "done" and task.is_done)
            or (status == "ongoing" and not task.is_done)
        ]

        if not matching_tasks:
            print(f"No {status} tasks found.")
            return

        for task in matching_tasks:
            print(task)

    def show_deadlines(self):
        today = date.today()
        upcoming_limit = today + timedelta(days=7)
        overdue = []
        upcoming = []

        for task in self.tasks:
            if task.is_done:
                continue

            deadline = datetime.strptime(
                task.deadline, "%Y-%m-%d"
            ).date()

            if deadline < today:
                overdue.append(task)
            elif deadline <= upcoming_limit:
                upcoming.append(task)

        print("\n--- Overdue Tasks ---")
        if overdue:
            for task in overdue:
                print(task)
        else:
            print("No overdue tasks.")

        print("\n--- Upcoming Tasks (Next 7 Days) ---")
        if upcoming:
            for task in upcoming:
                print(task)
        else:
            print("No upcoming tasks.")

    def save_csv(self):
        filename = Path("tasks.csv")
        fieldnames = [
            "task_no", "title", "desc",
            "deadline", "priority", "is_done"
        ]

        try:
            with filename.open("w", newline="", encoding="utf-8") as file:
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                writer.writeheader()

                for task in self.tasks:
                    writer.writerow({
                        "task_no": task.task_no,
                        "title": task.title,
                        "desc": task.desc,
                        "deadline": task.deadline,
                        "priority": task.priority,
                        "is_done": task.is_done
                    })

            print("Tasks saved successfully!")

        except OSError as error:
            print(f"Could not save tasks: {error}")

    def load_from_csv(self):
        filename = Path("tasks.csv")

        if not filename.exists():
            return

        loaded_tasks = []
        seen_numbers = set()

        try:
            with filename.open("r", newline="", encoding="utf-8") as file:
                reader = csv.DictReader(file)

                required_fields = {
                    "task_no", "title", "desc",
                    "deadline", "priority", "is_done"
                }

                if not required_fields.issubset(reader.fieldnames or []):
                    print("CSV file has an invalid format.")
                    return

                for row in reader:
                    task_no = int(row["task_no"])
                    title = row["title"].strip()
                    deadline = row["deadline"].strip()
                    priority = row["priority"].strip().capitalize()
                    is_done_text = row["is_done"].strip().lower()

                    datetime.strptime(deadline, "%Y-%m-%d")

                    if task_no < 1 or task_no in seen_numbers:
                        raise ValueError("Invalid or duplicate task number.")

                    if not title:
                        raise ValueError("A task has an empty title.")

                    if priority not in ("High", "Medium", "Low"):
                        raise ValueError("A task has an invalid priority.")

                    if is_done_text not in ("true", "false"):
                        raise ValueError("A task has an invalid completion status.")

                    task = Task(
                        task_no,
                        title,
                        row["desc"],
                        deadline,
                        priority,
                        is_done_text == "true"
                    )

                    loaded_tasks.append(task)
                    seen_numbers.add(task_no)

        except (OSError, ValueError, csv.Error) as error:
            print(f"Could not load tasks.csv: {error}")
            return

        self.tasks = loaded_tasks
        print(f"Loaded {len(self.tasks)} tasks.")


def main():
    manager = TaskManager()
    manager.load_from_csv()

    while True:
        print("\n===== PERSONAL PRODUCTIVITY MANAGER =====")
        print("1. Add Task")
        print("2. Show Tasks")
        print("3. Mark Task as Completed")
        print("4. Search/Filter by Status")
        print("5. Identify Overdue/Upcoming Tasks")
        print("6. Save Tasks")
        print("7. Exit")

        choice = input("Enter your choice: ").strip()

        if choice == "1":
            manager.add_task()

        elif choice == "2":
            manager.show_tasks()

        elif choice == "3":
            try:
                task_no = int(input("Enter task number to complete: "))
                manager.task_done(task_no)
            except ValueError:
                print("Enter a valid whole number.")

        elif choice == "4":
            print("1. Completed tasks")
            print("2. Ongoing tasks")
            status_choice = input("Choose status: ").strip()

            if status_choice == "1":
                manager.filter_by_status("done")
            elif status_choice == "2":
                manager.filter_by_status("ongoing")
            else:
                print("Invalid choice.")

        elif choice == "5":
            manager.show_deadlines()

        elif choice == "6":
            manager.save_csv()

        elif choice == "7":
            manager.save_csv()
            print("Goodbye!")
            break

        else:
            print("Invalid menu choice. Enter 1–7.")


if __name__ == "__main__":
    main()
