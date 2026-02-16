"""Integrated terrain-view game loop.

Orchestrates all three concurrent challenge areas (plane minigame,
active reasoning, terrain observation) within a single Pygame window,
then transitions to the post-game quiz and score report.
"""

from __future__ import annotations

import os
import random
from typing import List

import pygame

from skybound.config import (
    AIRCRAFT_COOLDOWN_RANGE,
    AIRCRAFT_MAX_CONCURRENT,
    BLACK,
    GAME_DURATION_TICKS,
    PANEL_MENU_HEIGHT_DIVISOR,
    PANEL_MENU_HEIGHT_EXTRA,
    PANEL_MENU_WIDTH_DIVISOR,
    PM_EMBED_X,
    PM_EMBED_Y,
    PM_PANEL_HEIGHT,
    PM_PANEL_WIDTH,
    ROTATION_ANGLE_CHOICES,
    ROTATION_DURATION_TICKS,
    ROTATION_SPEED,
    TARGET_FPS,
    TER_BACKGROUND_SCALE,
    TER_CLOUD_COOLDOWN_RANGE,
    TER_CLOUD_SPAWN_X_MARGIN,
    TER_CLOUD_SPAWN_Y,
    TER_SCREEN_HEIGHT,
    TER_SCREEN_WIDTH,
    TERRAIN_ASSETS,
    PANEL_ASSETS,
    WAYPOINT_COOLDOWN_RANGE,
    WHITE,
    load_difficulty,
)
from skybound.active_reasoning.game import ActiveReasoningGame
from skybound.plane_minigame.game import PlaneMinigame
from skybound.post_game.recall_quiz import RecallQuiz
from skybound.post_game.score_report import ScoreReport
from skybound.terrain_view.aircraft import Aircraft
from skybound.terrain_view.cloud import TerrainCloud
from skybound.terrain_view.indicator_light import IndicatorLight
from skybound.terrain_view.instrument_button import InstrumentButton
from skybound.terrain_view.waypoint import Waypoint
from skybound.ui.hover_button import HoverButton


