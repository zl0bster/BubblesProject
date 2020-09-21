# -*- coding: utf-8 -*-
#
# functions for coordinates transformation from angular to decart and back


import math
import simple_draw as sd


def angular_to_decart(distance: int, angle: int):
    x = int(distance * sd.cos(angle))
    y = int(distance * sd.sin(angle))
    return x, y


def vector_length(x: int, y: int):
    return (x * x + y * y) ** 0.5


def vector_angle(x: int, y: int):
    if x == 0 and y == 0:
        return 0
    if y < 0:
        return 360 - int(math.degrees(math.acos(float(x) / vector_length(x=x, y=y))))
    return int(math.degrees(math.acos(float(x) / vector_length(x=x, y=y))))


def decart_to_angular(x: int, y: int):
    """ atleast one value should be differ than zero """
    if x == 0 and y == 0:
        print('wrong decart arguments', x, y)
        return None
    distance = vector_length(x=x, y=y)
    angle = vector_angle(x=x, y=y)
    return distance, angle


def vectorize(point1, point2):
    x = point2[0] - point1[0]
    y = point2[1] - point1[1]
    return x, y


def reflectance_angle(normalToSurface, angle):
    reflection = normalToSurface + (normalToSurface - angle)
    if reflection < 0:
        return 360 + reflection
    elif reflection > 359:
        return reflection - 360
    return reflection


def vector_turn(point, turnValue: int):
    [length, angle] = decart_to_angular(x=point[0], y=point[1])
    angle += turnValue
    if angle < 0:
        angle = 360 + angle
    elif angle > 359:
        angle -= 360
    return angular_to_decart(distance=length, angle=angle)


def distance_point_line(point, linePoint1, linePoint2):
    # https://ru.wikipedia.org/wiki/%D0%A0%D0%B0%D1%81%D1%81%D1%82%D0%BE%D1%8F%D0%BD%D0%B8%D0%B5_%D0%BE%D1%82_%D1%82%D0%BE%D1%87%D0%BA%D0%B8_%D0%B4%D0%BE_%D0%BF%D1%80%D1%8F%D0%BC%D0%BE%D0%B9_%D0%BD%D0%B0_%D0%BF%D0%BB%D0%BE%D1%81%D0%BA%D0%BE%D1%81%D1%82%D0%B8
    numerator = abs(
        (linePoint2[1] - linePoint1[1]) * point[0] -
        (linePoint2[0] - linePoint1[0]) * point[1] +
        linePoint2[0] * linePoint1[1] - linePoint2[1] * linePoint1[0])
    denominator = ((linePoint2[1] - linePoint1[1]) ** 2 + (linePoint2[0] - linePoint1[0]) ** 2) ** 0.5
    return numerator / denominator
