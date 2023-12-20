#DIGITAL LINE CLEARANCE SYSTEM MINE 1A SUBSTATION - SOURCE CODE AUTHOR - NALLAPA REDDY KIRAN KUMAR REDDY - CPF NO - 48979

import tkinter as tk
import tkinter.ttk as ttk
import sqlite3
import cv2
from PIL import Image, ImageTk
import numpy as np
from pyzbar.pyzbar import decode

import tkinter.messagebox as messagebox
#import RPi.GPIO as GPIO
import os
import tkinter.font as tkFont
from revpimodio2 import *
from revpimodio import *
import time
from datetime import datetime
#import CUPS

# Check if the lock file exists
lock_file = "app_lock.lock"
if os.path.isfile(lock_file):
    messagebox.showerror("Error", "Another instance of the application is already running.")
    exit()
# Create the lock file
open(lock_file, 'w').close()

def open_history_window():

    global combo_box_state, history_window, history_button # Use the global variables

    cb1.config(state="disabled")

    # Create a new window 
    history_window = tk.Toplevel(my_w)
    history_window.title("History window to see the previous log_in and log_out details")

    # Set focus 
    history_window.focus_set()
    history_window.grab_set()

    # Increase the size of the window
    window_width = 800
    window_height = 400

    # Calculate the window position to center it on the screen
    screen_width = history_window.winfo_screenwidth()
    screen_height = history_window.winfo_screenheight()
    x_position = (screen_width - window_width) // 2
    y_position = (screen_height - window_height) // 2

    # Set the window size and position
    history_window.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")

    # Disable both minimize and maximize options
    history_window.grab_set()

    # Fetch data from the database
    data = fetch_logdata()

    # Display the data in a Treeview widget
    tree = ttk.Treeview(history_window, columns=("cpfno", "name", "authorised_by", "feeder", "login_time", "logout_time", "errors", "master_logout", "time_stamp"),
                        show="headings", height=15)
    vsb = ttk.Scrollbar(history_window, orient="vertical", command=tree.yview)
    hsb = ttk.Scrollbar(history_window, orient="horizontal", command=tree.xview)
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
    
    tree.pack(expand=True, fill="both")

    def on_window_close():
         global admin_window  # Use the global variables
         cb1.config(state="normal")
         history_window.destroy()
         history_window.grab_release()

    history_window.protocol("WM_DELETE_WINDOW", on_window_close)

    close_button = tk.Button(history_window, text="Close", command=on_window_close)
    close_button.pack()



# Your database connection function
def fetch_logdata():
    cur.execute("SELECT * FROM logdata ORDER BY time_stamp DESC")
    data = cur.fetchall()
    return data

def open_admin_window():

    global combo_box_state, admin_window,admin_button # Use the global variables

    cb1.config(state="disabled")

    # Create a new window 
    admin_window = tk.Toplevel(my_w)
    admin_window.title("Admin Window to configure Users in database")

    # Set focus 
    admin_window.focus_set()
    admin_window.grab_set()

    # Increase the size of the window
    window_width = 5000
    window_height = 800

    # Calculate the window position to center it on the screen
    screen_width = admin_window.winfo_screenwidth()
    screen_height = admin_window.winfo_screenheight()
    x_position = (screen_width - window_width) // 2
    y_position = (screen_height - window_height) // 2

    # Set the window size and position
    admin_window.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")

    # Disable both minimize and maximize options
    admin_window.grab_set()
    
    def validate_cpf_length(new_value):
        return new_value.isdigit() and len(new_value) <= 5

    validate_cpf_length_cmd = admin_window.register(validate_cpf_length)

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
        elif not existing_cpf and len(cpf)==5:
            # Insert the new user into the database
            cur.execute("INSERT INTO users (cpf_no, name, designation, phone_no, master) VALUES (?, ?, ?, ?, ?)",
                        (cpf, name, designation, phone, master))
            conn.commit()
            status_label_add.config(text="User added successfully!",fg="green")
        else:
            status_label_add.config(text="You are trying to add Invaid Cpf Number!",fg="red")

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
            entry_master_update.config(state='disabled') 
            status_label_update.config(text="")
        else:
            entry_name_update.delete(0, tk.END)
            entry_designation_update.delete(0, tk.END)
            entry_phone_update.delete(0, tk.END)
            entry_master_update.delete(0, tk.END)
            status_label_update.config(text="User not found!",fg="red")

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
            status_label_delete.config(text="User not found!",fg="red")

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

    def on_window_close():
        global admin_window  # Use the global variables
        cb1.config(state="normal")
        admin_window.destroy()
        admin_window.grab_release()

    admin_window.protocol("WM_DELETE_WINDOW", on_window_close)

    def stop_camera():
        global camera_running, cap
        if camera_running:
            camera_running = False
            resetqr()
            resetapproval("False")
            cap.release()
            label.imgtk = None
            label.configure(image=None)
            sel.set("Select the Feeder") # Set the combo box value back to default
            submitbutton.config(state="disabled")
            cb1.focus_set()
            for w in my_w.grid_slaves(row=5):  # all elements in row 5
             w.grid_remove()  # delete elements

    stop_camera()
    # Add User Section
    frame_add_user = tk.Frame(admin_window, padx=10, pady=10)
    frame_add_user.grid(row=0, column=0, padx=10, pady=10)

    label_header_add = tk.Label(frame_add_user, text="Add User", font=("Arial", 14, "bold"), bg="turquoise")
    label_header_add.grid(row=0, columnspan=2, pady=5)

    label_cpf = tk.Label(frame_add_user, text="CPF:")
    label_cpf.grid(row=1, column=0)
    entry_cpf = tk.Entry(frame_add_user, validate="key", validatecommand=(validate_cpf_length_cmd, "%P"))
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
    frame_update_user = tk.Frame(admin_window, padx=10, pady=10)
    frame_update_user.grid(row=0, column=1, padx=10, pady=10)

    label_header_update = tk.Label(frame_update_user, text="Update/View User", font=("Arial", 14, "bold"), bg="pale turquoise")
    label_header_update.grid(row=0, columnspan=2, padx=0, pady=5)

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
    #entry_master_update.config(state='disabled')
    entry_master_update.grid(row=6, column=1)

    status_label_update = tk.Label(frame_update_user, text="")
    status_label_update.grid(row=7, columnspan=2)

    update_submit_button = tk.Button(frame_update_user, text="Update User", command=update_user)
    update_submit_button.grid(row=8, columnspan=2)

    # Delete User Section
    frame_delete_user = tk.Frame(admin_window, padx=10, pady=10)
    frame_delete_user.grid(row=0, column=2, padx=10, pady=10)

    label_header_delete = tk.Label(frame_delete_user, text="Delete User", font=("Arial", 14, "bold"), bg="red")
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

    # Note label at the bottom
    note_label = tk.Label(admin_window, text="    NOTE: In-charge privilege for an user can be updated only through admin portal. ", pady=10, font=("Arial", 10, "bold"))
    note_label.grid(row=5, column=0, columnspan=3, sticky="ew")  # Positioned at the bottom

    # Close button for the window
    close_button = tk.Button(admin_window, text="Close Admin Window", command=on_window_close)
    close_button.grid(row=2, column=0, columnspan=3, pady=10)

    admin_window.columnconfigure(0, weight=1)  # Ensures horizontal centering of the label


