import qrcode
from PIL import Image, ImageDraw, ImageFont
import os

# Create a folder to save the stickers
OUTPUT_FOLDER = "generated_stickers"
if not os.path.exists(OUTPUT_FOLDER):
    os.makedirs(OUTPUT_FOLDER)

def generate_sticker(plate_number):
    # 1. Generate the QR Code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H, # High error correction (good for stickers that might get scratched)
        box_size=10,
        border=4,
    )
    qr.add_data(plate_number)
    qr.make(fit=True)

    qr_img = qr.make_image(fill_color="black", back_color="white").convert('RGB')

    # 2. Create a Canvas (QR Code + Space for Text)
    # We add 60 pixels at the bottom for the text
    canvas_width = qr_img.width
    canvas_height = qr_img.height + 60 
    
    final_image = Image.new('RGB', (canvas_width, canvas_height), 'white')
    
    # Paste the QR code onto the canvas
    final_image.paste(qr_img, (0, 0))

    # 3. Draw the Plate Number Text
    draw = ImageDraw.Draw(final_image)
    
    # Load a font (Using default if custom font not found)
    try:
        # Try to use a nice bold font if available on your system (adjust path as needed)
        font = ImageFont.truetype("arial.ttf", 30)
    except IOError:
        font = ImageFont.load_default()

    # Calculate text size to center it
    # Note: textbbox is the modern replacement for textsize in newer Pillow versions
    bbox = draw.textbbox((0, 0), plate_number, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    x_position = (canvas_width - text_width) / 2
    y_position = qr_img.height + 10 # 10px padding below QR

    draw.text((x_position, y_position), plate_number, fill="black", font=font)

    # 4. Save the file
    filename = f"{OUTPUT_FOLDER}/{plate_number}.png"
    final_image.save(filename)
    print(f"✅ Generated Sticker: {filename}")

# --- RUN THE SCRIPT ---
if __name__ == "__main__":
    # List of plates to generate
    plates_to_print = [
        "AD-1234",
        "AD-555-YL",
        "AD-999-AB"
    ]

    print("🖨️  Generating Keke Stickers...")
    for plate in plates_to_print:
        generate_sticker(plate)
    print("Done! Check the 'generated_stickers' folder.")