# 🍉 Fruit Ninja Deluxe Edition

A hand‑tracking remake of the classic **Fruit Ninja**, with brand‑new twists and power‑ups. Slice fruits, dodge bombs, and chase high scores — all powered by **OpenCV** and **MediaPipe**.

---

## ✨ Features

* Classic fruit slicing gameplay with your **hand as the blade**.
* **Bombs** 💣 — slice one and it’s game over.
* **Rainbow Fruits** 🌈 — extra points and flashy visuals.
* **Golden Fruit** 🟡 — icy blue bonus for massive score boosts.
* **Freeze Fruit** ❄️ — slow down gravity to gain control.
* **Frenzy Mode** 🔥 — triggered by combos; floods the screen with fruits.
* **Combo System** — slice multiple fruits quickly for multipliers.
* Splash effects, trails, explosions, and score multipliers.

---

## 🎮 How to Play

1. Run the program with your webcam active.
2. Use your **hand** to slice through fruits. The fingertip is tracked as your blade.
3. Slice fruits to score points:

   * Normal fruit: +100 pts
   * Rainbow fruit: +500 pts
   * Golden fruit: +1000 pts
   * Combos increase your multiplier.
4. Avoid bombs! Slicing one ends the game.
5. Power‑ups:

   * **Freeze fruit** slows down gravity.
   * **Rainbow fruit** cycles colors and adds extra points.
   * **Frenzy mode** spawns a fruit storm if you hit big combos.
6. Lose 3 lives → Game Over. Press `R` to restart. Press `Q` to quit.

---

## 🛠️ Installation & Setup

### Requirements

* Python 3.9+
* [OpenCV](https://pypi.org/project/opencv-python/)
* [MediaPipe](https://pypi.org/project/mediapipe/)
* NumPy

### Install dependencies

```bash
pip install opencv-python mediapipe numpy
```

### Run the game

```bash
python fruit_ninja_deluxe.py
```

---

## 🤝 Contributing

Want to add new power‑ups, graphics, or even multiplayer slicing? Open an issue or submit a PR.

---

## 📜 License

All rights reserved by the author. You may not copy, modify, or distribute without permission.
