import sqlite3
import tkinter as tk
from tkinter import ttk

# Function to fetch data from the SQLite database
def view_logs():
    conn = sqlite3.connect('ilcst.db')  # Replace 'your_database_name.db' with your actual database name
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM logdata")
    data = cursor.fetchall()
    conn.close()
    display_logs(data)

# Function to display the logs in a tkinter window with horizontal and vertical scrollbars
def display_logs(data):
    root = tk.Tk()
    root.title("Log Data")

    tree = ttk.Treeview(root, columns=("cpfno", "name", "authorised_by", "feeder", "login_time", "logout_time", "errors", "master_logout", "time_stamp"),
                        show="headings", height=15)

    vsb = ttk.Scrollbar(root, orient="vertical", command=tree.yview)
    hsb = ttk.Scrollbar(root, orient="horizontal", command=tree.xview)
    tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

    vsb.pack(side="right", fill="y")
    hsb.pack(side="bottom", fill="x")
    tree.pack(expand=True, fill="both")

    tree.heading("cpfno", text="CPF No")
    tree.heading("name", text="Name")
    tree.heading("authorised_by", text="Authorised By")
    tree.heading("feeder", text="Feeder")
    tree.heading("login_time", text="Login Time")
    tree.heading("logout_time", text="Logout Time")
    tree.heading("errors", text="Errors")
    tree.heading("master_logout", text="Master Logout")
    tree.heading("time_stamp", text="Time Stamp")

    # Set the background color of the header
    style = ttk.Style()
    style.configure("Treeview.Heading", background="blue")

    for col in tree['columns']:
        tree.heading(col, text=col.title(), anchor=tk.CENTER)

    for record in data:
        tree.insert("", "end", values=record)

    root.mainloop()

# Creating the GUI
root = tk.Tk()
root.title("View Logs")

view_logs_button = tk.Button(root, text="View Logs", command=view_logs)
view_logs_button.pack()

root.mainloop()