# Create RevPiModIO2 object
#pi = RevPiModIO(autorefresh=True)

# Define output pins corresponding to feeders
feeder_output_pins = {
    'Feeder-1': "O_1",
    'Feeder-2': "O_2",
    'Feeder-3': "O_3",
    'Feeder-4': "O_4"
}

# Define Input pins corresponding to feeders
feeder_input_pins = {
    'Feeder-1': "I_1",
    'Feeder-2': "I_2",
    'Feeder-3': "I_3",
    'Feeder-4': "I_4"
}

# Function to set feeder lock status
def set_feeder_output_status(feeder_number, lock_status):
    print("output pins set")
    """
    pin = feeder_output_pins.get(feeder_number)
    pi.write_value(pin, lock_status)
    pi.refresh()
    print(f"Feeder-{feeder_number} lock status set to {lock_status}")"""

# Function to get input status of a feeder
def get_feeder_input_status(feeder_number):
    print("Input status fetched")

    """ 
    pin = feeder_input_pins.get(feeder_number)
    input_status = pi.read_value(pin)
    print(f"Status of Feeder-{feeder_number} input: {input_status}")
    return input_status"""

# Function to get output status of a feeder
def get_feeder_output_status(feeder_number):
    print('Output status fetched')
    """pin = feeder_output_pins.get(feeder_number)
    output_status = pi.read_value(pin)
    print(f"Status of Feeder-{feeder_number} output: {output_status}")
    return output_status"""

# Function to compare input and output status for a feeder
def compare_input_output_status(feeder_number):
    """input_status = get_feeder_input_status(feeder_number)
    output_status = get_feeder_output_status(feeder_number)
    
    match_status = input_status == output_status
    print(f"Feeder-{feeder_number} input status: {input_status}")
    print(f"Feeder-{feeder_number} output status: {output_status}")"""
    print("Comparison of input and output pins done")
    
    return True
# Initialize the variable to store the last scanned cpfNo
#global last_scanned_cpf 

def display_header(root):

    # Load the background image
    background_image = Image.open("mines.jpeg")
    window_width = root.winfo_screenwidth()
    window_height = root.winfo_screenheight()
    resized_bg = background_image.resize((window_width, window_height))

    # Convert image to HSL color space
    hsl_image = resized_bg.convert("RGB").convert("HSV")
    brightness = 0.82  # Adjust the brightness factor here (1.0 is the original)

    # Increase or decrease the brightness
    h, s, l = hsl_image.split()
    l = l.point(lambda i: i * brightness)
    adjusted_image = Image.merge("HSV", (h, s, l)).convert("RGB")

    background_photo = ImageTk.PhotoImage(adjusted_image)

    # Create a label to hold the background image
    background_label = tk.Label(root, image=background_photo)
    background_label.image = background_photo  # Keep a reference to avoid garbage collection
    background_label.place(x=0, y=0, relwidth=1, relheight=1)

    # Header Frame
    header_frame = tk.Frame(root, bg="RoyalBlue4", pady=10)
    header_frame.grid(row=0, column=0, columnspan=2, sticky="nsew")
    image_filename = "nlclogo.png"
    # NLC Logo
    try:
        logo_image = Image.open(image_filename)
        logo_image = logo_image.resize((105, 100))
        logo_photo = ImageTk.PhotoImage(logo_image)
        root.logo_photo = logo_photo  # Store the PhotoImage as an attribute of the root window
        logo_label = tk.Label(header_frame, image=logo_photo)
        logo_label.grid(row=0, column=0, padx=0, pady=0, sticky="w")
    except FileNotFoundError:
        print("Logo image not found. Make sure the image file exists.")

    image_filename2="CMD.png"
    # Load the image for the extreme right
    try:
        right_image = Image.open(image_filename2)  # Replace with your image path
        right_image = right_image.resize((90, 100))  # Adjust size as needed
        right_photo = ImageTk.PhotoImage(right_image)
        right_label = tk.Label(header_frame, image=right_photo, bg="RoyalBlue4")
        right_label.image = right_photo  # Keep a reference to avoid garbage collection
        
        # Position the right image to the right of the title label
        right_label.place(relx=0.92, rely=0.49, anchor="e")  # Adjust position as needed
    except FileNotFoundError:
        print("Image not found. Make sure the image file exists.")

    image_filename2="D-M.png"
    # Load the image for the extreme right
    try:
        right_image = Image.open(image_filename2)  # Replace with your image path
        right_image = right_image.resize((90, 100))  # Adjust size as needed
        right_photo = ImageTk.PhotoImage(right_image)
        right_label = tk.Label(header_frame, image=right_photo, bg="RoyalBlue4")
        right_label.image = right_photo  # Keep a reference to avoid garbage collection
        
        # Position the right image to the right of the title label
        right_label.place(relx=0.99, rely=0.49, anchor="e")  # Adjust position as needed
    except FileNotFoundError:
        print("Image not found. Make sure the image file exists.")

    # Title
    title_label = ttk.Label(header_frame, text="DIGITALIZED LINE CLEARANCE SYSTEM", font=("Times New Roman", 25, 'bold'), background="RoyalBlue4",foreground="white")
    title_label.place(relx=0.5, rely=0.4, anchor="center")

    # label text for unit selection
    unit_label = ttk.Label(header_frame, text="MINE-1A SUBSTATION",
                       background='RoyalBlue4', foreground="white",
                       font=("Times New Roman", 17, 'bold'))
    unit_label.place(relx=0.5, rely=0.8, anchor="center")
    # Footer Label
    footer_label = tk.Label(my_w, text="DEVELOPED AND INTEGRATED BY MINE 1A ELECTRICAL BASE", bg="burlywood1", fg="black", font=("Arial", 12, "bold"))
    footer_label.place(relx=0.5, rely=0.92, anchor="center")
    # Admin Button
    admin_button = tk.Button(header_frame, text="Admin", command=open_admin_window, bg="orange", fg="black")
    admin_button.grid(row=0, column=2, padx=10)  # Adjust column and padding as needed
    admin_button.place(relx=0.085, rely=0.86, anchor="w")
    # History Button
    history_button = tk.Button(header_frame, text="History", command=open_history_window, bg="pale turquoise", fg="black")
    history_button.grid(row=0, column=2, padx=10)  # Adjust column and padding as needed
    history_button.place(relx=0.12, rely=0.86, anchor="w")


# Establish SQLITE Database Connection (If using SQLite3 -- Comment other connection modes if using SQLite)
current_directory = os.getcwd()
db_file = os.path.join(current_directory, "ilcst.db")
conn = sqlite3.connect(db_file)
cur = conn.cursor()

"""def print(qrCPF, qrName, selectedFeeder, scannedqrCode, login_time, logout_time, master):
    # Initialize a connection to the CUPS server
    conn = cups.Connection()
    # Get a list of available printers
    printers = conn.getPrinters()
    # printer's name
    printer_name = 'DLCS'
    # Check if the chosen printer is available
    if printer_name in printers:
        # Prepare the data to be printed
        data_to_print = f"qrCPF: {qrCPF}, qrName: {qrName}, selectedFeeder: {selectedFeeder}, scannedqrCode: {scannedqrCode}, datetime: login_time}"
        # Send data to the printer
        conn.printFile(printer_name, "-", {"cpi": "12", "lpi": "6"}, data_to_print)
        print("Printing successful.")
    else:
        print("Printer not found.")"""

