# FAULTY
## self.space_step() is not a valid method in SpaceScene


prompt = """

Generate manim code for a physics simulation that demonstrates object motion and collision. You can make these assumptions:
- `space.py` is available to import from
- manim library is available to import from
- focus only on the Scene/SpaceScene implementation

The scene should show:
1. A stationary ball 
2. Force application (shown with arrow)
3. Ball moving with constant velocity
4. Ball collision with wall
5. Animation continuing for 2 seconds after collision
6. Stop

Here are relevant code patterns to follow:

1. For creating and setting up the circle:
```python
circle = Circle().shift(LEFT * 0.5 + DOWN * 2)
circle.set_fill(ORANGE, opacity=0.5)
self.play(FadeIn(circle))
self.make_rigid_body(circle)
```

2. For creating wall:
```python
wall = Line([5.5, -3.5, 0], [5.5, 3.5, 0])
self.add(wall)
self.make_static_body(wall)
```

3. For applying force with arrow visualization:
```python
def get_points_for_push_force_on_circle(circle: Circle, angle):
    end_point = circle.point_at_angle(angle)
    circle_center = circle.get_center()
    force_direction = circle_center - end_point
    force_direction = force_direction / np.linalg.norm(force_direction)
    start_point = end_point - force_direction
    return start_point, end_point

def get_force_components(angle, magnitude):
    return magnitude * np.cos(angle), magnitude * np.sin(angle)

# Usage example:
angle = PI + PI / 6
magnitude = 2
start_point, end_point = get_points_for_push_force_on_circle(circle, angle)
force_x, force_y = get_force_components(angle - PI, magnitude)
force_arrow = Arrow(start=start_point, end=end_point, buff=0)
force_arrow.set_color(YELLOW)
self.play(Create(force_arrow))
circle.body.apply_impulse_at_local_point((force_x, force_y))
```

4. For collision detection:
```python
def collision_callback(self, arbiter, space, data):
    cps = arbiter.contact_point_set
    if len(cps.points) > 0:
        self.collision_occurred = True
        self.collision_normal = cps.normal
    return True

# Add collision handler:
self.add_collision_handler(collision_callback=self.collision_callback)
```

Keep the implementation minimal and focused on these core elements. The final animation should run for about 2 seconds after the collision occurs. 

IMPORTANT: Only output the complete code with the necessary imports and the class implementation inside the ```python``` code block. Do not include any other context or explanation in the response.   

"""

code = """
```python
from manim import *
from manimator.lib.space import SpaceScene
import numpy as np

class PhysicsCollisionDemo(SpaceScene):
    def construct(self):
        # Set up scene
        self.collision_occurred = False
        
        # Create circle
        circle = Circle().shift(LEFT * 3 + DOWN * 0.5)
        circle.set_fill(ORANGE, opacity=0.5)
        self.play(FadeIn(circle))
        self.make_rigid_body(circle)
        
        # Create wall
        wall = Line([5.5, -3.5, 0], [5.5, 3.5, 0])
        self.add(wall)
        self.make_static_body(wall)
        
        # Add collision handler
        self.add_collision_handler(collision_callback=self.collision_callback)
        
        # Apply force with arrow visualization
        angle = PI + PI / 6
        magnitude = 2
        start_point, end_point = self.get_points_for_push_force_on_circle(circle, angle)
        force_x, force_y = self.get_force_components(angle - PI, magnitude)
        
        force_arrow = Arrow(start=start_point, end=end_point, buff=0)
        force_arrow.set_color(YELLOW)
        self.play(Create(force_arrow))
        
        # Apply force and remove arrow
        circle.body.apply_impulse_at_local_point((force_x, force_y))
        self.play(FadeOut(force_arrow))
        
        # Run simulation until collision and 2 seconds after
        while not self.collision_occurred:
            self.space_step()
            self.wait(1/60)
            
        # Continue for 2 more seconds after collision
        end_time = self.time + 2
        while self.time < end_time:
            self.space_step()
            self.wait(1/60)

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
```
"""