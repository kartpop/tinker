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

    # FIX arrow size
    arrow_stroke_width = 6
    arrow_tip_length = 0.3

    def construct(self):

        grid = NumberPlane(
            x_range=[-7, 7, 1],
            y_range=[-4, 4, 1],
            background_line_style={
                "stroke_opacity": 0,
            },
        )
        grid.axes.set_stroke(opacity=0)
        self.add(grid)

        y_title = 3.5
        y_consider_text = 2.5
        x_circle = -5
        y_small = 1.5
        y_small_text = 0.75
        y_large = -1
        y_large_text = -2
        y_transition_text = -3

        explainer_text_size = 0.4

        small_mass_force = 1
        large_mass_force = 1

        second_law_title = (
            Text("Newton's Second Law of Motion").scale(0.75).move_to([0, y_title, 0])
        )
        self.play(Write(second_law_title))
        # Wait a while after each animation to let the user see the changes and absorb the information
        self.wait(1)

        # Setup small object
        small_size = 0.4
        small = (
            Circle()
            .set_fill(ORANGE, opacity=0.5)
            .move_to([x_circle, y_small, 0])
            .scale(small_size)
        )
        force_small = 1  # same magnitude Force applied on both objects
        # force_updater_small = lambda mob, dt: apply_force(mob, force_small, dt)
        start_point, end_point = get_points_for_push_force_on_circle(
            small, PI, force_small
        )
        force_arrow_small = Arrow(
            start=start_point,
            end=end_point,
            stroke_width=self.arrow_stroke_width,
            tip_length=self.arrow_tip_length,
            buff=0,
        )
        force_arrow_small.set_color(
            GRAY
        )  # Just for illustration; not to be used for animation, therefore color is gray
        # force_arrow_updater_small = lambda arrow: update_force_arrow(
        #     arrow, small, force_small
        # )

        # Setup large object
        large_size = 0.6
        large = (
            Circle()
            .set_fill(ORANGE, opacity=0.5)
            .move_to([x_circle, y_large, 0])
            .scale(large_size)
        )
        force_large = 1  # same magnitude Force applied on both objects
        # force_updater_large = lambda mob, dt: apply_force(mob, force_large, dt)
        start_point, end_point = get_points_for_push_force_on_circle(
            large, PI, force_large
        )
        # Show arrow just for illustration; not to be used for animation
        force_arrow_large = Arrow(
            start=start_point,
            end=end_point,
            stroke_width=self.arrow_stroke_width,
            tip_length=self.arrow_tip_length,
            buff=0,
        )
        force_arrow_large.set_color(GRAY)
        # force_arrow_updater_large = lambda arrow: update_force_arrow(
        #     arrow, large, force_large
        # )

        ponder_text_0a = (
            Text("Consider two bodies - small and large")
            .scale(0.5)
            .move_to([0, y_consider_text, 0])
            .to_edge(LEFT)
        )
        self.play(Write(ponder_text_0a))
        self.wait(0.5)
        self.play(FadeIn(small), FadeIn(large))
        # self.make_rigid_body(small, density=small_size)
        # self.make_rigid_body(large)
        self.wait(1)
        ponder_text_0b = (
            Text("- with the same value of force acting on both..")
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
        # def apply_force(mob, force, dt):
        #     mob.body.apply_force_at_world_point((force, 0), mob.body.position)

        # # Updater for the force arrow to keep it attached to the circle
        # def update_force_arrow(arrow, mob, force_magnitude):
        #     start_point, end_point = get_points_for_push_force_on_circle(
        #         mob, PI, force_magnitude
        #     )
        #     arrow.put_start_and_end_on(start_point, end_point)

        # large.add_updater(force_updater_large)
        # force_arrow_large.add_updater(force_arrow_updater_large)
        # small.add_updater(force_updater_small)
        # force_arrow_small.add_updater(force_arrow_updater_small)

        # self.wait(5.5)

        # # Stop simulation but keep the objects on the screen
        # large.remove_updater(force_updater_large)  # Stop applying the force
        # small.remove_updater(force_updater_small)  # Stop applying the force
        # force_arrow_large.remove_updater(
        #     force_arrow_updater_large
        # )  # Remove the updater
        # force_arrow_small.remove_updater(force_arrow_updater_small)
        # self.stop_rigidity(small, large)

        self.wait(2)

        ponder_text_2 = (
            Text(
                "smaller, lighter ball is agile and nimble and has low inertia - speeds up quickly",
                t2c={"low inertia": BLUE, "speeds up quickly": GREEN},
            )
            .scale(explainer_text_size)
            .move_to([0, y_small_text, 0])
            # .to_edge(LEFT)
        )
        self.play(Write(ponder_text_2))

        self.wait(2)
        ponder_text_3 = (
            Text(
                "larger, heavier ball is sluggish and has high inertia - speeds up slowly",
                t2c={"high inertia": BLUE, "speeds up slowly": GREEN},
            )
            .scale(explainer_text_size)
            .move_to([0, y_large_text, 0])
            # .to_edge(LEFT)
        )
        self.play(Write(ponder_text_3))
        self.wait(2)

        self.play(FadeOut(force_arrow_large), FadeOut(force_arrow_small))

        self.fma_animation(
            small_mass_mobject=small,
            large_mass_mobject=large,
            small_mass_density=small_size,
            large_mass_density=1,
            small_mass_force=1,
            large_mass_force=1,
            run_time=5.5,
            remove_pymunk_objects=False,
        )

        self.wait(3)
        question_text = (
            Text(
                "Alright, but what's the connection with Newton's second law?",
            )
            .scale(0.5)
            .move_to([0, y_transition_text, 0])
            .to_edge(LEFT)
        )
        self.play(Write(question_text))

        self.wait(3)

        # New scene

        # Don't play FadeOut for mobjects having updaters, especially pymunk objects
        # Otherwise, it will throw an error - pickling/threading error
        # self.remove_mobject_if_exists(mobjects_to_remove)
        self.remove(small, large)
        
        # A mobject used before with Pymunk should be replaced with a new one to avoid threading errors during future effects (eg. FadeOut)
        # small = self.remove_and_replace(small)
        # large = self.remove_and_replace(large)

        # Fadeout all other pure mobjects except the title
        # self.play(
        #     *[
        #         FadeOut(mob, shift=LEFT)
        #         for mob in self.mobjects
        #         if not mob == second_law_title
        #     ]
        # )

        self.play(
            FadeOut(ponder_text_0a),
            FadeOut(ponder_text_0b),
            FadeOut(ponder_text_2),
            FadeOut(ponder_text_3),
            FadeOut(question_text),
            # FadeOut(small),
            # FadeOut(large),
            
        )
        self.wait(1)

        # CONENIENCE CLASS FOR QUICK RENDERING DURING DEVELOPMENT

        # class NewtonsSecondLawScene2(SpaceScene):
        #     GRAVITY = (0, 0)

        #     # FIX arrow size
        #     arrow_stroke_width = 6
        #     arrow_tip_length = 0.3

        #     def construct(self):

        # grid = NumberPlane(
        #     x_range=[-7, 7, 1],
        #     y_range=[-4, 4, 1],
        #     background_line_style={
        #         "stroke_opacity": 0,
        #     },
        # )
        # grid.axes.set_stroke(opacity=0)
        # self.add(grid)

        # self.next_section("Second screen")
        # second_law_title = (
        #     Text("Newton's Second Law of Motion").scale(0.75).move_to([0, 3.5, 0])
        # )
        # self.add(second_law_title)

        # self.next_section("Second screen")

        # second_law_title = (
        #     Text("Newton's Second Law of Motion").scale(0.75).move_to([0, 3.5, 0])
        # )
        # self.add(second_law_title)
        # # Wait a while after each animation to let the user see the changes and absorb the information
        # self.wait(1)

        
        
        
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
            force_tex_brace.get_text("external force acting on the body", buff=0.1)
            .scale(0.7)
            .set_color(YELLOW)
        )
        self.play(GrowFromCenter(force_tex_brace))
        self.play(Write(force_tex_annotation, shift=UP))
        self.wait(2)
        self.play(FadeOut(force_tex_brace), FadeOut(force_tex_annotation))

        # Annotate mass
        mass_tex_brace = Brace(mass_tex, DOWN, stroke_width=0.25)
        mass_tex_annotation = (
            mass_tex_brace.get_text(
                "body's inertia - tendency to resist change in state",
                buff=0.1,
            )
            .scale(0.7)
            .set_color(ORANGE)
        )
        self.play(GrowFromCenter(mass_tex_brace))
        self.play(Write(mass_tex_annotation, shift=UP))
        self.wait(3)
        self.play(FadeOut(mass_tex_brace), FadeOut(mass_tex_annotation))

        # Annotate acceleration
        acceleration_tex_brace = Brace(acceleration_tex, DOWN)
        acceleration_tex_annotation = (
            acceleration_tex_brace.get_text("how fast its speed increases", buff=0.1)
            .scale(0.7)
            .set_color(GREEN)
        )
        self.play(GrowFromCenter(acceleration_tex_brace))
        self.play(Write(acceleration_tex_annotation, shift=UP))
        self.wait(2)
        acceleration_disclaimer_text = (
            Text("(not entirely accurate, but works for now!)", slant=ITALIC)
            .scale(0.4)
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
        
        
        explainer_setup_text = (
            Text(
                "Let's hold the value of force, mass, and acceleration constant, one by one...",
                line_spacing=1,
                
                t2c={"force": YELLOW, "mass": ORANGE, "acceleration": GREEN},
            )
            .scale(0.5)
            .next_to(force_tex_annotation, DOWN * 2)
            .to_edge(LEFT)
        )
        explainer_setup_text_2 = (
            Text(
                "...and observe how the other two behave.",
                line_spacing=1,
            )
            .scale(0.5)
            .next_to(explainer_setup_text, DOWN * 2)
            .to_edge(LEFT)
        )

        self.play(Write(explainer_setup_text))
        self.wait(2)
        self.play(Write(explainer_setup_text_2))
        self.wait(3)
        self.play(FadeOut(explainer_setup_text), FadeOut(explainer_setup_text_2))
        self.wait(1)

        

        # FIX PARAMETERS

        # x-axis
        x_force = -5
        x_mass = 0
        x_acceleration = 4.5

        # y-axis
        y_constant_annotations = 1.5
        y_smalls = 0
        y_smalls_annotations = -0.75
        y_larges = -2.25
        y_larges_annotations = -3.25

        # FIX text size for annotations
        anno_size = 0.4
        
        # Force and Acceleration arrows
        small_arrow_size = 1
        large_arrow_size = 1.75



        ## CONSTANT FORCE
        constant_force_text = (
            Text("Keep force constant")
            .scale(0.5)
            .move_to([x_force, y_constant_annotations, 0])
            .set_color(YELLOW)
        )
        self.play(FadeIn(constant_force_text))
        self.wait(2)

        # Two same magnitude force arrows one below the other
        # The force names force_arrow_small and force_arrow_large are just for convenience
        force_arrow_small = (
            Arrow(
                start=ORIGIN,
                end=[small_arrow_size, 0, 0],
                buff=0,
                stroke_width=self.arrow_stroke_width,
                tip_length=self.arrow_tip_length,
            )
            .move_to([x_force, y_smalls, 0])
            .set_color(YELLOW)
        )
        force_arrow_large = (
            Arrow(
                start=ORIGIN,
                end=[small_arrow_size, 0, 0],
                buff=0,
                stroke_width=self.arrow_stroke_width,
                tip_length=self.arrow_tip_length,
            )
            .move_to([x_force, y_larges, 0])
            .set_color(YELLOW)
        )
        self.play(Create(force_arrow_small), Create(force_arrow_large))
        self.wait(1)

        # small mass experiences more acceleration
        small_mass = (
            Circle()
            .set_fill(ORANGE, opacity=0.5)
            .scale(0.3)
            .move_to([x_mass, y_smalls, 0])
        )
        small_mass_text = (
            Text("small mass")
            .scale(anno_size)
            .move_to([x_mass, y_smalls_annotations, 0])
            .set_color(ORANGE)
        )
        self.play(FadeIn(small_mass), Write(small_mass_text))

        small_mass_experiences = (
            Text("experiences")
            .scale(anno_size)
            .move_to(
                [
                    (x_mass + x_acceleration) / 2,
                    y_smalls_annotations,
                    0,
                ]
            )
        ).set_color(BLUE)
        self.play(Write(small_mass_experiences))

        more_acceleration = (
            Arrow(
                start=ORIGIN,
                end=[large_arrow_size, 0, 0],
                buff=0,
                stroke_width=self.arrow_stroke_width,
                tip_length=self.arrow_tip_length,
            )
            .move_to([x_acceleration, y_smalls, 0])
            .set_color(GREEN)
        )
        more_acceleration_text = (
            Text("more acceleration")
            .scale(anno_size)
            .move_to([x_acceleration, y_smalls_annotations, 0])
        ).set_color(GREEN)
        self.play(Create(more_acceleration), Write(more_acceleration_text))
        self.wait(2)

        # large mass experiences less acceleration
        large_mass = (
            Circle()
            .set_fill(ORANGE, opacity=0.5)
            .scale(0.5)
            .move_to([x_mass, y_larges, 0])
        )
        large_mass_text = (
            Text("large mass")
            .scale(anno_size)
            .move_to([x_mass, y_larges_annotations, 0])
            .set_color(ORANGE)
        )
        self.play(FadeIn(large_mass), Write(large_mass_text))

        large_mass_experiences = (
            Text("experiences")
            .scale(anno_size)
            .move_to(
                [
                    (x_mass + x_acceleration) / 2,
                    y_larges_annotations,
                    0,
                ]
            )
        ).set_color(BLUE)
        self.play(Write(large_mass_experiences))

        less_acceleration = (
            Arrow(
                start=ORIGIN,
                end=[small_arrow_size, 0, 0],
                buff=0,
                stroke_width=self.arrow_stroke_width,
                tip_length=self.arrow_tip_length,
            )
            .move_to([x_acceleration, y_larges, 0])
            .set_color(GREEN)
        )
        less_acceleration_text = (
            Text("less acceleration")
            .scale(anno_size)
            .move_to([x_acceleration, y_larges_annotations, 0])
        ).set_color(GREEN)
        self.play(Create(less_acceleration), Write(less_acceleration_text))

        # Move the masses and forces into position for animation

        small_mass_shift_vector = [x_force, y_smalls, 0] - small_mass.get_center()
        large_mass_shift_vector = [x_force, y_larges, 0] - large_mass.get_center()
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
            small_mass_force=small_arrow_size,
            large_mass_force=small_arrow_size,
        )

        # Fadeout remaining text and make scene ready for next animation
        self.play(
            FadeOut(small_mass_text),
            FadeOut(large_mass_text),
            FadeOut(small_mass_experiences),
            FadeOut(large_mass_experiences),
            FadeOut(more_acceleration_text),
            FadeOut(less_acceleration_text),
            FadeOut(constant_force_text)
        )

        # self.wait(1)
        
        

        ### CONSTANT MASS
        constant_mass_text = (
            Text("Keep mass constant")
            .scale(0.5)
            .move_to([x_mass, y_constant_annotations, 0])
            .set_color(ORANGE)
        )
        self.play(FadeIn(constant_mass_text))
        self.wait(1)

        # Two same magnitude masses one below the other
        # Names small_mass and large_mass are just for convenience
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

        # small force causes less acceleration
        force_arrow_small = (
            Arrow(
                start=ORIGIN,
                end=[small_arrow_size, 0, 0],
                buff=0,
                stroke_width=self.arrow_stroke_width,
                tip_length=self.arrow_tip_length,
            )
            .move_to([x_force, y_smalls, 0])
            .set_color(YELLOW)
        )
        force_small_text = (
            Text("small force")
            .scale(anno_size)
            .move_to([x_force, y_smalls_annotations, 0])
            .set_color(YELLOW)
        )
        self.play(Create(force_arrow_small), Write(force_small_text))

        force_small_causes_text = (
            Text("causes")
            .scale(anno_size)
            .move_to(
                [
                    (x_mass + x_acceleration) / 2,
                    y_smalls_annotations,
                    0,
                ]
            )
        ).set_color(BLUE)
        self.play(Write(force_small_causes_text))

        less_acceleration = (
            Arrow(
                start=ORIGIN,
                end=[small_arrow_size, 0, 0],
                buff=0,
                stroke_width=self.arrow_stroke_width,
                tip_length=self.arrow_tip_length,
            )
            .move_to([x_acceleration, y_smalls, 0])
            .set_color(GREEN)
        )
        less_acceleration_text = (
            Text("less acceleration")
            .scale(anno_size)
            .move_to([x_acceleration, y_smalls_annotations, 0])
            .set_color(GREEN)
        )
        self.play(Create(less_acceleration), Write(less_acceleration_text))
        self.wait(1)

        # large force causes more acceleration
        force_arrow_large = (
            Arrow(
                start=ORIGIN,
                end=[large_arrow_size, 0, 0],
                buff=0,
                stroke_width=self.arrow_stroke_width,
                tip_length=self.arrow_tip_length,
            )
            .move_to([x_force, y_larges, 0])
            .set_color(YELLOW)
        )
        force_large_text = (
            Text("large force")
            .scale(anno_size)
            .move_to([x_force, y_larges_annotations, 0])
            .set_color(YELLOW)
        )

        self.play(Create(force_arrow_large), Write(force_large_text))

        force_large_causes_text = (
            Text("causes")
            .scale(anno_size)
            .move_to(
                [
                    (x_mass + x_acceleration) / 2,
                    y_larges_annotations,
                    0,
                ]
            )
        ).set_color(BLUE)
        self.play(Write(force_large_causes_text))

        more_acceleration = (
            Arrow(
                start=ORIGIN,
                end=[large_arrow_size, 0, 0],
                buff=0,
                stroke_width=self.arrow_stroke_width,
                tip_length=self.arrow_tip_length,
            )
            .move_to([x_acceleration, y_larges, 0])
            .set_color(GREEN)
        )
        more_acceleration_text = (
            Text("more acceleration")
            .scale(anno_size)
            .move_to([x_acceleration, y_larges_annotations, 0])
            .set_color(GREEN)
        )
        self.play(Create(more_acceleration), Write(more_acceleration_text))
        self.wait(1)

        # Move the masses and forces into position for animation
        small_mass_shift_vector = [x_force, y_smalls, 0] - small_mass.get_center()
        large_mass_shift_vector = [x_force, y_larges, 0] - large_mass.get_center()
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
            large_mass_density=0.3,
            small_mass_force=small_arrow_size,
            large_mass_force=large_arrow_size,
        )

        # Fadeout remaining text and make scene ready for next animation
        self.play(
            FadeOut(force_small_text),
            FadeOut(force_large_text),
            FadeOut(force_small_causes_text),
            FadeOut(force_large_causes_text),
            FadeOut(more_acceleration_text),
            FadeOut(less_acceleration_text),
            FadeOut(constant_mass_text)
        )

        self.wait(2)
        
    
        
        ##CONSTANT ACCELERATION
        constant_acceleration_text = (
            Text("Keep acceleration constant")
            .scale(0.5)
            .move_to([x_acceleration, y_constant_annotations, 0])
            .set_color(GREEN)
        )
        self.play(FadeIn(constant_acceleration_text))
        
        self.wait(1)
        
        # Two same magnitude accelerations one below the other
        # Names less_acceleration and more_acceleration are just for convenience
        less_acceleration = (
            Arrow(
                start=ORIGIN,
                end=[small_arrow_size, 0, 0],
                buff=0,
                stroke_width=self.arrow_stroke_width,
                tip_length=self.arrow_tip_length,
            )
            .move_to([x_acceleration, y_smalls, 0])
            .set_color(GREEN)
        )
        more_acceleration = (
            Arrow(
                start=ORIGIN,
                end=[small_arrow_size, 0, 0],
                buff=0,
                stroke_width=self.arrow_stroke_width,
                tip_length=self.arrow_tip_length,
            )
            .move_to([x_acceleration, y_larges, 0])
            .set_color(GREEN)
        )
        self.play(Create(less_acceleration), Create(more_acceleration))
        self.wait(1)
        
        # small force acting on small mass
        force_arrow_small = (
            Arrow(
                start=ORIGIN,
                end=[small_arrow_size, 0, 0],
                buff=0,
                stroke_width=self.arrow_stroke_width,
                tip_length=self.arrow_tip_length,
            )
            .move_to([x_force, y_smalls, 0])
            .set_color(YELLOW)
        )
        force_small_text = (
            Text("small force")
            .scale(anno_size)
            .move_to([x_force, y_smalls_annotations, 0])
            .set_color(YELLOW)
        )
        self.play(Create(force_arrow_small), Write(force_small_text))
        
        force_small_acting_on_text = (
            Text("acting on")
            .scale(anno_size)
            .move_to(
                [
                    (x_force + x_mass) / 2,
                    y_smalls_annotations,
                    0,
                ]
            )
        ).set_color(BLUE)
        self.play(Write(force_small_acting_on_text))
        
        small_mass = (
            Circle()
            .set_fill(ORANGE, opacity=0.5)
            .scale(0.3)
            .move_to([x_mass, y_smalls, 0])
        )
        small_mass_text = (
            Text("small mass")
            .scale(anno_size)
            .move_to([x_mass, y_smalls_annotations, 0])
            .set_color(ORANGE)
        )
        self.play(FadeIn(small_mass), Write(small_mass_text))
        
        self.wait(2)
        
        # large force acting on large mass
        force_arrow_large = (
            Arrow(
                start=ORIGIN,
                end=[large_arrow_size, 0, 0],
                buff=0,
                stroke_width=self.arrow_stroke_width,
                tip_length=self.arrow_tip_length,
            )
            .move_to([x_force, y_larges, 0])
            .set_color(YELLOW)
        )
        force_large_text = (
            Text("large force")
            .scale(anno_size)
            .move_to([x_force, y_larges_annotations, 0])
            .set_color(YELLOW)
        )
        self.play(Create(force_arrow_large), Write(force_large_text))
        
        force_large_acting_on_text = (
            Text("acting on")
            .scale(anno_size)
            .move_to(
                [
                    (x_force + x_mass) / 2,
                    y_larges_annotations,
                    0,
                ]
            )
        ).set_color(BLUE)
        self.play(Write(force_large_acting_on_text))
        
        large_mass = (
            Circle()
            .set_fill(ORANGE, opacity=0.5)
            .scale(0.5)
            .move_to([x_mass, y_larges, 0])
        )
        large_mass_text = (
            Text("large mass")
            .scale(anno_size)
            .move_to([x_mass, y_larges_annotations, 0])
            .set_color(ORANGE)
        )
        self.play(FadeIn(large_mass), Write(large_mass_text))
        
        # Move the masses and forces into position for animation
        small_mass_shift_vector = [x_force, y_smalls, 0] - small_mass.get_center()
        large_mass_shift_vector = [x_force, y_larges, 0] - large_mass.get_center()
        self.play(
            FadeOut(force_arrow_small),
            FadeOut(force_arrow_large),
            FadeOut(less_acceleration),
            FadeOut(more_acceleration),
            small_mass.animate.shift(small_mass_shift_vector),
            large_mass.animate.shift(large_mass_shift_vector),
        )
        
        self.fma_animation(
            small_mass_mobject=small_mass,
            large_mass_mobject=large_mass,
            small_mass_density=0.3,
            large_mass_density=0.3 * large_arrow_size/ small_arrow_size,
            small_mass_force=small_arrow_size,
            large_mass_force=large_arrow_size,
        )
        
        # Fadeout remaining text and make scene ready for next animation
        self.play(
            FadeOut(force_small_text),
            FadeOut(force_large_text),
            FadeOut(force_small_acting_on_text),
            FadeOut(force_large_acting_on_text),
            FadeOut(small_mass_text),
            FadeOut(large_mass_text),
            FadeOut(constant_acceleration_text) 
        )
        
        self.wait(2)
        
        """
        # EXPLAINER TEXT
        
        # FIX y
        y_force_text = 1.5
        y_mass_text = 0.5
        y_acceleration_text = -0.5
        y_acceleration_note = -1.5
        y_gist_text = -3.5
        
        
        # Move force, mass and acceleration explainer texts to the left edge, centered and right edge respectively

        # force_text
        force_tex_annotation.move_to([0, y_force_text, 0]).to_edge(LEFT)
        # force_tex_to_annotation_arrow: start from left of force and end at top of force_text
        force_tex_to_annotation_arrow = CurvedArrow(
            force_tex.get_left() + LEFT * 0.1,
            force_tex_annotation.get_top() + UP * 0.1,
            color=YELLOW,
            tip_length=0.15,
        )

        # mass_text
        mass_tex_annotation.move_to([0, y_mass_text, 0])
        # mass_tex_to_annotation_arrow: start from bottom of mass and end at top of mass_text
        mass_tex_to_annotation_arrow = CurvedArrow(
            mass_tex.get_bottom() + DOWN * 0.1,
            mass_tex_annotation.get_top() + UP * 0.1,
            color=ORANGE,
            tip_length=0.15,
        )

        # acceleration_text
        acceleration_tex_annotation.move_to([0, y_acceleration_text, 0]).to_edge(RIGHT)
        # acceleration_tex_to_annotation_arrow: start from right of acceleration and end at top of acceleration_text
        acceleration_tex_to_annotation_arrow = CurvedArrow(
            acceleration_tex.get_right() + RIGHT * 0.1,
            acceleration_tex_annotation.get_top() + UP * 0.1,
            color=GREEN,
            tip_length=0.15,
            angle=-PI / 2,  # Flip the direction of the arc
        )
        
        equation_annotation_group = VGroup(
            force_tex_annotation,
            force_tex_to_annotation_arrow,
            mass_tex_annotation,
            mass_tex_to_annotation_arrow,
            acceleration_tex_annotation,
            acceleration_tex_to_annotation_arrow,
        )

        self.play(
            GrowFromPoint(equation_annotation_group, second_law_equation.get_bottom().shift(DOWN * 0.5)),
        )
        self.wait(2)
        
        acceleration_note = (
            Text("Note: Acceleration is actually the rate at which velocity changes.", t2c={"velocity": BLUE})
            .scale(0.5)
            .move_to([0, y_acceleration_note, 0])
        )
        acceleration_note_2 = (
            Text("Velocity is the rate at which position changes.", t2c={"position": BLUE})
            .scale(0.5)
            .move_to([0, y_acceleration_note - 0.5, 0])
        )
        acceleration_note_3 = (
            Text("Rate of change of position depends on both the speed and the direction in which it is moving.", t2c={"speed": BLUE, "direction": BLUE})
            .scale(0.5)
            .move_to([0, y_acceleration_note - 1, 0])
        )
        acceleration_note_4 = (
            Text("Therefore, acceleration depends not only on change in speed, but also change in direction of the body.", t2c={"simplified": BLUE})
            .scale(0.5)
            .move_to([0, y_acceleration_note - 1.5, 0])
        )
        
        """
        
        final_text = (
            Text(
            "That's the gist of Newton's second law of motion.",
            line_spacing=1,
            )
            .scale(0.5)
            .move_to([-6.5, 0, 0], aligned_edge=LEFT)
        )

        self.play(Write(final_text))
        self.wait(3)
        
        

    def fma_animation(
        self,
        small_mass_mobject,
        large_mass_mobject,
        small_mass_density,
        large_mass_density,
        small_mass_force,
        large_mass_force,
        run_time=4,
        remove_pymunk_objects=True,
    ):
        force_updater_small = lambda mob, dt: apply_force(mob, small_mass_force, dt)
        start_point, end_point = get_points_for_push_force_on_circle(
            small_mass_mobject, PI, small_mass_force
        )
        force_arrow_small = Arrow(
            start=start_point,
            end=end_point,
            buff=0,
            stroke_width=self.arrow_stroke_width,
            tip_length=self.arrow_tip_length,
        )
        force_arrow_small.set_color(YELLOW)
        force_arrow_updater_small = lambda arrow: update_force_arrow(
            arrow, small_mass_mobject, small_mass_force
        )

        force_updater_large = lambda mob, dt: apply_force(mob, large_mass_force, dt)
        start_point, end_point = get_points_for_push_force_on_circle(
            large_mass_mobject, PI, large_mass_force
        )
        force_arrow_large = Arrow(
            start=start_point,
            end=end_point,
            buff=0,
            stroke_width=self.arrow_stroke_width,
            tip_length=self.arrow_tip_length,
        )
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
        force_arrow_large.remove_updater(
            force_arrow_updater_large
        )  # Remove the updater
        small_mass_mobject.remove_updater(
            force_updater_small
        )  # Stop applying the force
        force_arrow_small.remove_updater(force_arrow_updater_small)
        self.stop_rigidity(small_mass_mobject, large_mass_mobject)

        self.wait(2)

        self.play(FadeOut(force_arrow_large, force_arrow_small))
        
        # self.remove_mobject_if_exists(force_arrow_small, force_arrow_large)
        if remove_pymunk_objects:
            # Don't play FadeOut for mobjects having updaters, especially pymunk objects
            # Otherwise, it will throw an error - pickling/threading error
            self.remove_mobject_if_exists(
                small_mass_mobject, large_mass_mobject, force_arrow_small, force_arrow_large
            )
        else: # return mojects to be removed later
            return small_mass_mobject, large_mass_mobject, force_arrow_small, force_arrow_large
        

    def remove_mobject_if_exists(self, *mobjects):
        for mobject in mobjects:
            if mobject in self.mobjects:
                self.remove(mobject)
