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
        self.best_packed_items = []
        self.best_utilization = 0

    def pack_items_with_permutations(self, items, num_iterations=10):
        for i in range(num_iterations):
            items_sorted = sorted(items, key=lambda item: item.location)  # Sort items by location
            random.shuffle(items_sorted)  # Shuffle within the sorted list
            packed_items = self.pack_items(items_sorted)
            utilization = self.calculate_capacity_utilization(packed_items)

            print(f"Iteration {i+1}/{num_iterations}, Utilization: {utilization:.2%}")

            if utilization > self.best_utilization:
                self.best_packed_items = packed_items
                self.best_utilization = utilization

    def pack_items(self, items):
        packed_items = []
        load_order = 0
        
        for item in items:
            placed = False
            for orientation in item.possible_orientations():
                for z in range(self.height):
                    for y in range(self.length):
                        for x in range(self.width):
                            if self.can_place_item(x, y, z, orientation, packed_items):
                                load_order += 1
                                packed_items.append({
                                    "id": item.id,
                                    "position": (x, y, z),
                                    "orientation": orientation,
                                    "location": item.location,
                                    "load_order": load_order,
                                    "weight": item.weight
                                })
                                placed = True
                                break
                        if placed:
                            break
                    if placed:
                        break
                if placed:
                    break
            
            if not placed:
                print(f"Unable to place item {item.id}")
        
        return packed_items

    def can_place_item(self, x, y, z, orientation, packed_items):
        if (x + orientation[0] > self.width or
            y + orientation[1] > self.length or
            z + orientation[2] > self.height):
            return False
        
        for packed_item in packed_items:
            px, py, pz = packed_item['position']
            po = packed_item['orientation']
            if not (x + orientation[0] <= px or x >= px + po[0] or
                    y + orientation[1] <= py or y >= py + po[1] or
                    z + orientation[2] <= pz or z >= pz + po[2]):
                return False

        # Ensure the item is supported by the container floor or other items
        if z == 0:
            return True
        else:
            supported = False
            for packed_item in packed_items:
                px, py, pz = packed_item['position']
                po = packed_item['orientation']
                if (x < px + po[0] and x + orientation[0] > px and
                    y < py + po[1] and y + orientation[1] > py and
                    z == pz + po[2]):
                    supported = True
                    break
            return supported
        

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
