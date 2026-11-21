import minescript
import time
import math
import re

# =============== PEST CONFIGS ==================== #
PEST_ENTITY_TYPES = ("silverfish", "bat")
PEST_NAMES = (
    "mosquito", "cricket", "dragonfly", "rat", "beetle",
    "earthworm", "praying mantis", "slug", "locust",
    "mite", "fly", "moth",
)
PEST_PLOTS = [1, 3, 4, 8]
PEST_WARP_WAIT = 3.0
SCAN_Y = 77.0
FORWARD_AFTER_WARP = 1.0
SETTLE_AFTER_POS = 1.0
TAP_TIMES = 8
TAP_INTERVAL = 0.25
ARRIVE_DISTANCE_XZ = 2.0
MAX_FLY_STEPS = 300
JAR_SLOT = "key.hotbar.5"
FARM_SLOT = "key.hotbar.4"

# ============================================================
# TEXT SANITIZATION
# ============================================================
def strip_all_special(text):
    if text is None:
        return ""
    text = re.sub(r"Â§.", "", text)
    text = re.sub(r"§.", "", text)
    text = re.sub(r"[^\x20-\x7E]", "", text)
    return text

# ============================================================
# KEY HELPERS (Required for fly)
# ============================================================
def key_down(key):
    try: minescript.press_key_bind(key, True)
    except Exception: pass

def key_up(key):
    try: minescript.press_key_bind(key, False)
    except Exception: pass

def stop_movement():
    for key in ("key.forward", "key.back", "key.left", "key.right", "key.jump", "key.sneak", "key.attack", "key.use"):
        try: minescript.press_key_bind(key, False)
        except Exception: pass

def key_press(key, duration=0.05):
    try:
        minescript.press_key_bind(key, True)
        time.sleep(duration)
        minescript.press_key_bind(key, False)
    except Exception: pass

def select_slot(key):
    try:
        minescript.press_key_bind(key, True)
        time.sleep(0.05)
        minescript.press_key_bind(key, False)
        time.sleep(0.15)
    except Exception: pass

# ============================================================
# SCOREBOARD / PEST INFO
# ============================================================
def get_pest_info():
    sb = minescript.get_scoreboard()
    if sb is None:
        return {"total": None, "current_plot": None, "current_pests": None}
    result = {"total": None, "current_plot": None, "current_pests": None}
    for entry in (getattr(sb, "entries", None) or []):
        text = getattr(entry, "display_name", None) or getattr(entry, "name", None)
        if not text:
            continue
        clean = strip_all_special(text).strip()
        lower = clean.lower()
        if "garden" in lower:
            m = re.search(r"x\s*(\d+)", clean, re.IGNORECASE)
            if m: result["total"] = int(m.group(1))
            continue
        if "plot" in lower:
            m = re.search(r"plot\s*-?\s*(\d+).*?x\s*(\d+)", clean, re.IGNORECASE)
            if m:
                result["current_plot"] = int(m.group(1))
                result["current_pests"] = int(m.group(2))
    return result

# ============================================================
# PEST DETECTION
# ============================================================
def player_position():
    try:
        p = minescript.player_position()
        return (p[0], p[1], p[2])
    except Exception:
        return None

def is_pest(entity):
    etype = (entity.type or "").lower()
    if any(t in etype for t in PEST_ENTITY_TYPES):
        return True
    if "armor_stand" in etype:
        raw_name = entity.name or ""
        clean_name = strip_all_special(raw_name).lower()
        for pest_name in PEST_NAMES:
            if re.search(r"\b" + re.escape(pest_name) + r"\b", clean_name):
                return True
    return False

def find_nearest_pest():
    me = player_position()
    if me is None: return None
    best, best_dist = None, float("inf")
    for entity in minescript.entities(sort="nearest"):
        if "player" in entity.type: continue
        if not is_pest(entity): continue
        pos = getattr(entity, "position", None)
        if pos is None: continue
        d = math.sqrt((me[0]-pos[0])**2 + (me[1]-pos[1])**2 + (me[2]-pos[2])**2)
        if d < best_dist:
            best_dist = d
            best = (entity, (pos[0], pos[1], pos[2]), d)
    return best

