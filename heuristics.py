from given_data import container_size, data
import random
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

# Convert data to a list of Item objects
items = [Item(int(key), value['width'], value['length'], value['height'], value['weight'], value['location'])
         for key, value in data.items()]

class PackingAlgorithm:
    def __init__(self, width, length, height):
        self.width = int(width)
        self.length = int(length)
        self.height = int(height)
        self.large_section_width = int(self.width * 0.7)
        self.small_section_width = self.width - self.large_section_width
        self.best_packed_items = []
        self.best_utilization = 0

    def pack_items_with_permutations(self, items, num_iterations=1):
        for i in range(num_iterations):
            # Sort items by PO number (descending) and then by volume (descending)
            items_sorted = sorted(items, key=lambda item: (-int(item.location[2:]), -item.volume))
            
            packed_items = self.pack_items_by_po(items_sorted)
            utilization = self.calculate_capacity_utilization(packed_items)

            print(f"Iteration {i+1}/{num_iterations}, Utilization: {utilization:.2%}")

            if utilization > self.best_utilization:
                self.best_packed_items = packed_items
                self.best_utilization = utilization

    def pack_items_by_po(self, sorted_items):
        packed_items = []
        load_order = 0
        current_po = None

        for item in sorted_items:
            if item.location != current_po:
                current_po = item.location
                print(f"Packing items for {current_po}")
            
            placed = False
            best_position = None
            best_orientation = None

            for orientation in item.possible_orientations():
                position = self.find_position(orientation, packed_items)
                if position:
                    if not best_position or self.is_better_position(position, best_position):
                        best_position = position
                        best_orientation = orientation

            if best_position:
                load_order += 1
                packed_items.append({
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

        return packed_items

    def find_position(self, orientation, packed_items):
        item_width, item_length, item_height = orientation
        
        # Try placing in the larger section first
        position = self.find_position_in_section(orientation, packed_items, 0, self.large_section_width)
        if position:
            return position
        
        # If it doesn't fit in the larger section, try the smaller section
        return self.find_position_in_section(orientation, packed_items, self.large_section_width, self.width)

    def find_position_in_section(self, orientation, packed_items, start_x, end_x):
        item_width, item_length, item_height = orientation
        for y in range(self.length - item_length, item_length - 1, -1):  # Start from back
            for x in range(start_x, end_x - item_width + 1):  # Start from left of the section
                for z in range(self.height):  # Start from bottom
                    if self.can_place_item(x, y, z, orientation, packed_items):
                        return (x, y, z)
        return None


    def is_better_position(self, new_pos, current_best):
        if not current_best:
            return True
        # Prioritize: 1. Back (higher y), 2. Left (lower x), 3. Bottom (lower z)
        if new_pos[1] > current_best[1]:
            return True
        elif new_pos[1] == current_best[1]:
            if new_pos[0] < current_best[0]:
                return True
            elif new_pos[0] == current_best[0]:
                return new_pos[2] < current_best[2]
        return False

    def can_place_item(self, x, y, z, orientation, packed_items):
        item_width, item_length, item_height = orientation

        # Check if the item fits within the container dimensions
        if (x + item_width > self.width or
            y + item_length > self.length or
            z + item_height > self.height):
            return False
        
        # Check for overlap with other packed items
        for packed_item in packed_items:
            px, py, pz = packed_item['position']
            po = packed_item['orientation']
            if not (x + item_width <= px or x >= px + po[0] or
                    y + item_length <= py or y >= py + po[1] or
                    z + item_height <= pz or z >= pz + po[2]):
                return False

        # Ensure the item's bottom is fully supported
        if z == 0:
            return True
        else:
            supported_area = 0
            item_base_area = item_width * item_length
            for packed_item in packed_items:
                px, py, pz = packed_item['position']
                po = packed_item['orientation']
                if z == pz + po[2]:  # If the item is right above this packed item
                    overlap_x = max(0, min(x + item_width, px + po[0]) - max(x, px))
                    overlap_y = max(0, min(y + item_length, py + po[1]) - max(y, py))
                    supported_area += overlap_x * overlap_y
            return supported_area == item_base_area


    def calculate_capacity_utilization(self, packed_items):
        total_volume = sum(item['orientation'][0] * item['orientation'][1] * item['orientation'][2] for item in packed_items)
        container_volume = self.width * self.length * self.height
        return total_volume / container_volume

def main():
    container = PackingAlgorithm(container_size[0], container_size[1], container_size[2])
    container.pack_items_with_permutations(items)

    print("Best Packed Items:")
    for packed_item in container.best_packed_items:
        print(f"Item ID: {packed_item['id']}, Position: {packed_item['position']}, "
              f"Orientation: {packed_item['orientation']}, Location: {packed_item['location']}, "
              f"Load Order: {packed_item['load_order']}, Weight: {packed_item['weight']}")
 
    # Save packed items to a JSON file
    with open('packed_items.json', 'w') as f:
        json.dump(container.best_packed_items, f, indent=4)

    # Print the best capacity utilization
    print(f"Best Capacity Utilization: {container.best_utilization:.2%}")

if __name__ == "__main__":
    main()
