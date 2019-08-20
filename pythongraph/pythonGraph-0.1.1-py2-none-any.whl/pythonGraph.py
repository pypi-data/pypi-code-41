import collections
import math
import random

import pygame


# Pygame Window
win = None

# Pygame events
event_list = []

# Pygame Font ('None' will use the system default)
font = None

# Cache (Used to Prevent Loading the Same Media Multiple Times)
images = {}
sounds = {}

# Color Constants
Color = collections.namedtuple('Color',
                               ['BLACK', 'BLUE', 'BROWN', 'CYAN', 'GRAY',
                                'GREEN', 'LIGHT_BLUE', 'LIGHT_CYAN',
                                'LIGHT_GRAY', 'LIGHT_GREEN', 'LIGHT_MAGENTA',
                                'LIGHT_RED', 'MAGENTA', 'RED', 'WHITE',
                                'YELLOW'])
colors = Color(
    BLACK=(0, 0, 0),
    BLUE=(0, 0, 255),
    BROWN=(153, 76, 0),
    CYAN=(0, 255, 255),
    GRAY=(128, 128, 128),
    GREEN=(0, 128, 0),
    LIGHT_BLUE=(51, 153, 255),
    LIGHT_CYAN=(204, 255, 255),
    LIGHT_GRAY=(224, 224, 224),
    LIGHT_GREEN=(153, 255, 51),
    LIGHT_MAGENTA=(255, 153, 204),
    LIGHT_RED=(255, 102, 102),
    MAGENTA=(255, 0, 255),
    RED=(255, 0, 0),
    WHITE=(255, 255, 255),
    YELLOW=(255, 255, 0))

# Mouse Constants
MouseButton = collections.namedtuple('MouseButton',
                                     ['LEFT', 'RIGHT', 'CENTER'])
mouse_buttons = MouseButton(
    LEFT=1,
    CENTER=2,
    RIGHT=3)


# Window Operations
def open_window(width, height):
    global win
    pygame.init()
    pygame.mixer.init()
    win = pygame.display.set_mode((width, height))
    clear_window(colors.WHITE)
    set_window_title('pythonGraph')


def close_window():
    quit()


def clear_window(color):
    win.fill(color)


def get_window_height():
    width, height = pygame.display.get_surface().get_size()
    return height


def get_window_width():
    width, height = pygame.display.get_surface().get_size()
    return width


def set_window_title(title):
    pygame.display.set_caption(title)


def update_window(refresh_rate=33):
    global event_list
    if win is not None:
        pygame.event.pump()
        del event_list[:]
        pygame.display.update()
        delay(refresh_rate)


# Colors Operations
def create_color(red, green, blue):
    return (red, green, blue)


def create_random_color():
    red = random.randint(0, 255)
    green = random.randint(0, 255)
    blue = random.randint(0, 255)
    return (red, green, blue)


# Drawing Operations
def _get_rectangle(x1, y1, x2, y2):
    # Assumes that we were given top left / bottom right coordinates (we verify
    # this later)
    top_left_x = x1
    top_left_y = y1
    bottom_right_x = x2
    bottom_right_y = y2

    # Adjusts the coordinates provided so that we know the top left and bottom
    # right
    if y2 < y1:
        top_left_y = y2
        bottom_right_y = y1

    if x2 < x1:
        top_left_x = x2
        bottom_right_x = x1

    return pygame.Rect(top_left_x, top_left_y, bottom_right_x - top_left_x,
                       bottom_right_y - top_left_y)


def draw_arc(x1, y1, x2, y2, start_x, start_y, end_x, end_y, color, width=2):
    # Creates the bounding rectangle (the rectangle that the arc will reside
    # within
    r = _get_rectangle(int(x1), int(y1), int(x2), int(y2))

    # Calculates the Starting Angle
    start_a = start_x - r.centerx
    start_b = start_y - r.centery
    start_angle = math.atan2(start_b, start_a)

    # Calculates the Ending Angle
    end_a = end_x - r.centerx
    end_b = end_y - r.centery
    # the negative makes the arc go counter-clockwise like Raptor
    end_angle = math.atan2(end_b, end_a) * -1.0

    pygame.draw.arc(win, color, r, start_angle, end_angle, int(width))


def draw_circle(x, y, radius, color, filled, width=2):
    global win
    if filled:
        pygame.draw.circle(win, color, [int(x), int(y)], int(radius), 0)
    else:
        pygame.draw.circle(win, color,
                           [int(x), int(y)], int(radius), int(width))


