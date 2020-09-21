# -*- coding: utf-8 -*-
#
# tests for functions for coordinates transformation from angular to decart and back

import transform_decart_ang as tda
import unittest


class test_callculations(unittest.TestCase):
    def test_length1(self):
        result = tda.vector_length(x=4, y=3)
        self.assertEqual(result, 5)

    def test_length2(self):
        result = tda.vector_length(x=0, y=7.0)
        self.assertEqual(result, 7, 'первый аргумент был = 0')

    def test_length3(self):
        result = tda.vector_length(x=6, y=0)
        self.assertEqual(result, 6, 'второй аргумент был = 0')

    def test_angle1(self):
        result = tda.vector_angle(x=2, y=1)
        self.assertEqual(result, 26)

    def test_angle2(self):
        result = tda.vector_angle(x=2, y=4)
        self.assertEqual(result, 63)

    def test_angle3(self):
        result = tda.vector_angle(x=3, y=3)
        self.assertEqual(result, 45)

    def test_angle4(self):
        result = tda.vector_angle(x=0, y=3.5)
        self.assertEqual(result, 90)

    def test_angle5(self):
        result = tda.vector_angle(x=6.2, y=0)
        self.assertEqual(result, 0)

    def test_angle6(self):
        result = tda.vector_angle(x=0, y=-5)
        self.assertEqual(result, 270)

    def test_angle7(self):
        result = tda.vector_angle(x=-10, y=0)
        self.assertEqual(result, 180)

    def test_angle8(self):
        result = tda.vector_angle(x=10, y=-10)
        self.assertEqual(result, 315)

    def test_angle9(self):
        result = tda.vector_angle(x=-10, y=10)
        self.assertEqual(result, 135)

    def test_angleA(self):
        result = tda.vector_angle(x=-10, y=-10)
        self.assertEqual(result, 225)

    def test_angleB(self):
        result = tda.vector_angle(x=0, y=0)
        self.assertEqual(result, 0)

    def test_vectorize1(self):
        result = tda.vectorize([0, 0], [2, 2])
        self.assertEqual(result, (2, 2))

    def test_vectorize2(self):
        result = tda.vectorize([1, 1], [3, 3])
        self.assertEqual(result, (2, 2))

    def test_vectorize3(self):
        result = tda.vectorize([3, 3], [1, 1])
        self.assertEqual(result, (-2, -2))

    def test_ang_dec1(self):
        result = tda.angular_to_decart(distance=10, angle=0)
        self.assertEqual(result, (10, 0))

    def test_ang_dec2(self):
        result = tda.angular_to_decart(distance=20, angle=270)
        self.assertEqual(result, (0, -20))

    def test_ang_dec3(self):
        result = tda.angular_to_decart(distance=220, angle=135)
        self.assertEqual(result, (-155, 155))

    def test_refl_ang1(self):
        result = tda.reflectance_angle(normalToSurface=90, angle=30)
        self.assertEqual(result, 150)

    def test_refl_ang2(self):
        result = tda.reflectance_angle(normalToSurface=45, angle=30)
        self.assertEqual(result, 60)

    def test_refl_ang3(self):
        result = tda.reflectance_angle(normalToSurface=150, angle=35)
        self.assertEqual(result, 265)

    def test_refl_ang4(self):
        result = tda.reflectance_angle(normalToSurface=0, angle=30)
        self.assertEqual(result, 330)

    def test_vec_turn1(self):
        result = tda.vector_turn(point=(20, 0), turnValue=90)
        self.assertEqual(result, (0, 20))

    def test_vec_turn2(self):
        result = tda.vector_turn(point=(20, 0), turnValue=-90)
        self.assertEqual(result, (0, -20))

    def test_dist_pnt_line1(self):
        result = tda.distance_point_line((2, 15), (-20, 0), (10, 0))
        self.assertEqual(result, 15)

    def test_dist_pnt_line2(self):
        result = tda.distance_point_line((3, 2), (0, 1), (0, 20))
        self.assertEqual(result, 3)


if __name__ == '__main__':
    unittest.main(verbosity=2)
