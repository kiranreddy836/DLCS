from revpimodio2 import *
from revpimodio import *

# Create RevPiModIO2 object
pi = RevPiModIO(autorefresh=True)

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
    pin = feeder_output_pins.get(feeder_number)
    pi.write_value(pin, lock_status)
    pi.refresh()
    print(f"Feeder-{feeder_number} lock status set to {lock_status}")

# Function to get input status of a feeder
def get_feeder_input_status(feeder_number):
    pin = feeder_input_pins.get(feeder_number)
    input_status = pi.read_value(pin)
    print(f"Status of Feeder-{feeder_number} input: {input_status}")
    return input_status

# Function to get output status of a feeder
def get_feeder_output_status(feeder_number):
    pin = feeder_output_pins.get(feeder_number)
    output_status = pi.read_value(pin)
    print(f"Status of Feeder-{feeder_number} output: {output_status}")
    return output_status

# Function to compare input and output status for a feeder
def compare_input_output_status(feeder_number):
    input_status = get_feeder_input_status(feeder_number)
    output_status = get_feeder_output_status(feeder_number)
    
    match_status = input_status == output_status
    print(f"Feeder-{feeder_number} input status: {input_status}")
    print(f"Feeder-{feeder_number} output status: {output_status}")
    return match_status

set_feeder_output_status('Feeder-1', True)

get_feeder_input_status('Feeder-1')
get_feeder_output_status('Feeder-1')
