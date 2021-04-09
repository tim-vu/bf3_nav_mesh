import pickle
from io import BytesIO

from shared.vector import Vec2, Vec3


class SparseLevel:

    def __init__(self, level, voxels, shape, min_chunk, max_chunk):
        self.level = level
        self.voxels = voxels
        self.shape = shape
        self.min_chunk = min_chunk
        self.max_chunk = max_chunk
        self.voxel_unit_size = Vec3(self.level.chunk_unit_width / self.level.chunk_width, self.level.chunk_unit_height / self.level.chunk_voxel_height, self.level.chunk_unit_depth / self.level.chunk_depth)

    @staticmethod
    def from_level(level, center_chunk, distance):

        chunks = [chunk for chunk in level.chunks if
                  max(abs(center_chunk.x - chunk.x), abs(center_chunk.z - chunk.z)) <= distance]

        min_chunk_x = float('inf')
        min_chunk_z = float('inf')
        max_chunk_x = float('-inf')
        max_chunk_z = float('-inf')

        for chunk in chunks:
            min_chunk_x = min(min_chunk_x, chunk.x)
            min_chunk_z = min(min_chunk_z, chunk.z)
            max_chunk_x = max(max_chunk_x, chunk.x)
            max_chunk_z = max(max_chunk_z, chunk.z)

        matrix_chunk_size = Vec2(max_chunk_x - min_chunk_x + 1, max_chunk_z - min_chunk_z + 1)

        voxels = {}

        for chunk in chunks:

            buffer = BytesIO(chunk.data)

            filled_positions = pickle.load(buffer)

            for x, y, z, v in filled_positions:
                abs_x = (level.chunk_width * (chunk.x - min_chunk_x) + x)
                abs_z = (level.chunk_depth * (chunk.z - min_chunk_z) + z)

                voxels[Vec3(abs_x, y, abs_z)] = v

        shape = (matrix_chunk_size.x * level.chunk_width, level.chunk_voxel_height, matrix_chunk_size.z * level.chunk_depth)

        return SparseLevel(level, voxels, shape, Vec2(min_chunk_x, min_chunk_z), Vec2(max_chunk_x, max_chunk_z))

    def validate_index(self, v, axis):

        if not isinstance(v, int):
            raise TypeError('index for axis %d must be an integer' % axis)

        if v < 0 or v >= self.shape[axis]:
            raise ValueError('index %d for axis %d is out of range' % (v, axis))

    def __getitem__(self, key):

        if not isinstance(key, tuple) or len(key) != 3:
            raise TypeError('item is not a valid index')

        self.validate_index(key[0], 0)
        self.validate_index(key[1], 1)
        self.validate_index(key[2], 2)

        key = Vec3(key[0], key[1], key[2])

        value = self.voxels.get(key)

        if not value:
            return 0

        return value

    def __setitem__(self, key, value):

        if not isinstance(key, tuple) or len(key) != 3:
            raise TypeError('item is is a valid index')

        self.validate_index(key[0], 0)
        self.validate_index(key[1], 1)
        self.validate_index(key[2], 2)

        key = Vec3(key[0], key[1], key[2])

        self.voxels[key] = value
        return value

    def position_to_indices(self, position: Vec3):

        offset = position - Vec3(self.min_chunk.x * self.level.chunk_unit_width, self.level.chunk_unit_height_offset, self.min_chunk.z * self.level.chunk_unit_depth)

        return Vec3(int(offset.x // self.voxel_unit_size.x), int(offset.y // self.voxel_unit_size.y), int(offset.z // self.voxel_unit_size.z))
