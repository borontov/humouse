import math
import random
from typing import Optional, Union, Tuple, Type, TypeVar, List
import numpy as np
import scipy as si
from scipy import interpolate

# Create a generic variable that can be 'Parent', or any subclass.

T = TypeVar('T', bound='Parent')


class Point:
    def __init__(
        self,
        x: int,
        y: int,
        duration: Optional[float] = None
    ) -> None:
        self.x = x
        self.y = y
        self.duration = duration

    @classmethod
    def get_middle_point(cls: Type[T], first_point: T, second_point: T) -> T:
        x = (first_point.x + second_point.x) / 2
        y = (first_point.y + second_point.y) / 2
        return cls(x, y)

    @classmethod
    def get_distance(cls: Type[T], first_point: T, second_point: T) -> float:
        result = math.hypot(second_point.x - first_point.x, second_point.y - first_point.y)
        return result

    @classmethod
    def get_point_near_another(
        cls: Type[T],
        point: T,
        max_offset_x: Optional[Union[float, int]],
        max_offset_y: Optional[Union[float, int]],
    ) -> T:
        x_offset = random.uniform(-max_offset_x, max_offset_x)
        y_offset = random.uniform(-max_offset_y, max_offset_y)
        return cls((point.x + x_offset), (point.y + y_offset))

    @classmethod
    def convert_points_to_numpy_array(cls: Type[T], *args: T) -> np.ndarray:
        coordinates_tuples = []
        for point in args:
            coordinates_tuples.append((point.x, point.y))
        return np.array(coordinates_tuples)


class Spline:
    def __init__(self, x_i: List, y_i: List) -> None:
        self.x_i = x_i
        self.y_i = y_i

    @classmethod
    def interpolate(cls, points, t, number_of_points, ipl_t):
        k = number_of_points - 1
        points_tuple = interpolate.splrep(t, points, k=k)

        points_list = list(points_tuple)
        points_list[1] = points.tolist() + [0.0, 0.0, 0.0, 0.0]

        return interpolate.splev(ipl_t, points_list)

    @classmethod
    def parse_points_from_array(cls, points_array: np.ndarray) -> tuple:
        x = points_array[:, 0]
        y = points_array[:, 1]
        t = range(len(points_array))
        return x, y, t

    @classmethod
    def from_points(cls: Type[T], points: Tuple[Point], strategy) -> T:
        number_of_points = len(points)
        if number_of_points < 2:
            return None
        points_array = Point.convert_points_to_numpy_array(*points)
        x, y, t = cls.parse_points_from_array(points_array=points_array)

        spline_points_number = strategy.get_spline_points_number(points=points)

        ipl_t = np.linspace(0.0, len(points_array) - 1, spline_points_number)

        x_i = cls.interpolate(
            points=x,
            t=t,
            number_of_points=number_of_points,
            ipl_t=ipl_t
        )

        y_i = cls.interpolate(
            points=y,
            t=t,
            number_of_points=number_of_points,
            ipl_t=ipl_t
        )

        return cls(x_i, y_i)


class WebPoint(Point):
    def __init__(
        self,
        x: int,
        y: int,
        xpath: Optional[str] = None,
        duration: Optional[float] = None
    ) -> None:
        super().__init__(x=x, y=y, duration=duration)
        self.xpath = xpath
