import time
import os

import cv2
import mediapipe as mp
import pygame

# Motion tuning
MOVEMENT_THRESHOLD = 0.0025        # smaller value = more sensitive to quick moves
DIRECTION_CHANGE_TARGET = 4        # number of direction changes needed to trigger party mode
NO_MOTION_TIMEOUT = 0.5            # seconds with no strong motion before reset
HAND_LOST_GRACE = 1.5              # seconds we tolerate hands briefly disappearing

# Visual tuning
FLASH_INTERVAL_FRAMES = 1          # check for flash every frame during party mode
FLASH_INTENSITY_BASE = 0.3         # base flash brightness (lighter)
FLASH_INTENSITY_SCALE = 3.0        # extra brightness from motion

# Audio
MUSIC_FILE = "six_seven_theme.mp3"


def get_average_wrist_height(results):
    """Return average wrist y in normalized coordinates, or None if no hands."""
    if not results or not results.multi_hand_landmarks:
        return None

    mp_hands = mp.solutions.hands
    ys = []
    for hand_landmarks in results.multi_hand_landmarks:
        wrist = hand_landmarks.landmark[mp_hands.HandLandmark.WRIST]
        ys.append(wrist.y)
    if not ys:
        return None
    return sum(ys) / len(ys)


def apply_flash_effect(frame, intensity=0.5):
    """Overlay a white flash on the frame."""
    overlay = frame.copy()
    h, w, _ = frame.shape
    cv2.rectangle(overlay, (0, 0), (w, h), (255, 255, 255), -1)
    return cv2.addWeighted(overlay, intensity, frame, 1 - intensity, 0)


def load_music():
    """Load the music file from the same folder as this script."""
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        music_path = os.path.join(script_dir, MUSIC_FILE)
        if not os.path.exists(music_path):
            print(f"[audio] Music file not found at {music_path}")
            return False

        pygame.mixer.music.load(music_path)
        print(f"[audio] Loaded music file: {music_path}")
        return True
    except Exception as e:
        print("[audio] Error loading music:", e)
        return False


def start_music():
    if not pygame.mixer.music.get_busy():
        pygame.mixer.music.play(-1)
        print("[audio] Music started")


def stop_music():
    if pygame.mixer.music.get_busy():
        pygame.mixer.music.stop()
        print("[audio] Music stopped")


