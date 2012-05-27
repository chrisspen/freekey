=============================================================================
FreeKey - Allows limited keyboard use on a locked desktop
=============================================================================

Overview
--------
Monitors key presses system-wide and runs commands in response to certain
key presses.

This script was initially designed to allow the multimedia keys to still
function despite the desktop being locked, since the default behavior in some
Gnome configurations disable all special function keys when locked.

Installation
------------

::
    sudo apt-get install python-xlib
    sudo pip install https://github.com/chrisspen/freekey/zipball/master
    sudo python freekey.py install

The daemon should automatically launch when you login.

Usage
-----

Modify /etc/freekey.conf to associate events with shell commands.

Each line is of the form <event> <command>, where <event> is either
a key name or scan code.

To find a key's name or code, run `freekey.py echo` and press the key.

You can test it by running `freekey.py run`.