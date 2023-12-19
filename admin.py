import tkinter as tk
import tkinter.ttk as ttk
import cv2
from PIL import Image, ImageTk
from pyzbar.pyzbar import decode
import sqlite3

conn = sqlite3.connect('ilcst.db')
cur = conn.cursor()

def show_camera(window):
    cap = cv2.VideoCapture(0)
    label = tk.Label(window)
    label.pack()

    def detect_and_display_qr_codes():
        ret, frame = cap.read()
        if not ret:
            return
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        # Detect QR codes
        # (This part needs adjustment based on how you're using QR code detection)
        decoded_objects = decode(frame)
        for obj in decoded_objects:
           qr_data = obj.data.decode('utf-8')
           partsqr = qr_data.split("_")
           if len(partsqr) == 3:
                 name, qrCPF, qrMode = partsqr
           master_status = check_master_status(qrCPF)
           if master_status == 'Y':
                update_user()
                stop_camera()
           else:
                print("Master Status is N")
                custom_message_box("UPDATE FAILED", f" You do not have In-Charge Privileges to update the master flag", "dark orange")
                stop_camera()

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(frame)
        imgtk = ImageTk.PhotoImage(image=img)

        label.imgtk = imgtk
        label.configure(image=imgtk)

        if window.winfo_exists():
            label.after(10, detect_and_display_qr_codes)
        else:
            cap.release()

    detect_and_display_qr_codes()

def stop_camera():
    if 'cap' in globals():
        cap.release()
    root.after(10, root.destroy)

def start_camera_for_update():
    new_window = tk.Toplevel(root)
    new_window.title("Camera Feed")
    show_camera(new_window)

def check_master_status(qrCPF):
    query = "SELECT master FROM users WHERE cpf_no = ?"
    cur.execute(query, (qrCPF,))
    result = cur.fetchone()
    if result:
        return result[0]
    else:
        return None

def custom_message_box(title, message, bg_color):

    custom_box = tk.Toplevel()
    custom_box.configure(bg="White")
    # Disable window maximize button
    custom_box.resizable(False, False)
    
    # Remove the default title bar
    custom_box.overrideredirect(1)
    
    # Create a custom title bar frame with a background
    title_bar = tk.Frame(custom_box, bg=bg_color, relief="raised", bd=1)
    title_bar.pack(fill="x")
    
    # Create a label for the title within the custom title bar
    title_label = ttk.Label(title_bar, text=title, font=("Times New Roman", 16, "bold"),  background=bg_color)
    title_label.pack(side="left", padx=5)
    
    # Calculate screen width and height
    screen_width = custom_box.winfo_screenwidth()
    screen_height = custom_box.winfo_screenheight()
    
    # Calculate the window size and position it in the center
    window_width = 500  # Adjust as needed
    window_height = 180  # Adjust as needed
    x_position = (screen_width - window_width) // 2
    y_position = (screen_height - window_height) // 2
    
    # Set the window size and position
    custom_box.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")
    
    # Create a label with the message and set text wrapping
    message_label = ttk.Label(custom_box, text=message, font=("Arial", 11), wraplength=400,background="White")
    message_label.pack(pady=20)
    
    # Create an OK button
    ok_button = ttk.Button(custom_box, text="OK", command=custom_box.destroy)
    ok_button.pack()

    # Bind the Enter key to the OK button to activate it
    custom_box.bind("<Return>", lambda event=None: ok_button.invoke())
    # Set the focus to the OK button
    ok_button.focus_set()
    # Make the custom box modal (blocks input to other windows)
    custom_box.grab_set()
    
    # Wait for the custom box to be closed
    custom_box.wait_window(custom_box)

def add_user():
    # Retrieve data from the input fields
    cpf = entry_cpf.get()
    name = entry_name.get()
    designation = entry_designation.get()
    phone = entry_phone.get()
    master = entry_master.get()

    # Check if the CPF is unique
    cur.execute("SELECT cpf_no FROM users WHERE cpf_no=?", (cpf,))
    existing_cpf = cur.fetchone()
    if existing_cpf:
        status_label_add.config(text="CPF already exists!")
    else:
        # Insert the new user into the database
        cur.execute("INSERT INTO users (cpf_no, name, designation, phone_no, master) VALUES (?, ?, ?, ?, ?)",
                    (cpf, name, designation, phone, master))
        conn.commit()
        status_label_add.config(text="User added successfully!", fg="green")