def updatelogdata(qrCPF, qrName, selectedFeeder, scannedqrCode, login_time, logout_time, errors, master_logout,time_stamp):
    data_to_insert = (qrCPF, qrName, selectedFeeder, scannedqrCode, login_time, logout_time, errors, master_logout,time_stamp)
    insert_query = '''INSERT INTO logdata (cpfNo, name, feeder, authorised_by, login_time, logout_time, errors, master_logout, time_stamp)
                      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)'''
    cur.execute(insert_query, data_to_insert)
    conn.commit()

"""# Function to stop the camera feed
def stop_camera():
    global camera_running, cap
    if camera_running:
        camera_running = False
        resetqr()
        resetapproval("False")
        cap.release()"""

def stop_camera():
    global camera_running, cap
    if camera_running:
        camera_running = False
        resetqr()
        resetapproval("False")
        cap.release()
        label.imgtk = None
        label.configure(image=None)
        sel.set("Select the Feeder") # Set the combo box value back to default
        submitbutton.config(state="disabled")
        cb1.focus_set()
        for w in my_w.grid_slaves(row=5):  # all elements in row 5
            w.grid_remove()  # delete elements


# Function to enable or disable the "Select Feeder" combo box
def set_combo_box_state(state):
    cb1["state"] = state  # Set the state of the combo box

# Function to re-enable the "Select Feeder" combo box when the name selection window is closed
def on_name_selection_window_close(name_selection_window):
    global combo_box_state  # Use the global variable
    set_combo_box_state(combo_box_state)  # Restore the previous state
    name_selection_window.destroy()  # Close the name selection window

# Create a global variable to keep track of the name selection window state
name_selection_window = None  # Initialize name_selection_window

# Function to release the lock file when the application is closed
def on_main_window_close():
    # Delete the lock file
    if os.path.isfile(lock_file):
        os.remove(lock_file)
    my_w.destroy()

# Create a function to display names for logout in a new window (as a modal dialog)
def display_names_for_logout(selectedFeeder):
    global combo_box_state, name_selection_window  # Use the global variables

    cb1.config(state="disabled")

    # Create a new window for name selection
    name_selection_window = tk.Toplevel(my_w)
    name_selection_window.title("Select Name for Logout")

    # Set focus to the "Select Logout Users" window
    name_selection_window.focus_set()
    name_selection_window.grab_set()

    # Increase the size of the window
    window_width = 400
    window_height = 200

    # Calculate the window position to center it on the screen
    screen_width = name_selection_window.winfo_screenwidth()
    screen_height = name_selection_window.winfo_screenheight()
    x_position = (screen_width - window_width) // 2
    y_position = (screen_height - window_height) // 2

    # Set the window size and position
    name_selection_window.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")

    # Disable both minimize and maximize options
    name_selection_window.grab_set()

    def on_window_close():
        # Callback function to run when the name selection window is closed
        # Reset the state to indicate that the window is closed
        global name_selection_window  # Use the global variables
        cb1.config(state="normal")
        name_selection_window.destroy()
        name_selection_window.grab_release()

    name_selection_window.protocol("WM_DELETE_WINDOW", on_window_close)

    # Fetch names corresponding to the selected feeder number from the database
    query = "SELECT names FROM logindata WHERE feederno = ?"
    cur.execute(query, (selectedFeeder,))
    result = cur.fetchone()

    if result:
        names_list = result[0].split(',') if result[0] else []

        # Create a label for the combo box
        combo_label = ttk.Label(name_selection_window, text="Select a name to log out:")
        combo_label.pack(padx=10, pady=10)

        # Create a combo box to display names
        selected_name = tk.StringVar(value='Select')
        combo_box = ttk.Combobox(name_selection_window, textvariable=selected_name, values=names_list, state="readonly")
        combo_box.pack(padx=10, pady=10)

        def fetchcpf(name_to_logout):
            parts = name_to_logout.split('_')
            cpf_No = parts[1] if len(parts) > 1 else None
            return cpf_No

        def logout_selected_name():
            name_to_logout = selected_name.get()
            if name_to_logout:
                # Remove the selected name from the list
                names_list.remove(name_to_logout)
                updated_names = ",".join(names_list)
                query = "UPDATE logindata SET names = ? WHERE feederno = ?"
                cur.execute(query, (updated_names, selectedFeeder))
                conn.commit()
                initialize_feeder_info_window(my_w)
                status = compare_input_output_status(selectedFeeder)
                if status:
                    custom_message_box("User Logout", f"{name_to_logout} has been logged out from {selectedFeeder}.", "green")
                    name_selection_window.destroy()
                    cb1.config(state="normal")
                    updatelogdata(fetchcpf(name_to_logout), name_to_logout, selectedFeeder, fetchscannedQR(), None, datetime.now(), 'No Error.This is a master logout','Y', datetime.now())
                    stop_camera()
                else:
                    custom_message_box("ERROR IN LOCKING MECHANISM. FEEDBACK FAILED", f"{selectedFeeder} has not been locked due to feedback failure at the site", "dark orange")
                    names_list.append(name_to_logout)
                    updated_names = ",".join(names_list)
                    query = "UPDATE logindata SET names = ? WHERE feederno = ?"
                    cur.execute(query, (updated_names, selectedFeeder))
                    conn.commit()
                    initialize_feeder_info_window(my_w)
                    updatelogdata(fetchcpf(name_to_logout), name_to_logout, selectedFeeder, fetchscannedQR(), None, None, 'Feedback Error','Y', datetime.now())
                    cb1.config(state="normal")
                    stop_camera()

        def close_select_logout_window():
            name_selection_window.destroy()
            cb1.config(state="normal")

        # Create a submit button
        submit_button = ttk.Button(name_selection_window, text="Submit", command=logout_selected_name)
        submit_button.pack(padx=10, pady=10)
        # Add a close button
        close_button = tk.Button(name_selection_window, text="Close", command=close_select_logout_window)
        close_button.pack()
        name_selection_window.bind("<Return>", lambda event: name_selection_window.focus_get().invoke())
        # Wait for the name selection window to be closed without grabbing focus
        name_selection_window.wait_window(name_selection_window)
    else:
        custom_message_box("Feeder Not Found", f"Feeder {selectedFeeder} not found.", "red")

def custom_askyesno(title, message, bg_color):
    result = False  # Initialize the result as False
    def on_yes():
        nonlocal result
        result = True
        dialog.destroy()
    def on_no():
        nonlocal result
        result = False
        dialog.destroy()
    dialog = tk.Toplevel()

    # Create a custom title bar frame with a background
    title_bar = tk.Frame(dialog, bg=bg_color, relief="raised", bd=1)
    title_bar.pack(fill="x")
    
    # Create a label for the title within the custom title bar
    title_label = ttk.Label(title_bar, text=title, font=("Times New Roman", 16, "bold"),  background=bg_color)
    title_label.pack(side="left", padx=5)
    dialog.configure(bg="white")

    # Calculate screen width and height
    screen_width = dialog.winfo_screenwidth()
    screen_height = dialog.winfo_screenheight()
    
    # Calculate the window size and position it in the center
    window_width = 500  # Adjust as needed
    window_height = 180  # Adjust as needed
    x_position = (screen_width - window_width) // 2
    y_position = (screen_height - window_height) // 2
    
    # Set the window size and position
    dialog.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")
    dialog.resizable(False, False)
    
    # Remove the default title bar
    dialog.overrideredirect(1)

    message_label = ttk.Label(dialog, text=message, font=("Arial", 12, "bold"), wraplength=380, background="white")
    message_label.pack(pady=20)

    yes_button = ttk.Button(dialog, text="yes", command=on_yes)
    yes_button.pack(side="left", padx=10)

    no_button = ttk.Button(dialog, text="No", command=on_no)
    no_button.pack(side="right", padx=10)

    yes_button.focus_set()

    # Bind the Enter key to trigger the "Yes" and "No" button's action

    dialog.bind("<Return>", lambda event: dialog.focus_get().invoke())
    dialog.grab_set()  # Make the dialog modal
    dialog.wait_window()  # Wait for the dialog to be closed

    return result

