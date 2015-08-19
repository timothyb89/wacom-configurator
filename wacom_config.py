from wacom_lib import *

@profile(default=True)
def touchpad():
    set_button(bottom_right, lambda: set_profile(pen))

    set(touch + stylus, "rotate", "ccw")
    set(touch, 'Touch', 'on')


@profile()
def pen():
    set_button(bottom_right, lambda: set_profile(touchpad))

    set(touch + stylus, "rotate", "none")
    set(touch, 'Touch', 'off')

set(stylus + eraser, 'threshold', 20)

set_button(bottom_left, '1')
set_button(top_left, '3')

set_button(top_right, 'key lsuper')

xinput_set(touch, "Device Accel Constant Deceleration", 2.0)
