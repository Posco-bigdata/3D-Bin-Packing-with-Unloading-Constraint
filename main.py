import json
import os
import sys
from main_scenario_box import generate_box_scenario
from main_data import create_scenario
from rearrange_order import rearrange_order
from unload import process_unloading
import generate_barcodes as gb
from heuristics import PackingAlgorithm as OriginalPackingAlgorithm, Item as OriginalItem
from subvolume import PackingAlgorithm as SubvolumePackingAlgorithm, Item as SubvolumeItem

def main():
    scenario_number = input("시나리오 번호를 입력하세요: ")

    # 1. 박스 시나리오 생성
    generate_box_scenario(scenario_number)

    # 2. 메인 시나리오 생성
    container_size, items = create_scenario(scenario_number)

    # 3. 기존 heuristic을 사용한 아이템 패킹
    original_container = OriginalPackingAlgorithm(container_size[0], container_size[1], container_size[2])
    original_item_objects = [OriginalItem(int(key), value['width'], value['length'], value['height'], value['weight'], value['location'])
                    for key, value in items.items()]
    original_container.pack_items_with_permutations(original_item_objects)

    # 기존 heuristic 결과 저장
    with open(f'./scenario/packed_items_scenario_{scenario_number}_original.json', 'w') as f:
        json.dump(original_container.best_packed_items, f, indent=4)

    print(f"Original Heuristic - Best Capacity Utilization: {original_container.best_utilization:.2%}")

    # 기존 heuristic 적재 순서 재배열
    original_rearranged_items = rearrange_order(original_container.best_packed_items, container_size[0], container_size[1], container_size[2])
    original_rearranged_items_file = f'./scenario/rearranged_items_scenario_{scenario_number}_original.json'
    with open(original_rearranged_items_file, 'w') as f:
        json.dump(original_rearranged_items, f, indent=4)

    # 기존 heuristic 언로딩 시뮬레이션
    original_unloading_result = process_unloading(scenario_number, "original")
    if original_unloading_result:
        print("Original Heuristic Unloading Results:")
        print(f"Total operations: {original_unloading_result['total_operations']}")
        print(f"Unloading cost: {original_unloading_result['unloading_cost']}")
        print(f"Reloading count: {original_unloading_result['reloading_count']}")

    # 4. Subvolume 기법을 사용한 아이템 패킹
    subvolume_container = SubvolumePackingAlgorithm(container_size[0], container_size[1], container_size[2])
    subvolume_item_objects = [SubvolumeItem(int(key), value['width'], value['length'], value['height'], value['weight'], value['location'])
                    for key, value in items.items()]
    subvolume_container.pack_items_with_permutations(subvolume_item_objects)

    # Subvolume 결과 저장
    with open(f'./scenario/subvolume_packed_items_scenario_{scenario_number}.json', 'w') as f:
        json.dump(subvolume_container.best_packed_items, f, indent=4)

    unplaced_items_data = [
        {
            "id": item.id,
            "width": item.width,
            "length": item.length,
            "height": item.height,
            "weight": item.weight,
            "location": item.location
        }
        for item in subvolume_container.best_unplaced_items
    ]
    with open(f'./scenario/subvolume_unplaced_items_scenario_{scenario_number}.json', 'w') as f:
        json.dump(unplaced_items_data, f, indent=4)

    print(f"Subvolume Heuristic - Best Capacity Utilization: {subvolume_container.best_utilization:.2%}")

    # Subvolume 적재 순서 재배열
    subvolume_rearranged_items = rearrange_order(subvolume_container.best_packed_items, container_size[0], container_size[1], container_size[2])
    subvolume_rearranged_items_file = f'./scenario/rearranged_items_scenario_{scenario_number}_subvolume.json'
    with open(subvolume_rearranged_items_file, 'w') as f:
        json.dump(subvolume_rearranged_items, f, indent=4)

    # Subvolume 언로딩 시뮬레이션
    subvolume_unloading_result = process_unloading(scenario_number, "subvolume")
    if subvolume_unloading_result:
        print("Subvolume Heuristic Unloading Results:")
        print(f"Total operations: {subvolume_unloading_result['total_operations']}")
        print(f"Unloading cost: {subvolume_unloading_result['unloading_cost']}")
        print(f"Reloading count: {subvolume_unloading_result['reloading_count']}")

    # 7. 바코드 생성
    gb.generate_barcodes(scenario_number)

    print("모든 프로세스가 완료되었습니다.")

if __name__ == "__main__":
    main()