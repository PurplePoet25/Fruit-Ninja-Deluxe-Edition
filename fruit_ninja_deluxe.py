# Fruit Ninja Deluxe Edition - Enhanced
# Features: Bombs, Rainbow Fruits, Combos, Splash Effects, 
# NEW: Frenzy Mode, Freeze Fruit, Golden Fruit, Score Multipliers

import cv2
import time
import random
import mediapipe as mp
import math
import numpy as np

# Hand Tracking Setup
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=False, max_num_hands=1,
                       min_detection_confidence=0.7, min_tracking_confidence=0.5)

# Game State
Score = 0
Lives = 3
Fruits = []
Combos = []
slash_trail = []
splash_effects = []
rainbow_cycle = [(255, 0, 0), (255, 127, 0), (255, 255, 0), (0, 255, 0), (0, 0, 255), (75, 0, 130), (139, 0, 255)]
rainbow_index = 0
show_explosion = False
explosion_timer = 0
frenzy_mode = False
frenzy_timer = 0
freeze_mode = False
freeze_timer = 0
combo_multiplier = 1.0

# Configurations
gravity = 0.3
max_fruits = 3
spawn_rate = 1
next_spawn_time = 0
bomb_flash_interval = 0.1
bomb_flash_timer = time.time()
bomb_flash_state = True
rainbow_chance = 0.05
combo_window = 0.4
combo_timer = 0
combo_count = 0

# Slash
slash_length = 15
slash_thickness = 6
slash_color = (255, 255, 255)

# Constants
NORMAL_COLORS = [(255, 0, 0), (0, 255, 0), (0, 255, 255), (255, 0, 255)]
BOMB_COLOR = (0, 0, 0)
RAINBOW_COLOR = (255, 255, 255)
BOMB_SIZE = 30

# Utility Functions
def spawn_fruit():
    rand = random.random()
    if rand < 0.05:
        fruit_type = "freeze"      # Swapped: freeze fruit now gets golden color
        color = (255, 223, 50)     # Golden yellow
        size = 25
    elif rand < 0.1:
        fruit_type = "golden"      # Swapped: golden fruit now gets icy blue color
        color = (180, 255, 255)    # Icy blue
        size = 20
    elif rand < 0.2:
        fruit_type = "rainbow"
        color = RAINBOW_COLOR
        size = 30
    elif rand < 0.3:
        fruit_type = "bomb"
        color = BOMB_COLOR
        size = BOMB_SIZE
    else:
        fruit_type = "fruit"
        color = random.choice(NORMAL_COLORS)
        size = random.randint(20, 40)

    Fruits.append({
        "x": random.randint(50, 600),
        "y": 480,
        "vx": random.uniform(-2, 2),
        "vy": random.uniform(-17, -13),
        "gravity": gravity,
        "color": color,
        "type": fruit_type,
        "size": size,
        "time": time.time()
    })

def move_fruits():
    global Lives
    gravity_modifier = 0.1 if freeze_mode else 1
    for fruit in Fruits[:]:
        fruit["x"] += fruit["vx"] * gravity_modifier
        fruit["vy"] += fruit["gravity"] * gravity_modifier
        fruit["y"] += fruit["vy"] * gravity_modifier

        if fruit["y"] > 500:
            Fruits.remove(fruit)
            if fruit["type"] in ["fruit", "rainbow", "golden", "freeze"]:
                Lives -= 1

def add_splash(x, y, color):
    splash_effects.append({"x": x, "y": y, "color": color, "life": 1.0})

def draw_splashes(img):
    for splash in splash_effects[:]:
        alpha = splash["life"]
        overlay = img.copy()
        cv2.circle(overlay, (int(splash["x"]), int(splash["y"])), 30, splash["color"], -1)
        cv2.addWeighted(overlay, 0.25 * alpha, img, 1 - 0.25 * alpha, 0, img)
        splash["life"] -= 0.05
        if splash["life"] <= 0:
            splash_effects.remove(splash)

def distance(point1, point2):
    return math.hypot(point1[0] - point2[0], point1[1] - point2[1])

def draw_text(img, text, position, font, scale, color, thickness):
    cv2.putText(img, text, position, font, scale, (0, 0, 0), thickness + 3, lineType=cv2.LINE_AA)  # Black outline
    cv2.putText(img, text, position, font, scale, color, thickness, lineType=cv2.LINE_AA)


# Initialize camera
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Error: Could not open webcam.")
    exit()

previous_time = time.time()

