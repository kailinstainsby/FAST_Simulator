"""Plane Minigame — embeddable runner for the cloud-dodging side-panel.

All mutable game state is encapsulated inside :class:`PlaneMinigame` so that
the terrain-view game loop can instantiate, update, and read scores without
relying on module-level globals.
"""

from __future__ import annotations

import random
from typing import List

import pygame

from skybound.config import (
    BLACK,
    DIFFICULTY_PRESETS,
    PM_CLOUD_SPACING,
    PM_COLLISION_COOLDOWN_MS,
    PM_PANEL_HEIGHT,
    PM_PLANE_HEIGHT,
    WALL_SPAWN_THRESHOLD,
    load_difficulty,
)
from skybound.plane_minigame.cloud import Cloud
from skybound.plane_minigame.plane import Plane


class PlaneMinigame:
    """Self-contained plane-minigame that renders onto a provided surface.

    Parameters
    ----------
    difficulty : int, optional
        Difficulty level (1–5).  Defaults to the value in *difficulty.txt*.
    """

    def __init__(self, difficulty: int | None = None) -> None:
        self._difficulty = difficulty if difficulty is not None else load_difficulty()
        preset = DIFFICULTY_PRESETS.get(self._difficulty, DIFFICULTY_PRESETS[3])
        self._spawn_rate = preset.cloud_spawn_rate
        self._spawn_chance = preset.cloud_spawn_chance

        self.plane = Plane()
        self.clouds: List[Cloud] = []
        self.collisions: int = 0

        self._spawn_timer: int = 0
        self._last_collision_time: int = 0

    # ------------------------------------------------------------------
    # Cloud spawning
    # ------------------------------------------------------------------

    def _spawn_clouds(self, surface_width: int) -> None:
        """Spawn a new wave of clouds at the right edge of the surface."""
        gap_height = PM_PLANE_HEIGHT + 50
        gap_start = random.randint(0, PM_PANEL_HEIGHT - gap_height)

        if self._difficulty >= WALL_SPAWN_THRESHOLD:
            # Wall-with-gap pattern for higher difficulties
            for y in range(0, PM_PANEL_HEIGHT, PM_CLOUD_SPACING):
                if not (gap_start <= y < gap_start + gap_height):
                    if random.random() < self._spawn_chance:
                        self.clouds.append(Cloud(surface_width, y))
        else:
            # Horizontal row pattern for lower difficulties
            row_y = random.randint(0, PM_PANEL_HEIGHT // PM_CLOUD_SPACING) * PM_CLOUD_SPACING
            count = random.randint(2, 8)
            for i in range(count):
                self.clouds.append(
                    Cloud(surface_width + i * PM_CLOUD_SPACING, row_y)
                )

    # ------------------------------------------------------------------
    # Per-frame update
    # ------------------------------------------------------------------

    def update(self, surface: pygame.Surface) -> None:
        """Run one frame of game logic and render onto *surface*.

        This method handles input, cloud spawning, movement, collision
        detection, and drawing — everything needed for the embedded panel.
        """
        surface_width = surface.get_width()

        # Player input
        self.plane.handle_input()

        # Cloud spawning
        self._spawn_timer += 1
        if self._spawn_timer > self._spawn_rate:
            self._spawn_clouds(surface_width)
            self._spawn_timer = 0

        current_time = pygame.time.get_ticks()

        # Move clouds & check collisions
        for cloud in self.clouds[:]:  # iterate over a copy to allow removal
            cloud.move()
            if cloud.is_off_screen():
                self.clouds.remove(cloud)
                continue

            # Collision detection with cooldown
            if current_time - self._last_collision_time > PM_COLLISION_COOLDOWN_MS:
                if self.plane.collides_with(cloud.hitbox):
                    self.collisions += 1
                    self._last_collision_time = current_time
                    self.plane.start_flicker()

        # Draw
        surface.fill(BLACK)
        self.plane.update_flicker()
        self.plane.draw(surface)

        for cloud in self.clouds:
            cloud.draw(surface)
