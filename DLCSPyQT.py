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
                    if check_master_status(qrCPF)=="Y":
                        updateqr(qrCPF)
                    scannedqrCode = fetchscannedQR()
                    print("=====================qrCPF==================================:", qrCPF)
                    print("=====================last_scanned_cpf=======================:",scannedqrCode)
                    qrName = "_".join([name,qrCPF])
                    if result is not None:
                        names = result[0].split(",") if result[0] else []
                    else:
                        print("No matching record found.")
                    # Validate if its master
                    master_status = check_master_status(qrCPF)
                    approval_shown =fetchapproval()

                    if not approval_shown and master_status == "Y":
                        confirmation = custom_askyesnoforapproval("MASTER OPERATION DETECTED", "Select appropriate action. Select Approve other users button if you are allowing other users to scan their card","red")
                        if(confirmation):
                            print("confirmed")
                            custom_message_box("AUTHORIZATION SUCCESS", "User can Scan his Card now, cLICK OK to scan the card", "dark orange")
                            # Set the flag to True after showing the window
                            updateapproval(True)
                        else:
                            print("scanned")
    
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
