"""Cloud obstacle that scrolls horizontally across the plane-minigame panel."""

from __future__ import annotations

import pygame

from skybound.config import PM_CLOUD_SIZE, PM_CLOUD_SPEED, WHITE


class Cloud:
    """A rectangular cloud obstacle in the plane-minigame side-panel.

    Parameters
    ----------
    x, y : int
        Initial position (top-left corner).
    width, height : int
        Obstacle dimensions in pixels (default matches the embedded panel).
    """

    def __init__(
        self,
        x: int,
        y: int,
        width: int = PM_CLOUD_SIZE,
        height: int = PM_CLOUD_SIZE,
    ) -> None:
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.colour = WHITE
        self.hitbox = pygame.Rect(self.x, self.y, self.width, self.height)

    def update_hitbox(self) -> None:
        """Recalculate the hitbox rectangle to match the current position."""
        self.hitbox = pygame.Rect(self.x, self.y, self.width, self.height)

    def draw(self, surface: pygame.Surface) -> None:
        """Render the cloud and refresh its hitbox."""
        pygame.draw.rect(surface, self.colour, (self.x, self.y, self.width, self.height))
        self.update_hitbox()

    def move(self) -> None:
        """Advance the cloud one step to the left."""
        self.x -= PM_CLOUD_SPEED

    def is_off_screen(self) -> bool:
        """Return ``True`` when the cloud has scrolled fully off-screen."""
        return self.x + self.width < 0
