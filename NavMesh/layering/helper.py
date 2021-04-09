import numpy as np
from PIL import Image


def to_voxel_matrix(matrix):

    result = np.zeros(matrix.shape, dtype=bool)

    for x in range(matrix.shape[0]):
        for y in range(matrix.shape[1]):
            for z in range(matrix.shape[2]):

                if matrix[x, y, z] > 0:
                    result[x, y, z] = True

    return result


def is_accessible(sparse_matrix, player_voxel_height, position):

    if sparse_matrix[position] != 1:
        return False

    return is_free(sparse_matrix, player_voxel_height, position)


def is_free(sparse_matrix, player_voxel_height, position):
    return all(sparse_matrix[(position.x, position.y + e, position.z)] == 0 for e in range(1, min(player_voxel_height + 1, sparse_matrix.shape[1] - position.y)))


def is_inside(matrix, position):
    if any(e < 0 for e in position):
        return False

    return position.x < matrix.shape[0] and position.y < matrix.shape[1] and position.z < matrix.shape[2]


def flatten(matrix):

    floor_matrix = np.zeros((matrix.shape[0], matrix.shape[2]), dtype=bool)

    for x in range(0, matrix.shape[0]):
        for z in range(0, matrix.shape[2]):

            if not any(v == True for v in matrix[x, :, z]):
                continue

            floor_matrix[x, z] = True

    return floor_matrix


def matrix_to_image(matrix, color):

    image_data = np.zeros((matrix.shape[0], matrix.shape[1], 3), dtype=np.uint8)

    for x in range(matrix.shape[0]):
        for z in range(matrix.shape[1]):

            if matrix[x, z]:
                image_data[x, matrix.shape[1] - 1 - z] = color

    return Image.fromarray(image_data)
