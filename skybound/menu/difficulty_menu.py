"""Difficulty-selection menu with info pages.

Presents five difficulty buttons and a logo.  The player selects a
difficulty, then clicks the Skybound logo to start the test.  An info
button toggles instructional pages.
"""

from __future__ import annotations

import os
from typing import Optional

import pygame

from skybound.config import (
    BLACK,
    MAX_DIFFICULTY,
    MENU_FONT_SIZE,
    MENU_HEIGHT,
    MENU_WIDTH,
    MENU_ASSETS,
    WHITE,
    save_difficulty,
)
from skybound.ui.hover_button import HoverButton


def _load(filename: str) -> pygame.Surface:
    """Load an image from the menu-assets directory with alpha."""
    return pygame.image.load(os.path.join(MENU_ASSETS, filename)).convert_alpha()


# -----------------------------------------------------------------------
# Info-page text content
# -----------------------------------------------------------------------
_INFO_PAGES = {
    1: [
        (80, 30,  "SKYBOUND is a Pilot Natural Aptitude Test simulator,"),
        (80, 60,  "which is intended to be used for aspiring cadets, or"),
        (80, 90,  "anyone who wishes to practise their natural ability to"),
        (80, 120, "multitask, problem-solve and improve."),
        (80, 170, "To start the program, you must first click on a difficulty"),
        (80, 200, "button, and then you may proceed by pressing the logo,"),
        (80, 230, "which will then start the practise test."),
    ],
    2: [
        (80, 10,  "During the test, there will be 3 sections which you will"),
        (80, 40,  "be required to interact with, such as:"),
        (50, 90,  "Plane Minigame: you will be required to use your up/down"),
        (50, 120, "arrow keys to ensure your plane avoids the obstacles."),
        (50, 150, "Questions: you will be asked basic reasoning questions"),
        (50, 180, "throughout, requiring you to choose an answer."),
        (50, 210, "POV: you will need to watch the terrain as you 'fly' in"),
        (50, 240, "your plane, clicking the 'Aircraft' button when you spot one,"),
        (50, 270, "an aircraft, and the 'Waypoint' button when you change"),
        (50, 300, "your bearing."),
    ],
}
_TOTAL_INFO_PAGES = len(_INFO_PAGES)


def run_menu() -> Optional[int]:
    """Run the difficulty-selection menu and return the chosen level.

    Returns ``None`` if the user closes the window without starting.
    """
    pygame.init()

    screen = pygame.display.set_mode((MENU_WIDTH, MENU_HEIGHT))
    pygame.display.set_caption("Skybound FAST")
    font = pygame.font.SysFont(None, MENU_FONT_SIZE)

    # Load button images
    logo_button = HoverButton(190, 55, _load("skybound_title.png"), 0.15)
    info_button = HoverButton(20, 10, _load("info-button.png"), 0.4)
    left_button = HoverButton(280, 300, _load("left.png"), 0.4)
    right_button = HoverButton(310, 300, _load("right.png"), 0.4)

    difficulty_buttons = [
        HoverButton(50 + i * 100, 205, _load(f"{i + 1}.png"), 1)
        for i in range(MAX_DIFFICULTY)
    ]

    selected_difficulty = 0
    showing_info = False
    info_page = 1

    def _draw_text(text: str, x: int, y: int) -> None:
        surface = font.render(text, True, BLACK)
        screen.blit(surface, (x, y))

    # ------------------------------------------------------------------
    # Menu loop
    # ------------------------------------------------------------------
    running = True
    while running:
        screen.fill(WHITE)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return None

        if showing_info:
            # Render current info page
            for x, y, line in _INFO_PAGES[info_page]:
                _draw_text(line, x, y)

            if info_page > 1 and left_button.draw(screen):
                info_page -= 1
            if info_page < _TOTAL_INFO_PAGES and right_button.draw(screen):
                info_page += 1
            if info_button.draw(screen):
                showing_info = False
        else:
            if info_button.draw(screen):
                showing_info = True

            for i, btn in enumerate(difficulty_buttons, start=1):
                if btn.draw(screen):
                    selected_difficulty = i

            if logo_button.draw(screen):
                if selected_difficulty > 0:
                    save_difficulty(selected_difficulty)
                    pygame.quit()
                    return selected_difficulty

        pygame.display.update()

    pygame.quit()
    return None
