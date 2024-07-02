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

    return (x1 < x2 + w2 and x2 < x1 + w1 and
            y1 < y2 + l2 and y2 < y1 + l1 and
            z1 < z2 + h2 and z2 < z1 + h1)

def unload_items(packed_items):
    # Sort items by y-position (depth in the container)
    sorted_items = sorted(packed_items, key=lambda x: x['position'][1], reverse=True)

    # Group items by location
    location_groups = defaultdict(list)
    for item in sorted_items:
        location_groups[item['location']].append(item)

    total_operations = 0
    unloaded_items = []
    reloaded_items = []

    # Process locations in order (po1 to po5)
    for location in ['po1', 'po2', 'po3', 'po4', 'po5']:
        print(f"\nProcessing location: {location}")
        
        items_to_unload = location_groups[location]
        
        for item in items_to_unload:
            operations = 1  # Start with 1 for unloading the target item
            blocking_items = []

            # Check for blocking items
            for unloaded in unloaded_items + reloaded_items:
                if is_blocking(unloaded, item):
                    blocking_items.append(unloaded)

            # Unload blocking items
            for blocking in blocking_items:
                if blocking not in unloaded_items:
                    operations += 2  # Unload and reload
                    reloaded_items.remove(blocking)
                else:
                    operations += 1  # Just unload

            print(f"Unloading item {item['id']} (location {item['location']}): {operations} operations")
            total_operations += operations

            unloaded_items.append(item)
            if item in reloaded_items:
                reloaded_items.remove(item)

        # Reload items that were unloaded but belong to a different location
        for unloaded in unloaded_items.copy():
            if unloaded['location'] != location:
                reloaded_items.append(unloaded)
                unloaded_items.remove(unloaded)
                total_operations += 1
                print(f"Reloading item {unloaded['id']} (location {unloaded['location']}): 1 operation")

    return total_operations

def main():
    total_operations = unload_items(packed_items)
    print(f"\nTotal unloading operations: {total_operations}")

if __name__ == "__main__":
    main()