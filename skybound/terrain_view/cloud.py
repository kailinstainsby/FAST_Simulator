"""Terrain cloud with pseudo-3D perspective growth and lateral drift.

Clouds spawn near the horizon and grow exponentially as they "approach"
the viewer, drifting laterally away from the screen centre to simulate
forward flight.  When the aircraft banks (rotation), clouds are
translated to maintain the perspective illusion.
"""

from __future__ import annotations

import math
import os

import pygame

from skybound.config import (
    CLOUD_LINEAR_GROWTH,
    MAX_OBJECT_SIZE,
    PERSPECTIVE_DRIFT_DIVISOR,
    PERSPECTIVE_GROWTH_BASE,
    PERSPECTIVE_GROWTH_DAMPEN,
    ROTATION_TRANSLATION_FACTOR,
    TER_CLOUD_INITIAL_HEIGHT,
    TER_CLOUD_INITIAL_WIDTH,
    TER_SCREEN_WIDTH,
    TERRAIN_ASSETS,
    Y_DAMPEN,
)

_SPRITE_PATH = os.path.join(TERRAIN_ASSETS, "cloud.png")


class TerrainCloud:
    """A cloud that grows and drifts to simulate a 3-D fly-through.

    Parameters
    ----------
    spawn_x : int
        Horizontal spawn position (pixels from left edge).
    spawn_y : int
        Vertical position at spawn (typically the horizon line).
    """

    def __init__(self, spawn_x: int, spawn_y: int) -> None:
        self._image = pygame.image.load(_SPRITE_PATH).convert_alpha()
        self.x: float = spawn_x
        self.y: float = spawn_y
        self.x_size: float = TER_CLOUD_INITIAL_WIDTH
        self.y_size: float = TER_CLOUD_INITIAL_HEIGHT

    # ------------------------------------------------------------------
    # Per-frame update
    # ------------------------------------------------------------------

    def move(self) -> None:
        """Advance the cloud one frame: lateral drift + exponential growth.

        Lateral drift is proportional to the cloud's distance from the
        horizontal centre, simulating objects drifting outward as the
        aircraft flies forward.

        Growth follows: ``0.01 * exp(BASE * size - DAMPEN * size) + linear``
        which produces gentle initial growth that accelerates as the
        object "approaches" the camera.
        """
        # Lateral drift from screen centre
        self.x += (self.x - TER_SCREEN_WIDTH / 2) / PERSPECTIVE_DRIFT_DIVISOR

        # Exponential perspective growth (capped to prevent runaway)
        growth_exp = PERSPECTIVE_GROWTH_BASE - PERSPECTIVE_GROWTH_DAMPEN
        self.x_size += 0.01 * math.exp(growth_exp * self.x_size) + CLOUD_LINEAR_GROWTH
        self.y_size += 0.01 * math.exp(growth_exp * self.y_size) + CLOUD_LINEAR_GROWTH

        self.x_size = min(self.x_size, MAX_OBJECT_SIZE)
        self.y_size = min(self.y_size, MAX_OBJECT_SIZE)

    def apply_rotation(self, rotation_angle: float) -> None:
        """Translate the cloud to follow the camera's banking rotation.

        Parameters
        ----------
        rotation_angle : float
            Current rotation of the terrain view in degrees.
        """
        if rotation_angle == 0:
            return

        angle_rad = math.radians(rotation_angle)
        y_sign = -1.0 if rotation_angle > 0 else 1.0

        self.x += self.x * math.cos(angle_rad) * ROTATION_TRANSLATION_FACTOR
        self.y -= (
            self.y * math.sin(angle_rad) * ROTATION_TRANSLATION_FACTOR
            + y_sign * Y_DAMPEN
        )

    # ------------------------------------------------------------------
    # Drawing
    # ------------------------------------------------------------------

    def draw(self, surface: pygame.Surface, rotation_angle: float) -> None:
        """Render the cloud scaled to its current perspective size."""
        scaled = pygame.transform.smoothscale(
            self._image,
            (int(self.x_size), max(1, int(self.y_size))),
        )
        rotated = pygame.transform.rotate(scaled, rotation_angle)
        surface.blit(rotated, (self.x, self.y))

    # ------------------------------------------------------------------
    # Off-screen test
    # ------------------------------------------------------------------

    def is_off_screen(self) -> bool:
        """Return ``True`` when the cloud has drifted beyond visible area."""
        return self.x > TER_SCREEN_WIDTH or self.x + self.x_size < 0
