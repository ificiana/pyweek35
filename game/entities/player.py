import math

from pyglet.math import Vec2

from game.entities import Entity
from game.views.inventory import Inventory


class Player(Entity):
    def __init__(self, game_view):
        super().__init__("mc_idle.png")
        self.center_x, self.center_y = Vec2(0, 0)
        self.angle = -90
        self.normal_speed = 4.0
        self.speed = self.normal_speed
        self.game_view = game_view
        self.inventory = Inventory()
        self.enemy_touch_count = 0

    def update_animation(self, delta_time: float = 1 / 60):
        pass

    def move(self, delta_pos: Vec2, mouse_pos: Vec2):
        direction = mouse_pos - self.get_position()
        if direction.mag != 0:
            direction = direction.normalize()
            self.angle = math.degrees(direction.heading)
        self.center_x += delta_pos.x * self.speed
        self.center_y += delta_pos.y * self.speed

    def update_player(self):
        nearest_item, nearest_dist = None, 99999
        for item in self.game_view.pickables:
            distance = self.get_position() - item.get_position()
            if distance.mag < nearest_dist:
                nearest_dist = distance.mag
                nearest_item = item
        if nearest_item is not None and nearest_dist < 64:
            self.game_view.set_display_text("Press F to pick up")
            self.game_view.cur_item = nearest_item
        else:
            self.game_view.cur_item = None
            self.game_view.set_display_text("")

        self.hit_by_enemy()

    def hit_by_enemy(self):
        enemies_touching_playing = len(self.collides_with_list(self.game_view.enemies))
        if enemies_touching_playing >= 2:
            self.game_view.gameover()
        elif enemies_touching_playing >= 1:
            self.change_speed(slow_factor=0.5)
        else:
            self.change_speed(slow_factor=1)

    def attack(self):
        nearest_enemy, nearest_dist = None, 99999
        for enemy in self.game_view.enemies:
            distance = self.get_position() - enemy.get_position()
            if distance.mag < nearest_dist:
                nearest_dist = distance.mag
                nearest_enemy = enemy
        if nearest_enemy is not None and nearest_dist < 64 * 1.5:
            # TODO: Play attack animation
            nearest_enemy.take_damage(25)
            if nearest_enemy.health > 0:
                self.change_speed(0.5)
            else:
                self.change_speed(1)
            self.enemy_touch_count += 1

    def change_speed(self, slow_factor: float = 0.25):
        """1.0 for normal speed and 0.0 for complete stop"""
        self.speed = self.normal_speed * slow_factor