def main():
    print("[core] starting 67 Detector v5 ui_reset")

    # Audio setup
    try:
        pygame.mixer.init()
        print("[audio] pygame mixer initialized")
    except Exception as e:
        print("[audio] Error initializing pygame mixer:", e)
    music_loaded = load_music()

    # MediaPipe setup
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(
        static_image_mode=False,
        max_num_hands=2,
        min_detection_confidence=0.25,
        min_tracking_confidence=0.25,
    )
    drawing_utils = mp.solutions.drawing_utils

    # Camera setup
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    print("[core] camera opened:", cap.isOpened())
    if not cap.isOpened():
        return

    # Motion state
    last_height = None
    last_direction = None
    direction_changes = 0

    last_motion_time = time.time()      # last time we saw strong motion
    last_seen_hands_time = time.time()  # last time at least one hand was visible

    last_dy = 0.0
    current_direction = "none"

    party_mode = False
    frame_count = 0
    hud_visible = False   # HUD starts hidden until you move

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame_count += 1
        frame = cv2.flip(frame, 1)

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        rgb.flags.writeable = False
        results = hands.process(rgb)
        rgb.flags.writeable = True

        num_hands = len(results.multi_hand_landmarks) if results and results.multi_hand_landmarks else 0
        now = time.time()

        # Track if we have at least one hand
        if num_hands >= 1:
            last_seen_hands_time = now

        # Decide what to use for avg_height
        if num_hands >= 1:
            avg_height = get_average_wrist_height(results)
        else:
            # No hands this frame, use a grace period where we pretend the last position is still valid
            if last_height is not None and (now - last_seen_hands_time) <= HAND_LOST_GRACE:
                avg_height = last_height
            else:
                avg_height = None

        # Draw skeletons whenever hands are visible
        if results and results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                drawing_utils.draw_landmarks(
                    frame,
                    hand_landmarks,
                    mp_hands.HAND_CONNECTIONS,
                    drawing_utils.DrawingSpec(color=(0, 255, 0), thickness=3, circle_radius=4),
                    drawing_utils.DrawingSpec(color=(0, 0, 255), thickness=2, circle_radius=2),
                )

        # Motion and direction tracking
        if avg_height is not None:
            if last_height is not None:
                dy = avg_height - last_height
                last_dy = dy

                if abs(dy) > MOVEMENT_THRESHOLD:
                    current_direction = "up" if dy < 0 else "down"
                    last_motion_time = now
                    hud_visible = True  # as soon as we see motion, show HUD again

                    if last_direction is not None and current_direction != last_direction:
                        direction_changes += 1
                        print(
                            f"[motion] change {direction_changes} "
                            f"(dir={current_direction}, dy={dy:.4f})"
                        )

                        # Trigger party mode after enough direction changes
                        if direction_changes >= DIRECTION_CHANGE_TARGET and not party_mode:
                            party_mode = True
                            print("[core] 67 mode ON")
                            if music_loaded:
                                start_music()

                    last_direction = current_direction

            last_height = avg_height

        # If we have not had strong motion for a while, reset and stop party mode
        if now - last_motion_time > NO_MOTION_TIMEOUT:
            if party_mode:
                print("[core] 67 mode OFF (no motion)")
                party_mode = False
                if music_loaded:
                    stop_music()

            if direction_changes != 0:
                print("[motion] reset changes due to timeout")

            direction_changes = 0
            last_direction = None
            current_direction = "none"
            last_dy = 0.0
            last_motion_time = now
            hud_visible = False  # hide HUD when idle so it feels reset

        # HUD text (only when visible)
        if hud_visible:
            status_text = "67!!!" if party_mode else "Ready"
            cv2.putText(
                frame,
                status_text,
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                1.0,
                (0, 255, 0) if party_mode else (0, 255, 255),
                2,
                cv2.LINE_AA,
            )
            cv2.putText(
                frame,
                f"hands: {num_hands}",
                (10, 60),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255, 255, 255),
                2,
                cv2.LINE_AA,
            )
            cv2.putText(
                frame,
                f"changes: {direction_changes}",
                (10, 90),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255, 255, 255),
                2,
                cv2.LINE_AA,
            )
            cv2.putText(
                frame,
                f"dir: {current_direction}  dy: {last_dy:+.3f}",
                (10, 120),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 200, 255),
                2,
                cv2.LINE_AA,
            )

        # Velocity style flashes in party mode, tied to motion
        if party_mode:
            # Only flash when there is actual movement
            if abs(last_dy) > MOVEMENT_THRESHOLD:
                intensity = FLASH_INTENSITY_BASE + FLASH_INTENSITY_SCALE * abs(last_dy)
                # keep it lighter, not full white
                intensity = max(0.2, min(0.7, intensity))
                if frame_count % FLASH_INTERVAL_FRAMES == 0:
                    frame = apply_flash_effect(frame, intensity=intensity)

        cv2.imshow("67 Detector", frame)

        key = cv2.waitKey(1) & 0xFF

        # Manual music toggle for testing: press m to turn music on or off
        if key == ord("m") and music_loaded:
            if pygame.mixer.music.get_busy():
                print("[audio] manual toggle OFF (m key)")
                stop_music()
            else:
                print("[audio] manual toggle ON (m key)")
                start_music()

        if key == ord("q"):
            print("[core] q pressed, exiting")
            break

    cap.release()
    cv2.destroyAllWindows()
    if music_loaded:
        stop_music()
    print("[core] clean exit")


if __name__ == "__main__":
    main()