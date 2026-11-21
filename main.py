import minescript
import time
import threading
from minescript import EventQueue, EventType
from farms import garden
from farms import mining

# =============== CONFIGS ==================== #
stop_event      = threading.Event()
world_connected = threading.Event()
world_changed   = threading.Event()
macro_running   = False
is_running      = True

MENU_MAIN           = "main"
MENU_GARDEN         = "garden_profiles"
MENU_SETUP_SLOT     = "setup_slot"
MENU_SETUP_COORD    = "setup_coord"
MENU_DELETE_CONFIRM = "delete_confirm"

current_menu_state = MENU_MAIN
current_mode = None
selected_main_index = 0   
selected_profile_index = 0

MAIN_OPTIONS = ["Garden Farm", "Mining"]

temp_profile_name = ""
temp_hotbar_slot = 4
temp_rows = []
temp_waiting_for_end = False
profile_to_delete = ""

def log(msg):
    minescript.echo(f"[{time.strftime('%H:%M:%S')}] {msg}")

def show_main_menu():
    global current_menu_state
    current_menu_state = MENU_MAIN
    minescript.echo("====================================")
    minescript.echo("        AutoSkyBlock Menu           ")
    minescript.echo("====================================")
    for idx, option in enumerate(MAIN_OPTIONS):
        prefix = ">>" if idx == selected_main_index else "  "
        minescript.echo(f"{prefix} [{idx+1}] {option}")
    minescript.echo("====================================")
    minescript.echo("Press [Up/Down] to navigate")
    minescript.echo("Press [=] to select")
    minescript.echo("Press [-] to exit script")
    minescript.echo("====================================")

def show_garden_menu():
    global current_menu_state, selected_profile_index
    current_menu_state = MENU_GARDEN
    
    profile_names = garden.get_profile_names()
    
    minescript.echo("====================================")
    minescript.echo("        Garden Profiles             ")
    minescript.echo("====================================")
    
    if not profile_names:
        minescript.echo("No profiles found in config!")

    total_options = len(profile_names) + 1
    if selected_profile_index >= total_options:
        selected_profile_index = 0

    for idx, name in enumerate(profile_names):
        prefix = ">>" if idx == selected_profile_index else "  "
        minescript.echo(f"{prefix} [{idx+1}] {name}")
        
    add_idx = len(profile_names)
    prefix_add = ">>" if selected_profile_index == add_idx else "  "
    minescript.echo(f"{prefix_add} [+] Add New Profile")
        
    minescript.echo("====================================")
    minescript.echo("Press [Up/Down] to navigate")
    minescript.echo("Press [=] to select/start")
    minescript.echo("Press [-] to delete / go back")
    minescript.echo("====================================")

def show_coord_menu():
    global current_menu_state
    current_menu_state = MENU_SETUP_COORD
    
    minescript.echo("====================================")
    minescript.echo(f"Setting up: {temp_profile_name} (Slot: {temp_hotbar_slot})")
    minescript.echo("====================================")
    
    if not temp_rows:
        minescript.echo("No rows added yet.")
    else:
        for idx, row in enumerate(temp_rows):
            start_str = f"{row[0]}" if row[0] else "Not set"
            end_str = f"{row[1]}" if row[1] else "Not set"
            minescript.echo(f"Row {idx+1}: {start_str} -> {end_str}")
            
    if temp_waiting_for_end:
        minescript.echo(">> Waiting for END point...")
    elif temp_rows and not temp_waiting_for_end:
        minescript.echo(">> Last row complete. Move to next start point.")

    minescript.echo("------------------------------------")
    minescript.echo("Press [/] to set current coords.")
    minescript.echo("Press [=] to save all rows.")
    minescript.echo("Press [-] to cancel.")
    minescript.echo("====================================")

