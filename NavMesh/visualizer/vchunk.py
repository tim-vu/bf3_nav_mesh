from io import BytesIO
import pickle

from panda3d.core import GeomVertexData, GeomVertexWriter, GeomNode, LVector4
from panda3d.core import LVector3, GeomTriangles, Geom, GeomVertexFormat


class CubeFace:

    def __init__(self, offsets, normal):
        self.offsets = offsets
        self.normal = normal


class CubeFaces:
    FRONT = CubeFace([LVector3(0, 0, 0), LVector3(1, 0, 0), LVector3(1, 0, 1), LVector3(0, 0, 1)],
                     LVector3(0, -1, 0))
    BACK = CubeFace(
        [LVector3(0, 1, 0), LVector3(0, 1, 1), LVector3(1, 1, 1),
         LVector3(
             1, 1, 0)], LVector3(0, 1, 0))
    TOP = CubeFace([LVector3(0, 0, 1), LVector3(1, 0, 1), LVector3(1, 1, 1),
                    LVector3(0, 1, 1)], LVector3(0, 0, 1))
    BOTTOM = CubeFace([LVector3(0, 0, 0), LVector3(0, 1, 0), LVector3(1, 1, 0), LVector3(1, 0, 0)],
                      LVector3(0, 0, 1))
    LEFT = CubeFace([LVector3(0, 0, 0), LVector3(0, 0, 1), LVector3(0, 1, 1), LVector3(0, 1, 0)],
                    LVector3(0, 0, 1))
    RIGHT = CubeFace([LVector3(1, 0, 0), LVector3(1, 1, 0), LVector3(1, 1, 1),
                      LVector3(1, 0, 1)], LVector3(1, 0, 0))


class VChunkGeom:

    def __init__(self, voxel_unit_size):

        self.voxel_unit_size = voxel_unit_size
        self.triangles = GeomTriangles(Geom.UHStatic)

        self.format = GeomVertexFormat.getV3n3c4()
        self.v_data = GeomVertexData('square', self.format, Geom.UHStatic)

        self.vertex = GeomVertexWriter(self.v_data, 'vertex')
        self.normal = GeomVertexWriter(self.v_data, 'normal')
        self.color = GeomVertexWriter(self.v_data, 'color')

    def add_face(self, face, cube_x, cube_y, cube_z, color: LVector4):

        start_index = self.vertex.getWriteRow()

        vector = LVector3(cube_x * self.voxel_unit_size.x, cube_y * self.voxel_unit_size.z, cube_z * self.voxel_unit_size.y)

        for offset in face.offsets:

            scaled_offset = LVector3(self.voxel_unit_size.x * offset[0], self.voxel_unit_size.z * offset[1], self.voxel_unit_size.y * offset[2])

            self.vertex.addData3(vector + scaled_offset)
            self.normal.addData3(face.normal)
            self.color.addData4(color)

        self.add_triangles(start_index)

    def add_triangles(self, start_index):
        self.triangles.addVertices(start_index, start_index + 1, start_index + 2)
        self.triangles.closePrimitive()
        self.triangles.addVertices(start_index, start_index + 2, start_index + 3)
        self.triangles.closePrimitive()

    def get_geom(self):
        geom = Geom(self.v_data)
        geom.addPrimitive(self.triangles)

        return geom


class VChunk:

    def __init__(self, chunk_size, voxel_unit_size, chunk):
        self.chunk_size = chunk_size
        self.voxel_unit_size = voxel_unit_size
        self.chunk = chunk

        self.visible = False

        self.geom = None

        self.chunkNode = None

        self.load_chunk_data()

    @staticmethod
    def is_position_filled(position, data):

        return (position[0], position[1], position[2], 1) in data or (position[0], position[1], position[2], 1) in data

    def load_chunk_data(self):

        chunk_geom = VChunkGeom(self.voxel_unit_size)

        buffer = BytesIO(self.chunk.data)

        data = pickle.load(buffer)

        for x, y, z, v in data:

            color = LVector4(0, 255, 0, 1) if v == 1 else LVector4(255, 0, 0, 1)

            # Right
            if x == self.chunk_size.x - 1 or not VChunk.is_position_filled((x + 1, y, z), data):
                chunk_geom.add_face(CubeFaces.RIGHT, x, z, y, color)

            # Left
            if x == 0 or (x - 1, y, z) not in data:
                chunk_geom.add_face(CubeFaces.LEFT, x, z, y, color)

            # Top
            if y == self.chunk_size.y - 1 or not VChunk.is_position_filled((x, y + 1, z), data):
                chunk_geom.add_face(CubeFaces.TOP, x, z, y, color)

            # Bottom
            if y == 0 or not VChunk.is_position_filled((x, y - 1, z), data):
                chunk_geom.add_face(CubeFaces.BOTTOM, x, z, y, color)

            # Front
            if z == 0 or not VChunk.is_position_filled((x, y, z - 1), data):
                chunk_geom.add_face(CubeFaces.FRONT, x, z, y, color)

            # Back
            if z == self.chunk_size.z - 1 or not VChunk.is_position_filled((x, y, z + 1), data):
                chunk_geom.add_face(CubeFaces.BACK, x, z, y, color)

        self.geom = chunk_geom.get_geom()

    def show(self, app):

        if self.visible:
            return

        node = GeomNode('Chunk (%d, %d)' % (self.chunk.x, self.chunk.z))
        node.addGeom(self.geom)

        self.chunkNode = app.render.attachNewNode(node)

        print('Chunk: (%d, %d)' % (self.chunk.x, self.chunk.z))
        print('Chunk pos: ', self.chunk.x * app.level.chunk_unit_width, self.chunk.z * app.level.chunk_unit_depth, 0)
        self.chunkNode.setPos(self.chunk.x * app.level.chunk_unit_width, self.chunk.z * app.level.chunk_unit_depth, 0)

        pass





