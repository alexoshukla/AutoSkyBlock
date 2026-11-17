import minescript
import random
import time
import threading
from minescript import EventQueue, EventType
#===============CONFIGS=====================#
run = False
still_in_garden=False      #this feature will be added
movingkeys="LA"
#this times is for ranchers boot with speed of 220
movingforvard=1.94
movingtime=23
startmove=0.5
loopnumber=19
safezonemove=0.3
#===============starting====================#
minescript.echo("running script...")

def sleepmine(seconds):
    end = time.time() + seconds
    while time.time() < end and run:
        time.sleep(0.005)

def micro():
    while run:
        if still_in_garden:
            minescript.echo("good")
        else:
            minescript.execute("/lobby")
            sleepmine(25)
            minescript.execute("/skyblock")
            sleepmine(25)
            minescript.execute("/warp garden")
            sleepmine(3)
            minescript.press_key_bind("key.hotbar.4", True)
            sleepmine(0.1)
            minescript.press_key_bind("key.hotbar.4", False)
        for i in range(loopnumber):
            if not run:
                return
            minescript.player_press_attack(True)
            sleepmine(0.1)
            if i%2==0: 
                minescript.player_press_right(True)
                sleepmine(safezonemove)
                minescript.player_press_right(False)
                sleepmine(0.1)
                minescript.player_press_backward(True)
                sleepmine(0.2)
                minescript.player_press_backward(False)
                sleepmine(0.1)
                minescript.player_press_right(True)
                sleepmine(movingtime)
                minescript.player_press_right(False)
            else:
                minescript.player_press_left(True)
                sleepmine(safezonemove)
                minescript.player_press_left(False)
                sleepmine(0.1)
                minescript.player_press_backward(True)
                sleepmine(0.2)
                minescript.player_press_backward(False)
                sleepmine(0.1)
                minescript.player_press_left(True)
                sleepmine(movingtime)
                minescript.player_press_left(False)
            sleepmine(0.1)
            minescript.player_press_attack(False)
            sleepmine(0.1)
            minescript.player_press_forward(True)
            sleepmine(movingforvard)
            minescript.player_press_forward(False)
def key_listener():
    global run
    with EventQueue() as eq:
        eq.register_key_listener()
        while True:
            event = eq.get()
            if event.type == EventType.KEY and event.action == 1:
                if event.key == 61:      # "="
                    if not run:
                        run = True
                        minescript.echo("started")
                        threading.Thread(target=micro, daemon=True).start()
                        sleepmine(0.5)
                elif event.key == 45:    # "-"
                    run = False
                    minescript.echo("stopped")
                    sleepmine(0.5)

t = threading.Thread(target=key_listener)
t.start()
t.join()