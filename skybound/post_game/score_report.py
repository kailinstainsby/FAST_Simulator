"""Score calculation and results display.

Computes four aptitude categories from raw game data, renders a
two-page report, and determines an overall PASS / FAIL result.
"""

from __future__ import annotations

import pygame

from skybound.config import (
    BLACK,
    SCORE_ARC_CORRECT_WEIGHT,
    SCORE_ARC_INCORRECT_WEIGHT,
    SCORE_COLLISION_MAX,
    SCORE_COLLISION_WEIGHT,
    SCORE_OBSERVATION_PENALTY,
    SCORE_PATTERN_DROPOFF,
    SCORE_PATTERN_PENALTY,
    SCORE_PASS_THRESHOLD,
    SCORE_AIRCRAFT_WEIGHT,
    SCORE_ARC_WEIGHT,
    SCORE_COLLISION_PENALTY_WEIGHT,
    SCORE_QUIZ_WEIGHT,
    SCORE_WAYPOINT_WEIGHT,
    TER_SCREEN_HEIGHT,
    TER_SCREEN_WIDTH,
)

_TEXT_COLOUR = BLACK


class ScoreReport:
    """Renders a two-page score report onto a given surface.

    Parameters
    ----------
    screen : pygame.Surface
        The main display surface.
    """

    def __init__(self, screen: pygame.Surface) -> None:
        self._screen = screen

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _draw_text(
        self, text: str, x: int, y: int, size: int = 45
    ) -> None:
        font = pygame.font.Font(None, size)
        rendered = font.render(text, True, _TEXT_COLOUR)
        rect = rendered.get_rect(center=(x, y))
        self._screen.blit(rendered, rect)

    @staticmethod
    def _safe_ratio(numerator: int, denominator: int) -> float:
        """Return *numerator / denominator*, avoiding division by zero."""
        return numerator / denominator if denominator > 0 else 0.0

    # ------------------------------------------------------------------
    # Page 1 — summary
    # ------------------------------------------------------------------

    def draw_summary(
        self,
        *,
        collisions: int,
        waypoint_correct: int,
        waypoint_total: int,
        waypoint_incorrect: int,
        aircraft_correct: int,
        aircraft_total: int,
        aircraft_incorrect: int,
        arc_correct: int,
        arc_total: int,
        quiz_correct: int,
        quiz_total: int,
    ) -> None:
        """Render page 1: raw performance figures + PASS / FAIL."""
        cx = TER_SCREEN_WIDTH // 2

        self._draw_text(f"You collided with {collisions} clouds", cx, 150)
        self._draw_text(
            f"You detected {waypoint_correct} / {waypoint_total} waypoints, "
            f"and misinput {waypoint_incorrect}",
            cx, 200,
        )
        self._draw_text(
            f"You detected {aircraft_correct} / {aircraft_total} aircraft, "
            f"and misinput {aircraft_incorrect}",
            cx, 250,
        )
        self._draw_text(
            f"You correctly answered {arc_correct} / {arc_total} active questions",
            cx, 300,
        )
        self._draw_text(
            f"You correctly recalled {quiz_correct} / {quiz_total} questions",
            cx, 350,
        )

        # Composite pass/fail
        wp_acc = self._safe_ratio(waypoint_correct, waypoint_total)
        ac_acc = self._safe_ratio(aircraft_correct, aircraft_total)
        arc_acc = self._safe_ratio(arc_correct, arc_total)
        quiz_acc = self._safe_ratio(quiz_correct, quiz_total)
        collision_penalty = max(0, 1 - collisions / SCORE_COLLISION_MAX)

        final = (
            SCORE_WAYPOINT_WEIGHT * wp_acc
            + SCORE_AIRCRAFT_WEIGHT * ac_acc
            + SCORE_ARC_WEIGHT * arc_acc
            + SCORE_QUIZ_WEIGHT * quiz_acc
            - SCORE_COLLISION_PENALTY_WEIGHT * collision_penalty
        )

        verdict = "PASS" if final >= SCORE_PASS_THRESHOLD else "FAIL"
        self._draw_text(
            f"{verdict}! Final Score: {final:.2f}", cx, 50, size=60
        )

    # ------------------------------------------------------------------
    # Page 2 — detailed aptitude scores
    # ------------------------------------------------------------------

    def draw_detailed_scores(
        self,
        *,
        collisions: int,
        arc_correct: int,
        arc_total: int,
        quiz_correct: int,
        quiz_total: int,
        waypoint_correct: int,
        waypoint_total: int,
        waypoint_incorrect: int,
        aircraft_correct: int,
        aircraft_total: int,
        aircraft_incorrect: int,
    ) -> None:
        """Render page 2: four aptitude-category percentages."""
        cx = TER_SCREEN_WIDTH // 2
        collision_penalty = max(0, 1 - collisions / SCORE_COLLISION_MAX)
        arc_accuracy = self._safe_ratio(arc_correct, arc_total)

        # Multitasking score
        multitasking = (
            SCORE_COLLISION_WEIGHT * collision_penalty
            + SCORE_ARC_CORRECT_WEIGHT * arc_accuracy
            + SCORE_ARC_INCORRECT_WEIGHT * (1 - arc_accuracy)
        ) * 100

        # Pattern recognition score
        incorrect_ratio = min(
            1,
            (arc_total - arc_correct) * SCORE_PATTERN_PENALTY
            / SCORE_PATTERN_DROPOFF,
        ) if arc_total > 0 else 0
        pattern = max(0, arc_accuracy - incorrect_ratio) * 100

        # Memory recall score
        memory = self._safe_ratio(quiz_correct, quiz_total) * 100

        # Observation score
        total_events = waypoint_total + aircraft_total
        correct_obs = waypoint_correct + aircraft_correct
        incorrect_obs = waypoint_incorrect + aircraft_incorrect
        missed = max(0, total_events - correct_obs)
        observation = max(
            0,
            100
            - incorrect_obs * SCORE_OBSERVATION_PENALTY
            - missed ** 1.5,
        )

        self._draw_text(
            f"You achieved a multitasking score of {multitasking:.2f}%",
            cx, 100, size=50,
        )
        self._draw_text(
            f"You achieved a pattern recognition score of {pattern:.2f}%",
            cx, 150, size=50,
        )
        self._draw_text(
            f"You achieved a memory recall score of {memory:.2f}%",
            cx, 200, size=50,
        )
        self._draw_text(
            f"You achieved a observation rating of {observation:.2f}%",
            cx, 250, size=50,
        )
