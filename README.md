# 67 Detector

A tiny computer vision toy that detects the viral "6 7" hand motion and turns it into a mini light show with music.

The "6 7 motion" is a palm up, bounce style gesture: both hands move up and down like a scale, usually while someone says "six seven". This project watches your webcam, tracks your wrists with MediaPipe Hands, and when it sees you doing the motion enough times it:

- Shows a HUD with live motion info
- Plays a theme song
- Adds soft white flashes over the video timed to your movement

When you stop, everything fades out and the app resets so you can start again.

## Features

- Real time wrist tracking with MediaPipe Hands
- One or two hands work
- Direction change based motion logic
- Party mode after a set number of up and down bounces
- Automatic reset when you stop moving
- Music playback with pygame mixer
- Velocity style white flashes when motion is detected
- Manual music toggle on the keyboard

## Controls

- `q`  quit the app
- `m`  toggle music on or off manually

## Requirements

- Python 3 point 10 or 3 point 11
- A webcam
- Packages listed in `requirements.txt`

## Setup

Create and activate a virtual environment (optional but recommended):

```bash
python3 -m venv .venv
source .venv/bin/activate