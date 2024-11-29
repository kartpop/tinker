from manim import *
from space import *

class BoxOnPlane(SpaceScene):
    GRAVITY = (0, -9.81)

    def get_points_for_push_force_on_box(self, box: Rectangle, angle, magnitude: float=1):
        end_point = box.get_left()
        box_center = box.get_center()
        force_direction = box_center - end_point
        force_direction = force_direction / np.linalg.norm(force_direction)
        start_point = end_point - magnitude * force_direction
        return start_point, end_point
    
    def get_force_components(self, angle, magnitude):
        return magnitude * np.cos(angle), magnitude * np.sin(angle)
    
    def collision_callback(self, arbiter, space, data):
        cps = arbiter.contact_point_set
        if len(cps.points) > 0:
            # Set the collision flag and normal
            self.collision_occurred = True
            self.collision_normal = cps.normal
        return True

    def construct(self):
        box = Rectangle(width=2, height=1).shift(LEFT * 2 + DOWN * 2)
        box.set_fill(RED, opacity=0.5)
        self.play(FadeIn(box))
        self.make_rigid_body(box, density=0.3)

        plane = Line([-5, -3, 0], [5, -3, 0])
        self.add(plane)
        self.make_static_body(plane)
        self.wait(5)
        
        #Apply push force of magnitude and angle
        angle = 0
        magnitude = 5
        start_point, end_point = self.get_points_for_push_force_on_box(box, angle, magnitude)
        force_x, force_y = self.get_force_components(angle, magnitude)
        force_arrow = Arrow(start=start_point, end=end_point, buff=0)
        force_arrow.set_color(YELLOW)
        self.play(GrowArrow(force_arrow))
        self.wait(1)
        
        # Initialize collision flag
        self.collision_occurred = False
        self.collision_normal = None
        
        self.add_collision_handler(collision_callback=self.collision_callback)
        
        # Updater to check for collision
        def check_collision(dt):
            if self.collision_occurred:
                # self.collision_occurred = False  # Reset the flag
                normal = self.collision_normal
                self.arrow = Vector([normal.x, normal.y], color=YELLOW)
                self.arrow.next_to(box, DOWN, buff=0)
                self.add(self.arrow)
                # self.remove_updater(check_collision)  # Stop the updater
                # self.should_remove_arrow = True
                
        # Add the updater to the scene
        self.add_updater(check_collision)
        
        box.body.apply_impulse_at_local_point((force_x, force_y))
        self.wait(6)
        
        
        

        