import time
import os
import random

import cv2
import mediapipe as mp
import pygame
import imageio

# Motion tuning
MOVEMENT_THRESHOLD = 0.0025        # smaller value = more sensitive to quick moves
DIRECTION_CHANGE_TARGET = 4        # number of direction changes needed to trigger 67 mode
NO_MOTION_TIMEOUT = 0.5            # seconds with no strong motion before reset
HAND_LOST_GRACE = 1.5              # seconds we tolerate hands briefly disappearing

# Visual tuning
FLASH_INTERVAL_FRAMES = 1          # check for flash every frame during 67 mode
FLASH_INTENSITY_BASE = 0.3         # base flash brightness (lighter)
FLASH_INTENSITY_SCALE = 3.0        # extra brightness from motion

# Audio
MUSIC_FILE = "six_seven_theme.mp3"

# Popup settings (OpenCV windows)
POPUP_FOLDER = "popups"            # folder containing your gif files
POPUP_DELAY_SECONDS = 5.0          # seconds after music starts in 67 mode before popups start
POPUP_SHUFFLE_INTERVAL = 0.1      # seconds between "close one and reopen on top" events
POPUP_NUM_WINDOWS = 20              # how many popup windows at once (matches your seven gifs)
POPUP_WIDTH = 800                  # width to resize popup gif frames


def get_screen_size():
    try:
        import tkinter as tk
        root = tk.Tk()
        root.withdraw()
        w = root.winfo_screenwidth()
        h = root.winfo_screenheight()
        root.destroy()
        print(f"[screen] detected screen size: {w}x{h}")
        return w, h
    except Exception:
        print("[screen] tkinter not available, using default 1920x1080")
        return 1920, 1080



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


