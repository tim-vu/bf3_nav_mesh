import typing
from collections import defaultdict, namedtuple, OrderedDict
from enum import Enum

from navmesh.floor_plan import FloorPlan
from navmesh.math import get_intersection, Ray, LineSegment
from navmesh.polygon import Polygon
from shared.vector import Vec2

BOUNDARY = Polygon([
    Vec2(0, 0),
    Vec2(1, 0),
    Vec2(2, 0.5),
    Vec2(3, 0),
    Vec2(4, 0),
    Vec2(4, 1),
    Vec2(0, 1)
])

FLOOR_PLAN = FloorPlan(BOUNDARY, [])


class PortalType(Enum):
    vertex_vertex = 1
    vertex_edge = 2
    vertex_portal = 3


class AreaOfInterest(typing.NamedTuple):
    notch: Vec2
    vector1: Vec2
    vector2: Vec2


def find_notches(polygon: Polygon) -> list[int]:
    result = []

    for i in range(len(polygon)):

        v1 = polygon[i]
        v2 = polygon[(i + 1) % len(polygon)]
        v3 = polygon[(i + 2) % len(polygon)]

        vector1 = v2 - v1
        vector2 = v3 - v2

        if vector1.cross(vector2) < 0:
            result.append((i + 1) % len(polygon))

    return result


def get_edges(to_graph: dict[Vec2, set[Vec2]]) -> set[LineSegment]:
    result = set()

    for k, neighbours in to_graph.items():

        for n in neighbours:
            result.add(LineSegment(k, n))

    return result


def add_edges(polygon: Polygon, to_graph: dict[Vec2, set[Vec2]], from_graph: dict[Vec2, set[Vec2]]) -> None:
    for (i, vertex) in enumerate(polygon):
        to_graph[vertex].add(FLOOR_PLAN.boundary[(i + 1) % len(FLOOR_PLAN.boundary)])
        from_graph[FLOOR_PLAN.boundary[(i - 1) % len(FLOOR_PLAN.boundary)]].add(vertex)


def is_vertex_in_aoi(vertex: Vec2, area_of_interest: AreaOfInterest) -> bool:
    vector = vertex - area_of_interest.notch

    return area_of_interest.vector1.cross(vector) > 0 and vector.cross(area_of_interest.vector2) > 0


def main():
    notches = {
        FLOOR_PLAN.boundary: find_notches(FLOOR_PLAN.boundary)
    }

    for o in FLOOR_PLAN.obstacles:
        notches[o] = find_notches(o)

    to_graph: typing.Dict[Vec2, set[Vec2]] = defaultdict(set)
    from_graph: typing.Dict[Vec2, set[Vec2]] = defaultdict(set)
    portals: set[tuple[Vec2, Vec2]] = set()

    add_edges(FLOOR_PLAN.boundary, to_graph, from_graph)

    for o in FLOOR_PLAN.obstacles:
        add_edges(o, to_graph, from_graph)

    queue: typing.OrderedDict[tuple[Polygon, int], typing.Any] = OrderedDict()

    for polygon, n in notches.items():
        for i in n:
            queue[(polygon, i)] = None

    while len(queue) > 0:

        ((polygon, i), _) = queue.popitem()

        v2 = polygon[i]
        v1 = polygon[(i - 1) % len(polygon)]
        v3 = polygon[(i + 1) % len(polygon)]

        vector1 = v2 - v1
        vector2 = v2 - v3

        area_of_interest = AreaOfInterest(v2, vector1, vector2)

        distance = float('inf')

        for other_vertex in to_graph.keys():

            if other_vertex == v1 or other_vertex == v2 or other_vertex == v3:
                continue

            if not is_vertex_in_aoi(other_vertex, area_of_interest):
                continue

            dist = other_vertex.distance(v2)

            if dist < distance:
                distance = dist
                closest = other_vertex
                portal_type = PortalType.vertex_vertex

        notch_ray1 = Ray(v2, vector1)
        notch_ray2 = Ray(v2, vector2)

        for edge in get_edges(to_graph):

            q_l = get_intersection(notch_ray1, edge)
            q_r = get_intersection(notch_ray2, edge)

            if q_l is None and q_r is None and \
                    not is_vertex_in_aoi(edge.a, area_of_interest) and \
                    not is_vertex_in_aoi(edge.b, area_of_interest):
                continue




if __name__ == '__main__':
    main()
