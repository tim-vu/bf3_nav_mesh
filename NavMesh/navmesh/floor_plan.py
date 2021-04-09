from typing import List

from navmesh.polygon import Polygon


class FloorPlan:

    def __init__(self, boundary: Polygon, obstacles: List[Polygon]):
        self.boundary = boundary
        self.obstacles = obstacles
