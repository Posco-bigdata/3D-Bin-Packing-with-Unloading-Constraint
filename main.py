import json
import os
import sys
from main_data import create_scenario
from rearrange_order import rearrange_order
from unload import process_unloading
import generate_barcodes as gb
from heuristics import PackingAlgorithm as OriginalPackingAlgorithm, Item as OriginalItem
from subvolume import PackingAlgorithm as SubvolumePackingAlgorithm, Item as SubvolumeItem

def add_mapping_id_to_rearranged_items(scenario_number, packing_method):
    # Load the original data with mapping_id
    with open(f'./main_box_scenario_{scenario_number}.json', 'r') as f:
        original_data = json.load(f)

    # Load the rearranged items data
    rearranged_items_file = f'./scenario/rearranged_items_scenario_{scenario_number}_{packing_method}.json'
    with open(rearranged_items_file, 'r') as f:
        rearranged_items = json.load(f)

    # Add mapping_id to rearranged items
    for item in rearranged_items:
        item_id = str(item['id'])
        if item_id in original_data and 'mapping_id' in original_data[item_id]:
            item['mapping_id'] = original_data[item_id]['mapping_id']

    # Save the updated rearranged items data
    with open(rearranged_items_file, 'w') as f:
        json.dump(rearranged_items, f, indent=4)

    print(f"매핑 ID가 {rearranged_items_file}에 추가되었습니다.")


def main():
    scenario_number = input("시나리오 번호를 입력하세요: ")

    # . 메인 시나리오 생성
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

    add_mapping_id_to_rearranged_items(scenario_number, "original")

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

    add_mapping_id_to_rearranged_items(scenario_number, "subvolume")

    # Subvolume 언로딩 시뮬레이션
    subvolume_unloading_result = process_unloading(scenario_number, "subvolume")
    if subvolume_unloading_result:
        print("Subvolume Heuristic Unloading Results:")
        print(f"Total operations: {subvolume_unloading_result['total_operations']}")
        print(f"Unloading cost: {subvolume_unloading_result['unloading_cost']}")
        print(f"Reloading count: {subvolume_unloading_result['reloading_count']}")


    print("모든 프로세스가 완료되었습니다.")

if __name__ == "__main__":
    main()