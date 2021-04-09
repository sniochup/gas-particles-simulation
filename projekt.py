# ------------
# Simple gas particles simulation using arcade library.
# This program tracks a floating particle and shows
# number of collisions with other particles, average
# collision-free distance and frequency of collisions
# per unit of time as an console output.
# ------------

import arcade
from random import randint
from time import perf_counter
import math


# auxiliary class for physics calculations
class Vector:
    def __init__(self, x, y):
        self.x = x
        self.y = y


# for a single gas particle
class Circle:
    def __init__(self, posx, posy, velx, vely, radius):
        self.position = Vector(posx, posy)
        self.velocity = Vector(velx, vely)
        self.radius = radius


# ------------------------------------------------
# MAIN SETTINGS
n = 20              # number of particles
radius = 35         # radius of a particle
HEIGHT = 700        # screen height
WIDTH = 700         # screen width
speed_min = 20      # minimal particle start speed
speed_max = 80      # maximal particle start speed
process_time = 20   # simulation time
debug = False       # debug mode

# range of tolerance (10% of radius)
d = radius // 10

# wall boundaries
left = (1280 - HEIGHT) / 2
right = left + HEIGHT
lower = (720 - WIDTH) / 2
upper = lower + WIDTH

# arrays for calculations
circles = []
coordinates = []
red_distance = []

# ------------------------------------------------
# RANDOM ARRANGEMENT OF PARTICLES

# research object
# random particle direction direction
direction_x = randint(0, 1)
direction_y = randint(0, 1)
vel_x = randint(speed_min, speed_max) * math.pow(-1, direction_x)
vel_y = randint(speed_min, speed_max) * math.pow(-1, direction_y)

# position in the middle
pos_x = (left + right) / 2
pos_y = (lower + upper) / 2
circles.append(Circle(pos_x, pos_y, vel_x, vel_y, radius))
coordinates.append([pos_x, pos_y])

for i in range(1, n):
    # initial movement direction
    direction_x = randint(0, 1)
    direction_y = randint(0, 1)

    vel_x = randint(speed_min, speed_max) * math.pow(-1, direction_x)
    vel_y = randint(speed_min, speed_max) * math.pow(-1, direction_y)

    # initial positions without spawn collisions
    while True:
        too_close = False
        pos_x = randint(int(left + radius), int(right - radius))
        pos_y = randint(int(lower + radius), int(upper - radius))
        for elem in coordinates:
            # Pythagorean theorem for distances of particles
            if math.sqrt(
                    (pos_x - elem[0]) * (pos_x - elem[0]) + (pos_y - elem[1]) * (pos_y - elem[1])) <= 2 * radius + 5:
                too_close = True
                break
        if not too_close:
            coordinates.append([pos_x, pos_y])
            circles.append(Circle(pos_x, pos_y, vel_x, vel_y, radius))
            if debug:
                print("particle [", i, "] ", pos_x, pos_y)
            break


