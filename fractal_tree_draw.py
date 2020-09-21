# -*- coding: utf-8 -*-
#
# draws fractal tree on screen
#
#
# pip install simple_draw
#

import simple_draw as sd


def draw_branch(point,
                angle,
                length,
                color):
    branch = sd.get_vector(start_point=point, angle=angle, length=length, )
    branch.draw(color=color)
    return branch.end_point


def draw_fork(point,
              angle,
              tilt,
              length,
              color):
    angle1 = angle + tilt
    angle2 = angle - tilt
    vertex1 = draw_branch(point, angle1, length, color)
    vertex2 = draw_branch(point, angle2, length, color)
    return ([vertex1, angle1], [vertex2, angle2])


def fractal_tree(point,
                 length=100,
                 direction=90,
                 tilt=30,
                 scale=0.6,
                 color=sd.COLOR_DARK_GREEN):
    vertexes = draw_fork(point, direction, tilt, length, color)
    while length > 10:
        length *= scale
        for points in vertexes:
            fractal_tree(points[0], length, points[1], tilt, scale, color)
    return
