"""Post-round memory-recall quiz.

After the timed game session, the player is asked a series of questions
about in-game events they should have been observing (flash counts,
aircraft/waypoint totals, specific waypoint types).
"""

from __future__ import annotations

import random
from typing import Any, List, Optional, Tuple

import pygame

from skybound.config import (
    BLACK,
    LIGHT_GRAY,
    QUIZ_BUTTON_GAP,
    QUIZ_BUTTON_HEIGHT,
    QUIZ_BUTTON_START_Y,
    QUIZ_BUTTON_WIDTH_MARGIN,
    QUIZ_FONT_SIZE,
    QUIZ_MAX_QUESTIONS,
    WHITE,
    DARK_GRAY,
)


class RecallQuiz:
    """Interactive multi-choice quiz presented after the game session.

    Game-state attributes (``aircraft_count``, ``waypoint_count``, etc.)
    are populated by the terrain-view game loop before the first call to
    :meth:`generate_question`.

    Parameters
    ----------
    screen : pygame.Surface
        The main display surface to draw on.
    """

    def __init__(self, screen: pygame.Surface) -> None:
        self.screen = screen
        self.is_active = False

        self.correct_answers = 0
        self.incorrect_answers = 0
        self.questions_asked = 0

        # Populated by the game loop before quiz begins
        self.aircraft_count: int = 0
        self.waypoint_count: int = 0
        self.left_flashes: int = 0
        self.right_flashes: int = 0
        self.total_flashes: int = 0
        self.waypoints: List[int] = []

        self._asked: set[str] = set()
        self._question_text: str = ""
        self._correct_answer: Any = None
        self._options: List[Any] = []
        self._button_rects: List[Tuple[pygame.Rect, Any]] = []

    # ------------------------------------------------------------------
    # Question generation
    # ------------------------------------------------------------------

    def generate_question(self) -> None:
        """Select and display the next recall question.

        Automatically deactivates the quiz after ``QUIZ_MAX_QUESTIONS``
        questions have been asked.
        """
        if self.questions_asked >= QUIZ_MAX_QUESTIONS:
            self.is_active = False
            return

        candidates = [
            ("How many aircraft appeared on screen?", self.aircraft_count),
            ("How many waypoints appeared on screen?", self.waypoint_count),
            ("What is the total flashes the lights undertook?", self.total_flashes),
            ("How many flashes did the left light undertake?", self.left_flashes),
            ("How many flashes did the right light undertake?", self.right_flashes),
        ]

        if self.waypoints:
            index = random.randint(1, len(self.waypoints))
            candidates.append(
                (f"What was the Waypoint at position {index}?",
                 random.choice(self.waypoints))
            )

        available = [q for q in candidates if q[0] not in self._asked]
        if not available:
            self.is_active = False
            return

        self._question_text, self._correct_answer = random.choice(available)
        self._asked.add(self._question_text)
        self.questions_asked += 1

        # Generate three unique wrong answers
        wrong: set[Any] = set()
        while len(wrong) < 3:
            if isinstance(self._correct_answer, int):
                option = random.randint(1, 10)
            else:
                option = random.choice(self.waypoints) if self.waypoints else 0
            if option != self._correct_answer:
                wrong.add(option)

        self._options = list(wrong) + [self._correct_answer]
        random.shuffle(self._options)
        self.is_active = True

    # ------------------------------------------------------------------
    # Drawing
    # ------------------------------------------------------------------

    def draw(self) -> None:
        """Render the current question and answer buttons."""
        if not self.is_active:
            return

        self.screen.fill(WHITE)
        font = pygame.font.Font(None, QUIZ_FONT_SIZE)

        # Question text
        q_surface = font.render(self._question_text, True, DARK_GRAY)
        q_rect = q_surface.get_rect(center=(self.screen.get_width() / 2, 100))
        self.screen.blit(q_surface, q_rect)

        # Answer buttons
        btn_width = self.screen.get_width() - QUIZ_BUTTON_WIDTH_MARGIN
        self._button_rects.clear()

        for i, option in enumerate(self._options):
            rect = pygame.Rect(
                (self.screen.get_width() - btn_width) // 2,
                QUIZ_BUTTON_START_Y + i * (QUIZ_BUTTON_HEIGHT + QUIZ_BUTTON_GAP),
                btn_width,
                QUIZ_BUTTON_HEIGHT,
            )
            self._button_rects.append((rect, option))

            pygame.draw.rect(self.screen, LIGHT_GRAY, rect)
            text_surface = font.render(str(option), True, BLACK)
            text_rect = text_surface.get_rect(center=rect.center)
            self.screen.blit(text_surface, text_rect)

    # ------------------------------------------------------------------
    # Event handling
    # ------------------------------------------------------------------

    def handle_event(self, event: pygame.event.Event) -> None:
        """Process a click on one of the answer buttons."""
        if not self.is_active:
            return

        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            for rect, option in self._button_rects:
                if rect.collidepoint(mouse_pos):
                    if option == self._correct_answer:
                        self.correct_answers += 1
                    else:
                        self.incorrect_answers += 1

                    if self.questions_asked < QUIZ_MAX_QUESTIONS - 1:
                        self.generate_question()
                    else:
                        self.is_active = False
                    break
