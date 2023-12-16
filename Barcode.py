import cups
from datetime import datetime

def print(qr):
    # Initialize a connection to the CUPS server
    conn = cups.Connection()

    # Get a list of available printers
    printers = conn.getPrinters()

    # printer's name
    printer_name = 'DLCS'

    # Check if the chosen printer is available
    if printer_name in printers:
        # Prepare the data to be printed
        data_to_print = f"qrCPF: {qrCPF}, qrName: {qrName}, selectedFeeder: {selectedFeeder}, scannedqrCode: {scannedqrCode}, datetime: {datetime.now()}"

        # Send data to the printer
        conn.printFile(printer_name, "-", {"cpi": "12", "lpi": "6"}, data_to_print)
        print("Printing successful.")
    else:
        print("Printer not found.")
