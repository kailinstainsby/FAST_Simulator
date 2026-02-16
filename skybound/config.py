"""Centralised configuration for Skybound FAST.

Every magic number, asset path, colour definition, and difficulty preset lives
here so that the rest of the codebase references descriptive names instead of
raw literals.  The pseudo-3D perspective simulation parameters are documented
with their mathematical purpose.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Dict, Tuple

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIFFICULTY_FILE = os.path.join(PROJECT_ROOT, "difficulty.txt")

# Asset directories
MENU_ASSETS = os.path.join(PROJECT_ROOT, "assets", "menu")
PLANE_ASSETS = os.path.join(PROJECT_ROOT, "assets", "plane")
TERRAIN_ASSETS = os.path.join(PROJECT_ROOT, "assets", "terrain")
PANEL_ASSETS = os.path.join(PROJECT_ROOT, "assets", "panel")

# ---------------------------------------------------------------------------
# Colours  (RGB tuples)
# ---------------------------------------------------------------------------
WHITE: Tuple[int, int, int] = (255, 255, 255)
BLACK: Tuple[int, int, int] = (0, 0, 0)
RED: Tuple[int, int, int] = (170, 74, 68)
GREEN: Tuple[int, int, int] = (0, 255, 0)
DARK_GRAY: Tuple[int, int, int] = (50, 50, 50)
LIGHT_GRAY: Tuple[int, int, int] = (220, 220, 220)

# ---------------------------------------------------------------------------
# Difficulty Management
# ---------------------------------------------------------------------------
DEFAULT_DIFFICULTY = 3
MIN_DIFFICULTY = 1
MAX_DIFFICULTY = 5


def load_difficulty() -> int:
    """Load the persisted difficulty level from *difficulty.txt*."""
    try:
        with open(DIFFICULTY_FILE, "r") as fh:
            return int(fh.read().strip())
    except (FileNotFoundError, ValueError):
        return DEFAULT_DIFFICULTY


def save_difficulty(level: int) -> None:
    """Persist *level* to *difficulty.txt* for cross-module access."""
    with open(DIFFICULTY_FILE, "w") as fh:
        fh.write(str(level))


# ---------------------------------------------------------------------------
# Difficulty-dependent cloud-spawn presets
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class DifficultySettings:
    """Cloud-spawn parameters that scale with difficulty."""

    cloud_spawn_rate: int
    cloud_spawn_chance: float


DIFFICULTY_PRESETS: Dict[int, DifficultySettings] = {
    1: DifficultySettings(cloud_spawn_rate=300, cloud_spawn_chance=0.3),
    2: DifficultySettings(cloud_spawn_rate=200, cloud_spawn_chance=0.3),
    3: DifficultySettings(cloud_spawn_rate=125, cloud_spawn_chance=0.3),
    4: DifficultySettings(cloud_spawn_rate=200, cloud_spawn_chance=0.5),
    5: DifficultySettings(cloud_spawn_rate=150, cloud_spawn_chance=0.7),
}

# Difficulties ≥ this value use wall-with-gap spawning instead of row spawning
WALL_SPAWN_THRESHOLD = 4

# ---------------------------------------------------------------------------
# Menu Screen
# ---------------------------------------------------------------------------
MENU_WIDTH = 640
MENU_HEIGHT = 360
MENU_FONT_SIZE = 30
BUTTON_HOVER_SCALE = 1.2  # 20 % enlargement on hover

# ---------------------------------------------------------------------------
# Plane Minigame  (embedded 300 × 246 panel)
# ---------------------------------------------------------------------------
PM_PANEL_WIDTH = 300
PM_PANEL_HEIGHT = 246
PM_PLANE_HEIGHT = round(PM_PANEL_WIDTH / 7)       # ≈ 43 px
PM_PLANE_WIDTH = round(PM_PLANE_HEIGHT * 1.2)      # ≈ 51 px
PM_CLOUD_SIZE = 15
PM_CLOUD_SPACING = 15
PM_CLOUD_SPEED = 2
PM_PLANE_SPEED = 6
PM_COLLISION_COOLDOWN_MS = 1000

# Pixel-tuned hitbox offsets relative to the plane sprite.
# Each tuple is (x_offset, y_offset, width_reduction, height_reduction).
PM_BODY_HITBOX = (9, 19, 15, 37)
PM_TOP_WING_HITBOX = (14, 4, 45, 40)
PM_BOTTOM_WING_HITBOX = (14, 38, 45, 40)

# ---------------------------------------------------------------------------
# Collision flicker effect
# ---------------------------------------------------------------------------
FLICKER_DURATION_MS = 1000
FLICKER_TOGGLE_INTERVAL_MS = 167   # ≈ 6 flickers per second

# ---------------------------------------------------------------------------
# Active Reasoning (embedded 300 × 246 panel)
# ---------------------------------------------------------------------------
ARC_PANEL_WIDTH = 300
ARC_PANEL_HEIGHT = 246
ARC_PANEL_X = 960 - ARC_PANEL_WIDTH - 45          # 615
ARC_PANEL_Y = 270
ARC_BASE_COOLDOWN = 120            # frames before phase switch
ARC_DIFFICULTY_COOLDOWN_BONUS = 30  # extra frames per difficulty level below 5
ARC_FONT_SIZE = 25
ARC_TOTAL_QUESTIONS = 203
ARC_TEXT_COLOUR = GREEN

# ---------------------------------------------------------------------------
# Terrain View  (main 960 × 540 display)
# ---------------------------------------------------------------------------
TER_SCREEN_WIDTH = 960             # 1920 // 2
TER_SCREEN_HEIGHT = 540            # 1080 // 2
TER_BACKGROUND_SCALE = 1.0

# -- Pseudo-3D perspective simulation -------------------------------------
# Objects grow exponentially to simulate approach:
#   growth = 0.01 * exp(PERSPECTIVE_GROWTH_BASE * size
#                       - PERSPECTIVE_GROWTH_DAMPEN * size) + linear_rate
PERSPECTIVE_GROWTH_BASE = 0.05
PERSPECTIVE_GROWTH_DAMPEN = 0.045
CLOUD_LINEAR_GROWTH = 0.1
WAYPOINT_LINEAR_GROWTH = 0.05
MAX_OBJECT_SIZE = 3000             # cap to prevent runaway scaling

# Lateral drift (simulates objects sliding past the cockpit):
#   drift = (x - screen_centre_x) / PERSPECTIVE_DRIFT_DIVISOR
PERSPECTIVE_DRIFT_DIVISOR = 1000

# Rotation-induced translation (simulates aircraft banking):
#   dx = x * cos(angle) * ROTATION_TRANSLATION_FACTOR
#   dy = y * sin(angle) * ROTATION_TRANSLATION_FACTOR ± Y_DAMPEN
ROTATION_TRANSLATION_FACTOR = 0.0077
Y_DAMPEN = 0.1
ROTATION_SPEED = 0.25
ROTATION_ANGLE_CHOICES = [-15, 15]
ROTATION_DURATION_TICKS = 300      # 5 seconds at 60 FPS

# Terrain cloud spawn
TER_CLOUD_INITIAL_WIDTH = 10
TER_CLOUD_INITIAL_HEIGHT = 1
TER_CLOUD_SPAWN_Y = 180           # horizon line
TER_CLOUD_COOLDOWN_RANGE = (120, 300)
TER_CLOUD_SPAWN_X_MARGIN = 100

# Waypoint spawn
WAYPOINT_INITIAL_SIZE = 30
WAYPOINT_SPEED = 0.5
WAYPOINT_SPAWN_Y = 180
WAYPOINT_COOLDOWN_RANGE = (1500, 3000)

# Aircraft spawn
AIRCRAFT_COOLDOWN_RANGE = (1500, 3000)
AIRCRAFT_MAX_CONCURRENT = 2
AIRCRAFT_GROWTH_RATE = 0.05        # size increase per frame

# Aircraft type definitions — (speed, sprite_filename, (width, height))
AIRCRAFT_TYPES: Dict[int, Tuple[float, str, Tuple[int, int]]] = {
    3: (0.5, "plane3.png", (40, 40)),
    4: (0.5, "plane3.png", (40, 40)),
    5: (2.0, "plane5.png", (100, 100)),
    6: (0.8, "plane6.png", (40, 40)),
    7: (2.7, "plane7.png", (100, 100)),
    8: (3.0, "plane8.png", (40, 40)),
}
AIRCRAFT_DEFAULT: Tuple[float, str, Tuple[int, int]] = (0.5, "plane0.png", (30, 30))

# ---------------------------------------------------------------------------
# Instrument-panel layout
# ---------------------------------------------------------------------------
PANEL_MENU_WIDTH_DIVISOR = 5
PANEL_MENU_HEIGHT_EXTRA = 30
PANEL_MENU_HEIGHT_DIVISOR = 2.5
PANEL_BUTTON_OFFSET_X = 20
PANEL_AIRCRAFT_BUTTON_OFFSET_Y = 20
PANEL_WAYPOINT_BUTTON_OFFSET_Y = 60

# Plane-minigame sub-surface position inside the main window
PM_EMBED_X = 45
PM_EMBED_Y = TER_SCREEN_HEIGHT // 2               # 270

# ---------------------------------------------------------------------------
# Indicator Lights
# ---------------------------------------------------------------------------
LIGHT_FLASH_LENGTH_TICKS = 30      # 0.5 seconds at 60 FPS
LIGHT_TOTAL_TIME_WINDOW = 18000    # ticks across which flashes are distributed

# ---------------------------------------------------------------------------
# Post-Game Quiz
# ---------------------------------------------------------------------------
QUIZ_MAX_QUESTIONS = 4
QUIZ_BUTTON_WIDTH_MARGIN = 200
QUIZ_BUTTON_HEIGHT = 60
QUIZ_BUTTON_GAP = 20
QUIZ_BUTTON_START_Y = 200
QUIZ_FONT_SIZE = 40

# ---------------------------------------------------------------------------
# Scoring Weights & Thresholds
# ---------------------------------------------------------------------------
# Multitasking rating
SCORE_COLLISION_WEIGHT = 0.7
SCORE_ARC_CORRECT_WEIGHT = 0.2
SCORE_ARC_INCORRECT_WEIGHT = 0.1

# Pattern-recognition score
SCORE_PATTERN_PENALTY = 0.5
SCORE_PATTERN_DROPOFF = 2

# Observation score
SCORE_OBSERVATION_PENALTY = 10

# Final composite weights
SCORE_WAYPOINT_WEIGHT = 0.3
SCORE_AIRCRAFT_WEIGHT = 0.3
SCORE_ARC_WEIGHT = 0.2
SCORE_QUIZ_WEIGHT = 0.2
SCORE_COLLISION_PENALTY_WEIGHT = 0.1
SCORE_COLLISION_MAX = 10           # collision count at which penalty is maximum
SCORE_PASS_THRESHOLD = 0.8

# ---------------------------------------------------------------------------
# Game Timing
# ---------------------------------------------------------------------------
TARGET_FPS = 60
GAME_DURATION_TICKS = 7200         # 2 minutes at 60 FPS
