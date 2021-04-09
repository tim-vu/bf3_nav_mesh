import math
import re
import sys
from collections import OrderedDict

import numpy as np
import randomcolor
from simple_3dviz import Mesh
from simple_3dviz.window import show

from api.models.database import SessionLocal
from api.models.level import Level
from layering.helper import is_accessible, is_inside
from shared.vector import Vec2, Vec3
from layering.sparselevel import SparseLevel

LEVEL_ID = 2
CENTER_CHUNK = Vec2(-50, 44)
SEED_POSITION = Vec3(-344.275391, 69.154152, 309.750977)
CHUNK_DISTANCE = 10

PLAYER_RADIUS = 0.35
PLAYER_HEIGHT = 1.8

session = SessionLocal()

level = session.query(Level).get(LEVEL_ID)

if not Level:
    print('A level with the given id does not exist, exiting...')
    sys.exit(-1)

voxel_unit_size = Vec3(level.chunk_unit_width / level.chunk_width, level.chunk_unit_height / level.chunk_voxel_height, level.chunk_unit_depth / level.chunk_depth)
player_voxel_size = Vec3(1, math.ceil(PLAYER_HEIGHT / voxel_unit_size.y), 1)


level_matrix = SparseLevel.from_level(level, CENTER_CHUNK, CHUNK_DISTANCE)

label_matrix = SparseLevel(level, dict(), level_matrix.shape, level_matrix.min_chunk, level_matrix.max_chunk)


def visualize_layers(reachable_layers):

    layers = {}

    for (x, y, z), label in label_matrix.voxels.items():

        pos = Vec3(x, y, z)

        if label == 0 or label not in reachable_layers:
            continue

        if label in layers:
            layers[label][pos] = True
            continue

        layers[label] = np.zeros(label_matrix.shape, dtype=bool)
        layers[label][pos] = True

    color_gen = randomcolor.RandomColor()
    colors = color_gen.generate(count=len(layers), format_='rgb')

    for i in range(len(colors)):
        values = map(lambda e: int(e), re.findall('\\d+', colors[i]))
        values = list(values)
        colors[i] = (values[0] / 255, values[1] / 255, values[2] / 255)

    meshes = []

    i = 0
    for label in layers:
        color = colors[i]
        meshes.append(Mesh.from_voxel_grid(layers[label], colors=color))
        i += 1

    show(meshes)


queue = OrderedDict()

for (x, y, z), v in level_matrix.voxels.items():

    pos = Vec3(x, y, z)

    if not is_accessible(level_matrix, player_voxel_size.y, pos):
        continue

    label_matrix[pos] = -1
    queue[pos] = None

next_label = 1

NEIGHBOUR_DIRECTIONS = [
    Vec3(1, 0, 0),
    Vec3(-1, 0, 0),
    Vec3(0, 0, 1),
    Vec3(0, 0, -1)
]

DOWN = Vec3(0, -1, 0)
UP = Vec3(0, 1, 0)

connected_layers = set()

while len(queue) > 0:

    current_pos, _ = queue.popitem(False)

    if label_matrix[current_pos] == -1:

        current_label = next_label
        next_label += 1
    else:
        current_label = label_matrix[current_pos]

    label_matrix[current_pos] = current_label

    neighbours = set()

    for direction in NEIGHBOUR_DIRECTIONS:

        new_pos = current_pos + direction

        if not is_inside(level_matrix, new_pos):
            continue

        if level_matrix[new_pos] == 1:
            neighbours.add(new_pos)
            continue

        step_pos = new_pos

        while level_matrix[step_pos + UP] == 1:
            step_pos = step_pos + UP

        if step_pos != new_pos and is_accessible(level_matrix, player_voxel_size.y, step_pos):
            neighbours.add(step_pos)
            continue

        if level_matrix[new_pos] != 0:
            continue

        step_pos = new_pos

        while is_inside(level_matrix, step_pos + DOWN) and level_matrix[step_pos + DOWN] == 0 and level_matrix[current_pos.x, step_pos.y, current_pos.z] == 1:
            step_pos = step_pos + DOWN

        down_pos = step_pos + DOWN

        if is_inside(level_matrix, down_pos) and is_accessible(level_matrix, player_voxel_size.y, down_pos):
            neighbours.add(down_pos)

    for neighbour in neighbours:

        if label_matrix[neighbour] == -1:

            if all([label_matrix[neighbour.x, e, neighbour.z] != current_label for e in range(neighbour.y)]):
                label_matrix[neighbour] = current_label

                if neighbour in queue:
                    queue.move_to_end(neighbour, False)

            continue

        neighbour_label = label_matrix[neighbour]

        if neighbour_label != current_label:

            connected_layers.add((min(neighbour_label, current_label), max(neighbour_label, current_label)))

            continue

seed_indices = level_matrix.position_to_indices(SEED_POSITION)
# seed_indices = Vec3(0, 0, 0)

layer = label_matrix[seed_indices]

if layer == 0:
    sys.exit('The seed position is not part of a layer')

reachable_layers = set()
layer_queue = [layer]


while len(layer_queue) > 0:

    current_layer = layer_queue.pop(0)
    reachable_layers.add(current_layer)

    for sl, el in connected_layers:

        if sl == current_layer:
            layer_queue.append(el)

visualize_layers(set(reachable_layers))



