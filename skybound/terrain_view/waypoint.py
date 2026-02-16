"""Waypoint markers that appear along the flight path.

Waypoints spawn on the horizon and grow/drift with the same pseudo-3D
perspective system as terrain clouds.  Each waypoint has a type that
determines its sprite and is recorded for post-game recall questions.
"""

from __future__ import annotations

import math
import os

import pygame

from skybound.config import (
    MAX_OBJECT_SIZE,
    PERSPECTIVE_DRIFT_DIVISOR,
    PERSPECTIVE_GROWTH_BASE,
    PERSPECTIVE_GROWTH_DAMPEN,
    ROTATION_TRANSLATION_FACTOR,
    TER_SCREEN_WIDTH,
    TERRAIN_ASSETS,
    WAYPOINT_LINEAR_GROWTH,
    WAYPOINT_SPAWN_Y,
    Y_DAMPEN,
)

# Sprite filenames indexed by waypoint type  (note: type 2 has a legacy typo)
_WAYPOINT_SPRITES = {
    0: "waypoint0.png",
    1: "waypoint1.png",
    2: "wapoint2.png",  # original filename preserved
}


class Waypoint:
    """A waypoint marker that grows with pseudo-3D perspective.

    Parameters
    ----------
    x_pos : int
        Horizontal spawn position.
    waypoint_type : int
        Visual variant (0, 1, or 2) — also used for recall quiz scoring.
    """

    def __init__(self, x_pos: int, waypoint_type: int) -> None:
        sprite_file = _WAYPOINT_SPRITES.get(waypoint_type, _WAYPOINT_SPRITES[2])
        sprite_path = os.path.join(TERRAIN_ASSETS, sprite_file)
        self._image = pygame.image.load(sprite_path).convert_alpha()

        self.x_pos: float = x_pos
        self.y_pos: float = WAYPOINT_SPAWN_Y
        self.x_size: float = 30.0
        self.y_size: float = 30.0

    # ------------------------------------------------------------------
    # Per-frame update
    # ------------------------------------------------------------------

    def move(self) -> None:
        """Advance position using perspective drift and exponential growth.

        Uses the same mathematical model as terrain clouds but with a
        lower linear-growth rate (``WAYPOINT_LINEAR_GROWTH``), making
        waypoints approach more slowly.
        """
        self.x_pos += (self.x_pos - TER_SCREEN_WIDTH / 2) / PERSPECTIVE_DRIFT_DIVISOR

        growth_exp = PERSPECTIVE_GROWTH_BASE - PERSPECTIVE_GROWTH_DAMPEN
        self.x_size += 0.01 * math.exp(growth_exp * self.x_size) + WAYPOINT_LINEAR_GROWTH
        self.y_size += 0.01 * math.exp(growth_exp * self.y_size) + WAYPOINT_LINEAR_GROWTH

        self.x_size = min(self.x_size, MAX_OBJECT_SIZE)
        self.y_size = min(self.y_size, MAX_OBJECT_SIZE)

    def apply_rotation(self, rotation_angle: float) -> None:
        """Shift the waypoint to follow the camera's banking rotation."""
        if rotation_angle == 0:
            return

        angle_rad = math.radians(rotation_angle)
        y_sign = -1.0 if rotation_angle > 0 else 1.0

        self.x_pos += self.x_pos * math.cos(angle_rad) * ROTATION_TRANSLATION_FACTOR
        self.y_pos -= (
            self.y_pos * math.sin(angle_rad) * ROTATION_TRANSLATION_FACTOR
            + y_sign * Y_DAMPEN
        )

    # ------------------------------------------------------------------
    # Drawing
    # ------------------------------------------------------------------

    def draw(self, surface: pygame.Surface, rotation_angle: float) -> None:
        """Render the waypoint at its current perspective size."""
        scaled = pygame.transform.smoothscale(
            self._image,
            (int(self.x_size), int(self.y_size)),
        )
        rotated = pygame.transform.rotate(scaled, rotation_angle)
        surface.blit(rotated, (self.x_pos, self.y_pos))

    # ------------------------------------------------------------------
    # Off-screen test
    # ------------------------------------------------------------------

    def is_off_screen(self) -> bool:
        """Return ``True`` when the waypoint is well beyond visible area."""
        return self.x_pos > TER_SCREEN_WIDTH + 200 or self.x_pos + self.x_size < -200
