"""Image-based button that enlarges on hover and reports single clicks."""

from __future__ import annotations

import pygame

from skybound.config import BUTTON_HOVER_SCALE


class HoverButton:
    """A sprite-based button that scales up when the cursor hovers over it.

    Parameters
    ----------
    x, y : int
        Top-left position of the button on screen.
    image : pygame.Surface
        The source sprite to display.
    scale : float
        Base scale factor applied to *image*.
    """

    def __init__(self, x: int, y: int, image: pygame.Surface, scale: float) -> None:
        self._original_image = image
        self._original_width = image.get_width()
        self._original_height = image.get_height()
        self._scale = scale

        self.image = self._scaled_image(scale)
        self.rect = self.image.get_rect(topleft=(x, y))

        self._clicked = False
        self._enlarged = False

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _scaled_image(self, scale: float) -> pygame.Surface:
        """Return the source image scaled by *scale*."""
        width = int(self._original_width * scale)
        height = int(self._original_height * scale)
        return pygame.transform.scale(self._original_image, (width, height))

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def draw(self, surface: pygame.Surface) -> bool:
        """Draw the button and return ``True`` on the frame it is clicked.

        The button enlarges by 20 % while the cursor hovers over it and
        reverts to its base size when the cursor leaves.
        """
        action = False
        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()[0]

        if self.rect.collidepoint(mouse_pos):
            # Enlarge on first hover frame
            if not self._enlarged:
                self._enlarged = True
                enlarged_scale = self._scale * BUTTON_HOVER_SCALE
                self.image = self._scaled_image(enlarged_scale)
                self.rect = self.image.get_rect(center=self.rect.center)

            # Single-click detection (press edge)
            if mouse_pressed and not self._clicked:
                self._clicked = True
                action = True

            if not mouse_pressed:
                self._clicked = False
        else:
            # Revert to base size when cursor leaves
            if self._enlarged:
                self._enlarged = False
                self.image = self._scaled_image(self._scale)
                self.rect = self.image.get_rect(center=self.rect.center)

        surface.blit(self.image, self.rect)
        return action
