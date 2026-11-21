import minescript
import time
import math
import json
import os

# =============== CONFIGS ==================== #
CONFIG_FILE = os.path.join(os.path.dirname(__file__), "garden_config.json")

LOBBY_WAIT     = 2
SKYBLOCK_WAIT  = 3
GARDEN_WAIT    = 3
WORLD_TIMEOUT  = 20
WARP_TIMEOUT   = 5
ATTACK_REASSERT_INTERVAL = 0.025

# ============================================================
# JSON CONFIG HANDLER & DATA MANAGEMENT
# ============================================================
def get_raw_config():
    """Reads and returns the entire JSON config file."""
    if not os.path.exists(CONFIG_FILE):
        return None
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return None

def save_config_pretty(data):
    """Saves JSON config with coordinates on single lines for readability."""
    def format_json(obj, indent_level=0):
        indent = "    " * indent_level
        if isinstance(obj, dict):
            if not obj: return "{}"
            items = []
            for key, value in obj.items():
                items.append(f'{indent}    "{key}": {format_json(value, indent_level + 1)}')
            return "{\n" + ",\n".join(items) + f"\n{indent}}}"
        elif isinstance(obj, list):
            if len(obj) == 3 and all(isinstance(x, (int, float)) for x in obj):
                return f"[{', '.join(str(x) for x in obj)}]"
            elif len(obj) == 2 and all(isinstance(x, list) and len(x) == 3 for x in obj):
                return f"[{format_json(obj[0])}, {format_json(obj[1])}]"
            else:
                if not obj: return "[]"
                items = [format_json(item, indent_level + 1) for item in obj]
                return "[\n" + ",\n".join(f"{indent}    {item}" for item in items) + f"\n{indent}]"
        else:
            return json.dumps(obj)

    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        f.write(format_json(data))

def get_active_profile():
    """Returns the active profile's settings from the JSON."""
    data = get_raw_config()
    if not data: return None
    profiles = data.get("profiles", {})
    active_name = data.get("active_profile")
    if isinstance(profiles, dict) and active_name in profiles:
        return profiles[active_name]
    return None

def get_profile_names():
    """Returns a list of all profile names."""
    data = get_raw_config()
    if not data: return []
    profiles = data.get("profiles", {})
    return list(profiles.keys()) if isinstance(profiles, dict) else []

def add_profile(name, hotbar_slot, rows):
    """Adds a new profile and saves it."""
    data = get_raw_config() or {"active_profile": "", "profiles": {}}
    if "profiles" not in data: data["profiles"] = {}
    
    data["profiles"][name] = {
        "hotbar_slot": hotbar_slot,
        "waits": {"lobby": 2, "skyblock": 3, "garden": 3},
        "farming_rows": rows
    }
    if not data.get("active_profile"):
        data["active_profile"] = name
    save_config_pretty(data)

def remove_profile(name):
    """Removes a profile and saves the config."""
    data = get_raw_config()
    if not data: return
    if "profiles" in data and name in data["profiles"]:
        del data["profiles"][name]
        if data.get("active_profile") == name:
            remaining = list(data["profiles"].keys())
            data["active_profile"] = remaining[0] if remaining else ""
        save_config_pretty(data)

def set_active_profile(name):
    """Updates the active profile in the config."""
    data = get_raw_config()
    if data:
        data["active_profile"] = name
        save_config_pretty(data)

# ============================================================
# HELPER FUNCTIONS
# ============================================================
def sleepmine(seconds, stop_event):
    end = time.time() + seconds
    while time.time() < end and not stop_event.is_set():
        time.sleep(0.05)

def stop_movement():
    for key in ("key.forward", "key.back", "key.left", "key.right", "key.jump", "key.sneak", "key.attack", "key.use"):
        try: minescript.press_key_bind(key, False)
        except Exception: pass

