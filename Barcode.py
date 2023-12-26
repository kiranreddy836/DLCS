import cups

def print_text(printer_name, text):
    try:
        conn = cups.Connection()
        printers = conn.getPrinters()

        if printer_name not in printers:
            raise ValueError(f"Printer '{printer_name}' not found.")

        # Create a temporary file with the text
        temp_file_path = "/tmp/print_temp.txt"
        with open(temp_file_path, 'w') as temp_file:
            temp_file.write(text)

        # Print the temporary file
        conn.printFile(printer_name, temp_file_path, "Print Job", {})

        print("Text sent to the printer successfully.")
    except cups.IPPError as e:
        print(f"IPPError: {e}")
    except ValueError as ve:
        print(f"ValueError: {ve}")

# Usage
printer_name = "HP-LaserJet-M1005"  
text_to_print = "Hello, this is a test text for printing."

print_text(printer_name, text_to_print)
