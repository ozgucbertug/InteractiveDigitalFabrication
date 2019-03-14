from pynput.keyboard import Key, Listener

def on_press(key):
    if key == Key.esc:
        # Stop listener
        return False

# Collect events until released
with Listener(on_press=on_press) as listener:
    listener.join()