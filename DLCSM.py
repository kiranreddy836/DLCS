
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

    # Title
    title_label = ttk.Label(header_frame, text="DIGITALIZED LINE CLEARANCE SYSTEM", font=("Times New Roman", 25, 'bold'), background="RoyalBlue4",foreground="white")
    title_label.place(relx=0.5, rely=0.4, anchor="center")

    # label text for unit selection
    unit_label = ttk.Label(header_frame, text="MINE-1A SUBSTATION",
                       background='RoyalBlue4', foreground="white",
                       font=("Times New Roman", 17, 'bold'))
    unit_label.place(relx=0.5, rely=0.8, anchor="center")
    # Admin Button
    admin_button = tk.Button(header_frame, text="Admin", command=open_admin_window, bg="white", fg="black")
    admin_button.grid(row=0, column=2, padx=10)  # Adjust column and padding as needed


# Establish SQLITE Database Connection (If using SQLite3 -- Comment other connection modes if using SQLite)
current_directory = os.getcwd()
db_file = os.path.join(current_directory, "ilcst.db")
conn = sqlite3.connect(db_file)
cur = conn.cursor()


# Function to stop the camera feed
def stop_camera():
    global camera_running, cap
    if camera_running:
        camera_running = False
        resetqr()
        resetapproval("False")
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
name_selection_window = None  # Initialize name_selection_window

# Function to release the lock file when the application is closed
d
    # Create label for Feeders Info Frame
    label = tk.Label(feeder_info_frame, text="STATUS OF THE FEEDERS", font=("Times New Roman", 15, "bold"), background="yellow",foreground="red4")
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
    print(max_locked_by_width)
    # Set the "Locked By" column width with some padding
    tree.column("FEEDER NO : ", width=100)
    tree.column("LINE CLEARANCE STATUS", width=max_locked_by_width * 2)  # Adjust the multiplier as needed multiplier as needed
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

def display_scan_prompt():
        global prompt_window
        prompt_window = messagebox.showinfo("Incharge Authorization Success", "User can scan his card now. \nCamera will be closed automatically in a minute if no input is received.\nPlease click Okay to allow user to scan")
        # Function to destroy the scan prompt window
        label.after(1000, destroy_scan_prompt)
        
def destroy_scan_prompt():
        prompt_window.destroy()

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
                        confirmation = custom_askyesnoforapproval("MASTER OPERATION DETECTED", "Select Approve other users button if you are allowing other users to scan \nSelect Operate to lock or unlock the selected feeder","blue")
                        if(confirmation):
                            updateapproval("True")
                        else:
                        
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