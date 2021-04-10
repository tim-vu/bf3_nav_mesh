import math
from collections import namedtuple
from typing import NamedTuple


class Vec2(NamedTuple):

    x: float
    z: float

    def __add__(self, other):
        return Vec2(self.x + other.x, self.z + other.z)

    def __sub__(self, other):
        return Vec2(self.x - other.x, self.z - other.z)

    def __mul__(self, scalar):
        return Vec2(self.x*scalar, self.z*scalar)

    __rmul__ = __mul__

    def distance(self, other):
        return math.sqrt((other.x - self.x)**2 + (other.z - self.z)**2)

    def cross(self, other):
        return self.x*other.z - other.x*self.z

    def dot(self, other):
        return self.x*other.x + self.z*other.z


_vec3_tuple = namedtuple('Vec3', 'x y z')


class Vec3(_vec3_tuple):

    def __new__(cls, x: float, y: float, z: float):

        if not isinstance(x, (int, float)):
            raise TypeError('x must be an int or float')

        if not isinstance(y, (int, float)):
            raise TypeError('y must be an int or float')

        if not isinstance(z, (int, float)):
            raise TypeError('z must be an int or float')

        return _vec3_tuple.__new__(cls, x, y, z)

    def __add__(self, other):
        return Vec3(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other):
        return Vec3(self.x - other.x, self.y - other.y, self.z - other.z)

