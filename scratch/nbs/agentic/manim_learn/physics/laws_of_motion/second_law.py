from functools import partial
from manim import *
from space import *


def get_points_for_push_force_on_circle(circle: Circle, angle, magnitude=1):
    """
    Get the start and end points for the force arrow which represents the force applied on the circle mass.
    """
    end_point = circle.point_at_angle(angle)
    circle_center = circle.get_center()
    force_direction = circle_center - end_point
    force_direction = force_direction / np.linalg.norm(force_direction)
    start_point = end_point - magnitude * force_direction
    return start_point, end_point


class NewtonsSecondLaw(SpaceScene):
    GRAVITY = (0, 0)

    def construct(self):
        second_law_title = (
            Text("Newton's Second Law of Motion", font="Calibri")
            .scale(0.75)
            .to_edge(UP)
        )
        self.play(Write(second_law_title))
        # Wait a while after each animation to let the user see the changes and absorb the information
        self.wait(1)

        # Setup small object
        small_size = 0.4
        small = (
            Circle()
            .set_fill(ORANGE, opacity=0.5)
            .shift(LEFT * 5 + UP * 1.5)
            .scale(small_size)
        )
        force_small = 1  # same magnitude Force applied on both objects
        force_updater_small = lambda mob, dt: apply_force(mob, force_small, dt)
        start_point, end_point = get_points_for_push_force_on_circle(
            small, PI, force_small
        )
        force_arrow_small = Arrow(start=start_point, end=end_point, buff=0)
        force_arrow_small.set_color(YELLOW)
        force_arrow_updater_small = lambda arrow: update_force_arrow(
            arrow, small, force_small
        )

        # Setup big object
        big_size = 0.6
        big = (
            Circle()
            .set_fill(ORANGE, opacity=0.5)
            .shift(LEFT * 5 + DOWN * 0.5)
            .scale(big_size)
        )
        force_big = 1  # same magnitude Force applied on both objects
        force_updater_big = lambda mob, dt: apply_force(mob, force_big, dt)
        start_point, end_point = get_points_for_push_force_on_circle(big, PI, force_big)
        force_arrow_big = Arrow(start=start_point, end=end_point, buff=0)
        force_arrow_big.set_color(YELLOW)
        force_arrow_updater_big = lambda arrow: update_force_arrow(
            arrow, big, force_big
        )

        ponder_text_0a = (
            Text("Consider two bodies,", font="Calibri")
            .scale(0.5)
            .next_to(second_law_title, DOWN * 2)
            .to_edge(LEFT)
        )
        self.play(Write(ponder_text_0a))
        self.wait(0.5)
        self.play(FadeIn(small), FadeIn(big))
        self.make_rigid_body(small, density=small_size)
        self.make_rigid_body(big)
        self.wait(1)
        ponder_text_0b = (
            Text(" with the same force applied on both..", font="Calibri")
            .scale(0.5)
            .next_to(ponder_text_0a, RIGHT, buff=0.1)
        )
        self.play(Write(ponder_text_0b))
        self.wait(0.5)
        self.play(
            Create(force_arrow_big, lag_ratio=1), Create(force_arrow_small, lag_ratio=1)
        )

        # Apply force continuously over time in each physics step
        def apply_force(mob, force, dt):
            mob.body.apply_force_at_world_point((force, 0), mob.body.position)

        # Updater for the force arrow to keep it attached to the circle
        def update_force_arrow(arrow, mob, force_magnitude):
            start_point, end_point = get_points_for_push_force_on_circle(
                mob, PI, force_magnitude
            )
            arrow.put_start_and_end_on(start_point, end_point)

        big.add_updater(force_updater_big)
        force_arrow_big.add_updater(force_arrow_updater_big)
        small.add_updater(force_updater_small)
        force_arrow_small.add_updater(force_arrow_updater_small)

        self.wait(5.5)

        # Stop simulation but keep the objects on the screen
        big.remove_updater(force_updater_big)  # Stop applying the force
        small.remove_updater(force_updater_small)  # Stop applying the force
        force_arrow_big.remove_updater(force_arrow_updater_big)  # Remove the updater
        force_arrow_small.remove_updater(force_arrow_updater_small)
        self.stop_rigidity(small, big)
        



        
        # # mob.body maybe causing pickling issues
        # small.body = None
        # big.body = None

        ponder_text_2 = (
            Text(
                "- lighter ball has low mass and low inertia, therefore speeds up quickly",
                font="Calibri",
                t2c={"low mass": BLUE, "low inertia": BLUE},
            )
            .scale(0.5)
            .next_to(big, 1.5 * DOWN)
            .to_edge(LEFT)
        )
        self.play(Write(ponder_text_2))

        self.wait(3)
        ponder_text_3 = (
            Text(
                "- heavier ball has high mass and high inertia, hence is sluggish to start off..",
                font="Calibri",
                t2c={"high mass": BLUE, "high inertia": BLUE},
            )
            .scale(0.5)
            .next_to(ponder_text_2, DOWN)
            .to_edge(LEFT)
        )
        self.play(Write(ponder_text_3))

        self.wait(3)
        question_text = (
            Text(
                "Alright, but what's the connection with Newton's second law?",
                font="Calibri",
            )
            .scale(0.5)
            .next_to(ponder_text_3, DOWN * 2)
            .to_edge(LEFT)
        )
        self.play(Write(question_text))

        self.wait(3)
        
        # New scene

        
        self.remove(small, big, force_arrow_small, force_arrow_big)
        
        
        self.play(*[FadeOut(mob, shift=LEFT) for mob in self.mobjects])
        self.wait(1)
            # for mob in self.mobjects:
            #     print(mob)
            #     self.play(FadeOut(mob, shift=LEFT))
        
        # second_law_formula = (
        #     MathTex(r"\vec{F} = m \vec{a}")
        #     .scale(1.5)
        #     .to_edge(UP)
        # )
        # self.play(Write(second_law_formula))
        # self.wait(1)
        