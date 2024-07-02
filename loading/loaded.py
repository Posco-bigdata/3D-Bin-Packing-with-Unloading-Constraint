import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import numpy as np
import matplotlib.animation as animation

# 박스의 규격 (가로, 세로, 높이)와 개수, 라벨
box_specs = [
    (1, 1, 1, 10, 'A'),
    (2, 1, 1, 10, 'B'),
    (1, 2, 1, 10, 'C'),
    (1, 1, 2, 5, 'A'),
    (2, 2, 1, 5, 'B'),
    (2, 1, 2, 5, 'C'),
    (1, 2, 2, 5, 'A')
]

# 적재될 컨테이너의 크기
container_size = (6,6,6)

# 라벨에 따른 색상
label_colors = {
    'A': 'cyan',
    'B': 'magenta',
    'C': 'yellow'
}

def create_box(origin, size):
    x, y, z = origin
    dx, dy, dz = size
    return [
        [(x, y, z), (x + dx, y, z), (x + dx, y + dy, z), (x, y + dy, z)],
        [(x, y, z), (x, y, z + dz), (x, y + dy, z + dz), (x, y + dy, z)],
        [(x, y, z), (x + dx, y, z), (x + dx, y, z + dz), (x, y, z + dz)],
        [(x + dx, y, z), (x + dx, y + dy, z), (x + dx, y + dy, z + dz), (x + dx, y, z + dz)],
        [(x, y + dy, z), (x + dx, y + dy, z), (x + dx, y + dy, z + dz), (x, y + dy, z + dz)],
        [(x, y, z + dz), (x + dx, y, z + dz), (x + dx, y + dy, z + dz), (x, y + dy, z + dz)]
    ]

# 라벨을 기준으로 정렬
sorted_box_specs = sorted(box_specs, key=lambda x: x[4])

# 적재될 박스들의 위치와 크기 리스트
boxes_to_load = []

# 박스를 적재하기 위한 초기 좌표
current_position = np.array([0, 0, 0])

for spec in sorted_box_specs:
    size = spec[:3]
    count = spec[3]
    label = spec[4]
    
    for _ in range(count):
        if (current_position[0] + size[0] <= container_size[0] and
            current_position[1] + size[1] <= container_size[1] and
            current_position[2] + size[2] <= container_size[2]):
            
            boxes_to_load.append((current_position.copy(), size, label))
            
            current_position[0] += size[0]
            
            if current_position[0] + size[0] > container_size[0]:
                current_position[0] = 0
                current_position[1] += size[1]
                
                if current_position[1] + size[1] > container_size[1]:
                    current_position[1] = 0
                    current_position[2] += size[2]

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')
ax.set_xlim(0, container_size[0])
ax.set_ylim(0, container_size[1])
ax.set_zlim(0, container_size[2])

def update_box(num):
    ax.cla()  # Clear the previous boxes
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    ax.set_xlim(0, container_size[0])
    ax.set_ylim(0, container_size[1])
    ax.set_zlim(0, container_size[2])
    
    for i in range(num + 1):
        position, size, label = boxes_to_load[i]
        box = create_box(position, size)
        ax.add_collection3d(Poly3DCollection(box, facecolors=label_colors[label], linewidths=1, edgecolors='r', alpha=.5))

ani = animation.FuncAnimation(fig, update_box, frames=len(boxes_to_load), interval=500, repeat=False)

plt.show()