class MyWindow(arcade.Window):
    def __init__(self, width, height, title):
        super().__init__(width, height, title, False, False, 1 / 60, False)
        self.set_location(400, 200)

        arcade.set_background_color((20, 0, 15))

        # auxiliary variables
        self.time_1 = 0
        self.time_2 = 0
        self.delta_time = 1
        self.time_end = process_time
        self.time_spans = 0
        self.red_hits = 0
        self.red_time_start = perf_counter()

        # two particles for collision detection between them
        self.circ1 = None
        self.circ2 = None

    def collision(self):
        # assigning variables for shortened writing
        circ1 = self.circ1
        circ2 = self.circ2

        # distance between the centers, module
        module = math.sqrt((circ1.position.x - circ2.position.x) * (circ1.position.x - circ2.position.x) +
                           (circ1.position.y - circ2.position.y) * (circ1.position.y - circ2.position.y))
        if debug:
            print("collision detected, distance: ", module)

        # calculate unit normal vector (n) and tangent vector (t)
        n_x = (circ2.position.x - circ1.position.x) / module
        n_y = (circ2.position.y - circ1.position.y) / module
        z = Vector(n_x, n_y)

        t_x = -(circ2.position.y - circ1.position.y) / module
        t_y = (circ2.position.x - circ1.position.x) / module
        t = Vector(t_x, t_y)

        # projections of vectors v1 i v2 on the axes of local coordinate system by t & n vectors
        v1_n = (circ1.velocity.x * z.x) + (circ1.velocity.y * z.y)
        v1_t = (circ1.velocity.x * t.x) + (circ1.velocity.y * t.y)

        v2_n = (circ2.velocity.x * z.x) + (circ2.velocity.y * z.y)
        v2_t = (circ2.velocity.x * t.x) + (circ2.velocity.y * t.y)

        # tangent components do not change
        v1_t_prim = v1_t
        v2_t_prim = v2_t

        # normal components for equal masses
        v1_n_prim = v2_n
        v2_n_prim = v1_n

        # transforming vectors into ours coord. system
        v1_x = (v1_n_prim * z.x) + (v1_t_prim * t.x)
        v1_y = (v1_n_prim * z.y) + (v1_t_prim * t.y)

        v2_x = (v2_n_prim * z.x) + (v2_t_prim * t.x)
        v2_y = (v2_n_prim * z.y) + (v2_t_prim * t.y)

        v1 = Vector(v1_x, v1_y)
        v2 = Vector(v2_x, v2_y)

        return v1, v2  # return velocity of the two collided particles

    def check_collision(self):
        for obj in circles:

            # wall collision
            if obj.position.x > right - obj.radius - d:
                obj.velocity.x = abs(obj.velocity.x) * (-1)
            elif obj.position.x < left + obj.radius + d:
                obj.velocity.x = abs(obj.velocity.x)
            elif obj.position.y > upper - obj.radius - d:
                obj.velocity.y = abs(obj.velocity.y) * (-1)
            elif obj.position.y < lower + obj.radius + d:
                obj.velocity.y = abs(obj.velocity.y)

            # molecule collision
            hit_next = True
            while hit_next:
                for obj2 in circles:
                    # change of position
                    nex_x1 = obj.velocity.x * self.delta_time
                    nex_y1 = obj.velocity.y * self.delta_time
                    nex_x2 = obj2.velocity.x * self.delta_time
                    nex_y2 = obj2.velocity.y * self.delta_time

                    # if it's the same element
                    if obj == obj2:
                        pass
                    # Pythagorean theorem
                    elif math.sqrt(
                            (obj.position.x - obj2.position.x) * (obj.position.x - obj2.position.x) + (
                                    obj.position.y - obj2.position.y) * (obj.position.y - obj2.position.y)) < \
                            float(2 * obj.radius):
                        if obj.position.x < obj2.position.x:
                            if obj.position.x - radius > left:
                                obj.position.x -= radius
                            if obj2.position.x + radius < right:
                                obj2.position.x += radius
                        else:
                            if obj.position.x + radius < right:
                                obj.position.x += radius
                            if obj2.position.x - radius > left:
                                obj2.position.x -= radius

                    elif float(2 * obj.radius) < math.sqrt(
                            (obj.position.x - obj2.position.x) * (obj.position.x - obj2.position.x) + (
                                    obj.position.y - obj2.position.y) * (obj.position.y - obj2.position.y)) <= \
                            float(2 * (obj.radius + d)):
                        self.circ1 = obj
                        self.circ2 = obj2
                        v_1, v_2 = self.collision()
                        obj.velocity = v_1
                        obj2.velocity = v_2
                        if obj == circles[0] or obj2 == circles[0]:
                            self.red_hit()
                    elif math.sqrt((obj.position.x + nex_x1 - obj2.position.x + nex_x2) * (
                            obj.position.x + nex_x1 - obj2.position.x + nex_x2) + (
                                           obj.position.y + nex_y1 - obj2.position.y + nex_y2) * (
                                           obj.position.y + nex_y1 - obj2.position.y + nex_y2)) <= \
                            float(2 * obj.radius):
                        self.circ1 = obj
                        self.circ2 = obj2
                        v_1, v_2 = self.collision()
                        obj.velocity = v_1
                        obj2.velocity = v_2
                        if obj == circles[0] or obj2 == circles[0]:
                            self.red_hit()
                    else:
                        hit_next = False
            if self.time_end < process_time - 0.5:
                obj.position.x += obj.velocity.x * self.delta_time
                obj.position.y += obj.velocity.y * self.delta_time

    # while collision with tracked particle (red) calculate path and save in array
    def red_hit(self):
        self.red_hits += 1
        red_distance.append((perf_counter() - self.red_time_start) * math.sqrt(
            circles[0].velocity.x * circles[0].velocity.x + circles[0].velocity.y * circles[0].velocity.y))
        if debug:
            print("Red particle hits: ", self.red_hits)
            print("Traveled distance: ", red_distance)
        self.red_time_start = perf_counter()

    def on_draw(self):
        arcade.start_render()

        # output
        arcade.draw_text("Hits: {}".format(self.red_hits), right+75, (upper-lower)//2, arcade.color.CADMIUM_RED,
                         font_size=50)

        # borders
        arcade.draw_lrtb_rectangle_outline(left, right, upper, lower, arcade.color.ANTI_FLASH_WHITE, 2)

        # circles
        arcade.draw_circle_outline(circles[0].position.x, circles[0].position.y, circles[0].radius,
                                   arcade.color.CADMIUM_RED, 2)  # research object
        for obj in circles[1:]:  # others
            arcade.draw_circle_outline(obj.position.x, obj.position.y, obj.radius, arcade.color.ANTI_FLASH_WHITE, 2)

    def on_update(self, delta_time: float):
        self.time_1 = self.time_2
        self.time_2 = perf_counter()
        self.delta_time = self.time_2 - self.time_1
        self.time_end -= self.delta_time

        # counting time spans
        self.time_spans += 1

        # end of measurement
        if self.time_end < 0:
            for i in red_distance:
                if i < 1:
                    red_distance.remove(i)
            self.red_hits = len(red_distance)
            if self.red_hits != 0:
                print("Average free path of a tracked particle:", sum(red_distance) / self.red_hits)
            else:
                print("Particle did not collided")

            if self.time_spans != 0:
                print("Collision frequency of the red particle per unit of time: ", self.red_hits / self.time_spans)
            else:
                print("Zero time units")
            arcade.close_window()

        # check collisions
        self.check_collision()


MyWindow(1280, 720, 'Gas particles simulation')
arcade.run()
