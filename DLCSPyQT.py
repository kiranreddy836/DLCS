import tkinter as tk
from tkinter import ttk
import sqlite3

def display_database():
    # Connect to the SQLite database
    conn = sqlite3.connect('ilcst.db')
    cursor = conn.cursor()

    # Fetch data from the database table sorted by time_stamp
    cursor.execute("SELECT * FROM logdata ORDER BY time_stamp DESC")
    data = cursor.fetchall()

    # Close the database connection
    conn.close()

    # Create a Tkinter window
    root = tk.Tk()
    root.title("SQLite Table Display")

    # Create a style for the headers
    style = ttk.Style(root)
    style.theme_use("clam")
    style.configure("Treeview.Heading", background="green", foreground="white", font=("Arial", 10, "bold"))

    # Create a frame to hold the table
    frame = tk.Frame(root)
    frame.pack()

    # Define headers (excluding the empty first column)
    headers = ["CPF No", "Name", "Authorized By", "Feeder", "Login Time", "Logout Time", "Errors", "Master Logout", ""]

    # Create a scrollbar for both vertical and horizontal directions
    scrollbar_y = tk.Scrollbar(root, orient=tk.VERTICAL)
    scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)

    scrollbar_x = tk.Scrollbar(root, orient=tk.HORIZONTAL)
    scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)

    # Create a treeview to display the data
    tree = ttk.Treeview(frame, yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
    tree['columns'] = headers

    # Set up headings and column widths
    for header in headers:
        tree.heading(header, text=header)
        tree.column(header, width=150)  # Adjust width as needed

    # Insert data into the table
    for row in data:
        tree.insert("", tk.END, values=row[:8])  # Exclude the first element in each row

    tree.grid(row=0, column=0)
    scrollbar_y.config(command=tree.yview)
    scrollbar_x.config(command=tree.xview)

    root.mainloop()

# Call the function to display the database contents
display_database()
