from time import time

import arcade
from pyglet.math import Vec2

import assets
from game.entities.player import Player
from game.entities.enemy import Enemy
from game.sounds import change_music
from game.views import change_views, return_to_view
from game.views.inventory import Item, Door, get_inventory_ui

arcade.enable_timings()


class GameView(arcade.View):
    """The game window"""

    def __init__(self, level):
        super().__init__()

        # declare objects and entities
        self.cur_item = None
        self.walls = None
        self.floor = None
        self.objects = None
        self.pickables = None
        self.doors = None
        self.player = None
        self.physics_engine = None
        self.start_time = None
        self.bgm = None

        # special purpose bgm
        self.bgm2 = None

        # in game text popup
        self.display_text = ""

        # movement states
        self.movement = Vec2(0, 0)
        self.mouse_pos = Vec2(0, 0)

        # sprite lists
        self.enemies = arcade.SpriteList()
        self.wall_list = arcade.SpriteList()

        # Setup camera
        self.scene_camera = arcade.Camera(*self.window.size)
        self.gui_camera = arcade.Camera(*self.window.size)
        # select the level
        self.select_level(level)

    def select_level(self, level: int = 1):
        """Select the level and set up the game view"""

        # use_guided_path = True

        # if guided path is used, enemies get stuck to the wall...
        # if not used, the enemies just fly past like jets!!? huh? fixme

        # Fixed you. enemies never get stuck to wall.
        # No need of physics engine for enemies. Game runs faster
        # I'll let you choose what to keep

        # let's use guided path

        level_map = arcade.TileMap(
            assets.tilemaps.resolve(f"level{level}.tmx"),
            use_spatial_hash=True,
        )
        self.window.level = level

        # place objects
        self.floor = level_map.sprite_lists["floor"]
        self.walls = level_map.sprite_lists["walls"]
        self.objects = level_map.sprite_lists["objects"]
        self.doors = arcade.SpriteList(use_spatial_hash=True)
        self.pickables = arcade.SpriteList(use_spatial_hash=True)

        for item in level_map.sprite_lists["pickables"]:
            self.pickables.append(
                Item(
                    item.properties["file"],
                    Vec2(*item.position),
                    item.angle,
                    name_color=item.properties.get("name_color"),
                )
            )

        for door in level_map.sprite_lists["doors"]:
            self.doors.append(
                Door(
                    door.properties["file"],
                    Vec2(*door.position),
                    door.angle,
                    name_color=door.properties["name_color"],
                )
            )

        # Set up the player
        self.player = Player(self)
        self.player.position = level_map.sprite_lists["player"][0].position
        self.window.player = self.player

        # Set up the enemies
        arrows = level_map.sprite_lists["arrows"]
        barriers = [self.walls, self.objects]

        for enemy in level_map.sprite_lists["enemies"]:
            e = Enemy(
                initial_pos=enemy.position,
                arrows=arrows,
                barriers=barriers,
                game_view=self,
            )
            self.enemies.append(e)

        # Create physics engine for collision
        self.physics_engine = arcade.PhysicsEngineSimple(
            self.player, barriers + [self.enemies]
        )

        # Start time
        self.start_time = time()

    def attach_inventory(self):
        self.window.views["InventoryView"] = {
            # Shows the inventory
            "keys": return_to_view("GameView"),
            "color": arcade.color.BLACK,
            "ui": get_inventory_ui(self.window),
        }
        return self

    def update_inventory(self):
        self.attach_inventory()

    def clear_inventory(self):
        self.window.inventory.clear()

    def remove_enemy_from_world(self, enemy: Enemy):
        self.enemies.remove(enemy)

    def set_display_text(self, text: str):
        self.display_text = text

    def on_show_view(self):
        """This is run once when we switch to this view"""

        # set game background
        arcade.set_background_color(arcade.csscolor.BLACK)

        # Reset the viewport, necessary if we have a scrolling game and we need
        # to reset the viewport back to the start so we can see what we draw.
        arcade.set_viewport(0, self.window.width, 0, self.window.height)
        self.window.bgm = change_music(
            self.window,
            self.window.bgm,
            assets.sounds.horror,
            looping=True,
            volume=0.2,
            speed=0.5,
        )
        if self.bgm is None:
            self.bgm = change_music(
                self.window, self.bgm, assets.sounds.heart, volume=0.6, looping=True
            )
            # self.bgm2 = change_music(self.window, self.bgm2,
            # assets.sounds.insomnia, volume=0.2, looping=True)
        else:
            self.bgm.play()
            # self.bgm2.play()

    def on_hide_view(self):
        self.bgm.pause()
        # self.bgm2.pause()

    def screen_to_world_point(self, screen_point: Vec2):
        return screen_point + self.scene_camera.position

    def on_mouse_motion(self, x: int, y: int, dx: int, dy: int):
        # Use the mouse to look around
        self.mouse_pos.x, self.mouse_pos.y = x, y

    def on_update(self, delta_time: float):
        self.player.move(self.movement, self.screen_to_world_point(self.mouse_pos))
        self.player.update_player()
        cam_pos = Vec2(
            self.player.center_x - self.window.width / 2,
            self.player.center_y - self.window.height / 2,
        )
        self.scene_camera.move_to(cam_pos)
        self.physics_engine.update()

        # if player is close to enemy update movement
        for enemy in self.enemies:
            if enemy.is_close_to_player(self.player.get_position()):
                enemy.chase_player(self.player.get_position())
            else:
                enemy.back_to_patrolling()

        self.enemies.update()

    def gameover(self):
        self.clear_inventory()
        self.window.views["GameView"] = self.window.get_level_view(1)
        change_views(self.window, "GameOver")

    def on_key_press(self, symbol: int, modifiers: int):
        """Handle Keyboard Input."""

        # Navigate with WASD or Arrow keys

        match symbol:
            case arcade.key.DOWN | arcade.key.S:
                self.movement.y = -1
            case arcade.key.UP | arcade.key.W:
                self.movement.y = 1
            case arcade.key.LEFT | arcade.key.A:
                self.movement.x = -1
            case arcade.key.RIGHT | arcade.key.D:
                self.movement.x = 1
            case arcade.key.Q:
                self.player.attack()
            case arcade.key.G:
                self.gameover()
            case arcade.key.I:
                assets.sounds.click.play(volume=self.window.sfx_vol)
                change_views(self.window, "InventoryView")
            case arcade.key.F:
                if self.cur_item:
                    assets.sounds.click.play(volume=self.window.sfx_vol)
                    self.display_text = ""
                    self.window.inventory.add_item(self.cur_item)
                    self.update_inventory()
                    self.cur_item = None
            case arcade.key.ESCAPE:
                assets.sounds.click.play(volume=self.window.sfx_vol)
                change_views(self.window, "Pause")

        # add fail-check
        self.movement.clamp(-1, 1)

    def on_key_release(self, symbol: int, modifiers: int):
        match symbol:
            case arcade.key.DOWN | arcade.key.S:
                self.movement.y = 0
            case arcade.key.UP | arcade.key.W:
                self.movement.y = 0
            case arcade.key.LEFT | arcade.key.A:
                self.movement.x = 0
            case arcade.key.RIGHT | arcade.key.D:
                self.movement.x = 0

            # add fail-check
        self.movement.clamp(-1, 1)

    def on_draw(self):
        """Draw this view"""

        # clean view
        self.clear()

        self.scene_camera.use()
        if self.floor is not None:
            self.floor.draw()
        self.doors.draw()
        self.walls.draw()
        if self.objects is not None:
            self.objects.draw()
        if self.pickables is not None:
            self.pickables.draw()
        self.enemies.draw()

        # TODO: remove from final, for debug
        # if self.enemies[0].arrows:
        #     for i in self.enemies[0].arrows:
        #         i.draw_hit_box()

        self.player.draw()

        # Add GUI
        self.gui_camera.use()
        arcade.Text(
            f"Health: 100, Time: "
            f"{':'.join(map(lambda x: f'{int(x):02d}', divmod(time() - self.start_time, 60)))}",
            self.window.width - 200,
            self.window.height - 25,
        ).draw()
        arcade.Text(
            f"FPS: {int(arcade.get_fps())}",
            20,
            self.window.height - 25,
        ).draw()
        arcade.Text("Press ESC to pause; press I to enter the inventory", 10, 10).draw()
        arcade.Text(
            self.display_text,
            0,
            self.window.height / 2 + 100,
            width=self.window.width,
            align="center",
            font_size=24,
            bold=True,
            color=arcade.color.WHITE,
        ).draw()
