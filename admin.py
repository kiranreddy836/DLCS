import tkinter as tk
import tkinter.ttk as ttk
import cv2
from PIL import Image, ImageTk
from pyzbar.pyzbar import decode
import sqlite3
import re

conn = sqlite3.connect('ilcst.db')
cur = conn.cursor()

# Functions for managing feeders in the database
def check_feeder_exists(feeder_no):
    query = "SELECT feeder_no FROM feeders WHERE feeder_no=?"
    cur.execute(query, (feeder_no,))
    result = cur.fetchone()
    return result is not None


def add_feeder_to_db():
    feeder_number = entry_feeder_number.get().strip()  # Retrieve feeder number
    status = entry_status.get().strip()  # Retrieve status
    input_pin = entry_input_pin_add.get().strip()  # Retrieve input pin
    output_pin = entry_output_pin_add.get().strip()  # Retrieve output pin

    # Validate the feeder number format
    feeder_format = re.compile(r'^Feeder-\d{1,2}$')
    if not feeder_format.match(feeder_number):
        status_label_add_feeder.config(text="Invalid feeder format (Correct format e.g. Feeder-1/Feeder-21)", fg="red")
        return

    # Check if any of the fields are empty
    print(feeder_number, status, input_pin, output_pin)  # Add this line for debugging
    if not all([feeder_number, status, input_pin, output_pin]):
        status_label_add_feeder.config(text="All fields are mandatory!", fg="red")
        return

    # Check if the feeder already exists
    query = "SELECT feeder_no FROM feeders WHERE feeder_no = ?"
    cur.execute(query, (feeder_number,))
    existing_feeder = cur.fetchone()

    if existing_feeder:
        status_label_add_feeder.config(text="Feeder already exists!", fg="red")
        return

    # Insert the feeder details into the database
    cur.execute("INSERT INTO feeders (feeder_no, isActive, input_pin, output_pin) VALUES (?, ?, ?, ?)",
                (feeder_number, status, input_pin, output_pin))
    conn.commit()

    status_label_add_feeder.config(text="Feeder added successfully", fg="green")
    entry_feeder_number.delete(0, tk.END)
    entry_status.delete(0, tk.END)
    entry_input_pin_add.delete(0, tk.END)
    entry_output_pin_add.delete(0, tk.END)


def update_feeder_status(feeder_no, is_active, input_pin, output_pin):
    cur.execute("UPDATE feeders SET isActive=?, input_pin=?, output_pin=? WHERE feeder_no=?",
                (is_active, input_pin, output_pin, feeder_no))
    conn.commit()

def get_feeder_status():
    feeder_number = entry_feeder_number_update.get()
    feeder_format = re.compile(r'^Feeder-\d{1,2}$')

    if not feeder_format.match(feeder_number):
        status_label_update_feeder.config(text="Invalid feeder format", fg="red")
    else:
        query = "SELECT isActive, input_pin, output_pin FROM feeders WHERE feeder_no=?"
        cur.execute(query, (feeder_number,))
        result = cur.fetchone()

        if result is None:
            status_label_update_feeder.config(text="Feeder does not exist", fg="red")
        else:
            status = result[0]
            #status_label_update_feeder.config(text=f"Current Status: {status}", fg="green")
            input_pin = result[1]
            output_pin = result[2]

            entry_feeder_status_update.config(state=tk.NORMAL)
            entry_feeder_status_update.delete(0, tk.END)
            entry_feeder_status_update.insert(0, status)
            entry_feeder_status_update.config(state=tk.NORMAL)  # Enable status field for editing

            entry_input_pin.config(state=tk.NORMAL)
            entry_input_pin.delete(0, tk.END)
            entry_input_pin.insert(0, input_pin)
            entry_input_pin.config(state=tk.NORMAL)  # Enable input pin field for editing

            entry_output_pin.config(state=tk.NORMAL)
            entry_output_pin.delete(0, tk.END)
            entry_output_pin.insert(0, output_pin)
            entry_output_pin.config(state=tk.NORMAL)  # Enable output pin field for editing

            update_status_button.config(state=tk.NORMAL)  # Enable update status button

            # Ensure the update status button is disabled by default when fetching new details
            #update_status_button.config(state=tk.DISABLED)

def update_feeder_status_in_db():
    feeder_number = entry_feeder_number_update.get()
    is_active = entry_feeder_status_update.get()

    feeder_format = re.compile(r'^Feeder-\d{1,2}$')
    if not feeder_format.match(feeder_number):
        status_label_update_feeder.config(text="Invalid feeder format", fg="red")
    else:
        query = "SELECT isActive FROM feeders WHERE feeder_no=?"
        cur.execute(query, (feeder_number,))
        result = cur.fetchone()
        if result is None:
            status_label_update_feeder.config(text="Feeder does not exist", fg="red")
        else:
            update_feeder_status(feeder_number, is_active)
            status_label_update_feeder.config(text="Feeder status updated!", fg="green")


def show_camera(window):
    global cap
    cap = cv2.VideoCapture(0)
    label = tk.Label(window)
    label.pack()
    def on_close():
        stop_camera(window)

    window.protocol("WM_DELETE_WINDOW", on_close)

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
                stop_camera(window)
           else:
                print("Master Status is N")
                custom_message_box("UPDATE FAILED", f" You do not have In-Charge Privileges to update the master flag", "dark orange")
                stop_camera(window)

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

