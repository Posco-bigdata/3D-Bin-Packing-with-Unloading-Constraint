import json
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import matplotlib.animation as animation
from main_data import create_scenario

# Get user input for scenario number and packing method
scenario_number = int(input("Enter the scenario number: "))
packing_method = input("Choose packing method (heuristic/subvolume): ").lower()

# Get container size from create_scenario function
container_size, _ = create_scenario(scenario_number)

# Load packed items from the JSON file based on the chosen method
if packing_method == 'heuristic':
    file_path = f"./scenario/packed_items_scenario_{scenario_number}_original.json"
elif packing_method == 'subvolume':
    file_path = f"./scenario/subvolume_packed_items_scenario_{scenario_number}.json"
else:
    raise ValueError("Invalid packing method. Choose 'heuristic' or 'subvolume'.")

with open(file_path, 'r') as f:
    packed_items = json.load(f)

# Sort packed items by Load Order
packed_items.sort(key=lambda x: x['load_order'])

# Define color map for locations
colors = {
    'po1': (1.0, 0.7, 0.7),  # light red
    'po2': (1.0, 1.0, 0.7),  # light yellow
    'po3': (0.7, 0.7, 1.0),  # light blue
    'po4': (0.7, 1.0, 0.7),  # light green
    'po5': (0.9, 0.7, 0.9)   # light purple
}

# Function to draw a cuboid
def draw_cuboid(ax, position, size, color='blue', alpha=0.3):
    x, y, z = position
    dx, dy, dz = size

    cuboid = [
        [x, y, z],
        [x + dx, y, z],
        [x + dx, y + dy, z],
        [x, y + dy, z],
        [x, y, z + dz],
        [x + dx, y, z + dz],
        [x + dx, y + dy, z + dz],
        [x, y + dy, z + dz]
    ]

    edges = [
        [cuboid[0], cuboid[1], cuboid[2], cuboid[3]],
        [cuboid[4], cuboid[5], cuboid[6], cuboid[7]],
        [cuboid[0], cuboid[1], cuboid[5], cuboid[4]],
        [cuboid[2], cuboid[3], cuboid[7], cuboid[6]],
        [cuboid[1], cuboid[2], cuboid[6], cuboid[5]],
        [cuboid[4], cuboid[7], cuboid[3], cuboid[0]]
    ]

    faces = Poly3DCollection(edges, linewidths=1, edgecolors='black')
    faces.set_facecolor(color)
    faces.set_alpha(alpha)
    ax.add_collection3d(faces)

def init():
    ax.clear()
    # Draw container
    draw_cuboid(ax, (0, 0, 0), container_size, color='gray', alpha=0.1)
    
    # Set plot labels and limits
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    ax.set_xlim([0, container_size[0]])
    ax.set_ylim([0, container_size[1]])
    ax.set_zlim([0, container_size[2]])
    
    # Create a legend
    handles = [plt.Line2D([0], [0], color=colors[loc], lw=4) for loc in colors.keys()]
    ax.legend(handles, colors.keys())
    
    return ax,

def update(frame):
    ax.clear()
    init()
    
    # Draw packed items up to the current frame
    for item in packed_items[:frame+1]:
        position = item['position']
        size = item['orientation']
        location = item['location']
        color = colors.get(location, (0.5, 0.5, 0.5))  # Default to gray if location not found
        draw_cuboid(ax, position, size, color=color, alpha=0.7)
        # Adjust the text position slightly to avoid overlap with the cuboid
        text_position = (position[0] + size[0] / 2, position[1] + size[1] / 2, position[2] + size[2] / 2)
        ax.text(*text_position, f"{item['id']}", color='black')
    
    ax.set_title(f"{packing_method.capitalize()} Packing - Loading Step: {frame+1}")
    return ax,

# Create the figure and 3D axis
fig = plt.figure(figsize=(10, 8))
ax = fig.add_subplot(111, projection='3d')

# Create the animation with a shorter interval between frames
anim = animation.FuncAnimation(fig, update, frames=len(packed_items), init_func=init, blit=False, repeat=False, interval=200)

# Display the animation
plt.show()