def draw_ellipse(x1, y1, x2, y2, color, filled, width=2):
    global win
    r = _get_rectangle(int(x1), int(y1), int(x2), int(y2))
    if filled:
        pygame.draw.ellipse(win, color, r, 0)
    else:
        pygame.draw.ellipse(win, color, r, int(width))


def draw_image(filename, x, y, width, height):
    global win
    _load_image(filename)
    image = pygame.transform.scale(images[filename], (int(width), int(height)))
    win.blit(image, (x, y))


def draw_line(x1, y1, x2, y2, color, width=2):
    global win
    pygame.draw.line(win, color, (int(x1), int(y1)), (int(x2), int(y2)),
                     int(width))


def draw_pixel(x, y, color):
    global win
    win.set_at((int(x), int(y)), color)


def draw_rectangle(x1, y1, x2, y2, color, filled, width=2):
    global win
    r = _get_rectangle(int(x1), int(y1), int(x2), int(y2))
    if filled:
        pygame.draw.rect(win, color, r, 0)
    else:
        pygame.draw.rect(win, color, r, int(width))


# Text Operations
def write_text(text, x, y, color, font_size=30):
    global font
    font = pygame.font.SysFont('None', int(font_size))
    text = font.render(text, True, color)
    win.blit(text, (int(x), int(y)))


def draw_text(text, x, y, color, font_size=30):
    write_text(text, x, y, color, font_size)


# Sound
def play_sound_effect(filename):
    _load_sound(filename)
    sound = sounds[filename]
    channel = pygame.mixer.find_channel()  # Searches for an available channel
    if channel is not None:
        channel.play(sound)


def play_music(filename, loop=True):
    pygame.mixer.music.load(filename)

    if loop:
        pygame.mixer.music.play(-1)
    else:
        pygame.mixer.music.play(1)


def stop_music():
    pygame.mixer.music.stop()


# Events (Keyboard, Mouse, Window)
def _get_events():
    global event_list
    if (len(event_list) == 0):
        event_list = pygame.event.get()
    return event_list


# Event Operations (Keyboard, Mouse, Window)
def get_mouse_x():
    x, y = pygame.mouse.get_pos()
    return x


def get_mouse_y():
    x, y = pygame.mouse.get_pos()
    return y


def _get_key(key_string):
    # Removes the '[]' characters that surround some keys
    if len(key_string) > 1:
        key_string = key_string.replace("[", "")
        key_string = key_string.replace("]", "")
    return key_string


def key_pressed(which_key):
    for event in _get_events():
        if event.type == pygame.KEYDOWN:
            return _get_key(pygame.key.name(event.key)) == which_key
    return False


def key_down(which_key):
    # Gets the key codes of the pressed keys
    pressed = pygame.key.get_pressed()

    # Converts the key codes into friendly names ('a' instead of 137)
    buttons = [_get_key(pygame.key.name(k))
               for k, v in enumerate(pressed) if v]

    # Checks to see if the desired key is in the array
    return buttons.count(which_key) > 0


def key_released(which_key):
    for event in _get_events():
        if event.type == pygame.KEYUP:
            return _get_key(pygame.key.name(event.key)) == which_key
    return False


def mouse_button_pressed(which_button):
    for event in _get_events():
        if event.type == pygame.MOUSEBUTTONDOWN:
            return event.button == which_button
    return False


def mouse_button_down(which_button):
    pressed = pygame.mouse.get_pressed()
    return pressed[which_button-1]


def mouse_button_released(which_button):
    for event in _get_events():
        if event.type == pygame.MOUSEBUTTONUP:
            return event.button == which_button
    return False


def window_closed():
    if win is None:
        return True
    else:
        for event in _get_events():
            if event.type == pygame.QUIT:
                close_window()
    return win is None


def window_not_closed():
    return not window_closed()


def quit():
    global win
    win = None
    pygame.quit()


# Miscellaneous Operations
def delay(time):
    pygame.time.delay(time)


def get_pressed_key():
    for event in _get_events():
        if event.type == pygame.KEYDOWN:
            return _get_key(pygame.key.name(event.key))
    return None


def _load_image(filename):
    global images
    if filename not in images.keys():
        images[filename] = pygame.image.load(filename).convert()


def _load_sound(filename):
    global sounds
    if filename not in sounds.keys():
        sound = pygame.mixer.Sound(filename)
        sounds[filename] = sound
