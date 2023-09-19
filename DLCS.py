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

# Check if the lock file exists
lock_file = "app_lock.lock"
if os.path.isfile(lock_file):
    messagebox.showerror("Error", "Another instance of the application is already running.")
    exit()
# Create the lock file
open(lock_file, 'w').close()

# Establish SQLITE Database Connection (If using SQLite3 -- Comment other connection modes if using SQLite)
db_file = r"C:\DLCS\ilcst.db"
conn = sqlite3.connect(db_file)
cur = conn.cursor()

# Function to stop the camera feed
def stop_camera():
    global camera_running, cap
    if camera_running:
        camera_running = False
        cap.release()

# Function to enable or disable the "Select Feeder" combo box
def set_combo_box_state(state):
    cb1["state"] = state  # Set the state of the combo box

# Function to re-enable the "Select Feeder" combo box when the name selection window is closed
def on_name_selection_window_close(name_selection_window):
    global combo_box_state  # Use the global variable
    set_combo_box_state(combo_box_state)  # Restore the previous state
    name_selection_window.destroy()  # Close the name selection window

# Create a global variable to keep track of the name selection window state
name_selection_window_open = False
name_selection_window = None  # Initialize name_selection_window

# Function to release the lock file when the application is closed
def on_main_window_close():
    # Delete the lock file
    if os.path.isfile(lock_file):
        os.remove(lock_file)
    my_w.destroy()

# Create a function to display names for logout in a new window (as a modal dialog)
def display_names_for_logout(selectedFeeder):
    global combo_box_state, name_selection_window_open, name_selection_window  # Use the global variables

    # Check if the name selection window is already open
    if name_selection_window_open:
        custom_message_box("Window Open", "The name selection window is already open.", "info")
        return

    # Set the state to indicate that the window is open
    name_selection_window_open = True

    # Disable the "Contact Details" button
    show_contact_button.config(state="disabled")
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
    name_selection_window.attributes("-toolwindow", 1)

    def on_window_close():
        # Callback function to run when the name selection window is closed
        # Reset the state to indicate that the window is closed
        global name_selection_window_open, name_selection_window  # Use the global variables
        name_selection_window_open = False
        # Re-enable the "Contact Details" button
        show_contact_button.config(state="normal")
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
                custom_message_box("User Logout", f"{name_to_logout} has been logged out from {selectedFeeder}.", "green")
                name_selection_window.destroy()
                cb1.config(state="normal")
                show_contact_button.config(state="normal")
        def close_select_logout_window():
            name_selection_window.destroy()
            cb1.config(state="normal")
            show_contact_button.config(state="normal")

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


def logout_user(feeder_no, user_to_logout):
        query = "SELECT names FROM logindata WHERE feederno = ?"
        cur.execute(query, (feeder_no,))
        result = cur.fetchone()

        if result:
            names = result[0].split(',') if result[0] else []
            if user_to_logout in names:
                names.remove(user_to_logout)
                updated_names = ",".join(names)
                query = "UPDATE logindata SET names = ? WHERE feederno = ?"
                cur.execute(query, (updated_names, feeder_no))
                conn.commit()
                initialize_feeder_info_window(my_w)
                custom_message_box("User Logout", f"{user_to_logout} has been logged out from {feeder_no}.", "green")
            else:
                custom_message_box("User Not Found", f"{user_to_logout} is not logged into {feeder_no}.", "orange red")
        else:
            custom_message_box("Feeder Not Found", f"Feeder {feeder_no} not found.", "red")

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

    yes_button = ttk.Button(dialog, text="Yes", command=on_yes)
    yes_button.pack(side="left", padx=10)

    no_button = ttk.Button(dialog, text="No", command=on_no)
    no_button.pack(side="right", padx=10)

    yes_button.focus_set()

    # Bind the Enter key to trigger the "Yes" and "No" button's action

    dialog.bind("<Return>", lambda event: dialog.focus_get().invoke())
    dialog.grab_set()  # Make the dialog modal
    dialog.wait_window()  # Wait for the dialog to be closed

    return result

