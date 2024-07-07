import json
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.animation as animation
from main_data import container_size

# Load the packed items
scenario_number = int(input("Enter the scenario number: "))
with open(f'./scenario/rearranged_items_scenario_{scenario_number}.json', 'r') as f:
    packed_items = json.load(f)

# Load the unloading operations
with open(f'./scenario/unloading_operations_scenario_{scenario_number}.json', 'r') as f:
    operations = json.load(f)

# Create a figure and 3D axis
fig = plt.figure(figsize=(12, 8))
ax = fig.add_subplot(111, projection='3d')

# Set the axis limits
ax.set_xlim(0, container_size[0])
ax.set_ylim(0, container_size[1])
ax.set_zlim(0, container_size[2])

# Set labels
ax.set_xlabel('Width')
ax.set_ylabel('Length')
ax.set_zlabel('Height')

# Colors for different locations
location_colors = {'po1': 'red', 'po2': 'blue', 'po3': 'green', 'po4': 'yellow', 'po5': 'purple'}

# Dictionary to store item positions
item_positions = {item['id']: item for item in packed_items}

# Set to keep track of temporarily removed items
temporarily_removed = set()

def update(frame):
    ax.clear()
    ax.set_xlim(0, container_size[0])
    ax.set_ylim(0, container_size[1])
    ax.set_zlim(0, container_size[2])
    ax.set_xlabel('Width')
    ax.set_ylabel('Length')
    ax.set_zlabel('Height')
    
    if frame < len(packed_items):
        # Initial packing visualization
        for i in range(frame + 1):
            item = packed_items[i]
            color = location_colors.get(item['location'], 'gray')
            ax.bar3d(item['position'][0], item['position'][1], item['position'][2],
                     item['orientation'][0], item['orientation'][1], item['orientation'][2],
                     color=color, alpha=0.8)
        ax.set_title(f"Packing items: {frame + 1}/{len(packed_items)}")
    else:
        # Unloading visualization
        op_index = frame - len(packed_items)
        step_index = 0
        item_index = 0
        for i, step in enumerate(operations):
            if op_index < len(step['items']):
                step_index = i
                item_index = op_index
                break
            op_index -= len(step['items'])
        
        current_step = operations[step_index]
        current_location = current_step['step'].split(': ')[1]
        current_item = current_step['items'][item_index]
        
        ax.set_title(f"Unloading at {current_location}: {current_item['action']} item {current_item['item_id']}")
        
        if current_item['action'] in ['Unload', 'Unload blocking item']:
            if current_item['item_id'] in item_positions:
                del item_positions[current_item['item_id']]
        elif current_item['action'] == 'Temporarily unload blocking item':
            temporarily_removed.add(current_item['item_id'])
        elif current_item['action'] == 'Reload temporarily unloaded item':
            if current_item['item_id'] in temporarily_removed:
                temporarily_removed.remove(current_item['item_id'])
        
        for item_id, item in item_positions.items():
            if item_id not in temporarily_removed:
                color = location_colors.get(item['location'], 'gray')
                ax.bar3d(item['position'][0], item['position'][1], item['position'][2],
                         item['orientation'][0], item['orientation'][1], item['orientation'][2],
                         color=color, alpha=0.8)
            else:
                # Visualize temporarily removed items above the container
                temp_z = container_size[2] + 50  # Place them above the container
                ax.bar3d(item['position'][0], item['position'][1], temp_z,
                         item['orientation'][0], item['orientation'][1], item['orientation'][2],
                         color='orange', alpha=0.5)  # Use a distinct color for temporarily removed items
    
    return ax

# Create the animation
total_frames = len(packed_items) + sum(len(step['items']) for step in operations)
anim = animation.FuncAnimation(fig, update, frames=total_frames, interval=100, blit=False, repeat=False)

# Show the plot
plt.show()

# Save the animation (optional)
# anim.save('container_packing_and_unloading.mp4', writer='ffmpeg', fps=10)