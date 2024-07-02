import pybullet as p
import pybullet_data
import json
import time
import numpy as np
import random

# Load packed items from the JSON file
with open('packed_items.json', 'r') as f:
    packed_items = json.load(f)

# Sort items by load order in descending order (reverse of loading order)
packed_items.sort(key=lambda x: x['load_order'], reverse=True)

# Scaling factor
scaling_factor = 0.6

# Apply scaling to the container size
container_size = [170, 275, 160]
container_size = np.array(container_size) * scaling_factor

# Initialize PyBullet
p.connect(p.GUI)
p.setAdditionalSearchPath(pybullet_data.getDataPath())

# Create the container
container = p.createCollisionShape(p.GEOM_BOX, halfExtents=container_size / 2)
container_visual = p.createVisualShape(p.GEOM_BOX, halfExtents=container_size / 2, rgbaColor=[1, 1, 1, 0.1])
p.createMultiBody(baseMass=0, baseCollisionShapeIndex=container, baseVisualShapeIndex=container_visual, basePosition=container_size / 2)

# Function to add a box to the simulation
def add_box(position, size, weight, color):
    collision_shape = p.createCollisionShape(p.GEOM_BOX, halfExtents=size / 2)
    visual_shape = p.createVisualShape(p.GEOM_BOX, halfExtents=size / 2, rgbaColor=color)
    box_id = p.createMultiBody(baseMass=weight, baseCollisionShapeIndex=collision_shape, baseVisualShapeIndex=visual_shape, basePosition=position)
    return box_id

# Function to remove a box from the simulation
def remove_box(box_id):
    p.removeBody(box_id)

# Add the packed items to the simulation
box_ids = []
for item in packed_items:
    # Apply scaling to the item dimensions and position
    position = (np.array(item['position']) + np.array(item['dimensions']) / 2) * scaling_factor
    size = np.array(item['dimensions']) * scaling_factor
    weight = item['weight']  # Get the weight of the item
    color = [random.random(), random.random(), random.random(), 1]  # Assign a random color
    
    # Check if the box is within the container bounds
    if np.all(position + size / 2 <= container_size) and np.all(position - size / 2 >= 0):
        box_id = add_box(position, size, weight, color)
        box_ids.append(box_id)
    else:
        print(f"Box {item['load_order']} is out of container bounds and won't be added.")

# Set camera parameters
camera_target_position = container_size / 2
camera_distance = max(container_size) * 1.5
camera_yaw = 45
camera_pitch = -30

p.resetDebugVisualizerCamera(cameraDistance=camera_distance,
                             cameraYaw=camera_yaw,
                             cameraPitch=camera_pitch,
                             cameraTargetPosition=camera_target_position)

# Run the simulation
p.setGravity(0, 0, -9.81)

# Simulate the environment for a few seconds before unloading
for _ in range(240):
    p.stepSimulation()
    time.sleep(1./240.)

# Unload the items in reverse order
for box_id in reversed(box_ids):
    remove_box(box_id)
    # Simulate the environment for a short time after each removal
    for _ in range(60):
        p.stepSimulation()
        time.sleep(1./240.)

# Keep the simulation window open
input("Press Enter to exit...")

# Disconnect from the simulation
p.disconnect()
