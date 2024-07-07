import json
import time
from pynput import keyboard

def on_press(key):
    global barcode_input, last_input_time
    try:
        barcode_input += key.char
        last_input_time = time.time()
    except AttributeError:
        pass

def on_release(key):
    if key == keyboard.Key.enter:
        return False

def read_barcode(timeout=5):
    global barcode_input, last_input_time
    barcode_input = ""
    last_input_time = time.time()

    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        while time.time() - last_input_time < timeout:
            if not listener.running:
                break
            time.sleep(0.1)
        listener.stop()
    
    return barcode_input.strip()

def load_json(filename):
    with open(filename, 'r') as f:
        return json.load(f)

def update_json(data, filename):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)

def get_next_mapping_id(data):
    existing_mapping_ids = [box.get('mapping_id', -1) for box in data.values()]
    return max(existing_mapping_ids + [-1]) + 1

def main():
    json_filename = 'main_box_scenario_777.json'
    data = load_json(json_filename)
    last_activity_time = time.time()

    while True:
        print("Scan box ID (5 second timeout):")
        barcode = read_barcode()
        
        current_time = time.time()
        if current_time - last_activity_time > 10:
            print("No activity for 10 seconds. Saving and exiting.")
            update_json(data, json_filename)
            break

        if not barcode:
            print("No box ID scanned. Try again.")
            continue

        last_activity_time = current_time
        print(f"Scanned box ID: {barcode}")

        if barcode in data:
            if 'mapping_id' not in data[barcode]:
                next_mapping_id = get_next_mapping_id(data)
                data[barcode]['mapping_id'] = next_mapping_id
                print(f"Box found. Assigned new mapping ID: {next_mapping_id}")
            else:
                print(f"Box already has a mapping ID: {data[barcode]['mapping_id']}")
            print(f"Box details: {data[barcode]}")
        else:
            print("Box ID not found in data.")

        update_json(data, json_filename)

if __name__ == "__main__":
    main()