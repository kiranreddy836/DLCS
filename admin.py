import tkinter as tk
import sqlite3
import cv2
from pyzbar.pyzbar import decode

def start_camera_for_update():
    cap = cv2.VideoCapture(0)
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        # Convert the frame to grayscale for QR code detection
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        # Detect QR codes
        decoded_objects = decode(frame)
        for obj in decoded_objects:
            qr_data = obj.data.decode('utf-8')
            name, cpf, status = qr_data.split('_')
            if check_master_status(cpf) == 'Y':
                update_user()
            else:
                print("Master status is not 'ON'. Update not allowed.")
                
        if cv2.waitKey(1) :
            break
    cap.release()
    cv2.destroyAllWindows()

# Function to check master status from the users table
def check_master_status(qrCPF):
    query = "SELECT master FROM users WHERE cpf_no = ?"
    cur.execute(query, (qrCPF,))
    result = cur.fetchone()
    if result:
        return result[0]
    else:
        return None

def open_camera_for_update():
    camera_window = tk.Toplevel(root)
    camera_window.title('Camera Interface')
    start_camera_for_update()


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
        status_label_add.config(text="User added successfully!",fg="green")

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

# Create the database and connection
conn = sqlite3.connect('user_database.db')
cur = conn.cursor()

# GUI setup
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
