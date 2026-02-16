"""Aircraft entities that traverse the terrain view.

Aircraft spawn off-screen (left or right) and cross the viewport at a
type-dependent speed.  They grow slightly each frame to simulate
approach, and their trajectory is adjusted when the camera banks.
"""

from __future__ import annotations

import math
import os

import pygame

from skybound.config import (
    AIRCRAFT_DEFAULT,
    AIRCRAFT_GROWTH_RATE,
    AIRCRAFT_TYPES,
    ROTATION_TRANSLATION_FACTOR,
    TER_SCREEN_WIDTH,
    TERRAIN_ASSETS,
    Y_DAMPEN,
)


class Aircraft:
    """A single aircraft flying across the terrain view.

    Parameters
    ----------
    from_left : bool
        ``True`` if the aircraft enters from the left edge;
        ``False`` if from the right.
    y_pos : int
        Vertical spawn position.
    aircraft_type : int
        Type index that determines sprite, speed, and size.
        See ``config.AIRCRAFT_TYPES`` for the lookup table.
    """

    def __init__(self, from_left: bool, y_pos: int, aircraft_type: int) -> None:
        self.clicked = False

        # Look up type-specific properties (speed, sprite, size)
        speed, sprite_file, (w, h) = AIRCRAFT_TYPES.get(
            aircraft_type, AIRCRAFT_DEFAULT
        )
        self._speed = speed
        self.x_size: float = w
        self.y_size: float = h

        sprite_path = os.path.join(TERRAIN_ASSETS, sprite_file)
        self._image = pygame.image.load(sprite_path).convert_alpha()

        # Spawn off-screen; flip sprite + invert speed depending on direction
        if from_left:
            self.x_pos: float = -self.x_size
            self._image = pygame.transform.flip(self._image, True, False)
        else:
            self.x_pos = TER_SCREEN_WIDTH
            self._speed = -self._speed

        self.y_pos: float = y_pos

    # ------------------------------------------------------------------
    # Per-frame update
    # ------------------------------------------------------------------

    def move(self) -> None:
        """Advance position and grow slightly to simulate approach."""
        self.x_pos += self._speed
        self.x_size += AIRCRAFT_GROWTH_RATE
        self.y_size += AIRCRAFT_GROWTH_RATE

    def apply_rotation(self, rotation_angle: float) -> None:
        """Shift position to follow the camera's banking rotation."""
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
        """Render the aircraft at its current size and rotation."""
        scaled = pygame.transform.smoothscale(
            self._image,
            (int(self.x_size), int(self.y_size)),
        )
        rotated = pygame.transform.rotate(scaled, rotation_angle)
        rect = rotated.get_rect(topleft=(self.x_pos, self.y_pos))
        surface.blit(rotated, rect.topleft)

    # ------------------------------------------------------------------
    # Off-screen test
    # ------------------------------------------------------------------

    def is_off_screen(self) -> bool:
        """Return ``True`` when the aircraft has left the visible area."""
        return self.x_pos > TER_SCREEN_WIDTH + 500 or self.x_pos + self.x_size < -500
