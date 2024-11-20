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
        second_law_title = Text("Newton's Second Law of Motion").scale(0.75).to_edge(UP)
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
            Text("Consider two bodies - one small, one big")
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
            Text("- with the same force acting on both..")
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

        self.wait(3)

        ponder_text_2 = (
            Text(
                "- lighter ball is agile, nimble and has low inertia - speeds up quickly",
                t2c={"low inertia": BLUE, "speeds up quickly": GREEN},
            )
            .scale(0.5)
            .next_to(big, 1.5 * DOWN)
            .to_edge(LEFT)
        )
        self.play(Write(ponder_text_2))

        self.wait(3)
        ponder_text_3 = (
            Text(
                "- heavier ball is sluggish and has high inertia - speeds up slowly",
                t2c={"high inertia": BLUE, "speeds up slowly": GREEN},
            )
            .scale(0.5)
            .next_to(ponder_text_2, DOWN)
            .to_edge(LEFT)
        )
        self.play(Write(ponder_text_3))

        # bullets = BulletedList(
        #     "lighter ball is agile, nimble and has low inertia - speeds up quickly",
        #     "heavier ball is sluggish and has high inertia - speeds up slowly",
        #     tex_to_color_map={"low inertia": BLUE, "high inertia": BLUE, "speeds up quickly": GREEN, "speeds up slowly": GREEN},

        # ).scale(0.5).next_to(big, 1.5 * DOWN).to_edge(LEFT)
        # self.play(Write(bullets))

        self.wait(3)
        question_text = (
            Text(
                "Alright, but what's the connection with Newton's second law?",
            )
            .scale(0.5)
            .next_to(pond, DOWN * 2)
            .to_edge(LEFT)
        )
        self.play(Write(question_text))

        self.wait(3)

        # New scene

        # Don't play FadeOut for mobjects having updaters, especially pymunk objects
        # Otherwise, it will throw an error - pickling/threading error
        self.remove(small, big, force_arrow_small, force_arrow_big)

        # Fadeout all other pure mobjects except the title
        self.play(
            *[
                FadeOut(mob, shift=LEFT)
                for mob in self.mobjects
                if not mob == second_law_title
            ]
        )
        self.wait(1)


# CONENIENCE CLASS FOR QUICK RENDERING DURING DEVELOPMENT


