import json
import os
import barcode
from barcode.codex import Code128
from barcode.writer import ImageWriter
from main_data import create_scenario

def generate_barcodes(scenario_number):
    # Load items from JSON file
    filename = f'./main_box_scenario_{scenario_number}.json'
    with open(filename, 'r') as f:
        items = json.load(f)

    # Create a directory for barcodes if it doesn't exist
    barcode_dir = f'./barcodes_scenario_{scenario_number}'
    os.makedirs(barcode_dir, exist_ok=True)

    # Generate barcodes for each item ID
    for item_id, item_data in items.items():
        # Convert item_id to string (required by the barcode library)
        item_id_str = str(item_id)
        
        # Generate the barcode
        barcode_img = Code128(item_id_str, writer=ImageWriter())
        
        # Save the barcode as a PNG image
        barcode_path = os.path.join(barcode_dir, f'{item_id_str}.png')
        barcode_img.save(barcode_path)

    print(f"바코드가 생성되어 '{barcode_dir}' 디렉토리에 저장되었습니다.")

# Generate barcodes for the items in the scenario
def main():
    scenario_number = int(input("Enter the scenario number: "))
    generate_barcodes(scenario_number)

if __name__ == "__main__":
    main()
