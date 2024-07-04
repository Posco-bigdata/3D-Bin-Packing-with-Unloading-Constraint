import json
from collections import defaultdict

# Load container size
from given_data import container_size

# Load packed items
with open('packed_items.json', 'r') as f:
    packed_items = json.load(f)

def is_blocking(item1, item2):
    x1, y1, z1 = item1['position']
    w1, l1, h1 = item1['orientation']
    x2, y2, z2 = item2['position']
    w2, l2, h2 = item2['orientation']

    if z1 < z2 + h2 and z2 < z1 + h1:
        if y1 < y2:
            return True
        elif y1 < y2 + l2 and y2 < y1 + l1:
            if z1 > z2:
                return True
    
    return False

def unload_items(packed_items):
    sorted_items = sorted(packed_items, key=lambda x: x['position'][1], reverse=True)
    location_groups = defaultdict(list)
    for item in sorted_items:
        location_groups[item['location']].append(item)

    total_operations = 0
    unloaded_items = []
    temporarily_unloaded = []
    operations_log = []
    unload_order = 1

    for location in ['po1', 'po2', 'po3', 'po4', 'po5']:
        operations_log.append({"step": f"Processing location: {location}", "items": []})
        
        items_to_unload = location_groups[location]
        
        for item in items_to_unload:
            blocking_items = []

            for other_item in sorted_items:
                if other_item != item and other_item not in unloaded_items and is_blocking(other_item, item):
                    blocking_items.append(other_item)

            for blocking in blocking_items:
                total_operations += 1
                if blocking['location'] != location:
                    temporarily_unloaded.append(blocking)
                    operations_log[-1]["items"].append({
                        "action": "Temporarily unload",
                        "item_id": blocking['id'],
                        "location": blocking['location'],
                        "position": blocking['position'],
                        "unload_order": unload_order
                    })
                else:
                    unloaded_items.append(blocking)
                    operations_log[-1]["items"].append({
                        "action": "Unload",
                        "item_id": blocking['id'],
                        "location": blocking['location'],
                        "position": blocking['position'],
                        "unload_order": unload_order
                    })
                unload_order += 1

            total_operations += 1
            unloaded_items.append(item)
            operations_log[-1]["items"].append({
                "action": "Unload",
                "item_id": item['id'],
                "location": item['location'],
                "position": item['position'],
                "unload_order": unload_order
            })
            unload_order += 1

        for temp_item in temporarily_unloaded:
            total_operations += 1
            operations_log[-1]["items"].append({
                "action": "Reload",
                "item_id": temp_item['id'],
                "location": temp_item['location'],
                "position": temp_item['position'],
                "unload_order": unload_order
            })
            unload_order += 1

        temporarily_unloaded.clear()

    return total_operations, operations_log

def main():
    total_operations, operations_log = unload_items(packed_items)
    print(f"\nTotal unloading operations: {total_operations}")

    # Save operations log to a JSON file
    with open('unloading_operations.json', 'w') as f:
        json.dump(operations_log, f, indent=4)

    print("Unloading operations have been saved to 'unloading_operations.json'")

if __name__ == "__main__":
    main()