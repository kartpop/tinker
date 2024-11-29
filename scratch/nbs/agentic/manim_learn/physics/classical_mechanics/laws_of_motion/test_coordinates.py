from manim import *

class CompleteGridExample(Scene):
    def construct(self):
        # Create a NumberPlane with grid lines
        grid = NumberPlane(
            x_range=[-7, 7, 1],
            y_range=[-4, 4, 1],
            background_line_style={
                "stroke_opacity": 0,
            }
        )
        grid.axes.set_stroke(opacity=0)
        self.add(grid)

        # Add dots at each grid intersection
        for x in range(-7, 8):
            for y in range(-4, 5):
                dot = Dot(point=grid.coords_to_point(x, y), radius=0.05, color=WHITE)
                self.add(dot)

        # Position shapes at specific grid points
        circle = Circle(radius=0.3, color=YELLOW).move_to(grid.coords_to_point(3, 2))
        square = Square(side_length=0.5, color=RED).move_to(grid.coords_to_point(-2, -1))
        triangle = Triangle(color=GREEN).move_to(grid.coords_to_point(0, 0))

        self.add(circle, square, triangle)
        self.wait(2)