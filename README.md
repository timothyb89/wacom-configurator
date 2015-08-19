wacom-configurator
==================

A small Python utility to manage your Wacom tablets under Linux. Works well with
hotplugged or wireless tablets, makes it easy to set any parameters normally
set via `xinput` or `xsetwacom`, and supports profiles.

Requirements
------------
System commands:
 * `notify-send`
 * `xinput`

Python dependencies (available via `pip`):
 * `sh`
 * `pyudev`

Usage
-----
 1. Clone the repository
 2. Configure device names and buttons numbers in `wacom_lib.py`. They are pre-
    configured for an Intuos Pen and Touch (small) tablet.
 3. Make desired changes to `wacom_config.py` (see below)
 4. Run `wacom` to initialize connected devices now, or `wacom monitor` to
    continuously monitor for new devices (works great with wireless!)

Configuration Syntax
--------------------
The configuration file is just a Python script. Using function calls, you can
set wacom and xinput properties, bind buttons (directly to code within the
config file, if desired), and create and switch between different configuration
profiles.

The config file should be prefixed with `from wacom_lib import *`, which
provides:
 * Device constants: `stylus`, `eraser`, `touch`, `pad`
 * Button constants: `top_left`, `top_right`, `bottom_left`, `bottom_right`
 * Functions:
   * `set(targets, property, value)`: set the specified property to the given
     value for each target using `xsetwacom`. For example,
     `set(touch + stylus, 'rotate', 'half')` flips the stylus and touchpad 180
     degrees.
   * `toggle(targets, prop)`: toggles the given property if it uses `0`, `1`,
     `on`, or `off` values. Alternative mappings can be specified as keyword
     arguments, e.g. `toggle(touch, 'Touch', on='off', off='on')` will toggle
     the touchpad. Note that the extra mappings for on/off are only provided for
     example and aren't needed for this particular case.
   * `set_button(button, action)`: set the given button number to some action.
     Actions can either be a single number string representing a mouse button
     to click, a macro string such as `key +shift H -shift e l l o`, or a
     Python callable, such as a `lambda`.
   * `xinput_set(targets, prop, value, type='float')`: sets the specified xinput
     property to the given value for each of the given targets. If a `type` is
     provided, use that datatype for the `xinput` call.
   * `switch_profile(profile)`: switch to the given profile. If a string is
     provided, the profile is looked up by name. If a reference to the profile
     function itself is given, it will be used directly. The newly-activated
     profile will be stored to the `.wacom_profile` file in the same directory
     as the `wacom` script.

Profiles
--------
Profiles are functions inside the configuration file with a `@profile()`
decorator. They can make use of any or all of the functions listed above.

When first run, a default profile will be selected that is set as active and
executed. The default profile can be specified explicitly using
`@profile(default=True)`, otherwise it will be the first profile in the config
file. After the first run, the previously-active profile will always be used, so
device state will remain active between, e.g., reboots or reconnects.

To switch between profiles, button actions and other events can call
`switch_profile()`.

Other notes:
 * To manually switch between profiles, run `wacom <profile>`, where `<profile>` is
   the name of the profile to switch to.
 * To reset the profile to the default, remove the hidden `.wacom_profile` file
   created in the same directory as the `wacom` script.
 * To manually name a profile, add a `name='...'` keyword argument to the
   function decorator, for example: `@profile(name='my_profile')`. If not
   provided, the name of the function is used as the profile name.

Button Actions
--------------
Buttons can be easily bound directly to mouse buttons and keyboard keys, or with
the help of an external application like `xbindkeys` or window managers provided
in XFCE, KDE, or GNOME, bound indirectly to Python code within the config file.

To do so:

 1. Write your desired action in the config file using `set_button()`, with an
    action pointing to a function or a lambda rather than a constant value.
 2. Run `wacom` to update key bindings.
 3. Using your keybinding application or control panel of choice, map the
    combination `Ctrl + Super + Shift + Alt + <button number>` to the command
    `wacom <button number>`.
 4. The binding should begin working immediately.

Config Examples
---------------

### Toggle the touchpad
```python
set_button(top_left, lambda: toggle(touch, 'Touch'))
```

### Switch between profiles
```python
@profile()
def a():
    set_button(bottom_right, lambda: set_profile(b))

@profile()
def b():
    set_button(bottom_right, lambda: set_profile(a))
```
Note that you can chain together as many different profiles as you'd like.
