import json
from collections import defaultdict
import numpy as np
import os

# Load container size
from given_data import container_size

def is_in_untakeout_field(item1, item2):
    x1, y1, z1 = item1['position']
    l1, w1, h1 = item1['orientation']
    x2, y2, z2 = item2['position']
    l2, w2, h2 = item2['orientation']

    # Define F1, F2, F3 conditions based on the right view
    F1 = x2 > x1 and z2 > z1 + h1
    F2 = z2 > z1 and x1 + l1 < x2 < x1 + l1 + max(200 - z1, 60)
    F3 = x2 > x1 + l1 + max(200 - z1, 60)

    # Define Fy condition based on the front view
    Fy = y1 < y2 < y1 + w1

    # Check if item2 is within the container
    in_container = (0 <= x2 < container_size[0] and 
                    0 <= y2 < container_size[1] and 
                    0 <= z2 < container_size[2])

    return ((F1 or F2 or F3) and Fy and in_container)

def is_blocking(item1, item2):
    if is_in_untakeout_field(item1, item2):
        return True

    # Additional logic for checking if any item is in front (y) or above (z) item1
    x1, y1, z1 = item1['position']
    l1, w1, h1 = item1['orientation']
    x2, y2, z2 = item2['position']
    l2, w2, h2 = item2['orientation']
    
    # Check if item2 is directly in front of item1 (y-axis alignment)
    in_front = y1 + w1 <y2 and z1 < z2 < z1 + h1

    # Check if item2 is directly above item1 (z-axis alignment)
    above = z1 + h1 <z2 and x1 < x2 < x1 + l1 and y1 < y2 < y1 + w1

    return in_front or above


def unload_items(packed_items):
    sorted_items = sorted(packed_items, key=lambda x: x['load_order'])  # 적재 순서대로 정렬
    location_groups = defaultdict(list)
    for item in sorted_items:
        location_groups[item['location']].append(item)

    total_operations = 0
    unloading_cost = 0
    unloaded_items = []
    operations_log = []
    unload_order = 1

    for location in ['po1', 'po2', 'po3', 'po4', 'po5']:
        operations_log.append({"step": f"Processing location: {location}", "items": []})
        
        items_to_unload = location_groups[location]
        
        for item in items_to_unload:
            item_cost = 0
            blocking_items = []

            # Check for blocking items
            for other_item in sorted_items:
                if other_item not in unloaded_items and is_blocking(item, other_item):
                    blocking_items.append(other_item)

            if item['location'] == location and not blocking_items:
                # Directly unload if there are no blocking items
                total_operations += 1
                unloaded_items.append(item)
                operations_log[-1]["items"].append({
                    "action": "Unload",
                    "item_id": item['id'],
                    "location": item['location'],
                    "position": item['position'],
                    "unload_order": unload_order,
                    "unloading_cost": item_cost  # No cost as it is directly unloaded
                })
                unload_order += 1
                continue  # Skip further checks for this item

            # If blocked, unload blocking items, then unload desired item, then reload blocking items
            for blocking in blocking_items:
                # Unload the blocking item
                operations_log[-1]["items"].append({
                    "action": "Unload blocking item",
                    "item_id": blocking['id'],
                    "location": blocking['location'],
                    "position": blocking['position'],
                    "unloading_cost": 1
                })
                total_operations += 1
                item_cost += 1

            # Unload the desired item
            operations_log[-1]["items"].append({
                "action": "Unload",
                "item_id": item['id'],
                "location": item['location'],
                "position": item['position'],
                "unload_order": unload_order,
                "unloading_cost": item_cost
            })
            total_operations += 1
            unloading_cost += item_cost
            unloaded_items.append(item)
            unload_order += 1

            # Reload the blocking items
            for blocking in blocking_items:
                operations_log[-1]["items"].append({
                    "action": "Reload blocking item",
                    "item_id": blocking['id'],
                    "location": blocking['location'],
                    "position": blocking['position'],
                    "unloading_cost": 1
                })
                total_operations += 1

    return total_operations, unloading_cost, operations_log

def main():
    # 시나리오 번호 입력 받기
    scenario_number = input("시나리오 번호를 입력하세요: ")
    
    # 시나리오 파일 경로
    scenario_file = f'./scenario/packed_items_scenario_{scenario_number}.json'
    
    # 시나리오 파일 존재 확인
    if not os.path.exists(scenario_file):
        print(f"Error: 시나리오 파일 '{scenario_file}'을 찾을 수 없습니다.")
        return

    # 시나리오 파일에서 packed_items 로드
    with open(scenario_file, 'r') as f:
        packed_items = json.load(f)

    # 언로딩 작업 수행
    total_operations, unloading_cost, operations_log = unload_items(packed_items)
    
    print(f"\n시나리오 {scenario_number}:")
    print(f"총 언로딩 작업 수: {total_operations}")
    print(f"총 언로딩 비용: {unloading_cost}")

    # 결과를 JSON 파일로 저장
    result_file = f'./scenario/unloading_operations_scenario_{scenario_number}.json'
    with open(result_file, 'w') as f:
        json.dump(operations_log, f, indent=4)

    print(f"언로딩 작업 결과가 '{result_file}'에 저장되었습니다.")

if __name__ == "__main__":
    main()