import json
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.animation as animation
from given_data import container_size

# Load the packed items
with open('packed_items.json', 'r') as f:
    packed_items = json.load(f)

# Load the unloading operations
with open('unloading_operations.json', 'r') as f:
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

# Sort packed items by load_order in reverse
packed_items.sort(key=lambda x: x['load_order'], reverse=True)

# Dictionary to store item positions
item_positions = {item['id']: item for item in packed_items}

def get_sorted_operations(operations):
    all_items = []
    for step in operations:
        location_items = [item for item in step['items'] if item['action'] != 'Reload']
        location_items.sort(key=lambda x: x['unload_order'], reverse=True)
        all_items.extend(location_items)
        reloads = [item for item in step['items'] if item['action'] == 'Reload']
        all_items.extend(reloads)
    return all_items

sorted_operations = get_sorted_operations(operations)

# Function to update the plot
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
        current_location = sorted_operations[op_index]['location']
        ax.set_title(f"Unloading at {current_location}")
        
        for i in range(op_index + 1):
            item = sorted_operations[i]
            item_id = item['item_id']
            action = item['action']
            
            if action in ['Unload', 'Temporarily unload']:
                if item_id in item_positions:
                    del item_positions[item_id]
            elif action == 'Reload':
                item_positions[item_id] = next(x for x in packed_items if x['id'] == item_id)
        
        for item in item_positions.values():
            color = location_colors.get(item['location'], 'gray')
            ax.bar3d(item['position'][0], item['position'][1], item['position'][2], 
                     item['orientation'][0], item['orientation'][1], item['orientation'][2], 
                     color=color, alpha=0.8)

    return ax

# Create the animation
total_frames = len(packed_items) + len(sorted_operations)
anim = animation.FuncAnimation(fig, update, frames=total_frames, interval=100, blit=False, repeat=False)

# Show the plot
plt.show()

# Save the animation (optional)
# anim.save('container_packing_and_unloading.mp4', writer='ffmpeg', fps=10)