def stop_camera(window):
    if 'cap' in globals():
        cap.release()
    window.destroy()

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
        update_submit_button.config(state=tk.NORMAL)  # Enable the button
    else:
        entry_name_update.delete(0, tk.END)
        entry_designation_update.delete(0, tk.END)
        entry_phone_update.delete(0, tk.END)
        entry_master_update.delete(0, tk.END)
        status_label_update.config(text="User not found!", fg="red")
        update_submit_button.config(state=tk.DISABLED)  # Keep the button disabled


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
        delete_submit_button.config(state=tk.NORMAL)  # Enable the button
    else:
        entry_name_delete.delete(0, tk.END)
        entry_designation_delete.delete(0, tk.END)
        entry_phone_delete.delete(0, tk.END)
        entry_master_delete.delete(0, tk.END)
        status_label_delete.config(text="User not found!", fg="red")
        delete_submit_button.config(state=tk.DISABLED)  # Keep the button disabled

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

# Function to update feeder status in the database
def update_feeder_status_in_db():
    feeder_number = entry_feeder_number_update.get()
    is_active = entry_feeder_status_update.get()
    input_pin = entry_input_pin.get()
    output_pin = entry_output_pin.get()

    update_feeder_status(feeder_number, is_active, input_pin, output_pin)
    status_label_update_feeder.config(text="Feeder status updated!", fg="green")
    # Clear fields after successful update
    entry_feeder_number_update.delete(0, tk.END)
    entry_feeder_status_update.delete(0, tk.END)
    entry_input_pin.delete(0, tk.END)
    entry_output_pin.delete(0, tk.END)
    
    # Disable the update status button after clearing the fields
    update_status_button.config(state=tk.DISABLED)


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
    entry_master.insert(0, 'N')  # Set default value to 'N'
    entry_master.config(state='disabled')  # Make the entry non-editable
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

    update_submit_button = tk.Button(frame_update_user, text="Update User", command=start_camera_for_update, state=tk.DISABLED)
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

    delete_submit_button = tk.Button(frame_delete_user, text="Delete User", command=confirm_delete, state=tk.DISABLED)
    delete_submit_button.grid(row=8, columnspan=2)

    # Add Feeder Section
    frame_add_feeder = tk.Frame(root, padx=10, pady=10)
    frame_add_feeder.grid(row=0, column=3, padx=10, pady=10)

    label_header_add_feeder = tk.Label(frame_add_feeder, text="Add Feeder", font=("Arial", 14, "bold"))
    label_header_add_feeder.grid(row=0, columnspan=2, pady=5)

    label_feeder_no = tk.Label(frame_add_feeder, text="Feeder Number:")
    label_feeder_no.grid(row=1, column=0)
    entry_feeder_number = tk.Entry(frame_add_feeder)
    entry_feeder_number.grid(row=1, column=1)

    label_status = tk.Label(frame_add_feeder, text="Status (Y/N):")
    label_status.grid(row=2, column=0)
    entry_status = tk.Entry(frame_add_feeder)
    entry_status.grid(row=2, column=1)

    label_input_pin_add = tk.Label(frame_add_feeder, text="Input Pin:")
    label_input_pin_add.grid(row=3, column=0)
    entry_input_pin_add = tk.Entry(frame_add_feeder)
    entry_input_pin_add.grid(row=3, column=1)

    label_output_pin_add = tk.Label(frame_add_feeder, text="Output Pin:")
    label_output_pin_add.grid(row=4, column=0)
    entry_output_pin_add = tk.Entry(frame_add_feeder)
    entry_output_pin_add.grid(row=4, column=1)

    status_label_add_feeder = tk.Label(frame_add_feeder, text="")
    status_label_add_feeder.grid(row=5, columnspan=2)

    submit_feeder_button = tk.Button(frame_add_feeder, text="Add Feeder", command=add_feeder_to_db)
    submit_feeder_button.grid(row=6, columnspan=2)


    # Update Feeder Status Section
    frame_update_feeder = tk.Frame(root, padx=10, pady=10)
    frame_update_feeder.grid(row=1, column=0, columnspan=4, padx=10, pady=10)

    label_header_update_feeder = tk.Label(frame_update_feeder, text="Update Feeder Status", font=("Arial", 14, "bold"))
    label_header_update_feeder.grid(row=0, columnspan=2, pady=5)

    label_feeder_no_update = tk.Label(frame_update_feeder, text="Feeder Number:")
    label_feeder_no_update.grid(row=1, column=0)
    entry_feeder_number_update = tk.Entry(frame_update_feeder)
    entry_feeder_number_update.grid(row=1, column=1)

    get_status_button = tk.Button(frame_update_feeder, text="Get Status", command=get_feeder_status)
    get_status_button.grid(row=2, columnspan=2)

    label_status_update = tk.Label(frame_update_feeder, text="Status (Y/N):")
    label_status_update.grid(row=3, column=0)
    entry_feeder_status_update = tk.Entry(frame_update_feeder, state=tk.DISABLED)
    entry_feeder_status_update.grid(row=3, column=1)

    label_input_pin = tk.Label(frame_update_feeder, text="Input Pin:")
    label_input_pin.grid(row=5, column=0)
    entry_input_pin = tk.Entry(frame_update_feeder, state=tk.DISABLED)
    entry_input_pin.grid(row=5, column=1)

    label_output_pin = tk.Label(frame_update_feeder, text="Output Pin:")
    label_output_pin.grid(row=6, column=0)
    entry_output_pin = tk.Entry(frame_update_feeder, state=tk.DISABLED)
    entry_output_pin.grid(row=6, column=1)

    status_label_update_feeder = tk.Label(frame_update_feeder, text="")
    status_label_update_feeder.grid(row=7, columnspan=2)

    update_status_button = tk.Button(frame_update_feeder, text="Update Status", command=update_feeder_status_in_db, state=tk.DISABLED)
    update_status_button.grid(row=8, columnspan=2)


    root.mainloop()
