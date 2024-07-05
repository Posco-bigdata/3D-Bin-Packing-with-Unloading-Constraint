import json
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import random
import matplotlib.animation as animation

# Load container size from given_data.py
from given_data import container_size

# Load packed items from the JSON file
scenario_number = int(input("Enter the scenario number: "))
with open(f"./scenario/packed_items_scenario_{scenario_number}.json", 'r') as f:
    packed_items = json.load(f)

# Sort packed items by Load Order
packed_items.sort(key=lambda x: x['load_order'])

# Generate random colors for each location
locations = list(set(item['location'] for item in packed_items))
random_colors = {location: [random.random(), random.random(), random.random()] for location in locations}

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
    handles = [plt.Line2D([0], [0], color=random_colors[loc], lw=4) for loc in locations]
    ax.legend(handles, locations)
    
    return ax,

def update(frame):
    ax.clear()
    init()
    
    # Draw packed items up to the current frame
    for item in packed_items[:frame+1]:
        position = item['position']
        size = item['orientation']
        location = item['location']
        color = random_colors[location]
        draw_cuboid(ax, position, size, color=color, alpha=0.7)
        ax.text(position[0], position[1], position[2], f"{item['id']}", color='black')
    
    ax.set_title(f"Loading Step: {frame+1}")
    return ax, 

# Create the figure and 3D axis
fig = plt.figure(figsize=(10, 8))
ax = fig.add_subplot(111, projection='3d')

# Create the animation with a 1-second interval between frames
anim = animation.FuncAnimation(fig, update, frames=len(packed_items), init_func=init, blit=False, repeat=False, interval=100)

# Save the animation as a GIF file 
anim.save('packing_animation.gif', writer='pillow', fps=1)

# Display the animation
plt.show()
