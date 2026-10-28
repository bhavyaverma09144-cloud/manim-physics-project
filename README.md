# Manim Physics Project

This repository contains a simple Manim scene for a double-pendulum-style mechanical linkages animation.

## Local setup

1. Create a virtual environment
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```
2. Install dependencies
   ```bash
   python -m pip install --upgrade pip
   python -m pip install -r requirements.txt
   ```
3. Render the animation
   ```bash
   manim -pqh scene.py MechanicalLinkage
   ```

The animation outputs are written to the `media/` directory.

## CI

The GitHub Actions workflow renders the scene automatically on pushes to `main` and uploads the generated video as an artifact.
