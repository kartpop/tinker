from functools import partial
from manim import *
# from manim.utils.space_ops import ManimFloat
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

        # Setup large object
        large_size = 0.6
        large = (
            Circle()
            .set_fill(ORANGE, opacity=0.5)
            .shift(LEFT * 5 + DOWN * 0.5)
            .scale(large_size)
        )
        force_large = 1  # same magnitude Force applied on both objects
        force_updater_large = lambda mob, dt: apply_force(mob, force_large, dt)
        start_point, end_point = get_points_for_push_force_on_circle(
            large, PI, force_large
        )
        force_arrow_large = Arrow(start=start_point, end=end_point, buff=0)
        force_arrow_large.set_color(YELLOW)
        force_arrow_updater_large = lambda arrow: update_force_arrow(
            arrow, large, force_large
        )

        ponder_text_0a = (
            Text("Consider two bodies - one small, one large")
            .scale(0.5)
            .next_to(second_law_title, DOWN * 2)
            .to_edge(LEFT)
        )
        self.play(Write(ponder_text_0a))
        self.wait(0.5)
        self.play(FadeIn(small), FadeIn(large))
        self.make_rigid_body(small, density=small_size)
        self.make_rigid_body(large)
        self.wait(1)
        ponder_text_0b = (
            Text("- with the same force acting on both..")
            .scale(0.5)
            .next_to(ponder_text_0a, RIGHT, buff=0.1)
        )
        self.play(Write(ponder_text_0b))
        self.wait(0.5)
        self.play(
            Create(force_arrow_large, lag_ratio=1),
            Create(force_arrow_small, lag_ratio=1),
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

        large.add_updater(force_updater_large)
        force_arrow_large.add_updater(force_arrow_updater_large)
        small.add_updater(force_updater_small)
        force_arrow_small.add_updater(force_arrow_updater_small)

        self.wait(5.5)

        # Stop simulation but keep the objects on the screen
        large.remove_updater(force_updater_large)  # Stop applying the force
        small.remove_updater(force_updater_small)  # Stop applying the force
        force_arrow_large.remove_updater(
            force_arrow_updater_large
        )  # Remove the updater
        force_arrow_small.remove_updater(force_arrow_updater_small)
        self.stop_rigidity(small, large)

        self.wait(3)

        ponder_text_2 = (
            Text(
                "- lighter ball is agile, nimble and has low inertia - speeds up quickly",
                t2c={"low inertia": BLUE, "speeds up quickly": GREEN},
            )
            .scale(0.5)
            .next_to(large, 1.5 * DOWN)
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

        # ).scale(0.5).next_to(large, 1.5 * DOWN).to_edge(LEFT)
        # self.play(Write(bullets))

        self.wait(3)
        question_text = (
            Text(
                "Alright, but what's the connection with Newton's second law?",
            )
            .scale(0.5)
            .next_to(ponder_text_3, DOWN * 2)
            .to_edge(LEFT)
        )
        self.play(Write(question_text))

        self.wait(3)

        # New scene

        # Don't play FadeOut for mobjects having updaters, especially pymunk objects
        # Otherwise, it will throw an error - pickling/threading error
        self.remove(small, large, force_arrow_small, force_arrow_large)

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
        """
        second_law_equation = MathTex(
            r"\mathrm{Force} = \mathrm{mass} \times \mathrm{acceleration}",
            tex_to_color_map={
                r"\mathrm{Force}": YELLOW,
                r"\mathrm{mass}": ORANGE,
                r"\mathrm{acceleration}": GREEN,
            },
            substrings_to_isolate=["Force", "mass", "acceleration"],
        ).next_to(second_law_title, DOWN * 2)
        force_tex = second_law_equation.get_part_by_tex("Force")
        mass_tex = second_law_equation.get_part_by_tex("mass")
        acceleration_tex = second_law_equation.get_part_by_tex("acceleration")

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
        force_tex_brace = Brace(force_tex, DOWN, stroke_width=0.15)
        force_tex_annotation = (
            force_tex_brace.get_text("force acting on the body", buff=0.1)
            .scale(0.5)
            .set_color(YELLOW)
        )
        self.play(GrowFromCenter(force_tex_brace))
        self.play(Write(force_tex_annotation, shift=UP))
        self.wait(1)
        self.play(FadeOut(force_tex_brace), FadeOut(force_tex_annotation))

        # Annotate mass
        mass_tex_brace = Brace(mass_tex, DOWN, stroke_width=0.25)
        mass_tex_annotation = (
            mass_tex_brace.get_text(
                "body's inertia - tendency to resist change in state",
                buff=0.1,
            )
            .scale(0.5)
            .set_color(ORANGE)
        )
        self.play(GrowFromCenter(mass_tex_brace))
        self.play(Write(mass_tex_annotation, shift=UP))
        self.wait(3)
        self.play(FadeOut(mass_tex_brace), FadeOut(mass_tex_annotation))

        # Annotate acceleration
        acceleration_tex_brace = Brace(acceleration_tex, DOWN)
        acceleration_tex_annotation = (
            acceleration_tex_brace.get_text("how fast the speed increases", buff=0.1)
            .scale(0.5)
            .set_color(GREEN)
        )
        self.play(GrowFromCenter(acceleration_tex_brace))
        self.play(Write(acceleration_tex_annotation, shift=UP))
        self.wait(3)
        acceleration_disclaimer_text = (
            Text("(not entirely accurate, but works for now!)", slant=ITALIC)
            .scale(0.3)
            .set_stroke(width=0.3)
            .set_color(GREEN)
            .next_to(acceleration_tex_annotation, DOWN, buff=0.1)
        )
        # self.play(FadeOut(acceleration_brace), FadeOut(acceleration_text))
        self.play(Write(acceleration_disclaimer_text))
        self.wait(2)

        # self.wait(3)
        self.play(
            FadeOut(acceleration_tex_brace),
            FadeOut(acceleration_tex_annotation),
            FadeOut(acceleration_disclaimer_text),
        )
        self.wait(1)

        # Move force, mass and acceleration explainer texts to the left edge, centered and right edge respectively

        # force_text
        force_tex_annotation.to_edge(LEFT)
        # force_tex_to_annotation_arrow: start from left of force and end at top of force_text
        force_tex_to_annotation_arrow = CurvedArrow(
            force_tex.get_left() + LEFT * 0.1,
            force_tex_annotation.get_top() + UP * 0.1,
            color=YELLOW,
            tip_length=0.15,
        )

        # mass_text
        # mass_tex_to_annotation_arrow: start from bottom of mass and end at top of mass_text
        mass_tex_to_annotation_arrow = CurvedArrow(
            mass_tex.get_bottom() + DOWN * 0.1,
            mass_tex_annotation.get_top() + UP * 0.1,
            color=ORANGE,
            tip_length=0.15,
        )

        # acceleration_text
        acceleration_tex_annotation.to_edge(RIGHT)
        # acceleration_tex_to_annotation_arrow: start from right of acceleration and end at top of acceleration_text
        acceleration_tex_to_annotation_arrow = CurvedArrow(
            acceleration_tex.get_right() + RIGHT * 0.1,
            acceleration_tex_annotation.get_top() + UP * 0.1,
            color=GREEN,
            tip_length=0.15,
            angle=-PI / 2,  # Flip the direction of the arc
        )

        self.play(
            FadeIn(
                force_tex_annotation,
                force_tex_to_annotation_arrow,
                mass_tex_annotation,
                mass_tex_to_annotation_arrow,
                acceleration_tex_annotation,
                acceleration_tex_to_annotation_arrow,
            )
        )
        self.wait(1)
        """
        # CONVENIENCE SNIPPET, REMOVE LATER

        force_tex_annotation = (
            Text("force acting on the body")
            .scale(0.5)
            .next_to(second_law_title, DOWN * 5)
            .to_edge(LEFT)
            .set_color(YELLOW)
        )

        mass_tex_annotation = (
            Text("body's inertia - tendency to resist change in state")
            .scale(0.5)
            .next_to(second_law_title, DOWN * 5)
            .set_color(ORANGE)
        )

        acceleration_tex_annotation = (
            Text("how fast the speed increases")
            .scale(0.5)
            .next_to(second_law_title, DOWN * 5)
            .to_edge(RIGHT)
            .set_color(GREEN)
        )

        # self.add(force_tex_annotation, mass_tex_annotation, acceleration_tex_annotation)

        ## --- END SNIPPET --- ##

        """
        explainer_setup_text = (
            Text(
                "Let's anchor the value of force, mass and acceleration turn by turn.",
                line_spacing=1,
            )
            .scale(0.5)
            .next_to(force_tex_annotation, DOWN * 2)
            .to_edge(LEFT)
        )
        explainer_setup_text_2 = (
            Text(
                "Then let's observe how the other two behave.",
                line_spacing=1,
            )
            .scale(0.5)
            .next_to(explainer_setup_text, DOWN * 2)
            .to_edge(LEFT)
        )

        self.play(Write(explainer_setup_text))
        self.wait(1)
        self.play(Write(explainer_setup_text_2))
        self.wait(2)
        self.play(FadeOut(explainer_setup_text), FadeOut(explainer_setup_text_2))
        """
        
        grid = NumberPlane(
            x_range=[-7, 7, 1],
            y_range=[-4, 4, 1],
            background_line_style={
                "stroke_opacity": 0,
            }
        )
        grid.axes.set_stroke(opacity=0)
        self.add(grid)
        
        # x-axis
        x_force = -5
        x_mass = 0
        x_acceleration = 5
        
        # y-axis
        y_constant_annotations = 0
        y_smalls = -1
        y_smalls_annotations = -1.5
        y_larges = -3
        y_larges_annotations = -3.5
        
        # # FIX COORDINATES SUCH THAT ALL FORCES, MASSES, ACCELERATIONS AND THEIR ANNOTATIONS ARE ALIGNED
        # # x-axis
        # x_force = force_tex_annotation.get_x()
        # x_mass = mass_tex_annotation.get_x()
        # x_acceleration = acceleration_tex_annotation.get_x()
        # # y-axis
        # # y_constant_annotations = force_tex_annotation.get_y() - 2
        # # y_smalls = y_constant_annotations - 3
        # # y_smalls_annotations = y_smalls - 1
        # # y_larges = y_smalls - 7
        # # y_larges_annotations = y_larges - 1
        
        # y_constant_annotations = force_tex_annotation.get_y() + (DOWN * 2)[1]
        # y_smalls = y_constant_annotations + (DOWN * 3)[1]
        # y_smalls_annotations = y_smalls + DOWN[1]
        # y_larges = y_smalls + (DOWN * 7)[1]
        # y_larges_annotations = y_larges + DOWN[1]
        
        # FIX text size for annotations
        anno_size = 0.3
        
        
        """

        # CONSTANT FORCE
        constant_force_text = (
            Text("Constant force")
            .scale(0.5)
            .next_to(force_tex_annotation, DOWN * 2)
            .to_edge(LEFT)
            .set_color(YELLOW)
        )
        self.play(FadeIn(constant_force_text))
        self.wait(2)

        # Two same magnitude force arrows one below the other - below the constant_force_text, aligned to the left
        force_arrow_small = (
            Arrow(start=LEFT * 5, end=LEFT * 4, buff=0)
            .next_to(constant_force_text, DOWN * 3)
            .set_color(YELLOW)
        )
        force_arrow_large = (
            Arrow(start=LEFT * 5, end=LEFT * 4, buff=0)
            .next_to(force_arrow_small, DOWN * 7)
            .set_color(YELLOW)
        )
        self.play(Create(force_arrow_small), Create(force_arrow_large))

        # small mass experiences more acceleration
        small_mass = (
            Circle()
            .set_fill(ORANGE, opacity=0.5)
            .scale(0.3)
            .move_to([mass_tex_annotation.get_x(), force_arrow_small.get_y(), 0])
        )
        small_mass_text = (
            Text("small mass").scale(0.3).next_to(small_mass, DOWN).set_color(ORANGE)
        )
        self.play(FadeIn(small_mass), Write(small_mass_text))

        small_mass_experiences = (
            Text("experiences")
            .scale(0.3)
            .move_to(
                [
                    (mass_tex_annotation.get_x() + acceleration_tex_annotation.get_x())
                    / 2,
                    small_mass_text.get_y(),
                    0,
                ]
            )
        ).set_color(BLUE)
        self.play(Write(small_mass_experiences))

        more_acceleration = (
            Arrow(
                start=LEFT * 5.5, end=LEFT * 4, buff=0, stroke_width=3, tip_length=0.15
            )
            .move_to(
                [acceleration_tex_annotation.get_x(), force_arrow_small.get_y(), 0]
            )
            .set_color(GREEN)
        )
        more_acceleration_text = (
            Text("more acceleration")
            .scale(0.3)
            .move_to([more_acceleration.get_x(), small_mass_text.get_y(), 0])
        ).set_color(GREEN)
        self.play(Create(more_acceleration), Write(more_acceleration_text))
        self.wait(2)

        # large mass experiences less acceleration
        large_mass = (
            Circle()
            .set_fill(ORANGE, opacity=0.5)
            .scale(0.6)
            .move_to([mass_tex_annotation.get_x(), force_arrow_large.get_y(), 0])
        )
        large_mass_text = (
            Text("large mass").scale(0.3).next_to(large_mass, DOWN).set_color(ORANGE)
        )
        self.play(FadeIn(large_mass), Write(large_mass_text))

        large_mass_experiences = (
            Text("experiences")
            .scale(0.3)
            .move_to(
                [
                    (mass_tex_annotation.get_x() + acceleration_tex_annotation.get_x())
                    / 2,
                    large_mass_text.get_y(),
                    0,
                ]
            )
        ).set_color(BLUE)
        self.play(Write(large_mass_experiences))

        less_acceleration = (
            Arrow(
                start=LEFT * 4.5, end=LEFT * 4, buff=0, stroke_width=3, tip_length=0.15
            )
            .move_to(
                [acceleration_tex_annotation.get_x(), force_arrow_large.get_y(), 0]
            )
            .set_color(GREEN)
        )
        less_acceleration_text = (
            Text("less acceleration")
            .scale(0.3)
            .move_to([less_acceleration.get_x(), large_mass_text.get_y(), 0])
        ).set_color(GREEN)
        self.play(Create(less_acceleration), Write(less_acceleration_text))

        # Move the masses and forces into position for animation
        small_mass_start_centre = [
            force_tex_annotation.get_x(),
            force_arrow_small.get_y(),
            0,
        ]
        small_mass_shift_vector = small_mass_start_centre - small_mass.get_center()
        large_mass_start_centre = [
            force_tex_annotation.get_x(),
            force_arrow_large.get_y(),
            0,
        ]
        large_mass_shift_vector = large_mass_start_centre - large_mass.get_center()
        self.play(
            FadeOut(force_arrow_small),
            FadeOut(force_arrow_large),
            FadeOut(more_acceleration),
            FadeOut(less_acceleration),
            small_mass.animate.shift(small_mass_shift_vector),
            large_mass.animate.shift(large_mass_shift_vector),
        )

        self.fma_animation(
            small_mass_mobject=small_mass,
            large_mass_mobject=large_mass,
            small_mass_density=0.3,
            large_mass_density=0.6,
            small_mass_force=1,
            large_mass_force=1,
        )

        # Fadeout remaining text and make scene ready for next animation
        self.play(
            FadeOut(small_mass_text),
            FadeOut(large_mass_text),
            FadeOut(small_mass_experiences),
            FadeOut(large_mass_experiences),
            FadeOut(more_acceleration_text),
            FadeOut(less_acceleration_text),
        )
        
        """
        


        # CONSTANT MASS
        constant_mass_text = (
            Text("Constant mass")
            .scale(0.5)
            .move_to([x_mass, y_constant_annotations, 0])
            .set_color(ORANGE)
        )
        self.play(FadeIn(constant_mass_text))
        self.wait(1)

        # Two same magnitude masses one below the other
        small_mass = (
            Circle()
            .set_fill(ORANGE, opacity=0.5)
            .scale(0.3)
            .move_to([x_mass, y_smalls, 0])
        )
        large_mass = (
            Circle()
            .set_fill(ORANGE, opacity=0.5)
            .scale(0.3)
            .move_to([x_mass, y_larges, 0])
        )
        self.play(FadeIn(small_mass), FadeIn(large_mass))
        self.wait(1)
        
        small_mass_text = (
            Text("small mass").scale(anno_size).move_to([x_mass, y_smalls_annotations,0]).set_color(ORANGE)
        )
        large_mass_text = (
            Text("large mass").scale(anno_size).move_to([x_mass, y_larges_annotations,0]).set_color(ORANGE)
        )
        self.play(Write(small_mass_text), Write(large_mass_text))
        
        # small force causes more acceleration

    def fma_animation(
        self,
        small_mass_mobject,
        large_mass_mobject,
        small_mass_density,
        large_mass_density,
        small_mass_force,
        large_mass_force,
        run_time=4,
    ):
        # if condition == "constant_force":
        #     force_small = 1
        #     force_large = 1
        #     size_small = 0.3
        #     size_large = 0.6
        # elif condition == "constant_mass":
        #     force_small = 0.5
        #     force_large = 1
        #     size_small = 0.3
        #     size_large = 0.3
        # elif condition == "constant_acceleration":
        #     force_small = 1
        #     force_large = 2
        #     size_small = 0.3
        #     size_large = 0.6

        # Setup small object
        # small_size = 0.4
        # small = (
        #     Circle()
        #     .set_fill(ORANGE, opacity=0.5)
        #     .shift(LEFT * 5 + UP * 1.5)
        #     .scale(small_size)
        # )
        # force_small = 1  # same magnitude Force applied on both objects
        force_updater_small = lambda mob, dt: apply_force(mob, small_mass_force, dt)
        start_point, end_point = get_points_for_push_force_on_circle(
            small_mass_mobject, PI, small_mass_force
        )
        force_arrow_small = Arrow(start=start_point, end=end_point, buff=0)
        force_arrow_small.set_color(YELLOW)
        force_arrow_updater_small = lambda arrow: update_force_arrow(
            arrow, small_mass_mobject, small_mass_force
        )

        # Setup large object
        # large_size = 0.6
        # large = (
        #     Circle()
        #     .set_fill(ORANGE, opacity=0.5)
        #     .shift(LEFT * 5 + DOWN * 0.5)
        #     .scale(large_size)
        # )
        # force_large = 1  # same magnitude Force applied on both objects
        force_updater_large = lambda mob, dt: apply_force(mob, large_mass_force, dt)
        start_point, end_point = get_points_for_push_force_on_circle(
            large_mass_mobject, PI, large_mass_force
        )
        force_arrow_large = Arrow(start=start_point, end=end_point, buff=0)
        force_arrow_large.set_color(YELLOW)
        force_arrow_updater_large = lambda arrow: update_force_arrow(
            arrow, large_mass_mobject, large_mass_force
        )

        self.make_rigid_body(small_mass_mobject, density=small_mass_density)
        self.make_rigid_body(large_mass_mobject, density=large_mass_density)
        self.wait(1)

        self.play(
            Create(force_arrow_large, lag_ratio=1),
            Create(force_arrow_small, lag_ratio=1),
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

        large_mass_mobject.add_updater(force_updater_large)
        force_arrow_large.add_updater(force_arrow_updater_large)
        small_mass_mobject.add_updater(force_updater_small)
        force_arrow_small.add_updater(force_arrow_updater_small)

        self.wait(run_time)

        # Stop simulation but keep the objects on the screen
        large_mass_mobject.remove_updater(
            force_updater_large
        )  # Stop applying the force
        small_mass_mobject.remove_updater(
            force_updater_small
        )  # Stop applying the force
        force_arrow_large.remove_updater(
            force_arrow_updater_large
        )  # Remove the updater
        force_arrow_small.remove_updater(force_arrow_updater_small)
        self.stop_rigidity(small_mass_mobject, large_mass_mobject)

        self.wait(2)

        # Don't play FadeOut for mobjects having updaters, especially pymunk objects
        # Otherwise, it will throw an error - pickling/threading error
        self.remove(
            small_mass_mobject, large_mass_mobject, force_arrow_small, force_arrow_large
        )
