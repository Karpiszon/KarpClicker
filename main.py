from pynput.mouse import Button, Controller, Listener as MouseListener
from pynput.keyboard import Key, Listener as KeyListener
from threading import Thread
import random
import time

mouse = Controller()

# ustawienia
TOGGLE_KEY_LEFT = Key.f6
TOGGLE_KEY_RIGHT = Key.f7
EXIT_KEY = Key.f9
CPS_MIN = 12
CPS_MAX = 18
JITTER_MOVE = 1        # losowy ruch przed kliknięciem
IGNORE_WINDOW = 0.03    

autoclicker_left_enabled = False
autoclicker_right_enabled = False
holding_left = False
holding_right = False
active = True
last_self_click_left = 0.0
last_self_click_right = 0.0


def rand_delay():
    cps = random.uniform(CPS_MIN, CPS_MAX)
    base = 1 / cps
    return base + random.uniform(-0.004, 0.004)


def maybe_jitter():
    if JITTER_MOVE:
        dx = random.randint(-JITTER_MOVE, JITTER_MOVE)
        dy = random.randint(-JITTER_MOVE, JITTER_MOVE)
        if dx or dy:
            x, y = mouse.position
            mouse.position = (x + dx, y + dy)


def clicker_loop(button, is_enabled_fn, is_holding_fn, set_last_click_fn):
    while active:
        if is_enabled_fn() and is_holding_fn():
            maybe_jitter()
            mouse.click(button)
            set_last_click_fn(time.time())
            time.sleep(max(rand_delay(), 0.01))
        else:
            time.sleep(0.02)


def set_last_left(t):
    global last_self_click_left
    last_self_click_left = t


def set_last_right(t):
    global last_self_click_right
    last_self_click_right = t


def on_click(x, y, button, pressed):
    global holding_left, holding_right

    if button == Button.left:
        if time.time() - last_self_click_left < IGNORE_WINDOW:
            return
        holding_left = pressed

    elif button == Button.right:
        if time.time() - last_self_click_right < IGNORE_WINDOW:
            return
        holding_right = pressed


def on_press(key):
    global autoclicker_left_enabled, autoclicker_right_enabled, active
    if key == TOGGLE_KEY_LEFT:
        autoclicker_left_enabled = not autoclicker_left_enabled
        print("Lewy clicker:", "AKTYWNY (trzymaj LPM)" if autoclicker_left_enabled else "wyłączony")
    elif key == TOGGLE_KEY_RIGHT:
        autoclicker_right_enabled = not autoclicker_right_enabled
        print("Prawy clicker:", "AKTYWNY (trzymaj PPM)" if autoclicker_right_enabled else "wyłączony")
    elif key == EXIT_KEY:
        active = False
        print("Kończę działanie.")
        return False


Thread(target=clicker_loop, args=(Button.left, lambda: autoclicker_left_enabled, lambda: holding_left, set_last_left), daemon=True).start()
Thread(target=clicker_loop, args=(Button.right, lambda: autoclicker_right_enabled, lambda: holding_right, set_last_right), daemon=True).start()

mouse_listener = MouseListener(on_click=on_click)
mouse_listener.start()

with KeyListener(on_press=on_press) as kl:
    kl.join()

mouse_listener.stop()