# ============================================================
# COORDINATE MOVEMENT
# ============================================================
def move_to_coords(target_x, target_y, target_z, threshold, stop_event, log_func, keep_attacking=False):
    log_func(f"Moving to ({target_x:.1f}, {target_y:.1f}, {target_z:.1f})...")
    current_key = None

    while not stop_event.is_set():
        try:
            px, py, pz = minescript.player_position()
            yaw = minescript.player().yaw
        except Exception as e:
            log_func(f"Error getting position: {e}")
            break

        dist = math.sqrt((px - target_x)**2 + (py - target_y)**2 + (pz - target_z)**2)
        if dist <= threshold: break

        fwd_x = -math.sin(math.radians(yaw))
        fwd_z = math.cos(math.radians(yaw))
        right_x = -fwd_z
        right_z = fwd_x

        dir_x = target_x - px
        dir_z = target_z - pz

        dot = dir_x * fwd_x + dir_z * fwd_z
        cross = dir_x * right_x + dir_z * right_z

        if abs(dot) > abs(cross):
            new_key = "key.forward" if dot > 0 else "key.back"
        else:
            new_key = "key.right" if cross > 0 else "key.left"

        if new_key != current_key:
            if current_key is not None:
                minescript.press_key_bind(current_key, False)
            minescript.press_key_bind(new_key, True)
            current_key = new_key

        if keep_attacking:
            minescript.player_press_attack(True)

        time.sleep(0.05)

    if current_key is not None:
        minescript.press_key_bind(current_key, False)

    stop_movement()
    sleepmine(0.1, stop_event)

# ============================================================
# TRAVEL LOGIC
# ============================================================
def goto(cmd, wait_after, label, stop_event, world_changed, world_connected, log_func):
    log_func(f"-> {label}")
    world_changed.clear()
    world_connected.clear()
    minescript.execute(cmd)
    if world_changed.wait(5.0):
        if not world_connected.wait(WORLD_TIMEOUT):
            log_func(f"timeout: never reconnected after {label}")
            return False
    else:
        log_func(f"No world transition for {label}")
    sleepmine(wait_after, stop_event)
    return not stop_event.is_set()

def goto_warp_garden(wait_after, label, stop_event, world_changed, world_connected, log_func):
    log_func(f"-> {label}")
    world_changed.clear()
    world_connected.clear()
    minescript.execute("/warp garden")
    if world_changed.wait(WARP_TIMEOUT):
        if not world_connected.wait(WORLD_TIMEOUT):
            log_func("timeout: never reconnected after warp garden")
            return False
    else:
        log_func("No world change (in-world teleport)")
    sleepmine(wait_after, stop_event)
    return not stop_event.is_set()

# ============================================================
# FARMING LOGIC
# ============================================================
def micro(stop_event, world_connected, world_changed, log_func):
    log_func("Garden Macro started")
    profile = get_active_profile()
    
    if not profile:
        log_func("Error: No active profile found!")
        return

    hotbar_slot = profile.get("hotbar_slot", 4)
    rows = profile.get("farming_rows", [])
    waits = profile.get("waits", {})
    threshold = profile.get("reached_threshold", 1.5)

    if not rows:
        log_func("No farming rows defined! Stopping.")
        return

    try:
        while not stop_event.is_set():
            if not goto("/lobby", waits.get("lobby", 2), "lobby", stop_event, world_changed, world_connected, log_func): break
            if not goto("/skyblock", waits.get("skyblock", 3), "skyblock", stop_event, world_changed, world_connected, log_func): break
            if not goto_warp_garden(waits.get("garden", 3), "garden", stop_event, world_changed, world_connected, log_func): break
            
            if stop_event.is_set(): break

            log_func("Toggling sneak to disable fly...")
            minescript.player_press_sneak(True)
            sleepmine(0.2, stop_event)
            minescript.player_press_sneak(False)
            sleepmine(0.2, stop_event)

            keybind = f"key.hotbar.{hotbar_slot}"
            minescript.press_key_bind(keybind, True)
            sleepmine(0.1, stop_event)
            minescript.press_key_bind(keybind, False)
            sleepmine(0.1, stop_event)

            for i, row in enumerate(rows):
                if stop_event.is_set(): break
                start_x, start_y, start_z = row[0]
                end_x, end_y, end_z = row[1]
                
                log_func(f"Farming row {i+1}/{len(rows)}...")
                move_to_coords(start_x, start_y, start_z, threshold, stop_event, log_func, keep_attacking=False)
                
                minescript.player_press_attack(True)
                move_to_coords(end_x, end_y, end_z, threshold, stop_event, log_func, keep_attacking=True)
                minescript.player_press_attack(False)
                
                minescript.player_press_backward(True)
                sleepmine(1.0, stop_event)
                minescript.player_press_backward(False)
    finally:
        stop_movement()
        log_func("Garden Macro stopped")