def main():
    global current_menu_state, selected_main_index, selected_profile_index
    global macro_running, current_mode, is_running
    global temp_profile_name, temp_hotbar_slot, temp_rows, temp_waiting_for_end, profile_to_delete

    with EventQueue() as eq:
        eq.register_key_listener()
        eq.register_world_listener()

        log("Script loaded.")
        show_main_menu()

        while is_running:
            event = eq.get()

            if event.type == EventType.KEY and event.action == 1:
                if macro_running:
                    if event.key == ord("-"):
                        stop_event.set()
                        macro_running = False
                        current_mode = None
                        log("Stop requested...")
                        time.sleep(0.5)
                        show_main_menu()
                    continue

                if current_menu_state == MENU_MAIN:
                    if event.key == 265:
                        selected_main_index = (selected_main_index - 1) % len(MAIN_OPTIONS)
                        show_main_menu()
                    elif event.key == 264:
                        selected_main_index = (selected_main_index + 1) % len(MAIN_OPTIONS)
                        show_main_menu()
                    elif event.key == ord("="): 
                        if selected_main_index == 0:
                            selected_profile_index = 0
                            show_garden_menu()
                        elif selected_main_index == 1:
                            log("Mining is not implemented yet.")
                    elif event.key == ord("-"):
                        log("Exiting script...")
                        is_running = False
                        break

                elif current_menu_state == MENU_GARDEN:
                    profile_names = garden.get_profile_names()
                    num_profiles = len(profile_names)
                    total_options = num_profiles + 1

                    if event.key == 265:
                        selected_profile_index = (selected_profile_index - 1) % total_options
                        show_garden_menu()
                    elif event.key == 264:
                        selected_profile_index = (selected_profile_index + 1) % total_options
                        show_garden_menu()
                    elif event.key == ord("="):
                        if selected_profile_index == num_profiles:
                            # Start new profile setup
                            temp_profile_name = f"profile_{num_profiles + 1}"
                            temp_rows = []
                            temp_waiting_for_end = False
                            current_menu_state = MENU_SETUP_SLOT
                            minescript.echo("Step 1: Press a hotbar key [1-9] for farm item.")
                        else:
                            active_name = profile_names[selected_profile_index]
                            garden.set_active_profile(active_name)
                            log(f"Set active profile to: {active_name}")
                            current_mode = "garden"
                            macro_running = True
                            stop_event.clear()
                            log("Starting Garden Farm...")
                            threading.Thread(target=garden.micro, args=(stop_event, world_connected, world_changed, log), daemon=True).start()
                    elif event.key == ord("-"):
                        if selected_profile_index < num_profiles:
                            profile_to_delete = profile_names[selected_profile_index]
                            current_menu_state = MENU_DELETE_CONFIRM
                            minescript.echo(f"Delete {profile_to_delete}? Press [=] to confirm, [-] to cancel.")
                        else:
                            show_main_menu()

                elif current_menu_state == MENU_SETUP_SLOT:
                    if ord("1") <= event.key <= ord("9"):
                        temp_hotbar_slot = event.key - ord("0")
                        show_coord_menu()
                    elif event.key == ord("-"):
                        log("Setup cancelled.")
                        show_garden_menu()

                elif current_menu_state == MENU_SETUP_COORD:
                    if event.key == ord("/"): 
                        try:
                            x, y, z = minescript.player_position()
                            coords = [float(f"{x:.1f}"), float(f"{y:.1f}"), float(f"{z:.1f}")]
                            if not temp_waiting_for_end:
                                temp_rows.append([coords, None])
                                temp_waiting_for_end = True
                                log(f"Row {len(temp_rows)} Start set: {coords}")
                            else:
                                temp_rows[-1][1] = coords
                                temp_waiting_for_end = False
                                log(f"Row {len(temp_rows)} End set: {coords}")
                            show_coord_menu()
                        except Exception as e:
                            log(f"Error reading coords: {e}")
                    
                    elif event.key == ord("="):
                        valid_rows = [r for r in temp_rows if r[0] is not None and r[1] is not None]
                        if valid_rows:
                            garden.add_profile(temp_profile_name, temp_hotbar_slot, valid_rows)
                            log(f"Profile '{temp_profile_name}' saved with {len(valid_rows)} rows!")
                            show_garden_menu()
                        else:
                            log("No complete rows to save!")
                    
                    elif event.key == ord("-"):
                        log("Setup cancelled.")
                        show_garden_menu()

                elif current_menu_state == MENU_DELETE_CONFIRM:
                    if event.key == ord("="):
                        garden.remove_profile(profile_to_delete)
                        log(f"Deleted profile: {profile_to_delete}")
                        show_garden_menu()
                    elif event.key == ord("-"):
                        show_garden_menu()

            elif event.type == EventType.WORLD:
                if event.connected:
                    world_connected.set()
                else:
                    world_connected.clear()
                    world_changed.set()

    log("Script terminated. Goodbye!")

if __name__ == "__main__":
    main()