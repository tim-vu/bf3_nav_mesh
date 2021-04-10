import math
from typing import NamedTuple

from shared.vector import Vec2


class Ray(NamedTuple):
    origin: Vec2
    direction: Vec2


class LineSegment(NamedTuple):
    a: Vec2
    b: Vec2


# https://stackoverflow.com/questions/563198/how-do-you-detect-where-two-line-segments-intersect/
def get_intersection(ray: Ray, line_segment: LineSegment):

    p = ray.origin
    r = ray.direction

    q = line_segment.a
    s = line_segment.b - line_segment.a

    num = (q - p).cross(s)
    denom = r.cross(s)

    if denom == 0 and num == 0:

        t0 = (q - p).dot(r)/r.dot(r)
        t1 = t0 + s.dot(r)/r.dot(r)

        if t0 < 0 and t1 < 0:
            return None

        if t0 < 0:
            return t1

        return t0

    if denom == 0 and num != 0:
        return None

    t = num / denom

    if t < 0:
        return None

    u = (p - q).cross(r) / s.cross(r)

    if 0 <= u <= 1:
        return p + t*r

    return None


t_ray = Ray(Vec2(0, 0,), Vec2(1, 0))
segment = LineSegment(Vec2(-1, 0), (Vec2(-0.01, 0)))

print(get_intersection(t_ray, segment))
