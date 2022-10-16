from pynput import keyboard
import subprocess

from keymappings.converters import convert_to_readable_key

pressed = []

class Keymapping:
    def __init__(self) -> None:
        self.KEYMAPPINGS = []


    def add_keymappings(self, keymapping):
        self.KEYMAPPINGS.append(keymapping)

        return self

km = Keymapping()

km.add_keymappings({
    "key_sequences": [
        [{keyboard.Key.ctrl_l, keyboard.Key.alt_l, keyboard.Key.f4}],
    ],
    "command": "TERMINATE",
})
km.add_keymappings({
    "key_sequences": [
        [{keyboard.Key.ctrl_l, keyboard.KeyCode(char="w")}],
        [{keyboard.Key.ctrl_l, keyboard.KeyCode(char="W")}],
    ],
    "command": "TEST",
})
km.add_keymappings({
    "key_sequences": [
        [{keyboard.Key.ctrl_l, keyboard.KeyCode(char="w")},
         {keyboard.Key.ctrl_l, keyboard.KeyCode(char="a")}],
    ],
    "command": "KEK",
})
km.add_keymappings({
    "key_sequences": [
        [{keyboard.Key.cmd, keyboard.KeyCode(char="c")}],
        [{keyboard.Key.cmd, keyboard.KeyCode(char="C")}],
    ],
    "command": "Chrome",
})
km.add_keymappings({
    "key_sequences": [
        [{keyboard.Key.cmd, keyboard.KeyCode(char="o")}],
        [{keyboard.Key.cmd, keyboard.KeyCode(char="O")}],
    ],
    "command": "Opera",
})

def debug_arguments(func):
    def wrapper(*args, **kwargs):
        print(*args, **kwargs)
        func(*args, **kwargs)

    return wrapper


def with_decoration(func):
    def wrapper(*args, **kwargs):
        print('-----------')
        func(*args, **kwargs)
        print('-----------')

    return wrapper


@with_decoration
@debug_arguments
def run(s):
    # subprocess.Popen(s)
    subprocess.call(s, shell=True)


def match_keymappings(key, keymappings, matched_sequences):
    matched_keymappings = []

    print('key', key)
    try:
        print('key_vk', key.vk)
    except:
        pass

    if (not convert_to_readable_key(key) in pressed):
        pressed.append(convert_to_readable_key(key))

    print(pressed)

    for keymappings_index, keymapping in enumerate(keymappings):
        for key_sequences in keymapping["key_sequences"]:
            chord = key_sequences[matched_sequences[keymappings_index]]

            # if chord.issubset(pressed):
            if all(key in pressed for key in chord):
                matched_sequences[keymappings_index] += 1

                # Sequences has ended.
                if matched_sequences[keymappings_index] == len(key_sequences):
                    matched_sequences[keymappings_index] = 0
                    matched_keymappings.append(keymapping)
                    matched_sequences[keymappings_index] = 0

            # Sequence was interrupted.
            else:
                matched_sequences[keymappings_index] = 0

    print("Result", matched_keymappings)
    return matched_keymappings

def main():
    # [index: chord_index]
    # Example:
    #   [
    #       0: 1, # On first keymapping (e.g., [Ctrl+Alt+A, Ctrl-B]) first chord (Ctrl+Alt+A) was matched.
    #       1: 0, # Second keymapping wasn't matched yet.
    #   ]
    matched_sequences = [0 for _ in km.KEYMAPPINGS]

    def on_press(key):
        for c in match_keymappings(key, km.KEYMAPPINGS, matched_sequences):
            command = c["command"]

            if command == 'TERMINATE':
                return False

            if command == 'KEK':
                print('KEK')
                return

            if command == 'TEST':
                print('TEST')
                return

            run(command)


    def on_release(key):
        my_key = convert_to_readable_key(key) 

        if my_key in pressed:
            pressed.remove(my_key)

    # Collect events until released.
    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()


if __name__ == '__main__':
    main()