def get_user():
    cpf = entry_cpf_update.get()
    cur.execute("SELECT * FROM users WHERE cpf_no=?", (cpf,))
    user_details = cur.fetchone()
    if user_details:
        # Display user details for updating
        entry_cpf_update.delete(0, tk.END)
        entry_cpf_update.insert(0, user_details[0])  # Display CPF
        entry_name_update.delete(0, tk.END)
        entry_name_update.insert(0, user_details[1])  # Display name
        entry_designation_update.delete(0, tk.END)
        entry_designation_update.insert(0, user_details[2])  # Display designation
        entry_phone_update.delete(0, tk.END)
        entry_phone_update.insert(0, user_details[3])  # Display phone
        entry_master_update.delete(0, tk.END)
        entry_master_update.insert(0, user_details[4])  # Display master
        status_label_update.config(text="")
    else:
        entry_name_update.delete(0, tk.END)
        entry_designation_update.delete(0, tk.END)
        entry_phone_update.delete(0, tk.END)
        entry_master_update.delete(0, tk.END)
        status_label_update.config(text="User not found!", fg="red")

def update_user():
    cpf = entry_cpf_update.get()
    name = entry_name_update.get()
    designation = entry_designation_update.get()
    phone = entry_phone_update.get()
    master = entry_master_update.get()

    # Update the user details
    cur.execute("UPDATE users SET name=?, designation=?, phone_no=?, master=? WHERE cpf_no=?",
                (name, designation, phone, master, cpf))
    conn.commit()
    custom_message_box("UPDATE SUCCESS", f" You have successfully updated user details", "blue")
    status_label_update.config(text="User details updated!", fg="green")

def delete_user():
    cpf = entry_cpf_delete.get()
    cur.execute("SELECT * FROM users WHERE cpf_no=?", (cpf,))
    user_details = cur.fetchone()
    if user_details:
        # Display user details for deletion
        entry_cpf_delete.delete(0, tk.END)
        entry_cpf_delete.insert(0, user_details[0])  # Display CPF
        entry_name_delete.delete(0, tk.END)
        entry_name_delete.insert(0, user_details[1])  # Display name
        entry_designation_delete.delete(0, tk.END)
        entry_designation_delete.insert(0, user_details[2])  # Display designation
        entry_phone_delete.delete(0, tk.END)
        entry_phone_delete.insert(0, user_details[3])  # Display phone
        entry_master_delete.delete(0, tk.END)
        entry_master_delete.insert(0, user_details[4])  # Display master
        status_label_delete.config(text="")
    else:
        # Clear the entry fields
        entry_name_delete.delete(0, tk.END)
        entry_designation_delete.delete(0, tk.END)
        entry_phone_delete.delete(0, tk.END)
        entry_master_delete.delete(0, tk.END)
        status_label_delete.config(text="User not found!", fg="red")