# Function to initialize the feeder info window
def initialize_feeder_info_window(parent):
    feeder_info_frame = tk.Frame(parent, background="snow2")
    feeder_info_frame.place(relx=0.64, rely=0.08, relwidth=0.35, relheight=0.28)

    # Create label for Feeders Info Frame
    label = tk.Label(feeder_info_frame, text="STATUS OF THE FEEDERS", font=("Arial", 14, "bold"), background="snow2",foreground="blue")
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

    """# Set the GPIO mode to BCM
    GPIO.setmode(GPIO.BCM)

    # Set designated GPIO pins as an output (replace pin numbers with appropriate numbers for SBC)
    GPIO.setup(pin1, GPIO.OUT)
    GPIO.setup(pin2, GPIO.OUT)
    GPIO.setup(pin3, GPIO.OUT)
    GPIO.setup(pin4, GPIO.OUT)
    GPIO.setup(pin5, GPIO.OUT)
    GPIO.setup(pin6, GPIO.OUT)
    GPIO.setup(pin7, GPIO.OUT)
    GPIO.setup(pin8, GPIO.OUT)

    var1 = 0
    var2 = 0
    var3 = 0
    var4 = 0
    var5 = 0
    var6 = 0
    var7 = 0
    var8 = 0
 """

    for row in rows:
        # Use feeder Number and Status to activate the SBC pins based on user interaction with the GUI
        feeder_no = row[0]
        locked_names = row[1]

        """GPIO.output(pin1, GPIO.HIGH if feeder_no == "Feeder-1" and len(locked_names) != 0 else GPIO.LOW)
        GPIO.output(pin2, GPIO.HIGH if feeder_no == "Feeder-2" and len(locked_names) != 0 else GPIO.LOW)
        GPIO.output(pin3, GPIO.HIGH if feeder_no == "Feeder-3" and len(locked_names) != 0 else GPIO.LOW)
        GPIO.output(pin4, GPIO.HIGH if feeder_no == "Feeder-4" and len(locked_names) != 0 else GPIO.LOW)
        GPIO.output(pin5, GPIO.HIGH if feeder_no == "Feeder-5" and len(locked_names) != 0 else GPIO.LOW)
        GPIO.output(pin6, GPIO.HIGH if feeder_no == "Feeder-6" and len(locked_names) != 0 else GPIO.LOW)
        GPIO.output(pin7, GPIO.HIGH if feeder_no == "Feeder-7" and len(locked_names) != 0 else GPIO.LOW)
        GPIO.output(pin8, GPIO.HIGH if feeder_no == "Feeder-8" and len(locked_names) != 0 else GPIO.LOW)

        var1 = 0 if feeder_no == "Feeder-1" and len(locked_names) != 0 else 1
        var2 = 0 if feeder_no == "Feeder-2" and len(locked_names) != 0 else 1
        var3 = 0 if feeder_no == "Feeder-3" and len(locked_names) != 0 else 1
        var4 = 0 if feeder_no == "Feeder-4" and len(locked_names) != 0 else 1
        var5 = 0 if feeder_no == "Feeder-5" and len(locked_names) != 0 else 1
        var6 = 0 if feeder_no == "Feeder-6" and len(locked_names) != 0 else 1
        var7 = 0 if feeder_no == "Feeder-7" and len(locked_names) != 0 else 1
        var8 = 0 if feeder_no == "Feeder-8" and len(locked_names) != 0 else 1

        if var1==0:
            print("pin-1 status set low")
        if var2==0:
            print("pin-2 status set low")
        if var3==0:
            print("pin-3 status set low")
        if var4==0:
            print("pin-4 status set low")
        if var5==0:
            print("pin-5 status set low")
        if var6==0:
            print("pin-6 status set low")
        if var7==0:
            print("pin-7 status set low")
        if var8==0:
            print("pin-8 status set low") """

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
    print(max_locked_by_width)
    # Set the "Locked By" column width with some padding
    tree.column("FEEDER NO : ", width=100)
    tree.column("LINE CLEARANCE STATUS", width=max_locked_by_width * 2)  # Adjust the multiplier as needed multiplier as needed
    tree.pack()

