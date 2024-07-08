import json
import os
import barcode
from barcode.codex import Code128
from barcode.writer import ImageWriter
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO

def generate_barcodes(scenario_number, items):
    # Create a directory for barcodes if it doesn't exist
    barcode_dir = f'./barcodes_scenario_{scenario_number}'
    os.makedirs(barcode_dir, exist_ok=True)

    # Generate barcodes for each item ID
    for item_id, item_data in items.items():
        item_id_str = str(item_id)
        location = item_data['location']
        
        # Generate the barcode
        barcode_img = Code128(item_id_str, writer=ImageWriter())
        
        # Save the barcode to a BytesIO object
        img_buffer = BytesIO()
        barcode_img.write(img_buffer)
        
        # Open the image from the BytesIO object
        img = Image.open(img_buffer)
        
        # Create a new image with extra space for text
        new_img = Image.new('RGB', (img.width, img.height + 30), color='white')
        new_img.paste(img, (0, 0))
        
        # Add text to the image
        draw = ImageDraw.Draw(new_img)
        font = ImageFont.load_default()
        draw.text((10, img.height + 5), f"ID: {item_id_str}, Location: {location}", fill='black', font=font)
        
        # Save the new image
        barcode_path = os.path.join(barcode_dir, f'{item_id_str}.png')
        new_img.save(barcode_path)

    print(f"바코드가 생성되어 '{barcode_dir}' 디렉토리에 저장되었습니다.")