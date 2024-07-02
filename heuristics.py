from given_data import container_size, data
import random
import json

# Item class to represent each box
class Item:
    def __init__(self, id, width, length, height, weight, location):
        self.id = id
        self.width = width
        self.length = length
        self.height = height
        self.weight = weight
        self.orientation = (width, length, height)
        self.location = location

    def possible_orientations(self):
        orientations = [
            (self.width, self.length, self.height),
            (self.width, self.height, self.length),
            (self.length, self.width, self.height),
            (self.length, self.height, self.width),
            (self.height, self.width, self.length),
            (self.height, self.length, self.width)
        ]
        return orientations

# Convert data to a list of Item objects
items = []
for key, value in data.items():
    items.append(Item(int(key), value['width'], value['length'], value['height'], value['weight'], value['location']))

# SubVolume class to represent available spaces in the container
class SubVolume:
    def __init__(self, x, y, z, width, length, height):
        self.x = x
        self.y = y
        self.z = z
        self.width = width
        self.length = length
        self.height = height
    
    @property
    def position(self):
        return (self.x, self.y, self.z)

    @property
    def dimensions(self):
        return (self.width, self.length, self.height)
    
    def can_accommodate(self, item):
        item_width, item_length, item_height = item
        return self.width >= item_width and self.length >= item_length and self.height >= item_height

