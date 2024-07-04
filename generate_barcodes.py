import json
import os
import barcode
from barcode.codex import Code128
from barcode.writer import ImageWriter

# Load items from JSON file
with open('./generated_boxes.json', 'r') as f:
    items = json.load(f)

# Create a directory for barcodes if it doesn't exist
barcode_dir = 'barcodes'
os.makedirs(barcode_dir, exist_ok=True)

# Generate barcodes for each item ID
for item_id in items.keys():
    # Convert item_id to string (required by the barcode library)
    item_id_str = str(item_id)
    
    # Generate the barcode
    barcode = Code128(item_id_str, writer=ImageWriter())
    
    # Save the barcode as a PNG image
    barcode_path = os.path.join(barcode_dir, f'{item_id_str}.png')
    barcode.save(barcode_path)

print(f"Barcodes generated and saved in the '{barcode_dir}' directory.")
