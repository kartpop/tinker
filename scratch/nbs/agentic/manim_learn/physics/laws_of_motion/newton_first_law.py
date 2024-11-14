from manim import *
from space import *

# class NewtonsFirstLaw(SpaceScene):
#     GRAVITY = (0, 0)

#     def construct(self):
#         circle = Circle().shift(LEFT * 2 + DOWN * 1)
#         circle.set_fill(PINK, opacity=0.5)
#         self.make_rigid_body(circle)
#         self.add(circle)

#         wall = Line([4, -3.5, 0], [4, 3.5, 0])
#         self.add(wall)
#         self.make_static_body(wall)
#         self.wait(1)

#         # Apply force to the circle from the left
#         force_arrow = Arrow().next_to(circle, direction=LEFT, buff=0)
#         force_arrow.rotate(PI/6, about_point=force_arrow.get_right())
        
        
#         self.play(Create(force_arrow))
#         circle.body.apply_impulse_at_local_point((6, 3))
#         self.wait(0.25)
#         self.play(FadeOut(force_arrow))

#         # Initialize collision flag
#         self.collision_occurred = False
#         self.collision_normal = None

#         # Add collision handler
#         self.add_collision_handler(collision_callback=self.collision_callback)

#         # Updater to check for collision
#         def check_collision(dt):
#             if self.collision_occurred:
#                 self.collision_occurred = False  # Reset the flag
#                 normal = self.collision_normal
#                 arrow = Vector([normal.x, normal.y], color=YELLOW)
#                 arrow.next_to(circle, RIGHT, buff=0)
#                 self.add(arrow)
#                 self.remove_updater(check_collision)  # Stop the updater
#                 # Schedule the animation to play after the current frame
#                 self.animation_to_play = [Create(arrow), FadeOut(arrow)]

#         self.animation_to_play = []
#         # Add the updater to the scene
#         self.add_updater(check_collision)
#         self.wait(0)  # Ensure updaters are called at least once

#         # Play the animation outside the updater
#         if self.animation_to_play:
#             self.play(*self.animation_to_play, run_time=0.5)

#         self.wait(3)

#     def collision_callback(self, arbiter, space, data):
#         cps = arbiter.contact_point_set
#         if len(cps.points) > 0:
#             # Set the collision flag and normal
#             self.collision_occurred = True
#             self.collision_normal = cps.normal
#         return True
    

def get_points_for_push_force_on_circle(circle: Circle, angle):
    end_point = circle.point_at_angle(angle)
    circle_center = circle.get_center()
    force_direction = circle_center - end_point
    force_direction = force_direction / np.linalg.norm(force_direction)
    start_point = end_point - force_direction
    return start_point, end_point

def get_force_components(angle, magnitude):
    return magnitude * np.cos(angle), magnitude * np.sin(angle)

class NewtonsFirstLaw(SpaceScene):
    GRAVITY = (0, 0)

    def construct(self):
        circle = Circle().shift(LEFT * 2 + DOWN * 1)
        circle.set_fill(PINK, opacity=0.5)
        self.make_rigid_body(circle)
        self.add(circle)

        wall = Line([4, -3.5, 0], [4, 3.5, 0])
        self.add(wall)
        self.make_static_body(wall)
        self.wait(1)
        
        # Apply push force of magninute and angle
        angle = PI + PI/6
        start_point, end_point = get_points_for_push_force_on_circle(circle, angle)
        force_arrow = Arrow(start=start_point, end=end_point, buff=0)
        
        self.play(Create(force_arrow))
        circle.body.apply_impulse_at_local_point((6, 3))
        self.wait(0.25)
        self.play(FadeOut(force_arrow))

        # Initialize collision flag
        self.collision_occurred = False
        self.collision_normal = None

        # Add collision handler
        self.add_collision_handler(collision_callback=self.collision_callback)

        self.arrow = Vector([0, 0], color=YELLOW)

        # Updater to check for collision
        def check_collision(dt):
            if self.collision_occurred:
                self.collision_occurred = False  # Reset the flag
                normal = self.collision_normal
                arrow = Vector([normal.x, normal.y], color=YELLOW)
                arrow.next_to(circle, RIGHT, buff=0)
                self.add(arrow)
                self.remove_updater(check_collision)  # Stop the updater
                # self.wait(0.5)
                # Schedule the animation to play after the current frame
                # self.animation_to_play = [Create(arrow), FadeOut(arrow)]
                
        def remove_arrow(dt):
            self.remove(arrow)

        self.animation_to_play = []
        # Add the updater to the scene
        self.add_updater(check_collision)
        self.wait(0)  # Ensure updaters are called at least once

        # Play the animation outside the updater
        # if self.animation_to_play:
        #     self.play(*self.animation_to_play, run_time=0.5)

        self.wait(3)
        

    def collision_callback(self, arbiter, space, data):
        cps = arbiter.contact_point_set
        if len(cps.points) > 0:
            # Set the collision flag and normal
            self.collision_occurred = True
            self.collision_normal = cps.normal
        return True