class PackingAlgorithm:
    def __init__(self, width, length, height):
        self.width = width
        self.length = length
        self.height = height
        self.sub_volumes = [SubVolume(0, length, 0, width, length, height)]
        self.packed_items = []
        self.unloading_sequence = {}


    def pack_items_dbl(self, items):
        best_packing = []
        best_packing_count = 0
        iterations = 1000  # Number of iterations to attempt

        # Sort items based on location to ensure unloading in reverse order
        items.sort(key=lambda x: x.location, reverse=True)

        for _ in range(iterations):
            self.reset()
            random_items = random.sample(items, len(items))
            load_order = 0
            for item in random_items:
                placed = False
                random_orientations = random.sample(item.possible_orientations(), len(item.possible_orientations()))

                
                # Sort sub_volumes to prioritize bottom-left positions
                self.sub_volumes.sort(key=lambda sv: (-sv.y, sv.z, sv.x))            
                for subvolume in self.sub_volumes:
                    for orientation in random_orientations:
                        if subvolume.can_accommodate(orientation):
                            item_position = (subvolume.x, subvolume.y - orientation[1], subvolume.z)
                            if self.is_supported(item_position, orientation):
                                load_order += 1  # Increment load order
                                item_load_order = load_order  # Assign current load order
                                if item.id in self.unloading_sequence:
                                    item_load_order = self.unloading_sequence[item.id]  # Assign predefined unloading sequence
                                self.packed_items.append((item.id, item_position, orientation, item.location, item_load_order, item.weight))
                                new_subvolumes = self.create_new_subvolumes(subvolume, orientation, item_position)
                                self.sub_volumes.remove(subvolume)
                                for new_subvolume in new_subvolumes:
                                    self.insert_subvolume(new_subvolume)
                                placed = True
                                break
                    if placed:
                        break
                if not placed:
                    print(f"Item {item.id} could not be placed in this iteration.")
                    break
            if len(self.packed_items) > best_packing_count:
                best_packing = list(self.packed_items)
                best_packing_count = len(self.packed_items)

        self.packed_items = best_packing

    def insert_subvolume(self, new_subvolume):
        self.sub_volumes.append(new_subvolume)

    def create_new_subvolumes(self, subvolume, item, item_position):
        new_subvolumes = []
        item_x, item_y, item_z = item_position
        item_width, item_length, item_height = item

        subvolume_x, subvolume_y, subvolume_z = subvolume.position
        subvolume_width, subvolume_length, subvolume_height = subvolume.dimensions

        # Right of the item
        if subvolume_width > item_width:
            new_subvolumes.append(SubVolume(item_x + item_width, subvolume_y, item_z,
                                            subvolume_width - item_width, item_length, item_height))

        # Behind the item (towards the container's opening)
        if item_y > 0:
            new_subvolumes.append(SubVolume(item_x, item_y - item_length, item_z,
                                            item_width, item_y, item_height))

        # Above the item
        if subvolume_height > item_height:
            new_subvolumes.append(SubVolume(item_x, subvolume_y, item_z + item_height,
                                            item_width, item_length, subvolume_height - item_height))

        # Remaining space to the right and above
        if subvolume_width > item_width and subvolume_height > item_height:
            new_subvolumes.append(SubVolume(item_x + item_width, subvolume_y, item_z + item_height,
                                            subvolume_width - item_width, item_length, subvolume_height - item_height))

        # Remaining space behind and above
        if item_y > 0 and subvolume_height > item_height:
            new_subvolumes.append(SubVolume(item_x, item_y - item_length, item_z + item_height,
                                            item_width, item_y, subvolume_height - item_height))

        # Remaining space to the right and behind
        if subvolume_width > item_width and item_y > 0:
            new_subvolumes.append(SubVolume(item_x + item_width, item_y - item_length, item_z,
                                            subvolume_width - item_width, item_y, item_height))

        # Remaining space to the right, behind, and above
        if subvolume_width > item_width and item_y > 0 and subvolume_height > item_height:
            new_subvolumes.append(SubVolume(item_x + item_width, item_y - item_length, item_z + item_height,
                                            subvolume_width - item_width, item_y, subvolume_height - item_height))

        return new_subvolumes

    def is_supported(self, item_position, item_orientation):
        item_x, item_y, item_z = item_position
        item_width, item_length, item_height = item_orientation

        if item_z == 0:
            return True  # Item is on the floor

        # Check if there is a supporting box below
        for packed_item in self.packed_items:
            _, packed_position, packed_orientation, _, _, _ = packed_item
            packed_x, packed_y, packed_z = packed_position
            packed_width, packed_length, packed_height = packed_orientation

            if (packed_x <= item_x < packed_x + packed_width or packed_x < item_x + item_width <= packed_x + packed_width) and \
               (packed_y >= item_y > packed_y - packed_length or packed_y > item_y - item_length >= packed_y - packed_length) and \
               (packed_z + packed_height == item_z):
                return True

        return False

    def reset(self):
        self.sub_volumes = [SubVolume(0, self.length, 0, self.width, self.length, self.height)]
        self.packed_items = []
        
    def calculate_capacity_utilization(self):
        total_container_volume = self.width * self.length * self.height
        packed_volume = 0
        for item in self.packed_items:
            item_volume = item[2][0] * item[2][1] * item[2][2]
            packed_volume += item_volume
            print(f"Item ID: {item[0]}, Volume: {item_volume}, Cumulative Packed Volume: {packed_volume}")
        print(f"Total Container Volume: {total_container_volume}")
        return packed_volume / total_container_volume


def main():
    container = PackingAlgorithm(container_size[0], container_size[1], container_size[2])
    container.pack_items_dbl(items)

    print("Packed Items:")
    for packed_item in container.packed_items:
        print(f"Item ID: {packed_item[0]}, Position: {packed_item[1]}, Orientation: {packed_item[2]}, Location: {packed_item[3]}, Load Order: {packed_item[4]}, Weight: {packed_item[5]}")
 
    # Save packed items to a JSON file
    packed_items_data = [
        {"id": packed_item[0], "position": packed_item[1], "orientation": packed_item[2], "location": packed_item[3], "load_order": packed_item[4], "weight": packed_item[5], "dimensions": (packed_item[2][0], packed_item[2][1], packed_item[2][2])}
        for packed_item in container.packed_items
    ]
    with open('packed_items.json', 'w') as f:
        json.dump(packed_items_data, f, indent=4)

    # Calculate and print the capacity utilization
    capacity_utilization = container.calculate_capacity_utilization()
    print(f"Capacity Utilization: {capacity_utilization:.2%}")

if __name__ == "__main__":
    main()
