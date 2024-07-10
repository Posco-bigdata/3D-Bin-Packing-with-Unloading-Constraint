import json
from main_data import create_scenario

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
            (self.length, self.width, self.height)
        ]

class Container:
    def __init__(self, width, length, height):
        self.width = int(width)
        self.length = int(length)
        self.height = int(height)
        self.large_section_width = int(self.width * 0.7)
        self.packed_items = []
        self.space = [[[False for _ in range(self.height)] for _ in range(self.length)] for _ in range(self.width)]

    def pack_items(self, items):
        large_section_items = []
        small_section_items = []
        for item in items:
            if item.width <= self.large_section_width:
                large_section_items.append(item)
            else:
                small_section_items.append(item)

        self.pack_large_section(large_section_items)
        self.pack_small_section(small_section_items)

    def pack_large_section(self, items):
        items.sort(key=lambda x: int(x.location[2:]))  # Sort by PO number
        for item in items:
            placed = self.place_item(item, 0, self.large_section_width)
            if not placed:
                print(f"Cannot place item {item.id} in large section")

    def pack_small_section(self, items):
        for item in items:
            placed = self.place_item(item, self.large_section_width, self.width)
            if not placed:
                print(f"Cannot place item {item.id} in small section")

    def place_item(self, item, start_x, end_x):
        for orientation in item.possible_orientations():
            for x in range(start_x, end_x - orientation[0] + 1):
                for y in range(self.length - orientation[1] + 1):
                    for z in range(self.height):
                        if self.can_place_item(x, y, z, orientation):
                            self.packed_items.append({
                                "id": item.id,
                                "position": (x, y, z),
                                "orientation": orientation,
                                "location": item.location,
                                "weight": item.weight,
                                "load_order": len(self.packed_items) + 1
                            })
                            self.update_space(x, y, z, orientation)
                            return True
        return False

    def can_place_item(self, x, y, z, orientation):
        if x + orientation[0] > self.width or y + orientation[1] > self.length or z + orientation[2] > self.height:
            return False
        
        # Check if the space is empty
        for i in range(x, x + orientation[0]):
            for j in range(y, y + orientation[1]):
                for k in range(z, z + orientation[2]):
                    if self.space[i][j][k]:
                        return False
        
        # Check if the item is supported
        if z == 0:
            return True  # Item is on the floor
        else:
            supported_area = 0
            total_area = orientation[0] * orientation[1]
            for i in range(x, x + orientation[0]):
                for j in range(y, y + orientation[1]):
                    if self.space[i][j][z-1]:
                        supported_area += 1
            
            return supported_area / total_area >= 0.8  # At least 80% support

    def update_space(self, x, y, z, orientation):
        for i in range(x, x + orientation[0]):
            for j in range(y, y + orientation[1]):
                for k in range(z, z + orientation[2]):
                    self.space[i][j][k] = True
def main():
    scenario_number = int(input("Enter the scenario number: "))
    container_size, items = create_scenario(scenario_number)
    
    container = Container(container_size[0], container_size[1], container_size[2])
    item_objects = [Item(int(key), value['width'], value['length'], value['height'], value['weight'], value['location'])
                    for key, value in items.items()]
    
    container.pack_items(item_objects)

    # Save packed items to a JSON file
    output_file = f'./scenario/subvolume_packed_items_scenario_{scenario_number}.json'
    with open(output_file, 'w') as f:
        json.dump(container.packed_items, f, indent=4)

    print(f"Packed {len(container.packed_items)} items.")
    print(f"Packed items have been saved to {output_file}")

if __name__ == "__main__":
    main()