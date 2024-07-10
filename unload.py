import json
import os
from collections import defaultdict
from main_data import create_scenario

def is_in_untakeout_field(item1, item2, container_size):
    x1, y1, z1 = item1['position']
    w1, l1, h1 = item1['orientation']
    x2, y2, z2 = item2['position']
    w2, l2, h2 = item2['orientation']

    # Check if item2 is in front of item1
    in_front = y2 < y1 + l1

    # Check if item2 is above item1
    above = z2 >= z1 + h1

    # Check if item2 overlaps with item1 in the x-axis
    x_overlap = (x1 < x2 + w2) and (x2 < x1 + w1)

    # Check if item2 is within the container
    in_container = (0 <= x2 < container_size[0] and 
                    0 <= y2 < container_size[1] and 
                    0 <= z2 < container_size[2])

    return in_front and above and x_overlap and in_container

def is_blocking(item1, item2, container_size):
    return is_in_untakeout_field(item1, item2, container_size)

def calculate_unloading_time(item, human_height=180):
    x, y, z = item['position']
    l, w, h = item['orientation']
    weight = item['weight']
    
    # Calculate lifting height (from item's center to human height)
    lifting_height = human_height/100 - ((z + h / 2)/100)
    
    # Calculate moving distance (from item's position to container exit at y=0)
    moving_distance = y/100
    
    # Apply the formula
    T = 0.000001 + 0.0015 * moving_distance + 0.0002 * lifting_height
    return T  # Time in minutes

def unload_items(packed_items, container_size):
    location_groups = defaultdict(list)
    for item in packed_items:
        location_groups[item['location']].append(item)

    total_operations = 0
    unloading_cost = 0
    reloading_count = 0
    unloaded_items = []
    operations_log = []
    unload_order = 1
    temporarily_unloaded = []

    processing_locations = ['po1', 'po2', 'po3', 'po4', 'po5']
    
    for location in processing_locations:
        operations_log.append({"step": f"Processing location: {location}", "items": []})
        
        # Sort items by y coordinate (front to back)
        items_to_unload = sorted(location_groups[location], key=lambda x: (x['position'][1], -x['position'][2]))        
        while items_to_unload:
            item = items_to_unload.pop(0)
            remaining_items = [item for item in packed_items if item not in unloaded_items]
            blocking_items = [other_item for other_item in remaining_items 
                              if is_blocking(item, other_item, container_size)]

            for blocking_item in blocking_items:
                if blocking_item['location'] == location:
                    # Unload the blocking item if it's for this location
                    unloading_time = calculate_unloading_time(blocking_item)
                    unloading_cost += unloading_time
                    unloaded_items.append(blocking_item)
                    operations_log[-1]["items"].append({
                        "action": "Unload blocking item",
                        "item_id": blocking_item['id'],
                        "location": blocking_item['location'],
                        "position": blocking_item['position'],
                        "unload_order": unload_order,
                        "unloading_time": unloading_time
                    })
                    total_operations += 1
                    unload_order += 1
                    if blocking_item in items_to_unload:
                        items_to_unload.remove(blocking_item)
                else:
                    # Temporarily unload the blocking item if it's for a different location
                    if blocking_item not in temporarily_unloaded:
                        temporarily_unloaded.append(blocking_item)
                        operations_log[-1]["items"].append({
                            "action": "Temporarily unload blocking item",
                            "item_id": blocking_item['id'],
                            "location": blocking_item['location'],
                            "position": blocking_item['position'],
                            "unloading_cost": 1
                        })
                        total_operations += 1
                        unloading_cost += 1

            # Unload the item
            unloading_time = calculate_unloading_time(item)
            unloading_cost += unloading_time
            unloaded_items.append(item)
            operations_log[-1]["items"].append({
                "action": "Unload",
                "item_id": item['id'],
                "location": item['location'],
                "position": item['position'],
                "unload_order": unload_order,
                "unloading_time": unloading_time
            })
            total_operations += 1
            unload_order += 1

        # Reload temporarily unloaded items after processing each location
        if location != processing_locations[-1]:  # Don't reload after the last location
            # Sort temporarily unloaded items by y coordinate (back to front) and z coordinate (bottom to top)
            temporarily_unloaded.sort(key=lambda x: (-x['position'][1], x['position'][2]))
            
            for temp_item in temporarily_unloaded:
                operations_log[-1]["items"].append({
                    "action": "Reload temporarily unloaded item",
                    "item_id": temp_item['id'],
                    "location": temp_item['location'],
                    "position": temp_item['position'],
                    "unloading_cost": 1
                })
                total_operations += 1
                reloading_count += 1
                unloading_cost += 1
            
            temporarily_unloaded.clear()  # Clear the list after reloading

    return total_operations, unloading_cost, reloading_count, operations_log

def process_unloading(scenario_number, method):
    # create_scenario 함수를 사용하여 컨테이너 크기를 가져옵니다
    container_size, _ = create_scenario(scenario_number)

    if method == "original":
        scenario_file = f'./scenario/rearranged_items_scenario_{scenario_number}_original.json'
    elif method == "subvolume":
        scenario_file = f'./scenario/rearranged_items_scenario_{scenario_number}_subvolume.json'
    elif method == "bl_ffhdc":
        scenario_file = f'./scenario/rearranged_items_scenario_{scenario_number}_bl_ffhdc.json'
    else:
        print(f"Error: 잘못된 방법입니다. 'original', 'subvolume' 또는 'bl_ffhdc'를 선택하세요.")
        return None
    
    if not os.path.exists(scenario_file):
        print(f"Error: 시나리오 파일 '{scenario_file}'을 찾을 수 없습니다.")
        return None

    with open(scenario_file, 'r') as f:
        packed_items = json.load(f)

    total_operations, unloading_cost, reloading_count, operations_log = unload_items(packed_items, container_size)
    
    result_file = f'./scenario/unloading_operations_scenario_{scenario_number}_{method}.json'
    with open(result_file, 'w') as f:
        json.dump(operations_log, f, indent=4)

    print(f"언로딩 작업 결과가 '{result_file}'에 저장되었습니다.")

    return {
        'total_operations': total_operations,
        'unloading_cost': unloading_cost,
        'reloading_count': reloading_count
    }

def main():
    scenario_number = input("시나리오 번호를 입력하세요: ")
    
    methods = ["original", "subvolume", "bl_ffhdc"]
    
    for method in methods:
        result = process_unloading(scenario_number, method)
        if result:
            print(f"\n{method.capitalize()} 결과:")
            print(f"총 적재 횟수: {result['total_operations']}")
            print(f"하차 비용: {result['unloading_cost']}")
            print(f"재적재 횟수: {result['reloading_count']}")
        else:
            print(f"{method.capitalize()} 언로딩 프로세스를 완료할 수 없습니다.")

if __name__ == "__main__":
    main()