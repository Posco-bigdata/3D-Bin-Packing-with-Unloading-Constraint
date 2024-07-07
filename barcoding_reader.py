import json

def load_json_file(filename):
    with open(filename, 'r') as file:
        data = json.load(file)
    return data

def get_barcode_input():
    barcode_input = []
    print("Enter the barcode info (type 'done' to finish):")
    while True:
        user_input = input("Enter barcode ID (1-88): ")
        if user_input.lower() == 'done':
            break
        try:
            barcode_id = int(user_input)
            if barcode_id < 1 or barcode_id > 88:
                print("ID must be between 1 and 88.")
                continue
            barcode_input.append(str(barcode_id))
        except ValueError:
            print("Please enter a valid number.")
    return barcode_input

def map_barcodes_to_info(barcode_input, json_data):
    mapped_info = {}
    for barcode_id in barcode_input:
        if barcode_id in json_data:
            mapped_info[barcode_id] = json_data[barcode_id]
    return mapped_info

def save_json_file(filename, data):
    with open(filename, 'w') as file:
        json.dump(data, file, indent=4)

def main():
    json_filename = './generated_boxes.json'
    output_filename = './mapped_barcodes.json'

    # Load the existing JSON file
    json_data = load_json_file(json_filename)

    # Get barcode input from the keyboard
    barcode_input = get_barcode_input()

    # Map the barcodes to the corresponding info
    mapped_info = map_barcodes_to_info(barcode_input, json_data)

    # Save the mapped information to a new JSON file
    save_json_file(output_filename, mapped_info)
    print(f"Mapped information saved to {output_filename}")

if __name__ == "__main__":
    main()