def run_game(difficulty: int | None = None) -> None:
    """Run the full Skybound FAST test session.

    This is the main entry point called by the difficulty menu after a
    level has been selected.  It initialises all sub-systems, runs the
    timed game loop, and finishes with the post-game quiz and score
    report.

    Parameters
    ----------
    difficulty : int, optional
        Difficulty level (1–5).  If omitted, reads from *difficulty.txt*.
    """
    pygame.init()

    difficulty = difficulty if difficulty is not None else load_difficulty()
    clock = pygame.time.Clock()
    screen = pygame.display.set_mode((TER_SCREEN_WIDTH, TER_SCREEN_HEIGHT))
    pygame.display.set_caption("SKYBOUND FAST")

    # ----- Background -----
    bg_image = pygame.image.load(os.path.join(TERRAIN_ASSETS, "backdrop.png"))
    bg_width = int(bg_image.get_width() * TER_BACKGROUND_SCALE)
    bg_height = int(bg_image.get_height() * TER_BACKGROUND_SCALE)
    background = pygame.transform.smoothscale(bg_image, (bg_width, bg_height))
    rotation_origin = (TER_SCREEN_WIDTH // 2, int(TER_SCREEN_HEIGHT / 1.5))

    # ----- Sub-games -----
    plane_minigame = PlaneMinigame(difficulty)
    arc_minigame = ActiveReasoningGame(difficulty)
    plane_surface = pygame.Surface((PM_PANEL_WIDTH, PM_PANEL_HEIGHT))

    # ----- Instrument panel -----
    menu_width = TER_SCREEN_WIDTH // PANEL_MENU_WIDTH_DIVISOR
    menu_height = int(TER_SCREEN_HEIGHT / PANEL_MENU_HEIGHT_DIVISOR + PANEL_MENU_HEIGHT_EXTRA)
    menu_x = TER_SCREEN_WIDTH // 2 - menu_width // 2
    menu_y = TER_SCREEN_HEIGHT // 2
    menu_rect = pygame.Rect(menu_x, menu_y, menu_width, menu_height)

    menu_overlay_img = pygame.image.load(os.path.join(TERRAIN_ASSETS, "menu1.png"))
    menu_overlay = pygame.transform.smoothscale(menu_overlay_img, (menu_width, menu_height))

    aircraft_button = InstrumentButton(is_aircraft=True, menu_x=menu_x, menu_y=menu_y)
    waypoint_button = InstrumentButton(is_aircraft=False, menu_x=menu_x, menu_y=menu_y)

    # ----- Indicator lights -----
    max_flashes = difficulty + 5
    light_left = IndicatorLight(TER_SCREEN_WIDTH // 2, menu_y - 15, max_flashes)
    light_right = IndicatorLight(TER_SCREEN_WIDTH // 2 + 40, menu_y - 15, max_flashes)

    # ----- Entity lists -----
    terrain_clouds: List[TerrainCloud] = []
    aircraft_list: List[Aircraft] = []
    waypoint_list: List[Waypoint] = []

    # ----- Timers / counters -----
    ticks = 0
    cloud_timer = 0
    cloud_cooldown = random.randint(*TER_CLOUD_COOLDOWN_RANGE)
    aircraft_timer = 0
    aircraft_cooldown = random.randint(*AIRCRAFT_COOLDOWN_RANGE)
    waypoint_timer = 0
    waypoint_cooldown = random.randint(*WAYPOINT_COOLDOWN_RANGE)

    # ----- Observation tracking -----
    aircraft_total = 0
    aircraft_correct = 0
    aircraft_incorrect = 0
    waypoint_total = 0
    waypoint_correct = 0
    waypoint_incorrect = 0
    waypoint_active = False
    quiz_waypoint_types: List[int] = []

    # ----- Rotation state -----
    rotation_angle = 0.0
    rotation_target = 0.0
    is_rotating = False
    rotation_countdown = 0

    # ----- Post-game -----
    quiz = RecallQuiz(screen)
    report = ScoreReport(screen)

    # Report page navigation buttons
    left_img = pygame.image.load(os.path.join(PANEL_ASSETS, "left.png")).convert_alpha()
    right_img = pygame.image.load(os.path.join(PANEL_ASSETS, "right.png")).convert_alpha()
    left_button = HoverButton(420, 460, left_img, 0.8)
    right_button = HoverButton(480, 460, right_img, 0.8)
    report_page = 1

    # ===================================================================
    # Game loop
    # ===================================================================
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            quiz.handle_event(event)

        ticks += 1

        # ------ Trigger post-game quiz after time expires ------
        if ticks >= GAME_DURATION_TICKS and not quiz.is_active:
            quiz.aircraft_count = aircraft_total
            quiz.waypoint_count = waypoint_total
            quiz.left_flashes = light_left.flash_count
            quiz.right_flashes = light_right.flash_count
            quiz.total_flashes = light_left.flash_count + light_right.flash_count
            quiz.waypoints = quiz_waypoint_types
            quiz.generate_question()

        # ------ Quiz phase ------
        if quiz.is_active:
            quiz.draw()

        # ------ Score report phase ------
        if quiz.questions_asked >= 4:
            screen.fill(WHITE)
            if report_page == 1:
                report.draw_summary(
                    collisions=plane_minigame.collisions,
                    waypoint_correct=waypoint_correct,
                    waypoint_total=waypoint_total,
                    waypoint_incorrect=waypoint_incorrect,
                    aircraft_correct=aircraft_correct,
                    aircraft_total=aircraft_total,
                    aircraft_incorrect=aircraft_incorrect,
                    arc_correct=arc_minigame.correct_answers,
                    arc_total=arc_minigame.question_count,
                    quiz_correct=quiz.correct_answers,
                    quiz_total=quiz.questions_asked - 1,
                )
                if right_button.draw(screen):
                    report_page += 1

            if report_page == 2:
                report.draw_detailed_scores(
                    collisions=plane_minigame.collisions,
                    arc_correct=arc_minigame.correct_answers,
                    arc_total=arc_minigame.question_count,
                    quiz_correct=quiz.correct_answers,
                    quiz_total=quiz.questions_asked - 1,
                    waypoint_correct=waypoint_correct,
                    waypoint_total=waypoint_total,
                    waypoint_incorrect=waypoint_incorrect,
                    aircraft_correct=aircraft_correct,
                    aircraft_total=aircraft_total,
                    aircraft_incorrect=aircraft_incorrect,
                )
                if left_button.draw(screen):
                    report_page -= 1

        # ------ Active gameplay ------
        if not quiz.is_active and ticks <= GAME_DURATION_TICKS:
            # === Waypoint spawning ===
            waypoint_timer += 1
            if (
                waypoint_timer > waypoint_cooldown
                and random.randint(0, 1) == 1
                and len(waypoint_list) == 0
            ):
                waypoint_timer = 0
                waypoint_cooldown = random.randint(*WAYPOINT_COOLDOWN_RANGE)
                waypoint_active = True

                # Start a banking rotation
                rotation_countdown = ROTATION_DURATION_TICKS
                is_rotating = True
                rotation_target = random.choice(ROTATION_ANGLE_CHOICES)

                # Spawn waypoint on the side matching the turn direction
                if rotation_target > 0:
                    wp_x = random.randint(
                        TER_SCREEN_WIDTH // 2 + 100, TER_SCREEN_WIDTH - 300
                    )
                else:
                    wp_x = random.randint(300, TER_SCREEN_WIDTH // 2 - 100)

                wp_type = random.randint(0, 2)
                waypoint_list.append(Waypoint(wp_x, wp_type))
                quiz_waypoint_types.append(wp_type)
                waypoint_total += 1

            # === Rotation update ===
            if is_rotating:
                if rotation_countdown > 0:
                    rotation_countdown -= 1
                else:
                    if abs(rotation_angle - rotation_target) >= 0.5:
                        direction = 1 if rotation_target > rotation_angle else -1
                        rotation_angle += ROTATION_SPEED * direction
                    else:
                        rotation_target = 0

                    if abs(rotation_angle) <= 0.5 and rotation_target == 0:
                        is_rotating = False
            else:
                rotation_angle = 0.0

            # === Draw rotated background ===
            rotated_bg = pygame.transform.rotate(background, rotation_angle)
            bg_rect = rotated_bg.get_rect(center=rotation_origin)
            screen.blit(rotated_bg, bg_rect.topleft)

            # === Waypoints ===
            for wp in waypoint_list[:]:
                wp.draw(screen, rotation_angle)
                wp.move()

                if wp.is_off_screen():
                    waypoint_list.remove(wp)
                    waypoint_active = False

                if is_rotating:
                    wp.apply_rotation(rotation_angle)

            # === Terrain clouds ===
            cloud_timer += 1
            if cloud_timer > cloud_cooldown:
                if random.randint(0, 1) == 1:
                    spawn_x = random.randint(
                        TER_CLOUD_SPAWN_X_MARGIN,
                        TER_SCREEN_WIDTH - TER_CLOUD_SPAWN_X_MARGIN,
                    )
                    terrain_clouds.append(TerrainCloud(spawn_x, TER_CLOUD_SPAWN_Y))
                cloud_timer = 0
                cloud_cooldown = random.randint(*TER_CLOUD_COOLDOWN_RANGE)

            for cloud in terrain_clouds[:]:
                cloud.draw(screen, rotation_angle)
                cloud.move()

                if cloud.is_off_screen():
                    terrain_clouds.remove(cloud)

                if is_rotating:
                    cloud.apply_rotation(rotation_angle)

            # === Aircraft ===
            aircraft_timer += 1
            if (
                aircraft_timer > aircraft_cooldown
                and len(aircraft_list) < AIRCRAFT_MAX_CONCURRENT
                and random.randint(0, 1) == 1
            ):
                plane_type = (
                    random.randint(0, 8) if difficulty > 3
                    else random.randint(0, 3)
                )
                from_left = bool(random.randint(0, 1))
                y_pos = random.randint(20, 80)
                aircraft_list.append(Aircraft(from_left, y_pos, plane_type))
                aircraft_total += 1
                aircraft_timer = 0
                aircraft_cooldown = random.randint(*AIRCRAFT_COOLDOWN_RANGE)

            for ac in aircraft_list[:]:
                ac.draw(screen, rotation_angle)
                ac.move()

                if ac.is_off_screen():
                    aircraft_list.remove(ac)

                if is_rotating:
                    ac.apply_rotation(rotation_angle)

            # === Instrument panel ===
            pygame.draw.rect(screen, BLACK, menu_rect)
            screen.blit(menu_overlay, (menu_x, menu_y))

            # Waypoint button
            if waypoint_button.draw(screen):
                if waypoint_active:
                    waypoint_correct += 1
                    waypoint_active = False
                else:
                    waypoint_incorrect += 1

            # Aircraft button
            if aircraft_button.draw(screen):
                clicked_any = False
                for ac in aircraft_list:
                    if not ac.clicked:
                        ac.clicked = True
                        aircraft_correct += 1
                        clicked_any = True
                        break
                if not clicked_any:
                    aircraft_incorrect += 1

            # === Indicator lights ===
            light_left.update()
            light_left.draw(screen)
            light_right.update()
            light_right.draw(screen)

            # === Embedded plane minigame ===
            delta_time = clock.tick(TARGET_FPS) / 1000.0
            plane_minigame.update(plane_surface)
            screen.blit(plane_surface, (PM_EMBED_X, menu_y))

            # === Embedded ARC minigame ===
            arc_minigame.update(screen)

        pygame.display.update()
        clock.tick(TARGET_FPS)

    pygame.quit()
