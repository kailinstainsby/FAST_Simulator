"""Active Reasoning Challenges — timed question cycle for the embedded panel.

All state is encapsulated so the terrain-view game loop can instantiate,
update, and read scoring attributes without module-level globals.
"""

from __future__ import annotations

import random
from typing import List, Optional

import pygame

from skybound.config import (
    ARC_BASE_COOLDOWN,
    ARC_DIFFICULTY_COOLDOWN_BONUS,
    ARC_FONT_SIZE,
    ARC_PANEL_HEIGHT,
    ARC_PANEL_WIDTH,
    ARC_PANEL_X,
    ARC_PANEL_Y,
    ARC_TEXT_COLOUR,
    BLACK,
    load_difficulty,
)
from skybound.active_reasoning.question_database import (
    CORRECT_ANSWER,
    QUESTIONS,
    QUESTION_CONTEXT,
    QUESTION_TEXT,
    TOTAL_QUESTIONS,
)
from skybound.active_reasoning.quiz_button import QuizButton


class ActiveReasoningGame:
    """Self-contained ARC minigame rendered onto a sub-surface.

    Parameters
    ----------
    difficulty : int, optional
        Difficulty level (1–5).  Higher difficulty shortens the cooldown
        between question phases.
    """

    def __init__(self, difficulty: int | None = None) -> None:
        self._difficulty = difficulty if difficulty is not None else load_difficulty()

        self.width = ARC_PANEL_WIDTH
        self.height = ARC_PANEL_HEIGHT
        self._surface = pygame.Surface((self.width, self.height))

        # Question timing
        self._cooldown = ARC_BASE_COOLDOWN + (5 - self._difficulty) * ARC_DIFFICULTY_COOLDOWN_BONUS
        self._timer: int = 0

        # Question state
        self._completed: List[int] = []
        self._current_index: int = random.randint(0, TOTAL_QUESTIONS - 1)
        self._buttons: List[QuizButton] = []
        self._selected_answer: Optional[str] = None

        # Scoring
        self.correct_answers: int = 0
        self.incorrect_answers: int = 0
        self.question_count: int = 0

        self._load_new_question()

    # ------------------------------------------------------------------
    # Question management
    # ------------------------------------------------------------------

    def _load_new_question(self) -> None:
        """Pick an unseen question and create shuffled answer buttons."""
        self._selected_answer = None

        while self._current_index in self._completed:
            self._current_index = random.randint(0, TOTAL_QUESTIONS - 1)
        self._completed.append(self._current_index)

        # Shuffle answer indices (correct + 3 wrong)
        answer_order = [0, 1, 2, 3]
        random.shuffle(answer_order)

        entry = QUESTIONS[self._current_index]
        answers = [entry[CORRECT_ANSWER + offset] for offset in answer_order]

        self._buttons = [
            QuizButton(answers[i], i + 1, self.width, self.height)
            for i in range(4)
        ]

    # ------------------------------------------------------------------
    # Text rendering
    # ------------------------------------------------------------------

    def _draw_text(self, text: str, is_top: bool) -> None:
        """Render *text* centred on the upper or lower half of the panel."""
        font = pygame.font.Font(None, ARC_FONT_SIZE)
        rendered = font.render(text, True, ARC_TEXT_COLOUR)
        y_centre = self.height / 4 if is_top else self.height / 1.5
        rect = rendered.get_rect(center=(self.width / 2, y_centre))
        self._surface.blit(rendered, rect)

    # ------------------------------------------------------------------
    # Per-frame update
    # ------------------------------------------------------------------

    def update(self, main_surface: pygame.Surface) -> None:
        """Run one frame of ARC logic and blit onto *main_surface*.

        The update cycle has three phases that repeat:

        1. **Display phase** — show the question text.
        2. **Answer phase** — show answer buttons for selection.
        3. **Evaluate phase** — score the answer and load the next question.
        """
        self._surface.fill(BLACK)

        # Translate mouse position into panel-local coordinates
        mouse_x, mouse_y = pygame.mouse.get_pos()
        local_mouse = (mouse_x - ARC_PANEL_X, mouse_y - ARC_PANEL_Y)

        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                for button in self._buttons:
                    if button.is_clicked(local_mouse):
                        self._selected_answer = button.text

        self._timer += 1
        entry = QUESTIONS[self._current_index]

        if self._timer < self._cooldown:
            # Phase 1 — show question
            self._draw_text(entry[QUESTION_TEXT], is_top=True)
            self._draw_text(entry[QUESTION_CONTEXT], is_top=False)

        elif self._timer < 2 * self._cooldown:
            # Phase 2 — show answer buttons
            for button in self._buttons:
                button.draw(self._surface, selected=(self._selected_answer == button.text))

        else:
            # Phase 3 — evaluate and advance
            if self._selected_answer == entry[CORRECT_ANSWER]:
                self.correct_answers += 1
            else:
                self.incorrect_answers += 1
            self.question_count += 1

            self._timer = 0
            self._load_new_question()

        main_surface.blit(self._surface, (ARC_PANEL_X, ARC_PANEL_Y))
