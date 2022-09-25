import random
from abc import ABC, abstractmethod
from typing import Tuple

import numpy as np

from core.geometry import Point, Spline, WebPoint


class Strategy(ABC):
    @classmethod
    @abstractmethod
    def generate_sleep_time(cls):
        ...

    @classmethod
    @abstractmethod
    def generate_click_sleep_time(cls):
        ...

    @classmethod
    @abstractmethod
    def get_screen_center_offsets(cls):
        ...

    @classmethod
    @abstractmethod
    def get_scrolling_amount(cls):
        ...

    @classmethod
    @abstractmethod
    def generate_spline(cls, from_, to_):
        ...

    @classmethod
    @abstractmethod
    def generate_duration(cls, points):
        ...

    @classmethod
    @abstractmethod
    def get_spline_points_number(cls, points):
        ...

    @classmethod
    @abstractmethod
    def get_points(cls, from_, to_):
        ...

    @classmethod
    @abstractmethod
    def get_random_wandering_destination(cls, current_position):
        ...


class HumanLikeStrategy(Strategy):
    @classmethod
    def generate_sleep_time(cls):
        mu, sigma = 0.1, 0.6
        sleep_time = abs(np.random.choice(np.random.normal(mu, sigma, 1000))) * random.randint(0, 3)
        return sleep_time

    @classmethod
    def generate_click_sleep_time(cls):
        return random.uniform(0.001, 0.2)

    @classmethod
    def get_screen_center_offsets(cls):
        max_offset = 20
        x_offset = random.randint(-max_offset, max_offset)
        y_offset = random.randint(-max_offset, max_offset)
        return x_offset, y_offset

    @classmethod
    def get_scrolling_amount(cls):
        amount = random.randint(-5, -2)
        return amount

    @classmethod
    def generate_spline(cls, from_: Point, to_: Point):
        dist = Point.get_distance(from_, to_)
        if dist:
            between = Point.get_middle_point(from_, to_)
            first = from_
            second = Point.get_point_near_another(between, dist / random.uniform(2, 5), dist / random.uniform(2, 5))
            third = Point.get_point_near_another(to_, dist / random.randint(10, 50), dist / random.randint(10, 50))
            last = Point.get_point_near_another(to_, random.randint(0, 10), random.randint(0, 10))
            points = (first, second, third, last)
            spline = Spline.from_points(points=points, strategy=cls)
            return spline

    @classmethod
    def generate_duration(cls, points):
        points_count = len(points)
        mu, sigma = 0.00001, 0.001
        duration_first = np.random.normal(mu, sigma, 1000)
        mu, sigma = 0.01, 0.025
        duration_after = np.random.normal(mu, sigma, 1000)
        for key, point in enumerate(points):
            if key + 1 <= points_count / 2:
                point.duration = abs(np.random.choice(duration_first))
            else:
                point.duration = abs(np.random.choice(duration_after))

    @classmethod
    def get_spline_points_number(cls, points: Tuple[Point]) -> int:
        distance = Point.get_distance(points[0], points[-1])
        spline_points_number = distance // 6
        if spline_points_number < 3:
            return 3
        return int(spline_points_number)

    @classmethod
    def get_points(cls, from_: Point, to_: Point):
        points = []
        spline = cls.generate_spline(from_, to_)
        for x, y in zip(spline.x_i, spline.y_i):
            points.append(Point(x=x, y=y))
        cls.generate_duration(points)
        return points

    @classmethod
    def get_random_wandering_destination(cls, current_position):
        offset_x = random.uniform(-random.randint(50, 600), random.randint(50, 600))
        offset_y = random.uniform(-random.randint(50, 600), random.randint(50, 600))
        destination = WebPoint(
            current_position.x + offset_x,
            current_position.y + offset_y,
        )
        return destination
