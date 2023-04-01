import random
from pyglet.math import Vec2
from game.config import SCREEN_WIDTH, SCREEN_HEIGHT
from game.entities import Entity


class Enemy(Entity):
    def __init__(self, initial_pos, game_view, barriers, arrows=None):
        super().__init__("enemy.png")
        self.speed = 1.8
        self.health = 100
        self.game_view = game_view
        self.position = initial_pos
        self.rng = random.Random(f"{str(self.position)}1")
        self.arrows = arrows
        self.is_inside_view = True
        if arrows:
            (
                self.arrows_left,
                self.arrows_right,
                self.arrows_up,
                self.arrows_down,
            ) = arrows
        self.movement = Vec2(0, 0)
        self.state = 300

        if self.arrows:
            if self.collides_with_list(self.arrows_up):
                self.movement = Vec2(0, 1)
            elif self.collides_with_list(self.arrows_down):
                self.movement = Vec2(0, -1)
            elif self.collides_with_list(self.arrows_left):
                self.movement = Vec2(-1, 0)
            elif self.collides_with_list(self.arrows_right):
                self.movement = Vec2(1, 0)

        self.collision_radius = 2

    def move(self, reverse=False):
        if not self.is_inside_view:
            return
        n = Vec2(-1, -1) if reverse else Vec2(1, 1)
        if self.arrows:
            pos = Vec2(*self.position)
            self.position = pos + n * self.movement * Vec2(self.speed, self.speed)
        else:
            if self.state:
                if not self.state % 300:
                    self.angle = self.rng.choice(
                        [0, 45, 90, 135, 180, 225, 270, 315, 360]
                    )
                self.state -= 1
            else:
                self.state = 300
            self.forward(self.speed)

    def take_damage(
        self,
        amount: int = 20,
    ):
        self.health -= amount
        print(self.health)
        if self.health <= 0:
            print("DEATH")
            self.game_view.remove_enemy_from_world(self)

    def is_within_view(self):
        campos = self.game_view.scene_camera.position
        offset = Vec2(SCREEN_WIDTH / 1.8, SCREEN_HEIGHT / 1.8)
        if (
            self.center_x > campos.x + SCREEN_WIDTH / 2 + offset.x
            or self.center_x < campos.x + SCREEN_WIDTH / 2 - offset.x
            or self.center_y > campos.y + SCREEN_HEIGHT / 2 + offset.y
            or self.center_y < campos.y + SCREEN_HEIGHT / 2 - offset.y
        ):
            self.is_inside_view = False
        else:
            self.is_inside_view = True
        return self.is_inside_view

    def update(self):
        self.is_within_view()
        if not self.is_inside_view:
            return
        if self.arrows:
            if self.collides_with_list(self.arrows_up):
                self.movement = Vec2(0, 1)
            elif self.collides_with_list(self.arrows_down):
                self.movement = Vec2(0, -1)
            elif self.collides_with_list(self.arrows_left):
                self.movement = Vec2(-1, 0)
            elif self.collides_with_list(self.arrows_right):
                self.movement = Vec2(1, 0)

        self.move()
