from manim import *
from space import *


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
        first_law_title = (
            Text("Newton's First Law of Motion").scale(0.75).to_edge(UP)
        )
        self.play(Write(first_law_title))
        # Wait a while after each animation to let the user see the changes and absorb the information
        self.wait(1)

        circle = Circle().shift(LEFT * 0.5 + DOWN * 2)
        circle.set_fill(ORANGE, opacity=0.5)

        # Order is important; first add/play the mobject, then make rigid/static body
        self.play(FadeIn(circle))
        self.make_rigid_body(circle)

        # Add a wall to the right side of the screen
        wall = Line([5.5, -3.5, 0], [5.5, 3.5, 0])
        self.add(wall)
        self.make_static_body(wall)
        self.wait(1)

        first_line = (
            Text("An object at rest will remain at rest,")
            .scale(0.5)
            .next_to(first_law_title, 4 * DOWN)
            .to_edge(LEFT)
        )
        self.play(Write(first_line))
        self.wait(1)

        # Apply push force of magninute and angle
        angle = PI + PI / 6
        magnitude = 2
        start_point, end_point = get_points_for_push_force_on_circle(circle, angle)
        force_x, force_y = get_force_components(angle - PI, magnitude)
        force_arrow = Arrow(start=start_point, end=end_point, buff=0)
        force_arrow.set_color(YELLOW)

        second_line = (
            Text("unless acted upon by an external force.")
            .scale(0.5)
            .next_to(first_line, DOWN)
            .to_edge(LEFT)
        )
        self.play(Write(second_line))
        self.wait(1)
        self.play(Create(force_arrow, lag_ratio=1), run_time=0.5)
        circle.body.apply_impulse_at_local_point((force_x, force_y))
        self.wait(1)
        self.play(force_arrow.animate.set_color(LIGHT_GRAY).set_opacity(0.25))

        self.wait(1)
        third_line = (
            Text("An object in uniform motion will remain")
            .scale(0.5)
            .next_to(second_line, 3 * DOWN)
            .to_edge(LEFT)
        )
        third_line_b = (
            Text(
                "in uniform motion (moving at constant velocity),",
                t2c={"uniform motion": YELLOW, "constant velocity": BLUE},
            )
            .scale(0.5)
            .next_to(third_line, DOWN)
            .to_edge(LEFT)
        )
        self.play(Write(third_line))
        self.play(Write(third_line_b))

        # Initialize collision flag
        self.collision_occurred = False
        self.collision_normal = None

        # Add collision handler
        self.add_collision_handler(collision_callback=self.collision_callback)

        # self.arrow = Vector([0, 0], color=YELLOW)

        # def remove_arrow(dt):
        #     self.remove(self.arrow)
        #     self.remove_updater(remove_arrow)

        self.should_remove_arrow = False

        # Updater to check for collision
        def check_collision(dt):
            if self.collision_occurred:
                self.collision_occurred = False  # Reset the flag
                normal = self.collision_normal
                self.arrow = Vector([normal.x, normal.y], color=YELLOW)
                self.arrow.next_to(circle, RIGHT, buff=0)
                self.add(self.arrow)
                self.remove_updater(check_collision)  # Stop the updater
                self.should_remove_arrow = True

        self.animation_to_play = []
        # Add the updater to the scene
        self.add_updater(check_collision)
        self.wait_until(lambda: self.should_remove_arrow)
        self.wait(0.5)

        fourth_line = (
            Text("unless an external force changes its")
            .scale(0.5)
            .next_to(third_line_b, DOWN)
            .to_edge(LEFT)
        )
        fourth_line_b = (
            Text(
                "velocity - that is its speed or direction or both.",
                t2c={"velocity": YELLOW, "speed": BLUE, "direction": BLUE},
            )
            .scale(0.5)
            .next_to(fourth_line, DOWN)
            .to_edge(LEFT)
        )
        self.play(Write(fourth_line), self.arrow.animate.set_color(LIGHT_GRAY).set_opacity(0.25))
        self.play(
            Write(fourth_line_b)
        )
        # self.play()
        # self.add_updater(remove_arrow)
        # Play the animation outside the updater
        # if self.animation_to_play:
        #     self.play(*self.animation_to_play, run_time=0.5)
        # Stop the circle from moving


        circle.body.velocity = (0, 0)
        circle.body.angular_velocity = 0
        
        self.wait(5)

    def collision_callback(self, arbiter, space, data):
        cps = arbiter.contact_point_set
        if len(cps.points) > 0:
            # Set the collision flag and normal
            self.collision_occurred = True
            self.collision_normal = cps.normal
        return True
