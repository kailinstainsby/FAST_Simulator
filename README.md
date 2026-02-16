# Skybound FAST — Pilot Natural Aptitude Practice Test

A multi-task pilot aptitude test simulator built with **Pygame**, designed for
aspiring cadets or anyone who wants to sharpen their multitasking,
pattern-recognition and observational skills under pressure.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Pygame](https://img.shields.io/badge/Pygame-2.5%2B-green)

---

## Overview

Skybound FAST (Future Aptitude Selection Tool) recreates the style of natural
aptitude assessments used in pilot selection programmes. It simultaneously
tests the candidate across three concurrent challenge areas:

| Section | Description |
|---|---|
| **Plane Minigame** | Navigate a top-down plane through cloud obstacles using the arrow keys. |
| **Active Reasoning Challenges** | Answer timed logic / pattern-recognition questions that appear alongside the other tasks. |
| **Terrain Event Rendering** | Watch a simulated cockpit view for aircraft and waypoint events, reporting them via instrument-panel buttons. |

After the timed session ends, a **Post-Round Challenge** quiz tests recall of
in-game events (flash counts, aircraft spotted, waypoint bearings). A final
score report breaks results into four aptitude categories.

---

## Getting Started

### Prerequisites

* Python 3.10 or later
* Pygame 2.5+

### Installation

```bash
git clone https://github.com/<your-username>/skybound-fast.git
cd skybound-fast
pip install -r requirements.txt
```

### Running

```bash
python run.py
```

1. Select a **difficulty level** (1 – 5) from the menu.
2. Click the **Skybound logo** to launch the test.
3. Manage all three sections simultaneously for two minutes.
4. Answer the post-round recall quiz.
5. Review your score report.

---

## Project Structure

```
skybound-fast/
├── run.py                          # Application entry-point
├── difficulty.txt                  # Persisted difficulty setting
├── requirements.txt
│
├── skybound/                       # Main application package
│   ├── config.py                   # Centralised constants & difficulty management
│   ├── ui/
│   │   └── hover_button.py         # Image button with hover-enlarge effect
│   ├── menu/
│   │   └── difficulty_menu.py      # Difficulty selection screen
│   ├── plane_minigame/
│   │   ├── cloud.py                # Cloud obstacle entity
│   │   ├── plane.py                # Player-controlled plane
│   │   └── game.py                 # Minigame runner (standalone & embedded)
│   ├── active_reasoning/
│   │   ├── question_database.py    # 203-question bank
│   │   ├── quiz_button.py          # Quadrant answer button
│   │   └── game.py                 # Timed question cycle
│   ├── terrain_view/
│   │   ├── cloud.py                # Perspective cloud with pseudo-3D movement
│   │   ├── aircraft.py             # Aircraft entities
│   │   ├── waypoint.py             # Waypoint markers
│   │   ├── instrument_button.py    # Aircraft / waypoint report buttons
│   │   ├── indicator_light.py      # Flashing indicator lights
│   │   └── game.py                 # Integrated game loop
│   └── post_game/
│       ├── recall_quiz.py          # Post-round memory quiz
│       └── score_report.py         # Score calculation & display
│
└── assets/
    ├── menu/                       # Difficulty menu sprites
    ├── plane/                      # Plane minigame sprites
    ├── terrain/                    # Terrain-view sprites
    └── panel/                      # Navigation-arrow sprites
```

---

## Scoring

| Category | What It Measures |
|---|---|
| **Multitasking** | Ability to avoid collisions while answering questions. |
| **Pattern Recognition** | Accuracy on active reasoning challenges. |
| **Memory Recall** | Post-round quiz accuracy on in-game events. |
| **Observation** | Correctly reporting aircraft and waypoint events. |

A weighted final score determines an overall **PASS / FAIL** result.

---

## Difficulty Levels

| Level | Effect |
|---|---|
| 1 | Slow cloud spawns, basic aircraft types |
| 2 | Moderate cloud spawns |
| 3 | Default — balanced challenge |
| 4 | Dense cloud walls with gaps, more aircraft types |
| 5 | Highest density and spawn chance, full aircraft roster |

---

## Controls

| Key / Action | Function |
|---|---|
| **↑ / ↓ Arrow keys** | Move the plane up / down |
| **Mouse click** | Select answers, press instrument buttons |

---

## License

This project is provided for educational and portfolio purposes.