def confirm_delete():
    cpf = entry_cpf_delete.get()
    cur.execute("DELETE FROM users WHERE cpf_no=?", (cpf,))
    conn.commit()
    status_label_delete.config(text="User deleted successfully!", fg="green")
    # Clear the entry fields
    entry_cpf_delete.delete(0, tk.END)
    entry_name_delete.delete(0, tk.END)
    entry_designation_delete.delete(0, tk.END)
    entry_phone_delete.delete(0, tk.END)
    entry_master_delete.delete(0, tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Admin Screen")

    # Add User Section
    frame_add_user = tk.Frame(root, padx=10, pady=10)
    frame_add_user.grid(row=0, column=0, padx=10, pady=10)

    label_header_add = tk.Label(frame_add_user, text="Add User", font=("Arial", 14, "bold"))
    label_header_add.grid(row=0, columnspan=2, pady=5)

    label_cpf = tk.Label(frame_add_user, text="CPF:")
    label_cpf.grid(row=1, column=0)
    entry_cpf = tk.Entry(frame_add_user)
    entry_cpf.grid(row=1, column=1)

    label_name = tk.Label(frame_add_user, text="Name:")
    label_name.grid(row=2, column=0)
    entry_name = tk.Entry(frame_add_user)
    entry_name.grid(row=2, column=1)

    label_designation = tk.Label(frame_add_user, text="Designation:")
    label_designation.grid(row=3, column=0)
    entry_designation = tk.Entry(frame_add_user)
    entry_designation.grid(row=3, column=1)

    label_phone = tk.Label(frame_add_user, text="Phone:")
    label_phone.grid(row=4, column=0)
    entry_phone = tk.Entry(frame_add_user)
    entry_phone.grid(row=4, column=1)

    label_master = tk.Label(frame_add_user, text="Master:")
    label_master.grid(row=5, column=0)
    entry_master = tk.Entry(frame_add_user)
    entry_master.grid(row=5, column=1)

    status_label_add = tk.Label(frame_add_user, text="")
    status_label_add.grid(row=6, columnspan=2)

    submit_button = tk.Button(frame_add_user, text="Add User", command=add_user)
    submit_button.grid(row=7, columnspan=2)

    # Update User Section
    frame_update_user = tk.Frame(root, padx=10, pady=10)
    frame_update_user.grid(row=0, column=1, padx=10, pady=10)

    label_header_update = tk.Label(frame_update_user, text="Update User", font=("Arial", 14, "bold"))
    label_header_update.grid(row=0, columnspan=2, pady=5)

    label_cpf_update = tk.Label(frame_update_user, text="Enter CPF:")
    label_cpf_update.grid(row=1, column=0)
    entry_cpf_update = tk.Entry(frame_update_user)
    entry_cpf_update.grid(row=1, column=1)

    update_button = tk.Button(frame_update_user, text="Get User Details", command=get_user)
    update_button.grid(row=2, columnspan=2)

    label_name_update = tk.Label(frame_update_user, text="Name:")
    label_name_update.grid(row=3, column=0)
    entry_name_update = tk.Entry(frame_update_user)
    entry_name_update.grid(row=3, column=1)

    label_designation_update = tk.Label(frame_update_user, text="Designation:")
    label_designation_update.grid(row=4, column=0)
    entry_designation_update = tk.Entry(frame_update_user)
    entry_designation_update.grid(row=4, column=1)

    label_phone_update = tk.Label(frame_update_user, text="Phone:")
    label_phone_update.grid(row=5, column=0)
    entry_phone_update = tk.Entry(frame_update_user)
    entry_phone_update.grid(row=5, column=1)

    label_master_update = tk.Label(frame_update_user, text="Master:")
    label_master_update.grid(row=6, column=0)
    entry_master_update = tk.Entry(frame_update_user)
    entry_master_update.grid(row=6, column=1)

    status_label_update = tk.Label(frame_update_user, text="")
    status_label_update.grid(row=7, columnspan=2)

    update_submit_button = tk.Button(frame_update_user, text="Update User", command=start_camera_for_update)
    update_submit_button.grid(row=8, columnspan=2)

    # Delete User Section
    frame_delete_user = tk.Frame(root, padx=10, pady=10)
    frame_delete_user.grid(row=0, column=2, padx=10, pady=10)

    label_header_delete = tk.Label(frame_delete_user, text="Delete User", font=("Arial", 14, "bold"))
    label_header_delete.grid(row=0, columnspan=2, pady=5)

    label_cpf_delete = tk.Label(frame_delete_user, text="Enter CPF:")
    label_cpf_delete.grid(row=1, column=0)
    entry_cpf_delete = tk.Entry(frame_delete_user)
    entry_cpf_delete.grid(row=1, column=1)

    delete_button = tk.Button(frame_delete_user, text="Get User Details for Delete", command=delete_user)
    delete_button.grid(row=2, columnspan=2)

    label_name_delete = tk.Label(frame_delete_user, text="Name:")
    label_name_delete.grid(row=3, column=0)
    entry_name_delete = tk.Entry(frame_delete_user)
    entry_name_delete.grid(row=3, column=1)

    label_designation_delete = tk.Label(frame_delete_user, text="Designation:")
    label_designation_delete.grid(row=4, column=0)
    entry_designation_delete = tk.Entry(frame_delete_user)
    entry_designation_delete.grid(row=4, column=1)

    label_phone_delete = tk.Label(frame_delete_user, text="Phone:")
    label_phone_delete.grid(row=5, column=0)
    entry_phone_delete = tk.Entry(frame_delete_user)
    entry_phone_delete.grid(row=5, column=1)

    label_master_delete = tk.Label(frame_delete_user, text="Master:")
    label_master_delete.grid(row=6, column=0)
    entry_master_delete = tk.Entry(frame_delete_user)
    entry_master_delete.grid(row=6, column=1)

    status_label_delete = tk.Label(frame_delete_user, text="")
    status_label_delete.grid(row=7, columnspan=2)

    delete_submit_button = tk.Button(frame_delete_user, text="Delete User", command=confirm_delete)
    delete_submit_button.grid(row=8, columnspan=2)


    root.mainloop()