def load_popup_gifs():
    """
    Load all gifs and images from POPUP_FOLDER.

    Each entry in returned list is a list of OpenCV BGR frames
    resized to POPUP_WIDTH while keeping aspect ratio.
    To avoid using too much memory, we cap frames per gif.
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    folder = os.path.join(script_dir, POPUP_FOLDER)

    if not os.path.isdir(folder):
        print(f"[popup] folder not found: {folder}")
        return []

    files = []
    for name in os.listdir(folder):
        lower = name.lower()
        if lower.endswith(".gif") or lower.endswith(".png") or lower.endswith(".jpg") or lower.endswith(".jpeg"):
            files.append(os.path.join(folder, name))

    if not files:
        print("[popup] no images found in popups folder")
        return []

    MAX_FRAMES_PER_GIF = 30  # cap frames per gif to avoid huge memory usage
    all_sequences = []
    for path in files:
        try:
            frames = imageio.mimread(path)
            if not frames:
                print(f"[popup] no frames in {path}")
                continue

            # Subsample frames if there are too many
            if len(frames) > MAX_FRAMES_PER_GIF:
                step = max(1, len(frames) // MAX_FRAMES_PER_GIF)
                frames = frames[::step]

            cv_frames = []
            for f in frames:
                img = f
                if img.ndim == 3:
                    if img.shape[2] == 4:
                        img = cv2.cvtColor(img, cv2.COLOR_RGBA2BGR)
                    else:
                        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
                h, w = img.shape[:2]
                scale = POPUP_WIDTH / float(w)
                new_size = (POPUP_WIDTH, int(h * scale))
                img_resized = cv2.resize(img, new_size, interpolation=cv2.INTER_AREA)
                cv_frames.append(img_resized)

            if cv_frames:
                all_sequences.append(cv_frames)
                print(f"[popup] loaded {len(cv_frames)} frames from {path}")
        except Exception as e:
            print(f"[popup] error loading {path}:", e)

    print(f"[popup] total gif sequences loaded: {len(all_sequences)}")
    return all_sequences



def create_popup_windows(popup_gifs, screen_size):
    """
    Create POPUP_NUM_WINDOWS OpenCV windows showing random gifs
    at random positions across the entire screen.
    """
    if not popup_gifs:
        return []

    screen_w, screen_h = screen_size
    windows = []

    num_windows = POPUP_NUM_WINDOWS

    for i in range(num_windows):
        seq = random.choice(popup_gifs)
        name = f"67POP_{i}"

        cv2.namedWindow(name, cv2.WINDOW_NORMAL)
        try:
            cv2.setWindowProperty(name, cv2.WND_PROP_TOPMOST, 1)
        except Exception:
            # Some platforms or backends may not support this, so we just ignore it
            pass

        sample = seq[0]
        h_img, w_img = sample.shape[:2]

        max_x = max(0, screen_w - w_img)
        max_y = max(0, screen_h - h_img)
        x = random.randint(0, max_x) if max_x > 0 else 0
        y = random.randint(0, max_y) if max_y > 0 else 0

        cv2.moveWindow(name, x, y)

        windows.append({
            "name": name,
            "frames": seq,
            "idx": random.randint(0, len(seq) - 1),
            "x": x,
            "y": y,
        })

    print(f"[popup] created {len(windows)} popup windows at random positions")
    return windows




def destroy_popup_windows(popup_windows):
    """Close all popup windows and clear list."""
    for w in popup_windows:
        try:
            cv2.destroyWindow(w["name"])
        except Exception:
            pass
    popup_windows.clear()
    print("[popup] destroyed all popup windows")


def shuffle_one_popup_window(popup_windows, popup_gifs, screen_size):
    """
    Close one existing popup window and reopen it with a random gif
    at a new random position on the full screen.
    """
    if not popup_windows or not popup_gifs:
        return popup_windows

    screen_w, screen_h = screen_size

    idx = random.randrange(len(popup_windows))
    w_info = popup_windows[idx]
    name = w_info["name"]

    try:
        cv2.destroyWindow(name)
    except Exception:
        pass

    seq = random.choice(popup_gifs)
    cv2.namedWindow(name, cv2.WINDOW_NORMAL)
    try:
        cv2.setWindowProperty(name, cv2.WND_PROP_TOPMOST, 1)
    except Exception:
        # Some platforms or backends may not support this, so we just ignore it
        pass


    sample = seq[0]
    h_img, w_img = sample.shape[:2]
    max_x = max(0, screen_w - w_img)
    max_y = max(0, screen_h - h_img)
    x = random.randint(0, max_x) if max_x > 0 else 0
    y = random.randint(0, max_y) if max_y > 0 else 0

    cv2.moveWindow(name, x, y)

    popup_windows[idx] = {
        "name": name,
        "frames": seq,
        "idx": 0,
        "x": x,
        "y": y,
    }

    print(f"[popup] reshuffled window {name} to {x},{y}")
    return popup_windows



def main():
    print("[core] starting 67 Detector v12 full_screen_popups")

    screen_size = get_screen_size()

    try:
        pygame.mixer.init()
        print("[audio] pygame mixer initialized")
    except Exception as e:
        print("[audio] Error initializing pygame mixer:", e)
    music_loaded = load_music()

    popup_gifs = load_popup_gifs()

    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(
        static_image_mode=False,
        max_num_hands=2,
        min_detection_confidence=0.25,
        min_tracking_confidence=0.25,
    )
    drawing_utils = mp.solutions.drawing_utils

    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    print("[core] camera opened:", cap.isOpened())
    if not cap.isOpened():
        return

    last_height = None
    last_direction = None
    direction_changes = 0

    last_motion_time = time.time()
    last_seen_hands_time = time.time()

    last_dy = 0.0
    current_direction = "none"

    party_mode = False
    frame_count = 0
    hud_visible = False

    music_start_time = None
    popup_active = False
    popup_windows = []
    popup_last_shuffle_time = 0.0

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

        if num_hands >= 1:
            last_seen_hands_time = now

        if num_hands >= 1:
            avg_height = get_average_wrist_height(results)
        else:
            if last_height is not None and (now - last_seen_hands_time) <= HAND_LOST_GRACE:
                avg_height = last_height
            else:
                avg_height = None

        if results and results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                drawing_utils.draw_landmarks(
                    frame,
                    hand_landmarks,
                    mp_hands.HAND_CONNECTIONS,
                    drawing_utils.DrawingSpec(color=(0, 255, 0), thickness=3, circle_radius=4),
                    drawing_utils.DrawingSpec(color=(0, 0, 255), thickness=2, circle_radius=2),
                )

        if avg_height is not None:
            if last_height is not None:
                dy = avg_height - last_height
                last_dy = dy

                if abs(dy) > MOVEMENT_THRESHOLD:
                    current_direction = "up" if dy < 0 else "down"
                    hud_visible = True

                    if last_direction is not None and current_direction != last_direction:
                        direction_changes += 1
                        last_motion_time = now
                        print(
                            f"[motion] change {direction_changes} "
                            f"(dir={current_direction}, dy={dy:.4f})"
                        )

                        if direction_changes >= DIRECTION_CHANGE_TARGET and not party_mode:
                            party_mode = True
                            print("[core] 67 mode ON")
                            if music_loaded:
                                start_music()
                                music_start_time = time.time()
                                print("[core] music_start_time set")
                            else:
                                music_start_time = None

                    last_direction = current_direction

            last_height = avg_height

        idle_time = now - last_motion_time
        if idle_time > NO_MOTION_TIMEOUT:
            if party_mode:
                print(f"[core] 67 mode OFF (idle {idle_time:.2f}s)")
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
            hud_visible = False

            popup_active = False
            destroy_popup_windows(popup_windows)
            music_start_time = None

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

        if party_mode:
            if abs(last_dy) > MOVEMENT_THRESHOLD:
                intensity = FLASH_INTENSITY_BASE + FLASH_INTENSITY_SCALE * abs(last_dy)
                intensity = max(0.2, min(0.7, intensity))
                if frame_count % FLASH_INTERVAL_FRAMES == 0:
                    frame = apply_flash_effect(frame, intensity=intensity)

        if party_mode and music_start_time is not None and popup_gifs:
            music_elapsed = now - music_start_time
            if music_elapsed >= POPUP_DELAY_SECONDS and not popup_active:
                popup_active = True
                popup_last_shuffle_time = now
                popup_windows = create_popup_windows(popup_gifs, screen_size)
                print(f"[popup] popups activated after {music_elapsed:.2f}s")

        if popup_active and popup_windows:
            for w_info in popup_windows:
                frames_seq = w_info["frames"]
                if not frames_seq:
                    continue
                idx = w_info["idx"]
                frame_img = frames_seq[idx]
                cv2.imshow(w_info["name"], frame_img)
                w_info["idx"] = (idx + 1) % len(frames_seq)

            if now - popup_last_shuffle_time >= POPUP_SHUFFLE_INTERVAL:
                popup_last_shuffle_time = now
                popup_windows = shuffle_one_popup_window(popup_windows, popup_gifs, screen_size)

        cv2.imshow("67 Detector", frame)

        key = cv2.waitKey(1) & 0xFF

        if key == ord("m") and music_loaded:
            if pygame.mixer.music.get_busy():
                print("[audio] manual toggle OFF (m key)")
                stop_music()
                music_start_time = None
                popup_active = False
                destroy_popup_windows(popup_windows)
            else:
                print("[audio] manual toggle ON (m key)")
                start_music()
                music_start_time = time.time()
                popup_active = False
                destroy_popup_windows(popup_windows)

        if key == ord("q"):
            print("[core] q pressed, exiting")
            break

    cap.release()
    cv2.destroyAllWindows()
    if music_loaded:
        stop_music()
    destroy_popup_windows(popup_windows)
    print("[core] clean exit")


if __name__ == "__main__":
    main()
