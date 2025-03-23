import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
from datetime import datetime


def connect_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="dharshuvin21",
        database="todo_db",
        auth_plugin="mysql_native_password")



def load_tasks():
    tree.delete(*tree.get_children())
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tasks")
    for row in cursor.fetchall():
        tree.insert("", "end", values=row)
    conn.close()


def add_task():
    task_name = task_entry.get()
    due_date = due_date_entry.get()
    priority = priority_var.get()

    if not task_name or not due_date or not priority:
        messagebox.showerror("Error", "All fields are required!")
        return

    try:
        datetime.strptime(due_date, "%Y-%m-%d")  # Validate date format
    except ValueError:
        messagebox.showerror("Error", "Invalid date format! Use YYYY-MM-DD.")
        return

    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO tasks (task_name, due_date, priority) VALUES (%s, %s, %s)",
                   (task_name, due_date, priority))
    conn.commit()
    conn.close()

    task_entry.delete(0, tk.END)
    due_date_entry.delete(0, tk.END)
    priority_var.set("Low")

    load_tasks()


def edit_task():
    selected_item = tree.selection()
    if not selected_item:
        messagebox.showerror("Error", "Select a task to edit!")
        return

    item = tree.item(selected_item)["values"]
    task_id, task_name, due_date, priority = item

    task_entry.delete(0, tk.END)
    due_date_entry.delete(0, tk.END)
    task_entry.insert(0, task_name)
    due_date_entry.insert(0, due_date)
    priority_var.set(priority)

    def update_task():
        new_task_name = task_entry.get()
        new_due_date = due_date_entry.get()
        new_priority = priority_var.get()

        if not new_task_name or not new_due_date or not new_priority:
            messagebox.showerror("Error", "All fields are required!")
            return

        try:
            datetime.strptime(new_due_date, "%Y-%m-%d")  # Validate date format
        except ValueError:
            messagebox.showerror("Error", "Invalid date format! Use YYYY-MM-DD.")
            return

        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("UPDATE tasks SET task_name=%s, due_date=%s, priority=%s WHERE id=%s",
                       (new_task_name, new_due_date, new_priority, task_id))
        conn.commit()
        conn.close()

        task_entry.delete(0, tk.END)
        due_date_entry.delete(0, tk.END)
        priority_var.set("Low")

        load_tasks()
        edit_window.destroy()

    edit_window = tk.Toplevel(root)
    edit_window.title("Edit Task")
    tk.Label(edit_window, text="Task Name").grid(row=0, column=0, padx=5, pady=5)
    tk.Entry(edit_window, textvariable=tk.StringVar(value=task_name)).grid(row=0, column=1, padx=5, pady=5)
    tk.Label(edit_window, text="Due Date (YYYY-MM-DD)").grid(row=1, column=0, padx=5, pady=5)
    tk.Entry(edit_window, textvariable=tk.StringVar(value=due_date)).grid(row=1, column=1, padx=5, pady=5)
    tk.Label(edit_window, text="Priority").grid(row=2, column=0, padx=5, pady=5)
    ttk.Combobox(edit_window, textvariable=tk.StringVar(value=priority), values=["Low", "Medium", "High"]).grid(row=2,
                                                                                                                column=1,
                                                                                                                padx=5,
                                                                                                                pady=5)
    tk.Button(edit_window, text="Update Task", command=update_task).grid(row=3, column=0, columnspan=2, pady=10)


def delete_task():
    selected_item = tree.selection()
    if not selected_item:
        messagebox.showerror("Error", "Select a task to delete!")
        return

    task_id = tree.item(selected_item)["values"][0]

    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tasks WHERE id=%s", (task_id,))
    conn.commit()
    conn.close()

    load_tasks()

root = tk.Tk()
root.title("To-Do List App")

tk.Label(root, text="Task Name:").grid(row=0, column=0, padx=5, pady=5)
task_entry = tk.Entry(root)
task_entry.grid(row=0, column=1, padx=5, pady=5)

tk.Label(root, text="Due Date (YYYY-MM-DD):").grid(row=1, column=0, padx=5, pady=5)
due_date_entry = tk.Entry(root)
due_date_entry.grid(row=1, column=1, padx=5, pady=5)

tk.Label(root, text="Priority:").grid(row=2, column=0, padx=5, pady=5)
priority_var = tk.StringVar(value="Low")
priority_dropdown = ttk.Combobox(root, textvariable=priority_var, values=["Low", "Medium", "High"])
priority_dropdown.grid(row=2, column=1, padx=5, pady=5)

tk.Button(root, text="Add Task", command=add_task).grid(row=3, column=0, columnspan=2, pady=10)
tk.Button(root, text="Edit Task", command=edit_task).grid(row=4, column=0, columnspan=2, pady=5)
tk.Button(root, text="Delete Task", command=delete_task).grid(row=5, column=0, columnspan=2, pady=5)

columns = ("ID", "Task Name", "Due Date", "Priority")
tree = ttk.Treeview(root, columns=columns, show="headings")
for col in columns:
    tree.heading(col, text=col)
tree.grid(row=6, column=0, columnspan=2, padx=10, pady=10)

load_tasks()

root.mainloop()
