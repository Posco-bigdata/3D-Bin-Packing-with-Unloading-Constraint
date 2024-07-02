from given_data import container_size
import json
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from matplotlib.animation import FuncAnimation

class Item:
    def __init__(self, id, width, length, height, weight, location, position):
        self.id = id
        self.width = width
        self.length = length
        self.height = height
        self.weight = weight
        self.orientation = (width, length, height)
        self.location = location
        self.position = position

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

def load_packed_items(file_path):
    with open(file_path, 'r') as f:
        packed_items_data = json.load(f)
    packed_items = []
    for item in packed_items_data:
        position = tuple(item['position'])
        packed_items.append(Item(int(item['id']), item['dimensions'][0], item['dimensions'][1], item['dimensions'][2], item['weight'], item['location'], position))
    return packed_items

def draw_cube(ax, position, orientation, color='blue'):
    x, y, z = position
    dx, dy, dz = orientation
    vertices = [
        [x, y, z], [x + dx, y, z], [x + dx, y + dy, z], [x, y + dy, z],
        [x, y, z + dz], [x + dx, y, z + dz], [x + dx, y + dy, z + dz], [x, y + dy, z + dz]
    ]
    faces = [
        [vertices[j] for j in [0, 1, 2, 3]],
        [vertices[j] for j in [4, 5, 6, 7]],
        [vertices[j] for j in [0, 3, 7, 4]],
        [vertices[j] for j in [1, 2, 6, 5]],
        [vertices[j] for j in [0, 1, 5, 4]],
        [vertices[j] for j in [2, 3, 7, 6]]
    ]
    poly3d = Poly3DCollection(faces, facecolors=color, linewidths=1, edgecolors='r', alpha=.25)
    ax.add_collection3d(poly3d)
    return poly3d

def visualize_unloading(packed_items, delivery_locations):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    container_width, container_length, container_height = container_size
    ax.set_xlim(0, container_width)
    ax.set_ylim(0, container_length)
    ax.set_zlim(0, container_height)
    unloaded_items = set()
    patches_list = []
    temporary_storage = []
    operations_count = 0

    # Draw all items initially
    for item in packed_items:
        patch = draw_cube(ax, item.position, item.orientation)
        patches_list.append((item, patch))

    def update(frame):
        nonlocal unloaded_items, patches_list, temporary_storage, operations_count
        ax.cla()
        ax.set_xlim(0, container_width)
        ax.set_ylim(0, container_length)
        ax.set_zlim(0, container_height)

        if frame < len(delivery_locations):
            current_location = delivery_locations[frame]

            # Unload all items for the current location
            items_to_unload = [item for item in packed_items if item.location == current_location and item.id not in unloaded_items]

            # Sort by y, x, z for proper unloading
            items_to_unload.sort(key=lambda x: (x.position[1], x.position[0], x.position[2]))

            for item in items_to_unload:
                unloaded_items.add(item.id)
                operations_count += 1  # Increment operation count for unloading

            # Move non-delivery items to temporary storage
            temp_items = [item for item in packed_items if item.location != current_location and item.id not in unloaded_items]
            for item in temp_items:
                temporary_storage.append(item)
                operations_count += 1  # Increment operation count for temporary unloading

            # Re-load temporary storage items, considering the next delivery locations
            for item in temporary_storage:
                draw_cube(ax, item.position, item.orientation, color='green')
                operations_count += 1  # Increment operation count for reloading

            temporary_storage.clear()

        # Draw the remaining items
        patches_list = [(item, patch) for item, patch in patches_list if item.id not in unloaded_items]

        for item, patch in patches_list:
            draw_cube(ax, item.position, item.orientation)

        ax.text2D(0.05, 0.95, f"Operations: {operations_count}", transform=ax.transAxes)

        return []

    ani = FuncAnimation(fig, update, frames=len(delivery_locations) + 1, blit=False, repeat=False)
    plt.show()

def main():
    packed_items = load_packed_items('packed_items.json')
    delivery_locations = sorted(set(item.location for item in packed_items))  # Define the sequence of delivery points
    visualize_unloading(packed_items, delivery_locations)

if __name__ == "__main__":
    main()
