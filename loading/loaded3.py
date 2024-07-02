import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import numpy as np
import matplotlib.animation as animation

# 박스의 규격 (가로, 세로, 높이)와 개수, 라벨
box_specs = [
    (1, 1, 1, 20, 'A'),
    (2, 1, 1, 10, 'B'),
    (1, 2, 1, 10, 'C'),
    (1, 1, 2, 10, 'A'),
    (2, 2, 1, 10, 'B'),
    (2, 1, 2, 10, 'C')
]

# 적재될 컨테이너의 크기
container_size = (6, 6, 6)

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

def rotate_size(size, rotation):
    dx, dy, dz = size
    if rotation == 0:
        return dx, dy, dz
    elif rotation == 1:
        return dx, dz, dy
    elif rotation == 2:
        return dy, dx, dz
    elif rotation == 3:
        return dy, dz, dx
    elif rotation == 4:
        return dz, dx, dy
    elif rotation == 5:
        return dz, dy, dx

# 라벨을 기준으로 정렬한 후, 각 라벨 내에서 부피를 기준으로 내림차순 정렬
sorted_box_specs = sorted(box_specs, key=lambda x: (x[4], -x[0]*x[1]*x[2]))

# 적재될 박스들의 위치와 크기 리스트
boxes_to_load = []

# 컨테이너를 3D 배열로 초기화 (0: 빈 공간, 1: 차지한 공간)
container = np.zeros(container_size)

# 빈 공간 계산을 위한 변수
occupied_volume = 0

def can_place(container, position, size):
    x, y, z = position
    dx, dy, dz = size
    if x + dx > container.shape[0] or y + dy > container.shape[1] or z + dz > container.shape[2]:
        return False
    return np.all(container[x:x+dx, y:y+dy, z:z+dz] == 0)

def place_box(container, position, size):
    x, y, z = position
    dx, dy, dz = size
    container[x:x+dx, y:y+dy, z:z+dz] = 1

def find_position_for_box(container, size):
    for y in range(container.shape[1]):
        for x in range(container.shape[0]):
            for z in range(container.shape[2]):
                position = np.array([x, y, z])
                if can_place(container, position, size):
                    return position
    return None

for spec in sorted_box_specs:
    size = spec[:3]
    count = spec[3]
    label = spec[4]
    
    for _ in range(count):
        placed = False
        for rotation in range(6):
            rotated_size = rotate_size(size, rotation)
            position = find_position_for_box(container, rotated_size)
            if position is not None:
                boxes_to_load.append((position, rotated_size, label))
                place_box(container, position, rotated_size)
                occupied_volume += np.prod(rotated_size)
                placed = True
                break
        if not placed:
            print(f"Could not place box {size} with label {label}")

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

ani = animation.FuncAnimation(fig, update_box, frames=len(boxes_to_load), interval=200, repeat=False)

plt.show()

# 빈 공간 계산
total_volume = np.prod(container_size)
empty_volume = total_volume - occupied_volume
empty_percentage = (empty_volume / total_volume) * 100

print(f"빈 공간 비율: {empty_percentage:.2f}%")
