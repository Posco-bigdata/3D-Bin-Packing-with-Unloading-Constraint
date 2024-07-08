from main_data import create_scenario
import json 

class Item:
    def __init__(self, id, width, length, height, weight, location):
        self.id = id
        self.width = int(width)
        self.length = int(length)
        self.height = int(height)
        self.weight = weight
        self.location = location
        self.volume = self.width * self.length * self.height

    def possible_orientations(self):
        return [
            (self.width, self.length, self.height),
            (self.width, self.height, self.length),
            (self.length, self.width, self.height),
            (self.length, self.height, self.width),
            (self.height, self.width, self.length),
            (self.height, self.length, self.width)
        ]

class PackingAlgorithm:
    def __init__(self, width, length, height):
        self.width = int(width)
        self.length = int(length)
        self.height = int(height)
        self.packed_items = []
        self.unplaced_items = []
        self.utilization = 0

    def pack_items(self, items):
        # Sort items by height (decreasing)
        sorted_items = sorted(items, key=lambda item: -max(item.width, item.length, item.height))
        
        load_order = 0
        for item in sorted_items:
            placed = False
            best_position = None
            best_orientation = None
            
            for orientation in item.possible_orientations():
                position = self.find_bottom_left_position(orientation)
                if position:
                    if not best_position or self.is_better_position(position, best_position):
                        best_position = position
                        best_orientation = orientation

            if best_position:
                load_order += 1
                self.packed_items.append({
                    "id": item.id,
                    "position": best_position,
                    "orientation": best_orientation,
                    "location": item.location,
                    "load_order": load_order,
                    "weight": item.weight
                })
                placed = True
            
            if not placed:
                print(f"Unable to place item {item.id} from {item.location}")
                self.unplaced_items.append(item)

        self.utilization = self.calculate_capacity_utilization()

    def find_bottom_left_position(self, orientation):
        item_width, item_length, item_height = orientation
        for z in range(self.height):
            for y in range(self.length):
                for x in range(self.width):
                    if self.can_place_item(x, y, z, orientation):
                        return (x, y, z)
        return None

    def can_place_item(self, x, y, z, orientation):
        item_width, item_length, item_height = orientation

        # Check if the item fits within the container dimensions
        if (x + item_width > self.width or
            y + item_length > self.length or
            z + item_height > self.height):
            return False
        
        # Check for overlap with other packed items
        for packed_item in self.packed_items:
            px, py, pz = packed_item['position']
            po = packed_item['orientation']
            if not (x + item_width <= px or x >= px + po[0] or
                    y + item_length <= py or y >= py + po[1] or
                    z + item_height <= pz or z >= pz + po[2]):
                return False

        # Ensure the item is supported
        if z > 0:
            supported = False
            for packed_item in self.packed_items:
                px, py, pz = packed_item['position']
                po = packed_item['orientation']
                if (pz + po[2] == z and
                    x < px + po[0] and px < x + item_width and
                    y < py + po[1] and py < y + item_length):
                    supported = True
                    break
            if not supported:
                return False

        return True

    def is_better_position(self, new_pos, current_best):
        # Prioritize: 1. Lower z, 2. Lower y, 3. Lower x
        return (new_pos[2] < current_best[2] or
                (new_pos[2] == current_best[2] and new_pos[1] < current_best[1]) or
                (new_pos[2] == current_best[2] and new_pos[1] == current_best[1] and new_pos[0] < current_best[0]))

    def calculate_capacity_utilization(self):
        total_volume = sum(item['orientation'][0] * item['orientation'][1] * item['orientation'][2] for item in self.packed_items)
        container_volume = self.width * self.length * self.height
        return total_volume / container_volume

def main():
    scenario_number = int(input("Enter the scenario number: "))
    container_size, items = create_scenario(scenario_number)
    
    container = PackingAlgorithm(container_size[0], container_size[1], container_size[2])
    item_objects = [Item(int(key), value['width'], value['length'], value['height'], value['weight'], value['location'])
                    for key, value in items.items()]
    container.pack_items(item_objects)

    print("Packed Items:")
    for packed_item in container.packed_items:
        print(f"Item ID: {packed_item['id']}, Position: {packed_item['position']}, "
              f"Orientation: {packed_item['orientation']}, Location: {packed_item['location']}, "
              f"Load Order: {packed_item['load_order']}, Weight: {packed_item['weight']}")
 
    # Save packed items to a JSON file
    with open(f'./scenario/packed_items_scenario_{scenario_number}_blfh.json', 'w') as f:
        json.dump(container.packed_items, f, indent=4)

    unplaced_items_data = [
        {
            "id": item.id,
            "width": item.width,
            "length": item.length,
            "height": item.height,
            "weight": item.weight,
            "location": item.location
        }
        for item in container.unplaced_items
    ]
    with open(f'./scenario/unplaced_items_scenario_{scenario_number}_blfh.json', 'w') as f:
        json.dump(unplaced_items_data, f, indent=4)

    # Print the capacity utilization
    print(f"Capacity Utilization: {container.utilization:.2%}")

if __name__ == "__main__":
    main()