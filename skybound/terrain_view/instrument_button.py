"""Instrument-panel buttons for reporting aircraft and waypoint sightings."""

from __future__ import annotations

import os

import pygame

from skybound.config import (
    PANEL_AIRCRAFT_BUTTON_OFFSET_Y,
    PANEL_BUTTON_OFFSET_X,
    PANEL_WAYPOINT_BUTTON_OFFSET_Y,
    TERRAIN_ASSETS,
)


class InstrumentButton:
    """A small button on the instrument panel that detects single clicks.

    Parameters
    ----------
    is_aircraft : bool
        ``True`` for the aircraft button, ``False`` for the waypoint button.
        Determines the sprite and vertical position.
    menu_x : int
        Left edge of the instrument-panel rectangle.
    menu_y : int
        Top edge of the instrument-panel rectangle.
    """

    def __init__(self, is_aircraft: bool, menu_x: int, menu_y: int) -> None:
        sprite_name = "aircraftbutton.png" if is_aircraft else "waypointbutton.png"
        self._image = pygame.image.load(
            os.path.join(TERRAIN_ASSETS, sprite_name)
        )

        y_offset = (
            PANEL_AIRCRAFT_BUTTON_OFFSET_Y if is_aircraft
            else PANEL_WAYPOINT_BUTTON_OFFSET_Y
        )
        self._x = menu_x + PANEL_BUTTON_OFFSET_X
        self._y = menu_y + y_offset

        self.rect = self._image.get_rect(topleft=(self._x, self._y))
        self._was_pressed = False

    def draw(self, surface: pygame.Surface) -> bool:
        """Render the button and return ``True`` on a single-click edge.

        Uses a press-edge detector so that holding the mouse button does
        not fire repeatedly.
        """
        action = False
        mouse_pos = pygame.mouse.get_pos()
        mouse_down = pygame.mouse.get_pressed()[0]

        if self.rect.collidepoint(mouse_pos):
            if mouse_down and not self._was_pressed:
                action = True

        self._was_pressed = mouse_down
        surface.blit(self._image, (self._x, self._y))
        return action
