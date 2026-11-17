import minescript
import time
import threading

# =============== CONFIGS ==================== #
movingforward  = 1.94
movingtime     = 25
loopnumber     = 19
safezonemove   = 0.3

LOBBY_WAIT     = 2
SKYBLOCK_WAIT  = 3
GARDEN_WAIT    = 3
WORLD_TIMEOUT  = 20
WARP_TIMEOUT   = 5
ATTACK_REASSERT_INTERVAL = 0.1 # این رو تعریف کردم چون توی کدت بود ولی مقدار نداشت

# ============================================================
# HELPER FUNCTIONS
# ============================================================

def sleepmine(seconds, stop_event):
    end = time.time() + seconds
    while time.time() < end and not stop_event.is_set():
        time.sleep(0.05)

def hold_attack(duration, stop_event):
    end = time.time() + duration
    while time.time() < end and not stop_event.is_set():
        minescript.player_press_attack(True)
        time.sleep(ATTACK_REASSERT_INTERVAL)

def stop_movement():
    for key in (
        "key.forward", "key.back", "key.left", "key.right",
        "key.jump", "key.sneak", "key.attack", "key.use",
    ):
        try:
            minescript.press_key_bind(key, False)
        except Exception:
            pass

# ============================================================
# WORLD / TRAVEL
# ============================================================

def _scoreboard_contains_garden():
    try:
        sb = minescript.get_scoreboard()
        if sb is None:
            return False
        parts = []
        for value in (getattr(sb, "objective_name", None), getattr(sb, "display_name", None)):
            if value:
                parts.append(str(value))
        entries = getattr(sb, "entries", None)
        if entries:
            for entry in entries:
                for value in (getattr(entry, "name", None), getattr(entry, "display_name", None)):
                    if value:
                        parts.append(str(value))
        return "garden" in " ".join(parts).lower()
    except Exception:
        return False

def goto(cmd, wait_after, label, stop_event, world_changed, world_connected, log_func):
    log_func(f"-> {label}")
    world_changed.clear()
    world_connected.clear()
    minescript.execute(cmd)
    disconnected = world_changed.wait(5.0)
    if disconnected:
        if not world_connected.wait(WORLD_TIMEOUT):
            log_func(f"timeout: never reconnected after {label}")
            return False
        log_func(f"World transition completed: {label}")
    else:
        log_func(f"No world transition for {label}")
    sleepmine(wait_after, stop_event)
    return not stop_event.is_set()

def goto_warp_garden(wait_after, label, stop_event, world_changed, world_connected, log_func):
    log_func(f"-> {label}")
    world_changed.clear()
    world_connected.clear()
    minescript.execute("/warp garden")
    disconnected = world_changed.wait(WARP_TIMEOUT)
    if disconnected:
        if not world_connected.wait(WORLD_TIMEOUT):
            log_func("timeout: never reconnected after warp garden")
            return False
        log_func("World changed after /warp garden")
    else:
        log_func("No world change (in-world teleport)")
    sleepmine(wait_after, stop_event)
    
    if _scoreboard_contains_garden():
        log_func("Garden scoreboard detected")
    else:
        log_func("Garden scoreboard not detected; continuing")
    return not stop_event.is_set()

# ============================================================
# FARM MOVEMENT
# ============================================================

def move_side(direction, stop_event):
    if direction == "right":
        press = minescript.player_press_right
    else:
        press = minescript.player_press_left

    press(True)
    hold_attack(safezonemove, stop_event)
    press(False)
    sleepmine(0.1, stop_event)

    minescript.player_press_backward(True)
    hold_attack(0.2, stop_event)
    minescript.player_press_backward(False)
    sleepmine(0.1, stop_event)

    press(True)
    hold_attack(movingtime, stop_event)
    press(False)

def micro(stop_event, world_connected, world_changed, log_func):
    # این تابع حالا همه چیز رو به عنوان ورودی می‌گیره
    log_func("Macro started")

    try:
        while not stop_event.is_set():
            # 1. Travel
            if not goto("/lobby", LOBBY_WAIT, "lobby", stop_event, world_changed, world_connected, log_func):
                break
            if not goto("/skyblock", SKYBLOCK_WAIT, "skyblock", stop_event, world_changed, world_connected, log_func):
                break
            if not goto_warp_garden(GARDEN_WAIT, "garden", stop_event, world_changed, world_connected, log_func):
                break
            if stop_event.is_set():
                break

            # 2. Return to spawn
            log_func("Returning to garden spawn...")
            if not goto_warp_garden(GARDEN_WAIT, "garden (return)", stop_event, world_changed, world_connected, log_func):
                break

            # 3. Prepare
            minescript.press_key_bind("key.hotbar.4", True)
            sleepmine(0.1, stop_event)
            minescript.press_key_bind("key.hotbar.4", False)
            sleepmine(0.1, stop_event)

            minescript.player_press_sneak(True)
            sleepmine(0.3, stop_event)
            minescript.player_press_sneak(False)

            # 4. Farming loop
            for i in range(loopnumber):
                if stop_event.is_set():
                    break

                hold_attack(0.1, stop_event)
                move_side("right" if i % 2 == 0 else "left", stop_event)

                sleepmine(0.1, stop_event)
                minescript.player_press_attack(False)
                sleepmine(0.1, stop_event)

                minescript.player_press_forward(True)
                sleepmine(movingforward, stop_event)
                minescript.player_press_forward(False)

    finally:
        stop_movement()
        log_func("Macro stopped")