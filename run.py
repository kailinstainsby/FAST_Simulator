#!/usr/bin/env python3
"""Skybound FAST — Entry Point.

Launch the difficulty-selection menu, then start the timed aptitude
test at the chosen difficulty level.
"""

from skybound.menu.difficulty_menu import run_menu
from skybound.terrain_view.game import run_game


def main() -> None:
    difficulty = run_menu()
    if difficulty is not None:
        run_game(difficulty)


if __name__ == "__main__":
    main()