class NewtonsSecondLawScene2(SpaceScene):
    GRAVITY = (0, 0)

    def construct(self):

        self.next_section("Second screen")
        second_law_title = Text("Newton's Second Law of Motion").scale(0.75).to_edge(UP)
        self.add(second_law_title)

        second_law_equation = MathTex(
            r"\mathrm{Force} = \mathrm{mass} \times \mathrm{acceleration}",
            tex_to_color_map={
                r"\mathrm{Force}": YELLOW,
                r"\mathrm{mass}": ORANGE,
                r"\mathrm{acceleration}": GREEN,
            },
            substrings_to_isolate=["Force", "mass", "acceleration"],
        ).next_to(second_law_title, DOWN * 2)
        force = second_law_equation.get_part_by_tex("Force")        
        mass = second_law_equation.get_part_by_tex("mass")
        acceleration = second_law_equation.get_part_by_tex("acceleration")

        arrow_title_to_equation = CurvedArrow(
            second_law_title.get_left() + DOWN * 0.3,
            second_law_equation.get_left() + LEFT * 0.1,
            stroke_width=2,
            color=BLUE,
            radius=0.9,
            tip_length=0.15,
        )
        self.play(Write(second_law_equation))
        self.wait(0.5)
        self.play(Create(arrow_title_to_equation))
        self.wait(1)
        self.play(FadeOut(arrow_title_to_equation))
        self.wait(1)

        # Annotate Force
        force_brace = Brace(force, DOWN, stroke_width=0.15)
        force_text = (
            force_brace.get_text("force acting on the body", buff=0.1)
            .scale(0.5)
            .set_color(YELLOW)
        )
        self.play(GrowFromCenter(force_brace))
        self.play(Write(force_text, shift=UP))
        self.wait(1)
        self.play(FadeOut(force_brace), FadeOut(force_text))

        # Annotate mass
        mass_brace = Brace(mass, DOWN, stroke_width=0.25)
        mass_text = (
            mass_brace.get_text(
                "body's inertia - tendency to resist change in state",
                buff=0.1,
            )
            .scale(0.5)
            .set_color(ORANGE)
        )
        self.play(GrowFromCenter(mass_brace))
        self.play(Write(mass_text, shift=UP))
        self.wait(3)
        self.play(FadeOut(mass_brace), FadeOut(mass_text))

        # Annotate acceleration
        acceleration_brace = Brace(acceleration, DOWN)
        acceleration_text = (
            acceleration_brace.get_text("how fast the speed increases", buff=0.1)
            .scale(0.5)
            .set_color(GREEN)
        )
        self.play(GrowFromCenter(acceleration_brace))
        self.play(Write(acceleration_text, shift=UP))
        self.wait(3)
        acceleration_disclaimer_text = (
            Text("(not entirely accurate, but works for now!)", slant=ITALIC)
            .scale(0.3)
            .set_stroke(width=0.3)
            .set_color(GREEN)
            .next_to(acceleration_text, DOWN, buff=0.1)
        )
        # self.play(FadeOut(acceleration_brace), FadeOut(acceleration_text))
        self.play(Write(acceleration_disclaimer_text))
        self.wait(2)

        # acceleration_text_2 = (
        #     Text(
        #         "More accurately, acceleration is the rate of change of velocity of the body.\nVelocity is the speed of the body in a particular direction.\nTherefore acceleration measures how the speed and direction of\nmotion of the body changes over time.",
        #     )
        #     .scale(0.4)
        #     .set_color(GREEN)
        #     .next_to(acceleration_text, DOWN).to_edge(LEFT)
        # )
        # self.play(Write(acceleration_text_2))

        # self.wait(3)
        self.play(
            FadeOut(acceleration_brace),
            FadeOut(acceleration_text),
            FadeOut(acceleration_disclaimer_text),
        )
        self.wait(1)

        # Move force, mass and acceleration explainer texts to the left edge, centered and right edge respectively

        # force_text
        force_text.to_edge(LEFT)
        # force_arrow: start from left of force and end at top of force_text
        force_arrow = CurvedArrow(
            force.get_left() + LEFT * 0.1,
            force_text.get_top() + UP * 0.1,
            color=YELLOW,
            tip_length=0.15,
        )

        # mass_text
        # mass_arrow: start from bottom of mass and end at top of mass_text
        mass_arrow = CurvedArrow(
            mass.get_bottom() + DOWN * 0.1,
            mass_text.get_top() + UP * 0.1,
            color=ORANGE,
            tip_length=0.15,
        )

        # acceleration_text
        acceleration_text.to_edge(RIGHT)
        # acceleration_arrow: start from right of acceleration and end at top of acceleration_text
        acceleration_arrow = CurvedArrow(
            acceleration.get_right() + RIGHT * 0.1,
            acceleration_text.get_top() + UP * 0.1,
            color=GREEN,
            tip_length=0.15,
            angle=-PI / 2,  # Flip the direction of the arc
        )

        self.play(
            FadeIn(
                force_text,
                force_arrow,
                mass_text,
                mass_arrow,
                acceleration_text,
                acceleration_arrow,
            )
        )
        self.wait(1)

        explainer_setup_text = (
            Text(
                "Turn by turn, let's anchor the value of each one of\nforce, mass and acceleration. Then let's observe\nhow the other two behave."
            )
            .scale(0.6)
            .next_to(force_text, DOWN * 2).to_edge(LEFT)
        )
        
        self.play(Write(explainer_setup_text), run_time=3)
        self.wait(3)
        
        constant_force = Text("Constant force").scale(0.5).next_to(force_text, DOWN * 2).to_edge(LEFT).set_color(YELLOW)
        self.play(Transform(explainer_setup_text, constant_force))
        self.wait(2)
        
        
    def fma_animation(condition: str):
        if condition == "constant_force":
            force_small = 1
            force_big = 1
            size_small = 0.3
            size_big = 0.6
        elif condition == "constant_mass":
            force_small = 0.5
            force_big = 1
            size_small = 0.3
            size_big = 0.3
        elif condition == "constant_acceleration":
            force_small = 1
            force_big = 2
            size_small = 0.3
            size_big = 0.6
            
        
        
        
