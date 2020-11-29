# pip install simple-draw
# pip install split
# pip install pywin32
# --------------------
# pip install -r requirements.txt


import argparse
import random
import time
from operator import itemgetter

import simple_draw as sd
import split as split
from win32api import GetSystemMetrics

import fractal_tree_draw as fd
import transform_decart_ang as tda


# todo provide balls birth place while screen init
# todo move screen class definition to another module
# todo move screen objects definition to another file
# todo try to move screen creation to another file


def main():
    parser = parserDefinition()
    args = parser.parse_args()
    x_resolution = args.xres
    y_resolution = args.yres
    window = Screen(x_size=x_resolution, y_size=y_resolution)
    ballsN = 30
    blocksN = 4
    if args.mode == 'r':
        ballsN = args.nba
        blocksN = args.nbr
    window.screen_init(balls=ballsN, blocks=blocksN, wallWidth=4)
    while not sd.user_want_exit():
        window.do()
    sd.quit()


def parserDefinition():
    """
    command line arguments parse to adjust screen object parameters
    :return:
    parser data structure
    screen resolution
    definition mode: random or predefined
    if random mode then returns number of balls and bricks
    if predefined mode is set then

    parser.xres : int  - screen resolution
    parser.yres : int  - screen resolution
    parser.mode : 'r' | 'd'
    'r' - random mode:
        parser.nba : int  - balls number
        parser.nbr : int  - bricks number
        sample:
            python bubbles.py -x 1000 -y 600 r -nba 20 -nbr 4
    'd' - random mode:
        parser.file : str  - configuration file name
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('-x', '--xres', help='window x resolution', type=int, default=1600)
    parser.add_argument('-y', '--yres', help='window y resolution', type=int, default=950)
    subparsers = parser.add_subparsers(dest='mode')
    randParser = subparsers.add_parser('r')
    randParser.add_argument('-nba', help='number of balls', type=int, required=True)
    randParser.add_argument('-nbr', help='number of bricks', type=int, required=True)
    defParser = subparsers.add_parser('d')
    defParser.add_argument('-file', type=argparse.FileType('r'), help='scene config file path', required=True)
    return parser


class Screen:
    """Keeps list of all screen objects and resolution ond manages all its items
    provides movement, drawing, checking collisions and user interaction
    """

    def __init__(self, x_size=800, y_size=600):
        width = GetSystemMetrics(0)
        height = GetSystemMetrics(1)
        print(f"Screen resolution = {width} x {height}")
        self.x_resolution = x_size if x_size < width else width
        self.y_resolution = y_size if y_size < height else height
        self.mobile_objects = []
        self.static_objects = []
        self.lastObjectId = 0
        self.ballBirthPlace = [[int(0.1 * self.x_resolution),
                                int(0.1 * self.y_resolution)],
                               [int(0.9 * self.x_resolution),
                                int(0.9 * self.y_resolution)]]
        # self.contacting_items = {}
        sd.resolution = (self.x_resolution, self.y_resolution)
        # self.draw_screen_background()
        sd.take_background()
        print(self.ballBirthPlace)

    def draw_screen_background(self):
        fd.fractal_tree(sd.get_point(int(self.x_resolution * 0.3),
                                     int(self.y_resolution * 0.9)),
                        200, 275, 40, 0.6, )
        fd.fractal_tree(sd.get_point(int(self.x_resolution * 0.8),
                                     int(self.y_resolution * 0.1)),
                        150, 120, 30, 0.65, sd.COLOR_DARK_ORANGE)

    def add_mobile_item(self, mov_item):
        if isinstance(mov_item, MobileObject):
            self.mobile_objects.append(mov_item)

    def add_stationary_item(self, stat_item):
        if isinstance(stat_item, ScreenObject) and not isinstance(stat_item, MobileObject):
            self.static_objects.append(stat_item)

    def remove_mobile_item(self, mov_item):
        if isinstance(mov_item, MobileObject):
            itemName = id(mov_item)
            self.mobile_objects.remove(mov_item)
            print(f'Mobile item {itemName} removed')

    def move_mobile_items(self):
        for dinObj in self.mobile_objects:
            dinObj.make_movement()

    def export_mobile_items(self):
        headLine = "Xpos, Ypos, Xref, Yref, Xsize, Ysize, Speed Value, Speed Direction, Was Contact,"
        logTimeTuple = time.localtime(time.time())
        logTimeStr = f"{logTimeTuple.tm_year}-{logTimeTuple.tm_mon:}-{logTimeTuple.tm_mday} {logTimeTuple.tm_hour}-" \
                     f"{logTimeTuple.tm_min}-{logTimeTuple.tm_sec}"
        logFileName = f"balls log {logTimeStr}.csv"
        print(logFileName)
        try:
            logFile = open(logFileName, 'w')
            logFile.write(headLine + '\n')
            for dinObj in self.mobile_objects:
                data = dinObj.export_data()
                logFile.write(data + '\n')

        except OSError as errorMessage:
            print(errorMessage)
        finally:
            logFile.close()
            print(f"log file {logFileName} is closed")

    def manage_mobile_items_collisions(self):
        IMPULSE_COEF = 1.00
        MIN_SPEED = 3

        def mobObjectChangeSpeedDirection(item: MobileObject, normalVector):
            """ count a reflection angle"""
            [speedValue, direction] = item.get_speed()
            direction = tda.reflectance_angle(normalToSurface=normalVector, angle=direction)
            item.set_contact()
            item.set_speed(value=speedValue, direction=direction)

        def mobObjectDispersion(item: MobileObject, normalVector):
            [speedValue, direction] = item.get_speed()
            item.set_speed(value=speedValue, direction=normalVector)

        def mobObjectChangeSpeedValue(item1: MobileObject, item2: MobileObject):
            item1SpeedVal, item1SpeedDir = item1.get_speed()
            item1Radius = item1.xRelation
            item2SpeedVal, item2SpeedDir = item2.get_speed()
            item2Radius = item2.xRelation
            item1NewSpeed = max(int(round(item2Radius / item1Radius * item2SpeedVal * IMPULSE_COEF)), MIN_SPEED)
            item2NewSpeed = max(int(round(item1Radius / item2Radius * item1SpeedVal * IMPULSE_COEF)), MIN_SPEED)
            item1.set_speed(item1NewSpeed, item1SpeedDir)
            item2.set_speed(item2NewSpeed, item2SpeedDir)

        x_resolution, y_resolution = self.get_resolution()
        for statObj in self.static_objects:
            for mobObj in self.mobile_objects:
                [isContact, normalVector] = mobObj.check_contact(statObj)
                if isContact:
                    if mobObj.was_contact() == 0:
                        mobObjectChangeSpeedDirection(item=mobObj, normalVector=normalVector)
                        mobObj.speedValue = int(round(mobObj.speedValue * 1.02))
                        mobObj.set_contact()
                        if mobObj.is_to_die_now():
                            mobObj.die()
                        if statObj.is_to_die_now():
                            statObj.block_init(x_resolution, y_resolution)
                else:
                    mobObj.lost_contact()
                if mobObj.was_contact() > 2:
                    mobObjectDispersion(mobObj, normalVector)
                    # mobObjectChangeSpeed(item=mobObj, normalVector=normalVector)
                if mobObj.is_inside(statObj):
                    mobObj.ball_reset_position()
        for i in range(0, len(self.mobile_objects) - 1):
            for j in range(i + 1, len(self.mobile_objects)):
                mobObj1 = self.mobile_objects[i]
                mobObj2 = self.mobile_objects[j]
                [isContact, normalVector] = mobObj1.check_contact(mobObj2)
                if isContact:
                    if mobObj1.was_contact() == 0 and mobObj2.was_contact() == 0:
                        mobObjectChangeSpeedValue(mobObj1, mobObj2)
                    if mobObj1.was_contact() == 0:
                        mobObjectChangeSpeedDirection(item=mobObj1, normalVector=normalVector)
                        mobObj1.set_contact()
                        if mobObj1.is_to_die_now():
                            mobObj1.die()
                    if mobObj2.was_contact() == 0:
                        mobObjectChangeSpeedDirection(item=mobObj2, normalVector=normalVector)
                        mobObj2.set_contact()
                        if mobObj2.is_to_die_now():
                            mobObj2.die()
                else:
                    mobObj1.lost_contact()
                    mobObj2.lost_contact()
                if mobObj1.was_contact() > 1:
                    mobObjectDispersion(mobObj1, normalVector + 90)
                if mobObj2.was_contact() > 1:
                    mobObjectDispersion(mobObj2, normalVector + 270)

    def check_mobile_items_in_window(self):
        for mobObj in self.mobile_objects:
            if mobObj.is_out_of_window(self):
                # if mobObj is Ball:
                if type(mobObj) == Ball:
                    mobObj.ball_init()
                    print(" Runaway ball is returned ")

    def check_mobile_item_is_immovable(self):
        for mobObj in self.mobile_objects:
            if mobObj.is_immovable():
                mobObj.die()
                print(" Stopped ball is initialized ")

    def draw_items(self):
        sd.start_drawing()  # removes  blinking
        for statObj in self.static_objects:
            statObj.draw_item()
        for dinObj in self.mobile_objects:
            dinObj.draw_item()
        sd.finish_drawing()  # removes  blinking
        sd.sleep(0.06)
        sd.draw_background()

    # def __del__(self):
    #     pass

    def do(self):
        self.draw_items()
        self.manage_mobile_items_collisions()
        self.move_mobile_items()
        self.check_mobile_items_in_window()
        self.check_mobile_item_is_immovable()
        [cursorPos, mouseState] = sd.get_mouse_state()
        if mouseState[2] != 0:
            self.export_mobile_items()

    def screen_init(self, balls=3, blocks=1, wallWidth=3):
        x_lim, y_lim = self.get_resolution()
        wallBlocks = [[(0, 0), (wallWidth, y_lim - 1)],
                      [(wallWidth, 0), (x_lim - wallWidth, wallWidth)],
                      [(x_lim - 1 - wallWidth, 0), (x_lim - 1, y_lim - 1)],
                      [(wallWidth, y_lim - 1 - wallWidth), (x_lim - wallWidth, y_lim - 1)]]
        for wall in wallBlocks:
            blockTemp = Block(wall[0], wall[1], parent=self)
            self.add_stationary_item(blockTemp)
            print('wall block', id(wall), 'added')
        for wallBlock in self.static_objects:
            wallBlock.set_width(2)
            wallBlock.set_obj_type(wallBlock.WALLTYPE)
        while blocks > 0:
            block1 = Block(parent=self)
            block1.block_init(x_lim, y_lim)
            self.add_stationary_item(block1)
            print('block', blocks, 'added')
            blocks -= 1
        while balls > 0:
            ball1 = Ball(parent=self)
            # bottomLeft = self.ballBirthPlace[0]
            # topRight = self.ballBirthPlace[1]
            # bottomLeft, topRight = self.get_birth_place()
            # ball1.ball_init(bottomLeft, topRight)
            ball1.ball_init()
            self.add_mobile_item(ball1)
            print('balls', balls, 'added')
            balls -= 1

    def stat_items_issue(self, ignore=None):
        '''generates all stat items of screen object excepting ignored one'''
        for item in self.static_objects:
            if item is not ignore:
                yield item

    def mob_items_issue(self, ignore=None):
        '''generates all mobile items of screen object excepting ignored one'''
        for item in self.mobile_objects:
            if not item is ignore:
                yield item

    def get_resolution(self):
        return self.x_resolution, self.y_resolution

    def get_max_coordinate(self):
        return max(self.x_resolution, self.y_resolution)

    def get_new_object_id(self):
        self.lastObjectId += 1
        return self.lastObjectId

    def get_birth_place(self):
        return self.ballBirthPlace[0], self.ballBirthPlace[1]

    def set_birth_place(self, bottomLeft, topRight):
        assert len(bottomLeft) == 2
        assert len(topRight) == 2
        self.ballBirthPlace[0] = list(bottomLeft)
        self.ballBirthPlace[1] = list(topRight)


class ScreenObject:
    """ Has initial point coordinates, reference of own center and dimensions
    can be drawn with defined color and width
    parent field is stored to require window resolution and balls birthplace coordinates"""
    BALLTYPE = 10
    BLOCKTYPE = 20
    WALLTYPE = 30
    VOIDTYPE = 0

    def __init__(self, reference: list, relation: list, dimensions: list, parent: object = None):
        self.set_position(reference)
        self.set_dimensions(relation, dimensions)
        self.set_color(sd.COLOR_YELLOW)
        self.set_width(1)
        self.isRemovable = False
        self.tillRemove = 10
        self.parent = parent
        self.objectId = parent.get_new_object_id()
        self.objectType = self.VOIDTYPE

    def set_dimensions(self, relation: list, dimensions: list):
        self.xRelation = relation[0]
        self.yRelation = relation[1]
        self.xDimension = dimensions[0]
        self.yDimension = dimensions[1]

    def set_position(self, reference: list):
        self.xPosition = reference[0]
        self.yPosition = reference[1]

    def set_color(self, color=sd.COLOR_YELLOW):
        if color:
            self.color = color

    def set_width(self, width=None):
        if width:
            self.width = width

    def set_obj_type(self, objType: int):
        self.objectType = objType

    def set_lifetime(self, x=10):
        self.isRemovable = True
        self.tillRemove = x

    def set_radius(self, radius: int):
        pass

    def draw_item(self):
        pass

    def export_data(self):
        pass

    def import_data(self):
        pass

    def get_radius(self):
        pass

    def get_position(self):
        return self.xPosition, self.yPosition

    def get_ranges(self):
        r000degrees = self.xDimension - self.xRelation
        r090degrees = self.yDimension - self.yRelation
        r180degrees = self.xRelation
        r270degrees = self.yRelation
        return r000degrees, r090degrees, r180degrees, r270degrees

    def get_limits(self):
        point1 = [self.xPosition - self.xRelation, self.yPosition - self.yRelation]
        point2 = [point1[0] + self.xDimension, point1[1] + self.yDimension]
        return point1, point2

    def get_random_color(self):
        palette = [sd.COLOR_YELLOW,
                   sd.COLOR_PURPLE,
                   sd.COLOR_CYAN,
                   sd.COLOR_GREEN]
        color_count = len(palette) - 1
        color = palette[random.randint(0, color_count)]
        return color

    def get_obj_type(self):
        return self.objectType

    def get_obj_id(self):
        return self.objectId

    def screen_object_init(self, x0=0, y0=0, x_lim=200, y_lim=200):
        x = random.randint(x0, x_lim)
        y = random.randint(y0, y_lim)
        self.set_position(reference=[x, y])
        self.set_color(self.get_random_color())
        self.set_width(2)

    def is_inside(self, screenItem):
        x_own, y_own = self.get_position()
        (x1, y1), (x2, y2) = screenItem.get_limits()
        return (x1 < x_own < x2) and (y1 < y_own < y2)

    def is_removable(self):
        return self.isRemovable

    def is_to_die_now(self):
        if self.isRemovable:
            if self.tillRemove < 10:
                self.set_color(sd.COLOR_RED)
                if type(self) is Ball:
                    self.set_radius(int(0.9 * self.get_radius()))
                    if self.get_radius() < 5:
                        self.set_radius(5)
                    self.set_width(int(0.1 * self.get_radius()))
            if self.tillRemove < 1:
                return True
            else:
                self.tillRemove -= 1
        return False


class MobileObject(ScreenObject):
    """Any screen item that changes its coordinates, checks collision
    draws itself"""

    def __init__(self, reference: list, relation: list, dimensions: list, parent: object = None):
        super().__init__(reference, relation, dimensions, parent)
        self.set_speed(value=0, direction=0)
        self.wasContactBefore = 0

    def get_speed(self) -> (int, int):
        return self.speedValue, self.speedDirection

    def set_speed(self, value: int = 0, direction: int = 0):
        self.speedValue = value if value > 0 else 0
        self.speedDirection = direction if value > 0 else 0

    def was_contact(self) -> int:
        return self.wasContactBefore

    def set_contact(self):
        self.wasContactBefore += 1

    def export_data(self) -> str:
        export = f" {self.xPosition}, {self.yPosition}, {self.xRelation}, {self.yRelation}," \
                 f" {self.xDimension}, {self.yDimension}, {self.speedValue}, {self.speedDirection}," \
                 f" {self.wasContactBefore}"
        return export

    def import_data(self, data: str):
        parameters = split.data(',')
        xPos, yPos, xRel, yRel, xDim, yDim, speedVal, speedDir, wasContactBefore = int(itemgetter(parameters))
        self.set_position([xPos, yPos])
        self.set_dimensions([xRel, yRel], [xDim, yDim])
        self.set_speed(speedVal, speedDir)
        self.wasContactBefore = wasContactBefore

    def lost_contact(self):
        if self.wasContactBefore > 0:
            self.wasContactBefore -= 1
        if self.wasContactBefore < 0:
            self.wasContactBefore = 0

    def check_contact(self, opponent: ScreenObject) -> [bool, int]:
        def check_ball_block_contact(ball: Ball, block: Block) -> [bool, int]:
            def check_ball_vertex_contact(centre, vertex, radius) -> bool:
                [x, y] = tda.vectorize(point1=centre, point2=vertex)
                distance = int(tda.vector_length(x=x, y=y))
                return not (distance > radius)

            def check_ball_edge_contact(centre, radius, linePoint1, linePoint2):
                distance = abs(tda.distance_point_line(point=centre, linePoint1=linePoint1, linePoint2=linePoint2))
                return not (distance > radius)

            contactDetected = False
            normalToSurface = 0
            [referencePoint, oppositePoint] = block.get_limits()
            center = ball.get_position()
            ranges = ball.get_ranges()
            ballRadius = ranges[0]
            blockVertex = [referencePoint,
                           [oppositePoint[0], referencePoint[1]],
                           oppositePoint,
                           [referencePoint[0], oppositePoint[1]]]
            if referencePoint[0] <= center[0] <= oppositePoint[0]:
                contactDetected = (check_ball_edge_contact(centre=center,
                                                           radius=ballRadius,
                                                           linePoint1=blockVertex[3],
                                                           linePoint2=blockVertex[2])
                                   or check_ball_edge_contact(centre=center,
                                                              radius=ballRadius,
                                                              linePoint1=blockVertex[1],
                                                              linePoint2=blockVertex[0]))
                if contactDetected:
                    [x, y] = tda.vectorize(point1=blockVertex[0], point2=blockVertex[1])
                    normalToSurface = tda.vector_angle(x=x, y=y)
                    return [True, normalToSurface]
            elif referencePoint[1] <= center[1] <= oppositePoint[1]:
                contactDetected = (check_ball_edge_contact(centre=center,
                                                           radius=ballRadius,
                                                           linePoint1=blockVertex[0],
                                                           linePoint2=blockVertex[3])
                                   or check_ball_edge_contact(centre=center,
                                                              radius=ballRadius,
                                                              linePoint1=blockVertex[1],
                                                              linePoint2=blockVertex[2]))
                if contactDetected:
                    [x, y] = tda.vectorize(point1=blockVertex[1], point2=blockVertex[2])
                    normalToSurface = tda.vector_angle(x=x, y=y)
                    return [True, normalToSurface]
            else:
                for point in blockVertex:
                    if check_ball_vertex_contact(centre=center, vertex=point, radius=ballRadius):
                        [x, y] = tda.vectorize(point1=center, point2=point)
                        normalToSurface = 90 + tda.vector_angle(x=x, y=y)
                        return [True, normalToSurface]
            return [contactDetected, normalToSurface]

        def check_ball_ball_contact(ball1: Ball, ball2: Ball) -> [bool, int]:
            contactDistance = ball1.xRelation + ball2.xRelation  # xRelation is radius
            [x, y] = tda.vectorize(point1=ball1.get_position(), point2=ball2.get_position())
            ballDistance = tda.vector_length(x, y)
            if not ballDistance > contactDistance:
                return [True, 90 + tda.vector_angle(x, y)]
            return [False, 0]

        if isinstance(self, Ball) and not self.wasContactBefore:
            if isinstance(opponent, Block):
                return check_ball_block_contact(self, opponent)
            elif isinstance(opponent, Ball):
                return check_ball_ball_contact(self, opponent)
        return [False, 0]

    def make_movement(self):
        [x, y] = tda.angular_to_decart(distance=self.speedValue, angle=self.speedDirection)
        self.xPosition += x
        self.yPosition += y
        return

    def die(self):
        x, y = self.get_position()
        sd.snowflake(sd.get_point(x, y), 40)
        self.ball_init()

    def mobile_object_init(self):
        x = self.parent.get_max_coordinate()
        speed_limit = (int(x * 0.005), int(x * 0.008))
        speed_value = random.randint(*speed_limit)  # star before list unpacks the arguments
        speed_direction = random.randint(0, 360)
        self.set_speed(speed_value, speed_direction)
        return

    def is_out_of_window(self, window: Screen):
        x, y = self.get_position()
        pos = (max(abs(x), abs(y)))
        lim = window.get_max_coordinate()
        return lim < pos

    def is_immovable(self):
        if self.speedValue < 1:
            return self.is_to_die_now()


class Block(ScreenObject):
    """ rectangular static blocks """

    def __init__(self, reference=[0, 0], dimensions=[1, 1], parent: object = None):
        relation = [0, 0]
        super().__init__(reference, relation, dimensions, parent)
        self.init_points()
        self.set_obj_type(self.BLOCKTYPE)

    def draw_item(self):
        sd.rectangle(left_bottom=self.referencePoint, right_top=self.oppositePoint, color=self.color,
                     width=self.width)

    def init_points(self):
        self.referencePoint = sd.get_point(x=self.xPosition, y=self.yPosition)
        self.oppositePoint = sd.get_point(x=self.xPosition + self.xDimension, y=self.yPosition + self.yDimension)

    def block_init(self, x_lim=200, y_lim=200):
        wall_thickness = 5
        x_size = random.randint(int(x_lim * 0.05), int(x_lim * 0.3))
        y_size = random.randint(int(y_lim * 0.05), int(y_lim * 0.3))
        x0 = wall_thickness
        x_max = x_lim - x_size - wall_thickness
        y0 = x0
        y_max = y_lim - y_size - wall_thickness
        self.set_lifetime(random.randint(10, 100))
        self.set_dimensions(relation=[0, 0], dimensions=[x_size, y_size])
        self.screen_object_init(x0=x0, y0=y0, x_lim=x_max, y_lim=y_max)
        self.init_points()


class Ball(MobileObject):
    """ mobile balls with radius
        radius value is stored in xRelation of screenObject
    """

    def __init__(self, reference=[0, 0], radius=1, parent: object = None):
        relation = [radius, radius]
        dimensions = [radius * 2, radius * 2]
        super().__init__(reference, relation, dimensions, parent)
        self.set_obj_type(self.BALLTYPE)

    def draw_item(self):
        self.referencePoint = sd.get_point(x=self.xPosition, y=self.yPosition)
        if self.wasContactBefore > 0:
            color = sd.COLOR_DARK_RED
            width = 5
        else:
            color = self.color
            width = self.width
        sd.circle(center_position=self.referencePoint, radius=self.xRelation, color=color, width=width)
        return

    def get_radius(self):
        return self.xRelation

    def ball_init(self):
        ''' define start position in birthplace coordinates received, speed and radius for bubble in window '''
        radius_limit = (16, 50)
        radius = random.randint(*radius_limit)
        self.mobile_object_init()
        self.set_radius(radius)
        self.ball_reset_position()
        self.set_lifetime(random.randint(20, 50))
        print(f"Ball {self.get_obj_id()} initialized")

    def set_radius(self, radius):
        diameter = 2 * radius
        self.set_dimensions([radius, radius], [diameter, diameter])

    def ball_reset_position(self):
        # def ball_reset_position(self, x_lim, y_lim):
        #     wall_thickness = 5

        # x_lim = rightTop[0]
        # y_lim = rightTop[1]
        # x0 = leftBottom[0]
        # y0 = leftBottom[1]
        (x0, y0), (x_lim, y_lim) = self.parent.get_birth_place()
        x0 += self.xRelation + self.speedValue  # + wall_thickness
        y0 += self.xRelation + self.speedValue  # + wall_thickness
        x_max = x_lim - self.xRelation - self.speedValue  # - wall_thickness
        y_max = y_lim - self.xRelation - self.speedValue  # - wall_thickness
        self.screen_object_init(x0=x0, y0=y0, x_lim=x_max, y_lim=y_max)
        self.mobile_object_init()
        return


# =====================================================================================

if __name__ == '__main__':
    main()
