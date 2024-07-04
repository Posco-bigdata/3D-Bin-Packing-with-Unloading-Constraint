# container_size: A vector of length 3 describing the size of the container in the x, y, z dimension.
# item_size_set:  A list records the size of each item. The size of each item is also described by a vector of length 3.
import json
import random
import numpy as np
container_size = [170,250,160]
container_size = np.array(container_size) *0.8
 
with open('./generated_boxes.json', 'r') as file:
    data = json.load(file)