# ============================================================
# FLY & POSITIONING
# ============================================================
def is_flying():
    me1 = player_position()
    if me1 is None: return None
    minescript.press_key_bind("key.jump", True)
    time.sleep(0.3)
    minescript.press_key_bind("key.jump", False)
    time.sleep(0.2)
    me2 = player_position()
    if me2 is None: return None
    return (me2[1] - me1[1]) > 1.0

def activate_fly():
    try:
        minescript.press_key_bind("key.jump", True); time.sleep(0.05)
        minescript.press_key_bind("key.jump", False); time.sleep(0.2)
        minescript.press_key_bind("key.jump", True); time.sleep(0.05)
        minescript.press_key_bind("key.jump", False); time.sleep(1.0)
    except Exception: pass

def activate_fly_if_needed():
    flying = is_flying()
    if flying is True: return
    activate_fly()

def position_for_scanning():
    activate_fly_if_needed()
    me = player_position()
    if me is None: return False
    key_down("key.jump")
    key_down("key.forward")
    safety = 0
    while safety < 100:
        if stop_event.is_set(): break
        me = player_position()
        if me is None: break
        if me[1] >= SCAN_Y - 0.5: break
        time.sleep(0.1)
        safety += 1
    time.sleep(FORWARD_AFTER_WARP)
    key_up("key.jump")
    key_up("key.forward")
    stop_movement()
    time.sleep(SETTLE_AFTER_POS)
    return True

def fly_to_pest(target_pos, max_steps=MAX_FLY_STEPS, arrive_dist=ARRIVE_DISTANCE_XZ):
    step = 0
    while step < max_steps:
        if stop_event.is_set(): break
        me = player_position()
        if me is None: break
        dx = target_pos[0] - me[0]
        dz = target_pos[2] - me[2]
        d_xz = math.sqrt(dx*dx + dz*dz)
        if d_xz <= arrive_dist: break
        try: minescript.player_look_at(target_pos[0], me[1], target_pos[2])
        except Exception: pass
        dy = SCAN_Y - me[1]
        if dy > 1.0:
            key_down("key.jump"); key_up("key.sneak")
        elif dy < -1.0:
            key_up("key.jump"); key_down("key.sneak")
        else:
            key_up("key.jump"); key_up("key.sneak")
        key_down("key.forward")
        time.sleep(0.1)
        step += 1
    stop_movement()

def tap_use(times=TAP_TIMES, interval=TAP_INTERVAL):
    for _ in range(times):
        key_press("key.use", 0.05)
        time.sleep(interval)

# ============================================================
# KILL PESTS
# ============================================================
def kill_pests_in_current_plot(max_kills=10, stop_event=None):
    kills = 0
    while kills < max_kills:
        if stop_event and stop_event.is_set(): break
        target = find_nearest_pest()
        if target is None:
            break
        entity, pos, dist = target
        fly_to_pest(pos)
        select_slot(JAR_SLOT)
        try: minescript.player_look_at(pos[0], pos[1], pos[2])
        except Exception: pass
        time.sleep(0.2)
        tap_use(times=TAP_TIMES, interval=TAP_INTERVAL)
        kills += 1
        time.sleep(0.5)
    select_slot(FARM_SLOT)
    return kills

def run_pest_killer(stop_event, log_func):
    info = get_pest_info()
    total = info.get("total")
    log_func(f"Pest check: total pests = {total}")

    if not total:
        log_func("No pests to kill.")
        return

    for plot_num in PEST_PLOTS:
        if stop_event.is_set(): break
        info = get_pest_info()
        if not info.get("total"):
            log_func("All pests cleared.")
            break

        log_func(f"--- Pest plot {plot_num} ---")
        minescript.execute(f"/plottp {plot_num}")
        time.sleep(PEST_WARP_WAIT)
        position_for_scanning()

        info = get_pest_info()
        if info.get("current_plot") != plot_num:
            continue
        if not info.get("current_pests"):
            continue

        kills = kill_pests_in_current_plot(stop_event=stop_event)
        log_func(f"  killed {kills} pests")