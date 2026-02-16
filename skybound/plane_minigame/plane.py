"""Player-controlled plane with multi-region hitbox and collision flicker."""

from __future__ import annotations

import os

import pygame

from skybound.config import (
    FLICKER_DURATION_MS,
    FLICKER_TOGGLE_INTERVAL_MS,
    PLANE_ASSETS,
    PM_BODY_HITBOX,
    PM_BOTTOM_WING_HITBOX,
    PM_PANEL_HEIGHT,
    PM_PANEL_WIDTH,
    PM_PLANE_HEIGHT,
    PM_PLANE_SPEED,
    PM_PLANE_WIDTH,
    PM_TOP_WING_HITBOX,
)

_SPRITE_PATH = os.path.join(PLANE_ASSETS, "plane-topdown-sprite.png")


class Plane:
    """The player's plane in the embedded plane-minigame panel.

    The sprite is divided into three hitbox regions (body, top-wing,
    bottom-wing) whose offsets are pixel-tuned to the sprite artwork.
    On collision, the plane flickers for one second to provide visual
    feedback.
    """

    def __init__(self) -> None:
        self._image = pygame.image.load(_SPRITE_PATH).convert_alpha()
        self.x = 20
        self.y = 0

        # Hitbox regions — updated each frame via _update_hitboxes()
        self.hitbox = pygame.Rect(0, 0, 0, 0)
        self.hitbox_top_wing = pygame.Rect(0, 0, 0, 0)
        self.hitbox_bottom_wing = pygame.Rect(0, 0, 0, 0)
        self._update_hitboxes()

        # Collision flicker state
        self._visible = True
        self._flicker_start: int = 0
        self._flickering = False

    # ------------------------------------------------------------------
    # Hitbox calculation
    # ------------------------------------------------------------------

    def _update_hitboxes(self) -> None:
        """Recompute all three hitbox rects based on current position."""
        bx, by, bw, bh = PM_BODY_HITBOX
        self.hitbox = pygame.Rect(
            self.x + bx, self.y + by,
            PM_PLANE_WIDTH - bw, PM_PLANE_HEIGHT - bh,
        )

        tx, ty, tw, th = PM_TOP_WING_HITBOX
        self.hitbox_top_wing = pygame.Rect(
            self.x + tx, self.y + ty,
            PM_PLANE_WIDTH - tw, PM_PLANE_HEIGHT - th,
        )

        wx, wy, ww, wh = PM_BOTTOM_WING_HITBOX
        self.hitbox_bottom_wing = pygame.Rect(
            self.x + wx, self.y + wy,
            PM_PLANE_WIDTH - ww, PM_PLANE_HEIGHT - wh,
        )

    # ------------------------------------------------------------------
    # Movement
    # ------------------------------------------------------------------

    def handle_input(self) -> None:
        """Move the plane up or down based on arrow-key input.

        If both keys are held simultaneously the plane stays still.
        Movement is clamped to the panel boundaries.
        """
        keys = pygame.key.get_pressed()
        dy = 0

        if keys[pygame.K_DOWN] and not keys[pygame.K_UP]:
            dy = PM_PLANE_SPEED
        elif keys[pygame.K_UP]:
            dy = -PM_PLANE_SPEED

        self.y += dy
        self.y = max(0, min(self.y, PM_PANEL_HEIGHT - PM_PLANE_HEIGHT))

    # ------------------------------------------------------------------
    # Drawing
    # ------------------------------------------------------------------

    def draw(self, surface: pygame.Surface) -> None:
        """Scale and blit the plane sprite if currently visible, then
        refresh hitboxes."""
        if self._visible:
            scaled = pygame.transform.scale(self._image, (PM_PLANE_WIDTH, PM_PLANE_HEIGHT))
            surface.blit(scaled, (self.x, self.y))
        self._update_hitboxes()

    # ------------------------------------------------------------------
    # Collision flicker
    # ------------------------------------------------------------------

    def start_flicker(self) -> None:
        """Begin the collision-feedback flicker animation."""
        self._flicker_start = pygame.time.get_ticks()
        self._flickering = True

    def update_flicker(self) -> None:
        """Advance the flicker timer, toggling visibility each interval."""
        if not self._flickering:
            return

        elapsed = pygame.time.get_ticks() - self._flicker_start

        if elapsed <= FLICKER_DURATION_MS:
            self._visible = (elapsed // FLICKER_TOGGLE_INTERVAL_MS) % 2 == 0
        else:
            self._flickering = False
            self._visible = True

    # ------------------------------------------------------------------
    # Collision helpers
    # ------------------------------------------------------------------

    def collides_with(self, rect: pygame.Rect) -> bool:
        """Return ``True`` if any hitbox region overlaps *rect*."""
        return (
            self.hitbox.colliderect(rect)
            or self.hitbox_top_wing.colliderect(rect)
            or self.hitbox_bottom_wing.colliderect(rect)
        )
