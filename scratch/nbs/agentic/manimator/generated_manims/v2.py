from manim import *
from space import SpaceScene
import numpy as np

class CollisionDemo(SpaceScene):
    def construct(self):
        # Setup initial scene elements
        circle = Circle().shift(LEFT * 0.5 + DOWN * 2)
        circle.set_fill(ORANGE, opacity=0.5)
        
        wall = Line([5.5, -3.5, 0], [5.5, 3.5, 0])
        
        # Add objects to scene
        self.play(FadeIn(circle))
        self.add(wall)
        
        # Make physics bodies
        self.make_rigid_body(circle)
        self.make_static_body(wall)
        
        # Variables for tracking collision
        self.collision_occurred = False
        self.collision_time = 0
        
        # Setup collision detection
        self.add_collision_handler(collision_callback=self.collision_callback)
        
        # Apply force with arrow visualization
        angle = PI + PI / 6
        magnitude = 2
        start_point, end_point = self.get_points_for_push_force_on_circle(circle, angle)
        force_x, force_y = self.get_force_components(angle - PI, magnitude)
        
        force_arrow = Arrow(start=start_point, end=end_point, buff=0)
        force_arrow.set_color(YELLOW)
        self.play(Create(force_arrow))
        
        # Apply force
        circle.body.apply_impulse_at_local_point((force_x, force_y))
        self.wait()
        
        # Remove force arrow
        self.play(FadeOut(force_arrow))
        
        # Run physics simulation until collision and 1 seconds after
        while True:
            self.wait(1/10)
            if self.collision_occurred:
                self.collision_time += 1/10
                if self.collision_time >= 1:
                    break
                    
    def collision_callback(self, arbiter, space, data):
        cps = arbiter.contact_point_set
        if len(cps.points) > 0:
            self.collision_occurred = True
            self.collision_normal = cps.normal
        return True
        
    def get_points_for_push_force_on_circle(self, circle: Circle, angle):
        end_point = circle.point_at_angle(angle)
        circle_center = circle.get_center()
        force_direction = circle_center - end_point
        force_direction = force_direction / np.linalg.norm(force_direction)
        start_point = end_point - force_direction
        return start_point, end_point

    def get_force_components(self, angle, magnitude):
        return magnitude * np.cos(angle), magnitude * np.sin(angle)