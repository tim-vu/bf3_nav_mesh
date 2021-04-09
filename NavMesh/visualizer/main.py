import sys

from direct.gui.OnscreenText import OnscreenText, TextNode
from direct.showbase.ShowBase import ShowBase, PointLight, AmbientLight
from direct.showbase.ShowBaseGlobal import globalClock
from direct.task.TaskManagerGlobal import taskMgr
from panda3d.core import WindowProperties

from api.models import Level
from api.models.database import SessionLocal
from shared.vector import Vec3
from visualizer.vchunk import VChunk


class VisualizerApp(ShowBase):

    FOV = 90
    VIEW_DISTANCE_CHUNKS = 5

    def __init__(self, level, chunks):
        ShowBase.__init__(self)

        self.level = level

        self.disableMouse()

        wp = WindowProperties()
        #wp.setFullscreen(True)
        wp.setCursorHidden(True)
        wp.setMouseMode(WindowProperties.M_relative)
        #wp.setSize(800, 500)
        self.win.requestProperties(wp)

        self.camLens.setFov(VisualizerApp.FOV)

        self.keyMap = {
            'forward': 0,
            'backward': 0,
            'left': 0,
            'right': 0,
            'shift': 0
        }

        self.setBackgroundColor(0.53, 0.80, 0.92, 1)

        self.accept('escape', sys.exit)
        self.accept("a", self.set_key, ["left", True])
        self.accept("d", self.set_key, ["right", True])
        self.accept("w", self.set_key, ["forward", True])
        self.accept("s", self.set_key, ["backward", True])
        self.accept('lshift', self.set_key, ['shift', True])
        self.accept("a-up", self.set_key, ["left", False])
        self.accept("d-up", self.set_key, ["right", False])
        self.accept("w-up", self.set_key, ["forward", False])
        self.accept("s-up", self.set_key, ["backward", False])
        self.accept('lshift-up', self.set_key, ['shift', False])

        self.cameraMovementTask = taskMgr.add(self.camera_movement, "CameraMovement")
        self.cameraRotationTask = taskMgr.add(self.camera_rotation, 'CameraRotation')

        self.position_text = OnscreenText(text="Position: \nChunk: ", align=TextNode.ALeft, parent=self.pixel2d, fg=(1, 1, 1, 1), bg=(0, 0, 0, 0.7))
        self.position_text.setScale(18)
        self.position_text.setPos(5, -20)

        self.taskMgr.setupTaskChain('chunk_loader_chain', numThreads=6)

        self.create_lights()

        self.taskMgr.doMethodLater(0, self.load_chunks, 'Load Chunks', extraArgs=[chunks], appendTask=True)

        self.camera.setPos(-64 * 5, 54 * 5, 100)

    def create_lights(self):

        plight = PointLight('plight')
        plight.setColor((0.2, 0.2, 0.2, 1))
        plight_node = self.render.attachNewNode(plight)
        plight_node.setPos(-64 * 25, 54 * 25, 126)
        self.render.setLight(plight_node)

        alight = AmbientLight('alight')
        alight.setColor((0.2, 0.2, 0.2, 1))
        self.render.setLight(self.render.attachNewNode(alight))

    def set_key(self, key, value):
        self.keyMap[key] = value

    def recenter_mouse(self):
        self.win.movePointer(0,
                             int(self.win.getProperties().getXSize() / 2),
                             int(self.win.getProperties().getYSize() / 2))

    SENSITIVITY_MULTIPLIER = 20

    def camera_rotation(self, task):

        mw = self.mouseWatcherNode

        has_mouse = mw.hasMouse()

        if has_mouse:
            dx, dy = mw.getMouseX(), mw.getMouseY()
        else:
            dx, dy = 0, 0

        camera_h = self.camera.getH() + -dx * VisualizerApp.SENSITIVITY_MULTIPLIER
        camera_p = self.camera.getP() + dy * VisualizerApp.SENSITIVITY_MULTIPLIER

        self.camera.setH(camera_h)
        self.camera.setP(camera_p)

        self.recenter_mouse()
        return task.cont

    MOVE_SPEED = 3
    MOVE_SPEED_MULTIPLIER = 10

    def camera_movement(self, task):

        dt = globalClock.getDt()

        direction = self.render.getRelativeVector(self.camera, (0, 1, 0))
        direction.normalize()

        position = self.camera.getPos()

        move_speed = VisualizerApp.MOVE_SPEED

        if self.keyMap['shift']:
            move_speed *= VisualizerApp.MOVE_SPEED_MULTIPLIER

        if self.keyMap['forward']:
            position += direction * dt * move_speed
        if self.keyMap['backward']:
            position += direction * dt * -move_speed

        self.camera.setPos(position)

        chunk_x = position.x // self.level.chunk_width
        chunk_z = position.y // self.level.chunk_depth

        self.position_text.text = 'Position: (x: %04d, y: %04d, z: %04d)\nChunk (x: %02d, z: %02d)' % (position.x, position.z, position.y, chunk_x, chunk_z)

        return task.cont

    def load_chunks(self, chunks, task):

        for chunk in chunks:
            self.taskMgr.doMethodLater(0, self.load_chunk, 'Load Chunk', extraArgs=[chunk], appendTask=True,
                                       taskChain='chunk_loader_chain')

        return task.done

    def load_chunk(self, chunk, task):

        voxel_real_size = Vec3(self.level.chunk_unit_width / self.level.chunk_width, self.level.chunk_unit_height / self.level.chunk_voxel_height,
                               self.level.chunk_unit_depth / self.level.chunk_depth)

        chunk_size = Vec3(self.level.chunk_width, self.level.chunk_voxel_height, self.level.chunk_depth)

        chunk = VChunk(chunk_size, voxel_real_size, chunk)
        chunk.show(self)

        return task.done


def visualise_chunks(level, chunks):
    app = VisualizerApp(level, chunks)
    app.run()


if __name__ == '__main__':
    session = SessionLocal()

    level = session.query(Level).get(3)
    visualise_chunks(level, level.chunks)

