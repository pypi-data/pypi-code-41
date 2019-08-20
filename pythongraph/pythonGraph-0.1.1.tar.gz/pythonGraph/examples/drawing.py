#!/usr/bin/env python

import os.path

import pythonGraph


if '__main__' == __name__:
    # open window
    pythonGraph.open_window(800, 600)

    # Background Music Test
    pythonGraph.play_music(os.path.join(os.path.dirname(__file__),
                                        "media", "alien-spaceship.ogg"))
    # Background Color
    clear_color = pythonGraph.colors.WHITE

    # Last Pressed Key
    last_pressed_key = None

    # Bouncing Ball
    ball_x = 0
    ball_y = 0
    ball_x_velocity = 2
    ball_y_velocity = 4
    ball_color = pythonGraph.create_random_color()

    while pythonGraph.window_not_closed():
        # window title
        pythonGraph.set_window_title('{} ({},{}); Mouse: ({}, {})'.format(
            __name__,
            pythonGraph.get_window_width(), pythonGraph.get_window_height(),
            pythonGraph.get_mouse_x(), pythonGraph.get_mouse_y()))

        # clear Window
        pythonGraph.clear_window(clear_color)

        # drawing
        pythonGraph.draw_text("Welcome to pythonGraph!", 10, 10,
                              pythonGraph.create_color(255, 0, 0), 50)
        pythonGraph.draw_arc(10, 60, 200, 200, 200, 150, 10, 150,
                             pythonGraph.colors.BLUE, 5)

        image_path = os.path.join(os.path.split(os.path.abspath(__file__))[0],
                                  'media', 'test.png')
        pythonGraph.draw_image(image_path, 10, 150, 100.56, 100)

        pythonGraph.draw_rectangle(10, 260, 100, 350,
                                   pythonGraph.colors.GREEN, False, 2.223)
        pythonGraph.draw_circle(50, 410, 50, pythonGraph.colors.CYAN, True)
        pythonGraph.draw_ellipse(1, 460, 150, 550,
                                 pythonGraph.colors.LIGHT_MAGENTA, False, 5)
        pythonGraph.draw_line(225, 50, 225, pythonGraph.get_window_height(),
                              pythonGraph.colors.BROWN, 3)

        # drawing pixels (need to draw a bunch so you can see them)
        pythonGraph.draw_pixel(25, 575, pythonGraph.create_random_color())
        pythonGraph.draw_pixel(30, 575, pythonGraph.create_random_color())
        pythonGraph.draw_pixel(35, 575, pythonGraph.create_random_color())
        pythonGraph.draw_pixel(40, 575, pythonGraph.create_random_color())
        pythonGraph.draw_pixel(45, 575, pythonGraph.create_random_color())
        pythonGraph.draw_pixel(50, 575, pythonGraph.create_random_color())

        # Sound Test
        if pythonGraph.mouse_button_pressed(pythonGraph.mouse_buttons.LEFT):
            pythonGraph.play_sound_effect(os.path.join(
                os.path.dirname(__file__), "media", "magic-wand.ogg"))

        # Keyboard Events
        if pythonGraph.key_down('b'):
            clear_color = pythonGraph.colors.BLUE
        else:
            clear_color = pythonGraph.colors.WHITE

        if pythonGraph.get_pressed_key() is not None:
            last_pressed_key = pythonGraph.get_pressed_key()

        pythonGraph.draw_text("Last Pressed Key: " + str(last_pressed_key),
                              250, 60, pythonGraph.create_color(127, 0, 255),
                              30)

        # Simple Animation
        pythonGraph.draw_circle(ball_x, ball_y, 25, ball_color, True)
        ball_x += ball_x_velocity
        ball_y += ball_y_velocity
        if ball_x > pythonGraph.get_window_width() or ball_x < 0:
            ball_x_velocity *= -1.0
            ball_color = pythonGraph.create_random_color()
        if ball_y > pythonGraph.get_window_height() or ball_y < 0:
            ball_y_velocity *= -1.0
            ball_color = pythonGraph.create_random_color()

        pythonGraph.update_window()

        if pythonGraph.key_down('q'):
            pythonGraph.close_window()