def custom_askyesnoforapproval(title, message, bg_color):
    result1 = None  # Initialize the result as None
    
    def on_yes():
        nonlocal result1
        result1 = True
        dialog.destroy()
        
    def on_no():
        nonlocal result1
        result1 = False
        dialog.destroy()

    dialog = tk.Toplevel()
    dialog.configure(bg="white")
    dialog.overrideredirect(1)
    
    # Calculate screen width and height
    screen_width = dialog.winfo_screenwidth()
    screen_height = dialog.winfo_screenheight()
    
    # Calculate the window size and position it in the center
    window_width = 500  # Adjust as needed
    window_height = 180  # Adjust as needed
    x_position = (screen_width - window_width) // 2
    y_position = (screen_height - window_height) // 2
    
    # Set the window size and position
    dialog.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")
    dialog.resizable(False, False)
    
    # Create a custom title bar frame with a background
    title_bar = tk.Frame(dialog, bg=bg_color, relief="raised", bd=1)
    title_bar.pack(fill="x")
    
    # Create a label for the title within the custom title bar
    title_label = ttk.Label(title_bar, text=title, font=("Times New Roman", 16, "bold"), background=bg_color)
    title_label.pack(side="left", padx=5)
    
    message_label = ttk.Label(dialog, text=message, font=("Arial", 12, "bold"), wraplength=380, background="white")
    message_label.pack(pady=20)

    yes_button = ttk.Button(dialog, text="Approve Other Users", command=on_yes)
    yes_button.pack(side="left", padx=10)

    no_button = ttk.Button(dialog, text="Operate Self", command=on_no)
    no_button.pack(side="right", padx=10)

    yes_button.focus_set()

    dialog.bind("<Return>", lambda event: dialog.focus_get().invoke())
    dialog.grab_set()  
    dialog.wait_window()  

    return result1

# Function to initialize the feeder info window
def initialize_feeder_info_window(parent):
    feeder_info_frame = tk.Frame(parent, background="snow2")
    feeder_info_frame.place(relx=0.61, rely=0.18, relwidth=0.38, relheight=0.2)

    # Create label for Feeders Info Frame
    label = tk.Label(feeder_info_frame, text="STATUS OF THE FEEDERS", font=("Times New Roman", 15, "bold"), background="pale turquoise",foreground="red4")
    label.pack()

    # Create a horizontal scrollbar for the treeview
    h_scrollbar = ttk.Scrollbar(feeder_info_frame, orient="horizontal", style="Horizontal.TScrollbar")
    h_scrollbar.pack(side="bottom", fill="x")

    # Create a vertical scrollbar for the treeview
    y_scrollbar = ttk.Scrollbar(feeder_info_frame, orient="vertical", style="Vertical.TScrollbar")
    y_scrollbar.pack(side="right", fill="y")
    
    header_style = ttk.Style()
    header_style.configure("Treeview.Heading", font=("Arial", 11, "bold"))
    
    tree = ttk.Treeview(feeder_info_frame, columns=("FEEDER NO : ", "LINE CLEARANCE STATUS"), show="headings", xscrollcommand=h_scrollbar.set, yscrollcommand=y_scrollbar.set)
    
    # Disable selection
    tree.selection_set(())
    tree.bind("<ButtonRelease-1>", lambda event: tree.selection_set(()))

    tree.tag_configure("bold", font=("Arial", 10, "bold"))
   
    tree.heading("FEEDER NO : ", text="FEEDER NO : ", anchor="w")
    tree.heading("LINE CLEARANCE STATUS", text="LINE CLEARANCE STATUS", anchor="w")

    # Set the "Feeder No" column width as a percentage of the total frame width
    tree.column("FEEDER NO : ", width=int(feeder_info_frame.winfo_width() * 0.2))  # Adjust 0.2 as needed

    # Set the "Line Clearance Issued" column width as a percentage of the total frame width
    tree.column("LINE CLEARANCE STATUS", width=int(feeder_info_frame.winfo_width() * 0.6))  # Adjust 0.6 as needed


    h_scrollbar.config(command=tree.xview)  # Connect horizontal scrollbar to treeview
    y_scrollbar.config(command=tree.yview)  # Connect vertical scrollbar to treeview

    # Fetch feeder data from the database and update the treeview
    query = """
    SELECT ld.feederno, ld.names
    FROM logindata AS ld
    ORDER BY ld.feederno ASC
    """
    cur.execute(query)
    rows = cur.fetchall()
    
    for row in rows:
        # Use feeder Number and Status to activate the SBC pins based on user interaction with the GUI
        feeder_no = row[0]
        locked_names = row[1]
        lock_status = False
        if len(locked_names)!=0:
            lock_status = True
        set_feeder_output_status(feeder_no,lock_status)

        if locked_names:
           names_list = locked_names.split(',')
           first_name = names_list[0]
           other_names = ', '.join(names_list[1:])
           names_display = f"LC issued for :: {first_name}, {other_names}" if other_names else f"LC issued for :: {first_name}"
           bg_color = "spring green"
        else:
           names_list = []
           names_display = "LC not issued for this feeder"  # Set the default text
           bg_color = "sienna1"
        
        # Insert the row with the specified background color
        tree.insert("", "end", values=(feeder_no, names_display), iid=feeder_no, tags=("bg_color_" + bg_color,"bold"))
        tree.tag_configure("bg_color_" + bg_color, background=bg_color)

    # Calculate the maximum width needed for the "Locked By" column
    max_locked_by_width = max([len(name) for name in names_list], default=350)
    # Set the "Locked By" column width with some padding
    tree.column("FEEDER NO : ", width=100)
    tree.column("LINE CLEARANCE STATUS", width=max_locked_by_width * 300)  # Adjust the multiplier as needed multiplier as needed
    tree.pack()

def extract_cpf_no(name):
    # Extract the cpf_no from the name in the format "KIRAN_48979"
    parts = name.split('_')
    if len(parts) == 2:
        return parts[1]
    return None

# Build the Tkinter window
my_w = tk.Tk()
my_w.configure(bg="azure3")
my_w.resizable(False, False)

# Get screen width and height
screen_width = my_w.winfo_screenwidth()
screen_height = my_w.winfo_screenheight()

# Calculate the window size and position it in the center
window_width = int(screen_width * 1)  # You can adjust this as needed
window_height = int(screen_height * 1)  # You can adjust this as needed
x_position = (screen_width - window_width) // 2
y_position = (screen_height - window_height) // 2

# Set the window size and position
my_w.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")
my_w.title("DIGITALIZED LC SYSTEM")
display_header(my_w)
my_w.protocol("WM_DELETE_WINDOW", on_main_window_close)

