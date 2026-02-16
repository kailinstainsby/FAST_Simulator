"""Flashing indicator lights on the instrument panel.

Each light flashes a random number of times over the course of the game.
Flash times are pre-computed at creation so they are deterministic for a
given seed, and the total count is used in the post-game recall quiz.
"""

from __future__ import annotations

import os
import random

import pygame

from skybound.config import (
    LIGHT_FLASH_LENGTH_TICKS,
    LIGHT_TOTAL_TIME_WINDOW,
    TERRAIN_ASSETS,
)

_SPRITE_ACTIVE = os.path.join(TERRAIN_ASSETS, "lightactive.png")
_SPRITE_INACTIVE = os.path.join(TERRAIN_ASSETS, "lightinactive.png")


class IndicatorLight:
    """An instrument-panel light that flashes at pre-scheduled times.

    Parameters
    ----------
    x_pos : int
        Horizontal position on screen.
    y_pos : int
        Vertical position on screen.
    max_flashes : int
        Upper bound (inclusive) on the random number of flashes.
    """

    def __init__(self, x_pos: int, y_pos: int, max_flashes: int) -> None:
        self._sprite_active = pygame.image.load(_SPRITE_ACTIVE).convert_alpha()
        self._sprite_inactive = pygame.image.load(_SPRITE_INACTIVE).convert_alpha()

        self.x_pos = x_pos
        self.y_pos = y_pos

        self._active = False
        self.flash_count = 0
        self._flash_timer = 0

        # Pre-schedule random flash times over the game duration
        total_flashes = random.randint(2, max_flashes)
        self._flash_times = sorted(
            random.sample(range(LIGHT_TOTAL_TIME_WINDOW), total_flashes)
        )
        self._flash_index = 0
        self._elapsed = 0

    # ------------------------------------------------------------------
    # Per-frame update
    # ------------------------------------------------------------------

    def update(self) -> None:
        """Advance the light by one tick, triggering flashes on schedule."""
        self._elapsed += 1

        if self._active:
            self._flash_timer -= 1
            if self._flash_timer <= 0:
                self._active = False
        else:
            if (
                self._flash_index < len(self._flash_times)
                and self._elapsed >= self._flash_times[self._flash_index]
            ):
                self._trigger_flash()
                self._flash_index += 1

    def _trigger_flash(self) -> None:
        """Activate the light for one flash duration."""
        self._active = True
        self._flash_timer = LIGHT_FLASH_LENGTH_TICKS
        self.flash_count += 1

    # ------------------------------------------------------------------
    # Drawing
    # ------------------------------------------------------------------

    def draw(self, surface: pygame.Surface) -> None:
        """Render the active or inactive sprite."""
        sprite = self._sprite_active if self._active else self._sprite_inactive
        surface.blit(sprite, (self.x_pos, self.y_pos))
