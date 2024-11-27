from typing import Tuple
from manim import *
from manim.mobject.opengl.opengl_compatibility import ConvertToOpenGL
import pymunk

class Space(Mobject, metaclass=ConvertToOpenGL):
    def __init__(self, gravity: Tuple[float, float] = (0, -9.81), **kwargs):
        """An Abstract object for gravity.

        Parameters
        ----------
        gravity
            The direction and strength of gravity.
        """
        super().__init__(**kwargs)
        self.space = pymunk.Space()
        self.space.gravity = gravity
        self.space.sleep_time_threshold = 5
        
class SpaceScene(Scene):
    GRAVITY: Tuple[float, float] = 0, 0

    def __init__(self, renderer=None, **kwargs):
        """A basis scene for all of rigid mechanics. The gravity vector
        can be adjusted with ``self.GRAVITY``.
        """
        self.space = Space(gravity=self.GRAVITY)
        super().__init__(renderer=renderer, **kwargs)

    def setup(self):
        """Used internally"""
        self.add(self.space)
        self.space.add_updater(_step)

    def add_body(self, body: Mobject):
        """Bodies refer to pymunk's object.
        This method ties Mobjects to their Bodies.
        """
        if body.body != self.space.space.static_body:
            self.space.space.add(body.body)
        self.space.space.add(body.shape)
        
    def remove_body(self, body: Mobject):
        """Bodies refer to pymunk's object.
        This method removes Mobjects from the space.
        """
        if body.body != self.space.space.static_body:
            self.space.space.remove(body.body)
        self.space.space.remove(body.shape)

    def make_rigid_body(
        self,
        *mobs: Mobject,
        elasticity: float = 0.8,
        density: float = 1,
        friction: float = 0.8,
        collision_type: int = 1,
    ):
        """Make any mobject movable by gravity.
        Equivalent to ``Scene``'s ``add`` function.

        Parameters
        ----------
        mobs
            The mobs to be made rigid.
        elasticity
        density
        friction
            The attributes of the mobjects in regards to
            interacting with other rigid and static objects.
        """
        for mob in mobs:
            if not hasattr(mob, "body"):
                self.add(mob)
                mob.body = pymunk.Body()
                mob.body.position = mob.get_x(), mob.get_y()
                get_angle(mob)
                if not hasattr(mob, "angle"):
                    mob.angle = 0
                mob.body.angle = mob.angle
                get_shape(mob)
                mob.shape.density = density
                mob.shape.elasticity = elasticity
                mob.shape.friction = friction
                mob.shape.collision_type = collision_type
                mob.spacescene = self

                self.add_body(mob)
                mob.add_updater(_simulate)

            else:
                if mob.body.is_sleeping:
                    mob.body.activate()

    def make_static_body(
        self, *mobs: Mobject, elasticity: float = 1, friction: float = 0.8, collision_type: int = 0
    ) -> None:
        """Make any mobject interactable by rigid objects.

        Parameters
        ----------
        mobs
            The mobs to be made static.
        elasticity
        friction
            The attributes of the mobjects in regards to
            interacting with rigid objects.
        """
        for mob in mobs:
            if isinstance(mob, VGroup or Group):
                return self.make_static_body(*mob)
            mob.body = self.space.space.static_body
            get_shape(mob)
            mob.shape.elasticity = elasticity
            mob.shape.friction = friction
            mob.shape.collision_type = collision_type
            self.add_body(mob)

    def stop_rigidity(self, *mobs: Mobject, remove_from_pymunk_space: bool=True) -> None:
        """Stop the mobjects rigidity"""
        for mob in mobs:
            if isinstance(mob, VGroup or Group):
                self.stop_rigidity(*mob)
            if hasattr(mob, "body"):
                mob.body.sleep()
                if remove_from_pymunk_space:
                    # Remove the mobject from the pymunk space and any pymunk references from the mobject
                    self.remove_body(mob)
                    mob.shape = None # Remove the pymunk shape from the mobject
                    mob.body = None # Remove the pymunk body from the mobject
                    mob.remove_updater(_simulate)
    
    def remove_and_replace(self, mob: Mobject) -> Mobject:
        """Remove the mobjects from the scene and replace them with an identical new mobject. Effects such as FadeOut don't work on orignal mobjects"""
        new_mob = mob.copy()
        self.remove(mob)
        self.add(new_mob)
        return new_mob
                
    def add_collision_handler(self, collision_callback, collision_type_a: int = 0, collision_type_b: int = 1):
        """Add a collision handler to the space"""
        h = self.space.space.add_collision_handler(collision_type_a, collision_type_b)
        h.begin = begin
        h.pre_solve = collision_callback
        h.post_solve = post_solve
        h.separate = separate
    
def begin(arbiter, space, data):
    return True

def pre_solve(arbiter, space, data):
    pass

def post_solve(arbiter, space, data):
    pass

def separate(arbiter, space, data):
    pass
    

def _step(space, dt):
    space.space.step(dt)


def _simulate(b):
    x, y = b.body.position
    b.move_to(x * RIGHT + y * UP)
    b.rotate(b.body.angle - b.angle)
    b.angle = b.body.angle


def get_shape(mob: VMobject) -> None:
    """Obtains the shape of the body from the mobject"""
    if isinstance(mob, Circle):
        mob.shape = pymunk.Circle(body=mob.body, radius=mob.radius)
    elif isinstance(mob, Line):
        mob.shape = pymunk.Segment(
            mob.body,
            (mob.get_start()[0], mob.get_start()[1]),
            (mob.get_end()[0], mob.get_end()[1]),
            mob.stroke_width - 3.95,
        )
    elif issubclass(type(mob), Rectangle):
        width = np.linalg.norm(mob.get_vertices()[1] - mob.get_vertices()[0])
        height = np.linalg.norm(mob.get_vertices()[2] - mob.get_vertices()[1])
        mob.shape = pymunk.Poly.create_box(mob.body, (width, height))
    elif issubclass(type(mob), Polygram):
        vertices = [(a, b) for a, b, _ in mob.get_vertices() - mob.get_center()]
        mob.shape = pymunk.Poly(mob.body, vertices)
    else:
        mob.shape = pymunk.Poly.create_box(mob.body, (mob.width, mob.height))


def get_angle(mob: VMobject) -> None:
    """Obtains the angle of the body from the mobject.
    Used internally for updaters.
    """
    if issubclass(type(mob), Polygon):
        vec1 = mob.get_vertices()[0] - mob.get_vertices()[1]
        vec2 = type(mob)().get_vertices()[0] - type(mob)().get_vertices()[1]
        mob.angle = angle_between_vectors(vec1, vec2)
    elif isinstance(mob, Line):
        mob.angle = mob.get_angle()