def show_contact_details():
    contact_details_window = tk.Toplevel(my_w)
    contact_details_window.title("Contact Details")
        # Disable both minimize and maximize options
    contact_details_window.attributes("-toolwindow", 1)

    # Create a Treeview widget to display the contact details
    contact_tree = ttk.Treeview(contact_details_window, columns=("Name","Cpf Number","Phone Number") , show="headings")
    contact_tree.heading("Name", text="Name", anchor=tk.W)
    contact_tree.heading("Cpf Number", text="Cpf Number",anchor=tk.W)
    contact_tree.heading("Phone Number", text="Phone Number",anchor=tk.W)
    contact_tree.pack()

    # Fetch and display contact details from the 'users' table
    query = "SELECT name,cpf_no,phone_no FROM users"
    cur.execute(query)
    rows = cur.fetchall()

    for row in rows:
        name, cpf_no, phone_number = row
        contact_tree.insert("", "end", values=(name, cpf_no, phone_number))

    # Close button
    close_button = ttk.Button(contact_details_window, text="Close", command=contact_details_window.destroy)
    close_button.pack()

    # Set focus on the Close button
    close_button.focus_set()

    # Bind the Enter key event to the close button
    contact_details_window.bind('<Return>', lambda event=None: close_button.invoke())


# Build the Tkinter window
my_w = tk.Tk()
my_w.configure(bg="azure3")
my_w.resizable(False, False)
# Remove the default title bar
# Disable both minimize and maximize options
#my_w.attributes("-toolwindow", 1)


# Create a "Show Contact Details" button
show_contact_button = ttk.Button(my_w, text="Contacts Directory", command=show_contact_details)
show_contact_button.place(x=10, y=10)  # Adjust the coordinates as needed

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

my_w.protocol("WM_DELETE_WINDOW", on_main_window_close)

# Reduce the vertical spacing between rows
row_padding = (5, 0)

# Configure grid weights for responsive layout
my_w.columnconfigure(0, weight=1)
my_w.rowconfigure(0, weight=0)  # Reduce weight for title row
my_w.rowconfigure(1, weight=0)  # Reduce weight for unit row
my_w.rowconfigure(2, weight=0)  # Reduce weight for feeder label row
my_w.rowconfigure(3, weight=0)  # Reduce weight for combo box row
my_w.rowconfigure(4, weight=0)  # Reduce weight for submit button row
my_w.rowconfigure(5, weight=0)  # Reduce weight for frames row

# label text for title
title_label = ttk.Label(my_w, text="DIGITALIZED LINE CLEARANCE SYSTEM",
                        background='azure3', foreground="midnight blue", anchor="center",
                        font=("Times New Roman", 25, 'bold'))
title_label.grid(row=0, column=0, padx=20, pady=row_padding, columnspan=2)

# label text for unit selection
unit_label = ttk.Label(my_w, text="MINE-1A SUBSTATION",
                       background='azure3', foreground="midnight blue",
                       font=("Times New Roman", 20, 'bold'))
unit_label.grid(row=1, column=0, padx=20, pady=20, columnspan=2)

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
feeder_label.grid(row=2, column=0, padx=20, pady=10, columnspan=2)

cb1 = ttk.Combobox(my_w, values=displayfeeders, width=20, textvariable=sel,state="readonly")
cb1.grid(row=3, column=0, padx=10, pady=20, columnspan=2)

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

