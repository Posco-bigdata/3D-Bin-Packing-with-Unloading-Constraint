import json
import random

def generate_box_scenario(scenario_number):
    # Define the box specifications based on the given format
    box_specs = {
        "구 1호": (180, 160, 70, 2), #2
        "구 2호": (260, 180, 151, 2), #2
        "구 3호": (320, 240, 200, 2), #2
        "1호": (220, 190, 90, 12), #12
        "2-1호": (350, 250, 100, 10), # 10
        "2호": (270, 180, 150, 12), # 12
        "3호": (340, 250, 210, 12), #12 
        "4호": (410, 310, 280, 16), # 16
        "5호": (480, 380, 340, 10), #10
        "6호": (520, 480, 400, 10) #10
    }

    # Map the spec_id to each box type
    spec_id_map = {
        "구 1호": 1, "구 2호": 2, "구 3호": 3, "1호": 4, "2-1호": 5,
        "2호": 6, "3호": 7, "4호": 8, "5호": 9, "6호": 10
    }

    # Randomly generate locations
    locations = ["po1", "po2", "po3", "po4", "po5"]

    # Generate the JSON data with random weights and locations
    boxes_data = {}
    counter = 1

    for box_type, (width, length, height, quantity) in box_specs.items():
        spec_id = spec_id_map[box_type]
        for _ in range(quantity):
            box_data = {
                "spec_id": spec_id,
                "width": width*0.1,
                "length": length*0.1,
                "height": height*0.1,
                "volume": width * length * height * 0.001,
                "weight": round(random.uniform(1.0, 10.0), 2),  # Random weight between 1.0 and 10.0
                "location": random.choice(locations)
            }
            boxes_data[counter] = box_data
            counter += 1

    filename = f'./main_box_scenario_{scenario_number}.json'

    # Save the generated data to a JSON file
    with open(filename, 'w') as f:
        json.dump(boxes_data, f, ensure_ascii=False, indent=4)

    print(f"데이터가 {filename}에 저장되었습니다.")
    return filename

# This allows the script to be run standalone or imported as a module
if __name__ == "__main__":
    scenario_number = input("시나리오 번호를 입력하세요: ")
    generate_box_scenario(scenario_number)

# import json

# def generate_box_scenario(scenario_number):
#     filename = f'./main_box_scenario_777.json'

#     # Load the existing data from the JSON file
#     try:
#         with open(filename, 'r') as f:
#             boxes_data = json.load(f)
#     except FileNotFoundError:
#         print(f"Error: File {filename} not found.")
#         return None
#     except json.JSONDecodeError:
#         print(f"Error: File {filename} is not a valid JSON file.")
#         return None

#     # Save the loaded data back to the same JSON file
#     with open(filename, 'w') as f:
#         json.dump(boxes_data, f, ensure_ascii=False, indent=4)

#     print(f"데이터가 {filename}에서 읽어와 같은 위치에 저장되었습니다.")
#     return filename

# # This allows the script to be run standalone or imported as a module
# if __name__ == "__main__":
#     scenario_number = input("시나리오 번호를 입력하세요: ")
#     generate_box_scenario(scenario_number)