# Reduce the vertical spacing between rows
row_padding = (3, 0)

# Configure grid weights for responsive layout
my_w.columnconfigure(0, weight=1)
my_w.rowconfigure(0, weight=0)  # Reduce weight for title row
my_w.rowconfigure(1, weight=0)  # Reduce weight for unit row
my_w.rowconfigure(2, weight=0)  # Reduce weight for feeder label row
my_w.rowconfigure(3, weight=0)  # Reduce weight for combo box row
my_w.rowconfigure(4, weight=0)  # Reduce weight for submit button row
my_w.rowconfigure(5, weight=0)  # Reduce weight for frames row

# String for handling transitions
sel = tk.StringVar(value='Select the Feeder')

data = ("MINE-1A",)
cur.execute("select number from feeders where unit=?", data)
row = cur.fetchone()
feederCount = row[0]
displayfeeders = []

for i in range(feederCount):
    displayfeeders.append("Feeder-" + str(i+1))

# Combo box for selecting the feeder Number for the corresponding unit selected
feeder_label = ttk.Label(my_w, text="FEEDER NUMBER",
                         background='burlywood1', foreground="black",
                         font=("Times New Roman", 15, 'bold'))
feeder_label.grid(row=1, column=0, padx=20, pady=15)
#feeder_label.place()

cb1 = ttk.Combobox(my_w, values=displayfeeders, width=25, textvariable=sel,state="readonly")
cb1.grid(row=2, column=0, padx=10, pady=10)

def check_cpfNo(qrCpF):
    # Query the database for user details with the matching CPF
    cur.execute("SELECT cpf_no, name, phone_no FROM users WHERE cpf_no = ?", (qrCpF,))
    user_details = cur.fetchone()  # Assuming there's only one user with the same CPF
    return user_details

# Create the input field for CPF
def display_cpf_details():
    cpf_no = cpf_entry.get()
    # Query the database for user details with the matching CPF
    cur.execute("SELECT cpf_no, name, designation, phone_no FROM users WHERE cpf_no = ?", (cpf_no,))
    user_details = cur.fetchone()  # Assuming there's only one user with the same CPF
    # Clear the label text
    details_label.config(text="")

    if user_details:
        custom_font = ("Times New Roman", 11,"bold")
        # Update the label to display user details
        details_label.config(text=f"CPF Number:- {user_details[0]}\nName:- {user_details[1]}\nPhone Number:- {user_details[2]}", font=custom_font)
    else:
        details_label.config(text="User not found")

cpf_info_frame = tk.Frame(my_w, background="azure2")
cpf_info_frame.place(relx=0.01, rely=0.18, relwidth=0.32, relheight=0.1)
 # Create label for Feeders Info Frame
label = tk.Label(cpf_info_frame, text="GET CONTACT DETAILS", font=("Times New Roman", 14, "bold"),foreground="blue")
label.pack()
cpf_label = tk.Label(cpf_info_frame, text="Enter CPF Number:", font=("Times New Roman", 15, "bold"), background="snow2", foreground="red4")
cpf_label.pack(side="left", padx=10, pady=10)

cpf_entry = ttk.Entry(cpf_info_frame)
cpf_entry.pack(side="left", padx=10, pady=10)

cpf_submit_button = ttk.Button(cpf_info_frame, text="Submit CPF", command=display_cpf_details)
cpf_submit_button.pack(side="left", padx=10, pady=10)

# Create a label for displaying user details
details_label = tk.Label(my_w, text="", font=("Arial", 12), background="azure2")
details_label.place(relx=0.01, rely=0.27, relwidth=0.32, relheight=0.11)

# Set the initial focus to the combobox
cb1.focus_set()

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

def my_upd(*args):
    stop_camera()
    for w in my_w.grid_slaves(row=5):  # all elements in row 5
        w.grid_remove()  # delete elements

    # Combo box for selecting the feeder Number for the corresponding unit selected
    selectedFeeder = sel.get()
    print("Display the selected feeder" + selectedFeeder)
    print(selectedFeeder)
    # Check if the combo box is displaying the default value
    if selectedFeeder == "Select the Feeder":
        submitbutton.config(state="disabled")
    else:
        submitbutton.config(state="normal", command=lambda: submit(selectedFeeder))
    # Update the state of the submit button
    if not camera_running:
        submitbutton.config(state="normal", command=lambda: submit(selectedFeeder))
    else:
        submitbutton.config(state="disabled")
    submitbutton.grid(row=4, column=0, padx=20, pady=10, columnspan=2)

sel.trace('w', my_upd)

# Create a flag to track whether the camera is running
camera_running = False

# Create a reference to the camera capture
cap = None

# Function to check master status from the users table
def check_master_status(qrCPF):
    query = "SELECT master FROM users WHERE cpf_no = ?"
    cur.execute(query, (qrCPF,))
    result = cur.fetchone()
    if result:
        return result[0]
    else:
        return None
# Function to log out all users from a feeder
def logout_all_users(selectedFeeder):
    query = "UPDATE logindata SET names = '' WHERE feederno = ?"
    cur.execute(query, (selectedFeeder,))
    conn.commit()
    initialize_feeder_info_window(my_w)

def updateqr(qrCpf):
     query = "UPDATE qrdata SET scannedqr = ?"
     cur.execute(query, (qrCpf,))
     conn.commit()
def resetqr():
     resetscannedqr=None
     query = "UPDATE qrdata SET scannedqr = ?"
     cur.execute(query, (resetscannedqr,))
     conn.commit()

def fetchscannedQR():
     query = "SELECT scannedqr from qrdata"
     cur.execute(query)
     # Fetch the result
     result = cur.fetchone()
    # Check if result is not None before returning
     if result is not None:
        return result[0]
     else:
        return None
def resetapproval(approval_shown):
     query = "UPDATE approvals SET approvalshown = ?"
     cur.execute(query, (approval_shown,))
     conn.commit()

def fetchapproval():
     query = "SELECT approvalshown from approvals"
     cur.execute(query)
     # Fetch the result
     result = cur.fetchone()
    # Check if result is not None before returning
     if result is not None:
        return result[0]
     else:
        return None

def updateapproval(approval_shown):
     query = "UPDATE approvals SET approvalshown = ?"
     cur.execute(query, (approval_shown,))
     conn.commit()

def display_scan_prompt():
        global prompt_window
        prompt_window = messagebox.showinfo("Incharge Authorization Success", "User can scan his card now. \nCamera will be closed automatically in a minute if no input is received.\nPlease click Okay to allow user to scan")
   

