import json
import sys
from main_data import create_scenario

def rearrange_order(packed_items, container_width, container_length, container_height):
    large_section_width = int(container_width * 0.7)
    large_section = []
    small_section = []
    
    # Separate items into large and small sections
    for item in packed_items:
        if item['position'][0] + item['orientation'][0] <= large_section_width:
            large_section.append(item)
        else:
            small_section.append(item)
    
    # Sort and reassign load orders for large section
    large_section.sort(key=lambda x: x['load_order'])
    for i, item in enumerate(large_section):
        item['load_order'] = i + 1
    
    # Sort small section items by position[1] (descending) and position[2] (ascending)
    small_section.sort(key=lambda x: (-x['position'][1], x['position'][2]))
    
    # Apply new layering method to small section
    layers = []
    current_layer = []
    current_layer_length = 0
    buffer = 10  # 10-unit buffer
    
    while small_section:
        # Find the item with the largest position[1] value and smallest position[2]
        back_item = next((item for item in small_section if item['position'][2] == 0), small_section[0])
        small_section.remove(back_item)
        
        new_layer_length = container_length - back_item['position'][1]
        if new_layer_length > current_layer_length:
            if current_layer:
                layers.append(current_layer)
            current_layer = [back_item]
            current_layer_length = new_layer_length
        else:
            current_layer.append(back_item)
        
        # Stack items in the current layer
        fitting_items = []
        i = 0
        while i < len(small_section):
            item = small_section[i]
            item_distance = container_length - item['position'][1]
            if item_distance <= current_layer_length+buffer:
                fitting_items.append(item)
                small_section.pop(i)
            else:
                i += 1
        
        # Sort fitting items by height (ascending) and add to current layer
        fitting_items.sort(key=lambda x: x['position'][2])
        current_layer.extend(fitting_items)
    
    # Add the last layer
    if current_layer:
        layers.append(current_layer)
    # Reassign load orders for small section
    new_load_order = len(large_section) + 1
    rearranged_small_section = []
    for layer in layers:
        for item in layer:
            item['load_order'] = new_load_order
            new_load_order += 1
            rearranged_small_section.append(item)
    
    # Combine and return the rearranged items
    return large_section + rearranged_small_section


def process_rearrangement(scenario_number, method):
    # create_scenario 함수를 사용하여 컨테이너 크기와 아이템 데이터를 가져옵니다
    container_size, _ = create_scenario(scenario_number)
    container_width, container_length, container_height = container_size

    # Read the packed items JSON file
    if method == "original":
        input_file = f'./scenario/packed_items_scenario_{scenario_number}_original.json'
    elif method == "subvolume":
        input_file = f'./scenario/subvolume_packed_items_scenario_{scenario_number}.json'
    elif method == "bl_ffhdc":
        input_file = f'./scenario/packed_items_scenario_{scenario_number}_blfh.json'
    else:
        raise ValueError("Invalid method. Choose 'original', 'subvolume', or 'bl_ffhdc'.")

    with open(input_file, 'r') as f:
        packed_items = json.load(f)

    # Rearrange the order
    rearranged_items = rearrange_order(packed_items, container_width, container_length, container_height)
 
    # Write the output JSON file
    output_file = f'./scenario/rearranged_items_scenario_{scenario_number}_{method}.json'
    with open(output_file, 'w') as f:
        json.dump(rearranged_items, f, indent=4)

    print(f"Rearranged items for {method} method have been saved to {output_file}")
    return rearranged_items

def main():
    scenario_number = input("Enter the scenario number: ")
    
    # Process rearrangement for original heuristic
    original_rearranged_items = process_rearrangement(scenario_number, "original")
    print(f"Number of rearranged items (original heuristic): {len(original_rearranged_items)}")

    # Process rearrangement for subvolume method
    subvolume_rearranged_items = process_rearrangement(scenario_number, "subvolume")
    print(f"Number of rearranged items (subvolume method): {len(subvolume_rearranged_items)}")

    # Process rearrangement for bl_ffhdc method
    bl_ffhdc_rearranged_items = process_rearrangement(scenario_number, "bl_ffhdc")
    print(f"Number of rearranged items (bl_ffhdc method): {len(bl_ffhdc_rearranged_items)}")

if __name__ == "__main__":
    main()
