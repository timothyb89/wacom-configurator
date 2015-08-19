import os

from collections import Callable
from functools import partial
from sh import xsetwacom, xinput, xrandr, notify_send

SIMULATE = False

_action_map = {}

_profiles = {}
_default_profile = None
_current_profile = None

top_left = 3
top_right = 9
bottom_left = 1
bottom_right = 8

stylus = [
    "Wacom Intuos PT S Pen stylus",
    "Wacom Intuos PT S (WL) Pen stylus"
]

eraser = [
    "Wacom Intuos PT S Pen eraser",
    "Wacom Intuos PT S Pen stylus"
]

touch = [
    "Wacom Intuos PT S Finger touch",
    "Wacom Intuos PT S (WL) Finger touch"
]

pad = [
    "Wacom Intuos PT S Pad pad",
    "Wacom Intuos PT S (WL) Pad pad"
]

all_inputs = stylus + eraser + touch + pad

_active_targets = None
_displays = { line.split()[0] for line in xrandr() if not line.startswith(' ') }
_displays.remove('Screen')

_dir = os.path.dirname(os.path.abspath(__file__))
_profile_store = os.path.join(_dir, ".wacom_profile")


def set(targets, prop, value):
    if SIMULATE:
        return

    print 'active targets:', get_active_targets().intersection(targets)

    for target in get_active_targets().intersection(targets):
        print 'xsetwacom: %s=%r on %s' % (prop, value, target)
        xsetwacom.set(target, prop, value)


def toggle(targets, prop, **mappings):
    if not mappings:
        mappings = {
            'on': 'off',
            'off': 'on',
            '0': '1',
            '1': '0'
        }

    for target in get_active_targets().intersection(targets):
        old = str(xsetwacom.get(target, prop)).strip()
        if old in mappings:
            xsetwacom.set(target, prop, mappings[old])
        else:
            print "WARN: unknown value to toggle:", old


def set_button(button, action):
    if isinstance(action, Callable):
        _action_map[button] = action
        action = 'key +ctrl +super +shift +alt %d -alt -shift -super -ctrl' % button

    if SIMULATE:
        return

    for target in get_active_targets().intersection(pad):
        print 'xsetwacom: button %d="%s" on %s' % (button, action, target)
        xsetwacom.set(target, 'Button', button, action)


def xinput_set(targets, prop, value, type="float"):
    if SIMULATE:
        return

    for target in get_active_targets().intersection(targets):
        print 'xinput: %s=%r (%s) on %s' % (prop, value, type, target)
        xinput('set-prop', target, prop, value, type=type)


def get_active_targets(refresh=False):
    global _active_targets

    if not _active_targets or refresh:
        _active_targets = { target.strip() for target in xinput.list(name_only=True) }

    return _active_targets


def profile(default=False, name=None):
    def wrap(func):
        global _default_profile

        _name = name
        if not _name:
            _name = func.func_name

        _profiles[_name] = func
        if not _default_profile or default:
            _default_profile = _name

        return func

    return wrap


def reverse_lookup_profile(search_func):
    for profile_name, profile_func in _profiles.iteritems():
        if profile_func == search_func:
            return profile_name

    return None


def get_stored_profile():
    if not os.path.exists(_profile_store):
        return None

    with open(_profile_store, 'r') as f:
        return f.read().strip()


def set_profile(profile):
    global _current_profile

    print 'Setting current profile to', profile
    if isinstance(profile, basestring):
        if profile in _profiles:
            _current_profile = profile
            _profiles[profile]()
        else:
            print 'WARNING: Profile not found:', profile
            return
    else:
        _current_profile = reverse_lookup_profile(profile)
        profile()

    with open(_profile_store, 'w') as f:
        f.write(_current_profile)

    if not SIMULATE:
        notify_send("Profile Changed",
                    "Profile set to '%s'." % _current_profile,
                    icon="input-tablet",
                    expire_time=2000)