def show_frames(label, selectedFeeder):
    global camera_running, cap
    cap = cv2.VideoCapture(0)
    resetapproval("False")
    def detect_and_display_qr_codes():
        ret, frame = cap.read()
        if not ret:
            return
        # Convert the frame to grayscale for QR code detection
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Detect QR codes
        decoded_objects = decode(frame)
        for obj in decoded_objects:
            qr_data = obj.data.decode('utf-8')
            # Check if qr_data exists in the logindata table
            query = "SELECT names FROM logindata WHERE feederno = ?"
            cur.execute(query, (selectedFeeder,))
            result = cur.fetchone()
            partsqr = qr_data.split("_")

            if len(partsqr) == 3:
                name, qrCPF, qrMode = partsqr
                user_details = check_cpfNo(qrCPF)     
                if(user_details):
                    if check_master_status(qrCPF)=="Y" and fetchapproval()=="False":
                        updateqr(qrCPF)
                    scannedqrCode = fetchscannedQR()
                    qrName = "_".join([name,qrCPF])
                    if result is not None:
                        names = result[0].split(",") if result[0] else []
                    else:
                        print("No matching record found.")
                    # Validate if its master
                    master_status = check_master_status(qrCPF)
                    approval_shown =fetchapproval()

                    if approval_shown == "False" and master_status == "Y":
                        confirmation = custom_askyesnoforapproval("IN-CHARGE OPERATION DETECTED", "Select Approve other users button if you are allowing other users to scan \nSelect Operate Self button to lock or unlock the selected feeder","blue")
                        if(confirmation):
                            updateapproval("True")
                        else:
                            if "ON" in qr_data:
                                confirmation = custom_askyesno("IN-CHARGE SELF LOG_IN OPERATION", "You have scanned to lock the feeder,\nClick Yes if you are going to lock the selected Feeder \nClick No button to cancel and exit","orange")    
                                if(confirmation):
                                    if result is not None:
                                        # User is already logged in
                                        if len(names)!=0 and qrName not in names:
                                            names.append(qrName)
                                            # Update the names in the logindata table
                                            updated_names = ",".join(names)
                                            query = "UPDATE logindata SET names = ? WHERE feederno = ?"
                                            cur.execute(query, (updated_names, selectedFeeder))
                                            conn.commit()
                                            initialize_feeder_info_window(my_w)
                                            status = compare_input_output_status(selectedFeeder)
                                            if status:
                                                custom_message_box("LOCK SUCCESS - MULTIPLE LOCKS FOUND", f" You have locked the feeder Successfully.\n {selectedFeeder} is now locked by multiple persons", "dark orange")
                                                updatelogdata(qrCPF, qrName, selectedFeeder, scannedqrCode, datetime.now(), None, 'No Error','N', datetime.now())
                                                stop_camera()
                                            else:
                                                custom_message_box("ERROR IN LOCKING MECHANISM. FEEDBACK FAILED", f"{selectedFeeder} has not been locked due to feedback failure at the site", "dark orange")
                                                names.remove(qrName)
                                                # Update the names in the logindata table
                                                updated_names = ",".join(names)
                                                query = "UPDATE logindata SET names = ? WHERE feederno = ?"
                                                cur.execute(query, (updated_names, selectedFeeder))
                                                conn.commit()
                                                initialize_feeder_info_window(my_w)
                                                updatelogdata(qrCPF, qrName, selectedFeeder, scannedqrCode, None, None, 'Feedback Error','N', datetime.now())
                                                # Stop the camera feed
                                                stop_camera()

                                        elif len(names)!=0 and qrName in names: 
                                            custom_message_box("FEEDER ALREADY LOCKED", f"{selectedFeeder} is already locked by you", "pale turquoise")
                                            # Stop the camera feed
                                            updatelogdata(qrCPF, qrName, selectedFeeder, scannedqrCode, None, None, 'Feeder already locked','N', datetime.now())
                                            stop_camera()

                                        elif len(names) == 0:       
                                            # update data into the logindata table
                                            query = "UPDATE logindata SET names = ? WHERE feederno = ?"
                                            data = (qrName,selectedFeeder)
                                            cur.execute(query, data)
                                            conn.commit()
                                            initialize_feeder_info_window(my_w)
                                            status = compare_input_output_status(selectedFeeder)
                                            if status:
                                                    custom_message_box("LOCK SUCCESS", f"The {selectedFeeder} has been successfully locked by {qrName}", "SpringGreen3")
                                                    updatelogdata(qrCPF, qrName, selectedFeeder, scannedqrCode, datetime.now(), None, 'No Error','N', datetime.now())
                                                    # Stop the camera feed
                                                    stop_camera()
                                            else:
                                                custom_message_box("ERROR IN LOCKING MECHANISM. FEEDBACK FAILED", f"{selectedFeeder} has not been locked due to feedback failure at the site", "dark orange")
                                                # Revert the updated data in the logindata table
                                                query_revert = "UPDATE logindata SET names = ? WHERE feederno = ?"
                                                data_revert = ("", selectedFeeder)  # Assuming setting names to an empty string reverts the data
                                                cur.execute(query_revert, data_revert)
                                                conn.commit()
                                                initialize_feeder_info_window(my_w)
                                                updatelogdata(qrCPF, qrName, selectedFeeder, scannedqrCode, None, None, 'Feedback Error','N', datetime.now())
                                                # Stop the camera feed
                                                stop_camera()
                                    else:
                                        query = "INSERT INTO logindata (feederno, names) VALUES (?, ?)"
                                        data = (selectedFeeder, qrName)
                                        cur.execute(query, data)
                                        conn.commit()
                                        initialize_feeder_info_window(my_w)
                                        status = compare_input_output_status(selectedFeeder)
                                        if status:
                                            custom_message_box("LOCK SUCCESS", f"The {selectedFeeder} has been successfully locked by {qrName}", "SpringGreen3")
                                            # Stop the camera feed
                                            updatelogdata(qrCPF, qrName, selectedFeeder, scannedqrCode, datetime.now(), None, 'No Error','N')
                                            stop_camera()
                                        else:
                                            custom_message_box("ERROR IN LOCKING MECHANISM. FEEDBACK FAILED", f"{selectedFeeder} has not been locked due to feedback failure at the site", "dark orange")
                                            # Revert the updated data in the logindata table
                                            query_revert = "DELETE FROM logindata WHERE feederno = ?"
                                            data_revert = (selectedFeeder,)
                                            cur.execute(query_revert, data_revert)
                                            conn.commit()
                                            initialize_feeder_info_window(my_w)
                                            updatelogdata(qrCPF, qrName, selectedFeeder, scannedqrCode, None, None, 'Feedback Error','N', datetime.now())
                                            stop_camera()
                                else:
                                    custom_message_box("IN-CHARGE SELF LOG_IN OPERATION CANCELLED", "In-Charge Self log_In operation canceled", "red")
                                    updatelogdata(qrCPF, qrName, selectedFeeder, scannedqrCode, None, None, 'In-Charge Log In Cancelled','Y', datetime.now())
                                    stop_camera()

                            elif "OFF" in qr_data:
                                confirmation = custom_askyesno("IN-CHARGE SELF LOG_OUT OPERATION", "You have scanned for unlocking the feeder,\nClick Yes button if you are going to unlock the selected Feeder \nClick No button to cancel and exit","orange")    
                                if(confirmation):
                                    master_status = check_master_status(qrCPF)
                                    if result is not None:
                                        # User logged out, delete the corresponding name from the list
                                        if qrName in names and len(names)!=0:
                                            names.remove(qrName)
                                            updated_names = ",".join(names)
                                            query = "UPDATE logindata SET names = ? WHERE feederno = ?"
                                            cur.execute(query, (updated_names, selectedFeeder))
                                            conn.commit()
                                            initialize_feeder_info_window(my_w)
                                            status = compare_input_output_status(selectedFeeder)
                                            if status:
                                                custom_message_box("UNLOCK SUCCESS", f"{selectedFeeder} has been unlocked by {qrName} successfully", "SpringGreen3")
                                                updatelogdata(qrCPF, qrName, selectedFeeder, scannedqrCode, None, datetime.now(), 'No Error','N', datetime.now())
                                                stop_camera()
                                            else:
                                                custom_message_box("ERROR IN LOCKING MECHANISM. FEEDBACK FAILED", f"{selectedFeeder} has not been locked due to feedback failure at the site", "dark orange")
                                                names.append(qrName)
                                                updated_names = ",".join(names)
                                                query = "UPDATE logindata SET names = ? WHERE feederno = ?"
                                                cur.execute(query, (updated_names, selectedFeeder))
                                                conn.commit()
                                                initialize_feeder_info_window(my_w)
                                                updatelogdata(qrCPF, qrName, selectedFeeder, scannedqrCode, None, None, 'Feedback Error','N', datetime.now())
                                                stop_camera()

                                        elif master_status == "Y" and qrName not in names and len(names)!=0:
                                            # Master status is "Y", ask for confirmation before logging out all users
                                            confirmation = custom_askyesno("IN-CHARGE LOGOUT CONFIRMATION", f"{selectedFeeder} is not locked by you. Are you sure you want to log out other users using in-charge privileges?","red")
                                            if(confirmation):
                                                #logout_all_users(selectedFeeder)
                                                display_names_for_logout(selectedFeeder)
                                                #custom_message_box("MASTER LOGOUT", "All users logged out from the feeder", "red")
                                            else:
                                                # User canceled the operation
                                                custom_message_box("Operation Cancelled", "IN-CHARGE logout operation canceled", "blue")
                                                updatelogdata(qrCPF, qrName, selectedFeeder, scannedqrCode, None, None, 'In-Charge Log Out Cancelled','Y', datetime.now())
                                                stop_camera()

                                        elif qrName not in names and len(names)!=0:
                                            updatelogdata(qrCPF, qrName, selectedFeeder, scannedqrCode, None, None, 'Feeder Locked by Other User','N', datetime.now())
                                            custom_message_box("FEEDER NOT LOCKED BY YOU", f"You are trying to unlock the {selectedFeeder} which is not locked by you", "red")
                                        else:
                                            updatelogdata(qrCPF, qrName, selectedFeeder, scannedqrCode, None, None, 'Feeder Not Locked by anyone','N', datetime.now())
                                            custom_message_box("FEEDER NOT LOCKED BY ANY ONE", f"{selectedFeeder} is not locked by anyone. Close the Scanner", "pale turquoise")
                                            # Stop the camera feed
                                            stop_camera()
                                else:
                                    custom_message_box("IN-CHARGE SELF LOG_OUT OPERATION CANCELLED", "In-Charge Self log_Out operation canceled", "red")
                                    updatelogdata(qrCPF, qrName, selectedFeeder, scannedqrCode, None, None, 'In-Charge Log Out Cancelled','Y', datetime.now())
                                    stop_camera()

                    elif approval_shown == "True" and master_status == "Y" and fetchscannedQR()==qrCPF:
                        display_scan_prompt()

                    elif check_master_status(scannedqrCode)!="Y" and check_master_status(qrCPF) !="Y" :
                        custom_message_box("IN-CHARGE AUTHORIZATION REQUIRED", "\nFirst Incharge need to Scan his card to let you scan your QR code.\nClick OK Close the Scanner", "orange red")
                        # Stop the camera feed
                        updatelogdata(qrCPF, qrName, selectedFeeder, scannedqrCode,None, None, 'Needs Incharge Authorisation','N', datetime.now())
                        stop_camera()

                    elif ((check_master_status(scannedqrCode)=="Y" and check_master_status(qrCPF) !="Y") or (approval_shown == "True" and master_status == "Y" and fetchscannedQR()!=qrCPF)):
                            if "ON" in qr_data:
                                if result is not None:
                                    # User is already logged in
                                    if len(names)!=0 and qrName not in names:
                                        names.append(qrName)
                                        # Update the names in the logindata table
                                        updated_names = ",".join(names)
                                        query = "UPDATE logindata SET names = ? WHERE feederno = ?"
                                        cur.execute(query, (updated_names, selectedFeeder))
                                        conn.commit()
                                        initialize_feeder_info_window(my_w)
                                        status = compare_input_output_status(selectedFeeder)
                                        if status:
                                            custom_message_box("LOCK SUCCESS - MULTIPLE LOCKS FOUND", f" You have locked the feeder Successfully. {selectedFeeder} is now locked by multiple persons", "dark orange")
                                            # Stop the camera feed
                                            updatelogdata(qrCPF, qrName, selectedFeeder, scannedqrCode,datetime.now(), None, 'No Error','N',datetime.now())
                                            stop_camera()
                                        else:
                                            custom_message_box("ERROR IN LOCKING MECHANISM. FEEDBACK FAILED", f"{selectedFeeder} has not been locked due to feedback failure at the site", "dark orange")
                                            names.remove(qrName)
                                            # Update the names in the logindata table
                                            updated_names = ",".join(names)
                                            query = "UPDATE logindata SET names = ? WHERE feederno = ?"
                                            cur.execute(query, (updated_names, selectedFeeder))
                                            conn.commit()
                                            initialize_feeder_info_window(my_w)
                                            updatelogdata(qrCPF, qrName, selectedFeeder, scannedqrCode, None, None, 'Feedback Failed','N', datetime.now())
                                            stop_camera()
                                            
                                    elif len(names)!=0 and qrName in names: 
                                        custom_message_box("FEEDER ALREADY LOCKED", f"{selectedFeeder} is already locked by you", "pale turquoise")
                                        updatelogdata(qrCPF, qrName, selectedFeeder, scannedqrCode, None, None, 'Feeder already locked by user','N', datetime.now())
                                        # Stop the camera feed
                                        stop_camera()

                                    elif len(names) == 0:       
                                        # update data into the logindata table
                                        query = "UPDATE logindata SET names = ? WHERE feederno = ?"
                                        data = (qrName,selectedFeeder)
                                        cur.execute(query, data)
                                        conn.commit()
                                        initialize_feeder_info_window(my_w)
                                        status = compare_input_output_status(selectedFeeder)
                                        if status:
                                            custom_message_box("LOCK SUCCESS", f"The {selectedFeeder} has been successfully locked by {qrName}", "SpringGreen3")
                                            updatelogdata(qrCPF, qrName, selectedFeeder, scannedqrCode, datetime.now(), None, 'No Error','N', datetime.now())
                                            # Stop the camera feed
                                            stop_camera()
                                        else:
                                            custom_message_box("ERROR IN LOCKING MECHANISM. FEEDBACK FAILED", f"{selectedFeeder} has not been locked due to feedback failure at the site", "dark orange")
                                            # Revert the updated data in the logindata table
                                            query_revert = "UPDATE logindata SET names = ? WHERE feederno = ?"
                                            data_revert = ("", selectedFeeder)  # Assuming setting names to an empty string reverts the data
                                            cur.execute(query_revert, data_revert)
                                            conn.commit()
                                            initialize_feeder_info_window(my_w)
                                            updatelogdata(qrCPF, qrName, selectedFeeder, scannedqrCode, None, None, 'Feedback Failed','N', datetime.now())
                                            # Stop the camera feed
                                            stop_camera()
                                else:
                                    query = "INSERT INTO logindata (feederno, names) VALUES (?, ?)"
                                    data = (selectedFeeder, qrName)
                                    cur.execute(query, data)
                                    conn.commit()
                                    initialize_feeder_info_window(my_w)
                                    status = compare_input_output_status(selectedFeeder)
                                    if status:
                                        custom_message_box("LOCK SUCCESS", f"The {selectedFeeder} has been successfully locked by {qrName}", "SpringGreen3")
                                        updatelogdata(qrCPF, qrName, selectedFeeder, scannedqrCode, datetime.now(), None, 'No Error','N')
                                        # Stop the camera feed
                                        stop_camera()
                                    else:
                                        custom_message_box("ERROR IN LOCKING MECHANISM. FEEDBACK FAILED", f"{selectedFeeder} has not been locked due to feedback failure at the site", "dark orange")
                                        # Revert the updated data in the logindata table
                                        query_revert = "DELETE FROM logindata WHERE feederno = ?"
                                        data_revert = (selectedFeeder,)
                                        cur.execute(query_revert, data_revert)
                                        conn.commit()
                                        initialize_feeder_info_window(my_w)
                                        updatelogdata(qrCPF, qrName, selectedFeeder, scannedqrCode, None, None, 'Feedback Failed','N', datetime.now())
                                        # Stop the camera feed
                                        stop_camera()

                            elif "OFF" in qr_data:
                                master_status = check_master_status(qrCPF)
                                if result is not None:
                                    # User logged out, delete the corresponding name from the list
                                    if qrName in names and len(names)!=0:
                                        names.remove(qrName)
                                        updated_names = ",".join(names)
                                        query = "UPDATE logindata SET names = ? WHERE feederno = ?"
                                        cur.execute(query, (updated_names, selectedFeeder))
                                        conn.commit()
                                        initialize_feeder_info_window(my_w)
                                        status = compare_input_output_status(selectedFeeder)
                                        if status:
                                            custom_message_box("UNLOCK SUCCESS", f"{selectedFeeder} has been unlocked by {qrName} successfully", "SpringGreen3")
                                            updatelogdata(qrCPF, qrName, selectedFeeder, scannedqrCode, None, datetime.now(), 'No Error','N',datetime.now())
                                            stop_camera()
                                        else:
                                            custom_message_box("ERROR IN LOCKING MECHANISM. FEEDBACK FAILED", f"{selectedFeeder} has not been locked due to feedback failure at the site", "dark orange")
                                            names.append(qrName)
                                            updated_names = ",".join(names)
                                            query = "UPDATE logindata SET names = ? WHERE feederno = ?"
                                            cur.execute(query, (updated_names, selectedFeeder))
                                            conn.commit()
                                            initialize_feeder_info_window(my_w)
                                            updatelogdata(qrCPF, qrName, selectedFeeder, scannedqrCode, None, None, 'Feedback Failed','N', datetime.now())
                                            stop_camera()
                                    elif master_status == "Y" and qrName not in names and len(names)!=0:
                                        # Master status is "Y", ask for confirmation before logging out all users
                                        confirmation = custom_askyesno("IN-CHARGE LOGOUT CONFIRMATION", f"{selectedFeeder} is not locked by you. Are you sure you want to log out other users using master privileges?","red")
                                        if(confirmation):
                                            #logout_all_users(selectedFeeder)
                                            display_names_for_logout(selectedFeeder)
                                            stop_camera()
                                            #custom_message_box("MASTER LOGOUT", "All users logged out from the feeder", "red")
                                        else:
                                        # User canceled the operation
                                            custom_message_box("OPERATION CANCELLED", "In-Charge logout operation cancelled", "blue")
                                            stop_camera()
                                    elif qrName not in names and len(names)!=0:
                                        custom_message_box("FEEDER NOT LOCKED BY YOU", f"You are trying to unlock the {selectedFeeder} which is not locked by you", "red")
                                        updatelogdata(qrCPF, qrName, selectedFeeder, scannedqrCode, None, None, 'Feeder Not Locked by the user','N', datetime.now())
                                    else:
                                        custom_message_box("FEEDER NOT LOCKED BY ANY ONE", f"{selectedFeeder} is not locked by anyone. Close the Scanner", "pale turquoise")
                                        updatelogdata(qrCPF, qrName, selectedFeeder, scannedqrCode, None, None, 'Feeder Not Locked by anyone','N', datetime.now())
                                # Stop the camera feed
                                stop_camera() 

                else:
                    custom_message_box("USER NOT FOUND IN DATABASE", "User does not exist in database. Close the Scanner", "orange red")
                    updatelogdata(qrCPF, name, selectedFeeder, fetchscannedQR(), None, None, 'User does not exist in database','N', datetime.now())
                    # Stop the camera feed
                    stop_camera()
            else:
                custom_message_box("INVALID QR CODE DETECTED", "Invalid QR Code Scanned. Close the Scanner", "orange red")
                updatelogdata(None, None, selectedFeeder, None, None, None, 'Invalid QR Code','N', datetime.now())
                # Stop the camera feed
                stop_camera()

        # Convert the OpenCV frame to a Tkinter-compatible image
        img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(img)
        imgtk = ImageTk.PhotoImage(image=img)

        # Update the label with the new image
        label.imgtk = imgtk
        label.configure(image=imgtk)
        approval_shown = fetchapproval()
        if camera_running and (approval_shown == "False" or check_master_status(fetchscannedQR())=="Y"):
            # Call this function again after a delay to capture frames continuously
            label.after(10, detect_and_display_qr_codes)
        else:
            stop_camera()

    def start_camera():
        global camera_running
        if not camera_running:
            camera_running = True
            submitbutton.config(state="disabled")  # Disable the button when the camera starts
            detect_and_display_qr_codes()
             # Start a timer to close the camera feed window after 30 seconds
            #label.after(10000, stop_camera)  # 30,000 milliseconds (30 seconds)

    def stop_camera():
        global camera_running, cap
        if camera_running:
            camera_running = False
            resetqr()
            resetapproval("False")
            cap.release()
            label.imgtk = None
            label.configure(image=None)
            sel.set("Select the Feeder") # Set the combo box value back to default
            submitbutton.config(state="disabled")
            cb1.focus_set()
            for w in my_w.grid_slaves(row=5):  # all elements in row 5
             w.grid_remove()  # delete elements

    # Start the camera when the frame is shown
    start_camera()
# Function to handle key events
def handle_key_event(event):
    if event.keysym == 'Escape':  # Check if the "Escape" key is pressed
        stop_camera()  # Stop the camera feed
        sel.set("Select the Feeder") # Set the combo box value back to default
        submitbutton.config(state="disabled")
        for w in my_w.grid_slaves(row=5):  # all elements in row 5
            w.grid_remove()  # delete elements

# Function to handle the "SUBMIT" button click
def submit(selectedFeeder):
    label = tk.Label(my_w, width=600, height=400)
    label.grid(row=5, column=0, columnspan=2)
    show_frames(label, selectedFeeder)  # Pass the label to the show_frames function
    # Set the combo box back to the default value

# Create the submit button with an initial state of "disabled"
submitbutton = ttk.Button(my_w, width=10, text='SUBMIT', state="disabled")
submitbutton.grid(row=4, column=0, padx=20, pady=10, columnspan=2)
my_w.bind("<Return>", lambda event=None: submitbutton.invoke())
    
initialize_feeder_info_window(my_w)

my_w.bind('<Key>', handle_key_event)

my_w.mainloop()