while True:
    success, img = cap.read()
    if not success:
        break

    img = cv2.flip(img, 1)
    height, width, _ = img.shape
    rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb)
    now = time.time()

    if freeze_mode and now - freeze_timer > 3:
        freeze_mode = False

    if frenzy_mode and now - frenzy_timer > 5:
        frenzy_mode = False

    if Lives > 0 and results.multi_hand_landmarks:
        landmark = results.multi_hand_landmarks[0].landmark[8]
        cx, cy = int(landmark.x * width), int(landmark.y * height)
        slash_trail.append((cx, cy))
        if len(slash_trail) > slash_length:
            slash_trail.pop(0)

        sliced_this_frame = 0

        for fruit in Fruits[:]:
            for pt in slash_trail[-5:]:
                if distance(pt, (fruit["x"], fruit["y"])) < fruit["size"] + 10:
                    if fruit["type"] == "bomb":
                        add_splash(fruit["x"], fruit["y"], (0, 0, 255))
                        show_explosion = True
                        explosion_timer = now
                        Lives = 0
                    elif fruit["type"] == "freeze":
                        freeze_mode = True
                        freeze_timer = now
                        add_splash(fruit["x"], fruit["y"], (255, 223, 50))  # Splash with golden yellow color
                    elif fruit["type"] == "golden":
                        Score += int(1000 * combo_multiplier)
                        add_splash(fruit["x"], fruit["y"], (180, 255, 255))  # Splash with icy blue color
                    else:
                        Score += int((500 if fruit["type"] == "rainbow" else 100) * combo_multiplier)
                        slash_color = fruit["color"]
                        add_splash(fruit["x"], fruit["y"], fruit["color"])
                        Combos.append(time.time())
                        sliced_this_frame += 1
                    Fruits.remove(fruit)
                    break

        if sliced_this_frame >= 3:
            frenzy_mode = True
            frenzy_timer = now
            for _ in range(10):
                spawn_fruit()

    # Clean old combos beyond combo window
    Combos = [t for t in Combos if now - t < combo_window]
    combo_multiplier = 1.0 + 0.5 * len(Combos)

    if Lives > 0 and now > next_spawn_time and len(Fruits) < (10 if frenzy_mode else max_fruits):
        spawn_fruit()
        next_spawn_time = now + (1 / spawn_rate)

    if Lives > 0:
        move_fruits()

    # Draw red warning bars if any bomb is present
    if any(f["type"] == "bomb" for f in Fruits):
        cv2.rectangle(img, (0, 0), (5, height), (0, 0, 255), -1)
        cv2.rectangle(img, (width - 5, 0), (width, height), (0, 0, 255), -1)

    for fruit in Fruits:
        if fruit["type"] == "rainbow":
            fruit["color"] = rainbow_cycle[rainbow_index % len(rainbow_cycle)]

        center = (int(fruit["x"]), int(fruit["y"]))
        radius = fruit["size"]

        if fruit["type"] == "bomb":
            flash_phase = int((now - fruit["time"]) / bomb_flash_interval) % 2
            color = (255, 255, 255) if flash_phase == 0 else BOMB_COLOR
            cv2.circle(img, center, radius, color, -1)

        elif fruit["type"] == "freeze":
            # Freeze fruit is golden yellow
            cv2.circle(img, center, radius + 4, (255, 255, 255), -1)  # White outline
            cv2.circle(img, center, radius, (255, 223, 50), -1)       # Golden yellow fill

        elif fruit["type"] == "golden":
            # Golden fruit is icy blue
            cv2.circle(img, center, radius + 4, (255, 255, 255), -1)  # White outline
            cv2.circle(img, center, radius, (180, 255, 255), -1)      # Icy blue fill

        elif fruit["type"] == "rainbow":
            cv2.circle(img, center, radius + 6, (255, 255, 255), -1)
            cv2.circle(img, center, radius + 2, fruit["color"], -1)

        else:
            cv2.circle(img, center, radius, fruit["color"], -1)

    rainbow_index += 1
    draw_splashes(img)

    if show_explosion and now - explosion_timer < 0.6:
        overlay = img.copy()
        cv2.rectangle(overlay, (0, 0), (width, height), (0, 0, 255), -1)
        cv2.addWeighted(overlay, 0.4, img, 0.6, 0, img)
        cv2.putText(img, "BOOM!", (width // 3, height // 2), cv2.FONT_HERSHEY_DUPLEX, 3, (255, 255, 255), 6)

    if len(slash_trail) >= 2:
        cv2.polylines(img, [np.array(slash_trail)], False, slash_color, slash_thickness)

    cv2.putText(img, f"FPS: {int(1 / (time.time() - previous_time + 0.0001))}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    previous_time = time.time()
    draw_text(img, f"Score: {Score}", (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 3)
    draw_text(img, f"Lives: {Lives}", (450, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)
    draw_text(img, f"Combo x{combo_multiplier:.1f}", (200, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 215, 0), 2)

    special_y = 150
    if frenzy_mode:
        draw_text(img, "FRENZY!", (200, special_y), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 100, 100), 3)
        special_y += 40
    if freeze_mode:
        draw_text(img, "FREEZE!", (200, special_y), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 223, 50), 3)
        special_y += 40
    if any(f["type"] == "rainbow" for f in Fruits):
        draw_text(img, "RAINBOW!", (200, special_y), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 3)
        special_y += 40
    if any(f["type"] == "golden" for f in Fruits):
        draw_text(img, "GOLDEN!", (200, special_y), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (180, 255, 255), 3)

    if Lives <= 0:
        draw_text(img, "GAME OVER", (width // 4, height // 2), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 4)

    cv2.imshow("Fruit Ninja Deluxe", img)
    key = cv2.waitKey(5) & 0xFF

    if key == ord('q'):
        break
    elif key == ord('r') and Lives <= 0:
        # Restart game state
        Score = 0
        Lives = 3
        Fruits.clear()
        Combos.clear()
        slash_trail.clear()
        splash_effects.clear()
        frenzy_mode = False
        freeze_mode = False
        combo_multiplier = 1.0
        show_explosion = False
        next_spawn_time = time.time()
        rainbow_index = 0


cap.release()
cv2.destroyAllWindows()