def show_frames(label, selectedFeeder):
    global camera_running, cap
    cap = cv2.VideoCapture(0)

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
            points = obj.polygon
            if len(points) >= 4:
                # Draw a border around the QR code
                cv2.polylines(frame, [np.array(points)], True, (0, 255, 0), 2)

                # Display QR code data
                cv2.putText(frame, qr_data, (points[0][0], points[0][1] - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

                # Check if qr_data exists in the logindata table
                query = "SELECT names FROM logindata WHERE feederno = ?"
                cur.execute(query, (selectedFeeder,))
                result = cur.fetchone()
                print(result)

                # Split QR Code data
                print(qr_data)
                partsqr = qr_data.split("_")
                if len(partsqr) == 3:
                    name, qrCPF, qrMode = partsqr
                    print("String 2 Decoded:", qrCPF)
                    qrName = "_".join([name,qrCPF])
                    if result is not None:
                        names = result[0].split(",") if result[0] else []
                    else:
                        print("No matching record found.")
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
                                custom_message_box("LOCK SUCCESS - MULTIPLE LOCKS FOUND", f" You have locked the feeder Successfully. {selectedFeeder} is now locked by multiple persons", "dark orange")
                                # Stop the camera feed
                                stop_camera()

                            elif len(names)!=0 and qrName in names: 
                                custom_message_box("FEEDER ALREADY LOCKED", f"{selectedFeeder} is already locked by you", "pale turquoise")
                                # Stop the camera feed
                                stop_camera()

                            elif len(names) == 0:       
                                # update data into the logindata table
                                query = "UPDATE logindata SET names = ? WHERE feederno = ?"
                                data = (qrName,selectedFeeder)
                                cur.execute(query, data)
                                conn.commit()
                                initialize_feeder_info_window(my_w)
                                custom_message_box("LOCK SUCCESS", f"The {selectedFeeder} has been successfully locked by {qrName}", "SpringGreen3")
                                # Stop the camera feed
                                stop_camera()

                        else:
                            query = "INSERT INTO logindata (feederno, names) VALUES (?, ?)"
                            data = (selectedFeeder, qrName)
                            cur.execute(query, data)
                            conn.commit()
                            initialize_feeder_info_window(my_w)
                            custom_message_box("LOCK SUCCESS", f"The {selectedFeeder} has been successfully locked by {qrName}", "SpringGreen3")
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
                                custom_message_box("UNLOCK SUCCESS", f"{selectedFeeder} has been unlocked by {qrName} successfully", "SpringGreen3")
                            elif master_status == "Y" and qrName not in names and len(names)!=0:
                                # Master status is "Y", ask for confirmation before logging out all users
                                confirmation = custom_askyesno("MASTER LOGOUT CONFIRMATION", f"{selectedFeeder} is not locked by you. Are you sure you want to log out other users using master privileges?","red")
                                if(confirmation):
                                     #logout_all_users(selectedFeeder)
                                     display_names_for_logout(selectedFeeder)
                                     #custom_message_box("MASTER LOGOUT", "All users logged out from the feeder", "red")
                                else:
                                # User canceled the operation
                                 custom_message_box("Operation Cancelled", "Master logout operation canceled", "blue")
                            elif qrName not in names and len(names)!=0:
                                custom_message_box("FEEDER NOT LOCKED BY YOU", f"You are trying to unlock the {selectedFeeder} which is not locked by you", "red")
                            else:
                                custom_message_box("FEEDER NOT LOCKED BY ANY ONE", f"{selectedFeeder} is not locked by anyone. Close the Scanner", "pale turquoise")
                        # Stop the camera feed
                        stop_camera()
                else:
                    custom_message_box("UNAUTHORISED QR CODE DETECTED", "Unauthorised access detected. Close the Scanner", "orange red")
                    # Stop the camera feed
                    stop_camera()

        # Convert the OpenCV frame to a Tkinter-compatible image
        img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(img)
        imgtk = ImageTk.PhotoImage(image=img)

        # Update the label with the new image
        label.imgtk = imgtk
        label.configure(image=imgtk)

        if camera_running:
            # Call this function again after a delay to capture frames continuously
            label.after(20, detect_and_display_qr_codes)

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
# Bind the key event handler to the main window
my_w.bind('<Key>', handle_key_event)

my_w.mainloop()