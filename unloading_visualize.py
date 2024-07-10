import json
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import matplotlib.animation as animation
from main_data import create_scenario

def create_unloading_animation(scenario_number, packing_method, save_gif=False):
    # Get container size from create_scenario function
    container_size, _ = create_scenario(scenario_number)

    # Load packed items from the JSON file based on the chosen method
    if packing_method == 'heuristic':
        items_file = f"./scenario/rearranged_items_scenario_{scenario_number}_original.json"
        operations_file = f"./scenario/unloading_operations_scenario_{scenario_number}_original.json"
    elif packing_method == 'subvolume':
        items_file = f"./scenario/rearranged_items_scenario_{scenario_number}_subvolume.json"
        operations_file = f"./scenario/unloading_operations_scenario_{scenario_number}_subvolume.json"
    elif packing_method == 'bl_ffhdc':
        items_file = f"./scenario/rearranged_items_scenario_{scenario_number}_bl_ffhdc.json"
        operations_file = f"./scenario/unloading_operations_scenario_{scenario_number}_bl_ffhdc.json"
    else:
        raise ValueError("Invalid packing method. Choose 'heuristic', 'subvolume', or 'bl_ffhdc'.")

    with open(items_file, 'r') as f:
        packed_items = json.load(f)

    with open(operations_file, 'r') as f:
        operations = json.load(f)

    # Dictionary to store item positions
    item_positions = {item['id']: item for item in packed_items}

    # Set to keep track of temporarily removed items
    temporarily_removed = set()

    # Define color map for locations
    colors = {
        'po1': (1.0, 0.7, 0.7),  # light red
        'po2': (1.0, 1.0, 0.7),  # light yellow
        'po3': (0.7, 0.7, 1.0),  # light blue
        'po4': (0.7, 1.0, 0.7),  # light green
        'po5': (0.9, 0.7, 0.9)   # light purple
    }

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
        
        op_index = frame
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
        
        ax.set_title(f"{packing_method.capitalize()} Unloading at {current_location}: {current_item['action']} item {current_item['item_id']}")
        
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
                color = colors.get(item['location'], (0.5, 0.5, 0.5))  # Default to gray if location not found
                draw_cuboid(ax, item['position'], item['orientation'], color=color, alpha=0.7)
                text_position = (item['position'][0] + item['orientation'][0] / 2,
                                 item['position'][1] + item['orientation'][1] / 2,
                                 item['position'][2] + item['orientation'][2] / 2)
                ax.text(*text_position, f"{item['id']}", color='black')
            else:
                # Visualize temporarily removed items above the container
                temp_z = container_size[2] + 50  # Place them above the container
                draw_cuboid(ax, (item['position'][0], item['position'][1], temp_z),
                            item['orientation'], color='orange', alpha=0.5)
                text_position = (item['position'][0] + item['orientation'][0] / 2,
                                 item['position'][1] + item['orientation'][1] / 2,
                                 temp_z + item['orientation'][2] / 2)
                ax.text(*text_position, f"{item['id']}", color='black')
        
        return ax,

    # Create the figure and 3D axis
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='3d')

    # Create the animation
    total_frames = sum(len(step['items']) for step in operations)
    anim = animation.FuncAnimation(fig, update, frames=total_frames, init_func=init, blit=False, repeat=False, interval=200)

    if save_gif:
        # Save the animation as a GIF
        writer = animation.PillowWriter(fps=5)
        anim.save(f'{packing_method}_unloading_scenario_{scenario_number}.gif', writer=writer)
        print(f"{packing_method.capitalize()} unloading animation saved as {packing_method}_unloading_scenario_{scenario_number}.gif")
        plt.close(fig)  # Close the figure to free up memory
    else:
        # Display the animation
        plt.show()

# Main execution
scenario_number = int(input("Enter the scenario number: "))
save_option = input("Do you want to save the animations as GIFs? (yes/no): ").lower().strip()
save_gif = save_option in ['yes', 'y', 'true', '1']

# Create animations for all three packing methods
for method in ['heuristic', 'subvolume', 'bl_ffhdc']:
    create_unloading_animation(scenario_number, method, save_gif)