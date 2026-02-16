"""Quadrant-positioned answer button for the Active Reasoning panel."""

from __future__ import annotations

import pygame

from skybound.config import ARC_FONT_SIZE, ARC_TEXT_COLOUR, DARK_GRAY, BLACK


class QuizButton:
    """A rectangular button occupying one quadrant of the ARC panel.

    Parameters
    ----------
    text : str
        Answer text displayed on the button.
    quadrant : int
        Position index (1 = top-left, 2 = top-right, 3 = bottom-left,
        4 = bottom-right).
    panel_width, panel_height : int
        Dimensions of the parent panel surface.
    """

    _QUADRANT_ORIGINS = {
        1: (0, 0),       # top-left
        2: (1, 0),       # top-right
        3: (0, 1),       # bottom-left
        4: (1, 1),       # bottom-right
    }

    def __init__(
        self,
        text: str,
        quadrant: int,
        panel_width: int,
        panel_height: int,
    ) -> None:
        self.text = text
        self._font = pygame.font.Font(None, ARC_FONT_SIZE)

        half_w = panel_width // 2
        half_h = panel_height // 2
        col, row = self._QUADRANT_ORIGINS[quadrant]
        self.rect = pygame.Rect(col * half_w, row * half_h, half_w, half_h)

    def draw(
        self,
        surface: pygame.Surface,
        selected: bool = False,
    ) -> None:
        """Render the button, highlighted in dark grey if *selected*."""
        colour = DARK_GRAY if selected else BLACK
        pygame.draw.rect(surface, colour, self.rect)

        text_surface = self._font.render(self.text, True, ARC_TEXT_COLOUR)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)

    def is_clicked(self, pos: tuple[int, int]) -> bool:
        """Return ``True`` if *pos* (relative to the panel) is inside."""
        return self.rect.collidepoint(pos)
