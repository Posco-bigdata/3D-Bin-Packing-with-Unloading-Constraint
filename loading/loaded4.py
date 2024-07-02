import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import numpy as np
import matplotlib.animation as animation


# 적재될 컨테이너의 크기
container_size = ()

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

# 라벨을 기준으로 정렬한 후, 각 라벨 내에서 부피와 무게를 기준으로 정렬
sorted_box_specs = sorted(box_specs, key=lambda x: (x[5], -x[0]*x[1]*x[2], -x[3]))

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

def count_adjacent_faces(container, position, size):
    x, y, z = position
    dx, dy, dz = size
    faces = 0
    if x > 0 and np.all(container[x-1:x, y:y+dy, z:z+dz] == 1):
        faces += dy * dz
    if x + dx < container.shape[0] and np.all(container[x+dx:x+dx+1, y:y+dy, z:z+dz] == 1):
        faces += dy * dz
    if y > 0 and np.all(container[x:x+dx, y-1:y, z:z+dz] == 1):
        faces += dx * dz
    if y + dy < container.shape[1] and np.all(container[x:x+dx, y+dy:y+dy+1, z:z+dz] == 1):
        faces += dx * dz
    if z > 0 and np.all(container[x:x+dx, y:y+dy, z-1:z] == 1):
        faces += dx * dy
    if z + dz < container.shape[2] and np.all(container[x:x+dx, y:y+dy, z+dz:z+dz+1] == 1):
        faces += dx * dy
    return faces

def find_best_fit(container, size):
    best_position = None
    best_rotation = None
    max_adjacent_faces = -1

    for rotation in range(6):
        rotated_size = rotate_size(size, rotation)
        for y in range(container.shape[1]):
            for x in range(container.shape[0]):
                for z in range(container.shape[2]):
                    position = np.array([x, y, z])
                    if can_place(container, position, rotated_size):
                        adjacent_faces = count_adjacent_faces(container, position, rotated_size)
                        if adjacent_faces > max_adjacent_faces:
                            best_position = position
                            best_rotation = rotation
                            max_adjacent_faces = adjacent_faces

    return best_position, best_rotation

for spec in sorted_box_specs:
    size = spec[:3]
    count = spec[4]
    label = spec[5]
    
    for _ in range(count):
        placed = False
        best_position, best_rotation = find_best_fit(container, size)
        if best_position is not None and best_rotation is not None:
            rotated_size = rotate_size(size, best_rotation)
            boxes_to_load.append((best_position, rotated_size, label))
            place_box(container, best_position, rotated_size)
            occupied_volume += np.prod(rotated_size)
            placed = True
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
