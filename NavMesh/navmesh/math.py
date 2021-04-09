import math
from typing import NamedTuple

from shared.vector import Vec2


class Ray(NamedTuple):
    origin: Vec2
    direction: Vec2


class LineSegment(NamedTuple):
    a: Vec2
    b: Vec2


# https://rootllama.wordpress.com/2014/06/20/ray-line-segment-intersection-test-in-2d/
def get_intersection(ray: Ray, line_segment: LineSegment):

    v1 = ray.origin - line_segment.a
    v2 = line_segment.b - line_segment.a
    v3 = Vec2(-ray.direction.z, ray.direction.x)

    t1 = abs(v2.cross(v1)) / v2.dot(v3)
    t2 = v1.dot(v3) / v2.dot(v3)

    if t1 >= 0 and 0 <= t2 <= 1:
        return ray.origin + t1*ray.direction

    return None


t_ray = Ray(Vec2(0, 0), Vec2(1, 0))
segment = LineSegment(Vec2(0.9, 0.5), Vec2(1, -0.5))

print(get_intersection(t_ray, segment))
