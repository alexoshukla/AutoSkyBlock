import minescript
import time
import threading
from minescript import EventQueue, EventType
from farms import garden

# =============== CONFIGS ==================== #
stop_event      = threading.Event()
world_connected = threading.Event()
world_changed   = threading.Event()
macro_running   = False
world_name      = "?"

def log(msg):
    minescript.echo(f"[{time.strftime('%H:%M:%S')}] {msg}")

def main():
    global world_name, macro_running

    with EventQueue() as eq:
        eq.register_key_listener()
        eq.register_world_listener()

        log("Script loaded. Press = to start, - to stop")

        while True:
            event = eq.get()

            if event.type == EventType.KEY and event.action == 1:
                if event.key == 61:                    # =
                    if not macro_running:
                        macro_running = True
                        stop_event.clear()
                        threading.Thread(
                            target=garden.micro, 
                            args=(stop_event, world_connected, world_changed, log),
                            daemon=True
                        ).start()
                        
                        log("Started")
                    else:
                        log("Already running, ignoring")
                elif event.key == 45:                  # -
                    if macro_running:
                        stop_event.set()
                        log("Stop requested...")
                    else:
                        log("Not running")

            elif event.type == EventType.WORLD:
                if event.connected:
                    try:
                        world_name = minescript.world_info().name
                    except Exception:
                        world_name = "?"
                    world_connected.set()
                    log(f"Connected: {world_name}")
                else:
                    world_connected.clear()
                    world_changed.set()
                    log("Disconnected")

if __name__ == "__main__":
    main()