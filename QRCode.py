import qrcode
from PIL import Image, ImageDraw, ImageFont

def generate_id_card(data, name, designation, phone_number):
    # Check if the sample string contains 'IN' or 'OFF' to determine QR code color
    if 'IN' in data:
        qr_color = 'red'
    elif 'OFF' in data:
        qr_color = 'green'
    else:
        qr_color = 'black'  # Default color

    # Generate QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=8,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color=qr_color, back_color="white")

    # Create a blank canvas for ID card
    card_width = 550
    card_height = 300
    id_card = Image.new('RGB', (card_width, card_height), 'white')

    # Add header with logo and text
    header = Image.open('nlclogo.png')  # Replace with your logo image path
    header = header.resize((50, 90))  # Resize logo image as needed
    id_card.paste(header, (10, 10))

    draw = ImageDraw.Draw(id_card)
    font = ImageFont.load_default()

    # Increase font size for name, designation, and phone number
    larger_font = ImageFont.truetype("arial.ttf", 18)

    # Add heading text to the right side of the header
    draw.text((220, 10), "NLC INDIA LIMITED", fill='black', font=larger_font)

    # Add QR code to the ID card on the left side below the header
    id_card.paste(qr_img, (2, 50))

    # Add name, designation, and phone number text on the right side
    draw.text((260, 90), f"{name}", fill='black', font=larger_font)
    draw.text((260, 120), f"{designation}", fill='black', font=larger_font)
    draw.text((260, 150), f"{phone_number}", fill='black', font=larger_font)

    id_card.show()  # Display the ID card
    id_card.save("id_card.png")  # Save the ID card
    
# Sample data
sample_string_1 = "kiran_48979_IN"  # Contains 'IN'
sample_string_2 = "kiran_48979_OFF"    # Contains 'OFF'
sample_name = "Kiran Kumar Reddy"
sample_designation = "Deputy Executive Engineer"
sample_phone_number = "8790268112"

generate_id_card(sample_string_1, sample_name, sample_designation, sample_phone_number)
generate_id_card(sample_string_2, sample_name, sample_designation, sample_phone_number)
