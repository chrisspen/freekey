#!/usr/bin/python
"""
2012.5.26 CKS
Monitors and responds to key presses.
"""
from __future__ import print_function

import commands
import os
import re
import sys
import time

try:
    from Xlib.display import Display
    from Xlib import X
except ImportError as e:
    print('='*80, file=sys.stderr)
    print('Unable to import Xlib: %s' % (e,), file=sys.stderr)
    print('Please ensure python-xlib is installed.', file=sys.stderr)
    print('e.g. sudo apt-get install python-xlib', file=sys.stderr)
    print('='*80, file=sys.stderr)
    sys.exit(1)

from pyxhook import HookManager

from daemon import Daemon

VERSION = (0, 1, 3)
__version__ = '.'.join(map(str, VERSION))

ACTIONS = (
    INSTALL,
    UNINSTALL,
    START,
    STOP,
    RESTART,
    RUN,
    ECHO,
) = (
    'install',
    'uninstall',
    'start',
    'stop',
    'restart',
    'run',
    'echo',
)
#DEFAULT_ACTION = START
DEFAULT_ACTION = None
DEFAULT_PIDFILE = '/tmp/freekey.pid'
DEFAULT_CONF = os.environ.get('FREEKEY_CONF', '/etc/freekey.conf')
DEFAULT_BIN_DIR = '/usr/bin'
DEFAULT_PROFILE_SCRIPT = '/etc/profile.d/freekey.sh'

class FreeKey(Daemon):

    def __init__(self,
        conf=DEFAULT_CONF,
        control_c_kill=False,
        *args, **kwargs):

        super(FreeKey, self).__init__(*args, **kwargs)

        self.control_down = False
        self.shift_down = False
        self.alt_down = False
        self.altGr_down = False
        self.control_c_kill = control_c_kill

        # Process configuration file.
        assert os.path.isfile(conf), 'Configuration file %s not found.'
        self.event_to_command = {} # {scancode:command}
        i = 0
        for line in open(conf, 'r').readlines():
            i += 1
            line = line.strip()
            parts = line.split(' ')
            if not line or line.startswith('#'):
                continue
            if len(parts) < 2:
                print('Malformed line: %i' % i)
                continue
            scancode = parts[0]

#            if not scancode.isdigit():
#                print('Malformed scan code: %i' % i
#                continue
            #scancode = int(scancode)
            command = ' '.join(parts[1:])
            #print('Loaded command binding: %s = %s' % (scancode, command)
            self.event_to_command[scancode] = command

    def handle_keydown(self, event):
        #print('keydown:',event

        if event.Key in ["Control_R", "Control_L",]:
            self.control_down = True

        if event.Key in ["Shift_R", "Shift_L"]:
            self.shift_down = True

        if event.Key in ["Alt_L"]:
            self.alt_down = True

        if event.ScanCode in [108]:
            self.altGr_down = True

        if self.control_c_kill:
            if self.control_down and event.Key in ('C','c'):
                sys.exit()

        key = str(event.ScanCode)

        if self.altGr_down == True:
            key = "altgr_" + key

        if self.alt_down == True:
            key = "alt_" + key

        if self.shift_down == True:
            key = "shift_" + key

        if self.control_down == True:
            key = "ctrl_" + key

        command = self.event_to_command.get(key)
        if command:
            print('Running: %s' % command)
            os.system(command)

    def handle_keyup(self, event):
        #print('keyup:',event
        if event.Key in ["Control_R", "Control_L",]:
            self.control_down = False

        if event.Key in ["Shift_R", "Shift_L"]:
            self.shift_down = False

        if event.Key in ["Alt_L"]:
            self.alt_down = False

        if event.ScanCode in [108]:
            self.altGr_down = False

    def run(self):
        print('Running...')
        hm = HookManager()
        hm.HookKeyboard()
        hm.KeyDown = self.handle_keydown
        hm.KeyUp = self.handle_keyup
        hm.start()

def write_default_conf(fn):
    if os.path.isfile(fn):
        print('Configuration file %s exists. Skipping file generation.' % fn)
    open(fn, 'w').write(r"""#ScanCode Command
# Note: If you're running Cinnamon, substitute 'gnome-screensaver-command' with 'cinnamon-screensaver-command'
# volume up/down
122 gnome-screensaver-command -q | grep "is active" && bash -c '/usr/bin/pactl -- set-sink-volume `pacmd list-sinks | grep -P -o "(?<=\* index: )[0-9]+"` -10%'
123 gnome-screensaver-command -q | grep "is active" && bash -c '/usr/bin/pactl -- set-sink-volume `pacmd list-sinks | grep -P -o "(?<=\* index: )[0-9]+"` +10%'
# mute
121 gnome-screensaver-command -q | grep "is active" && bash -c 'for i in $(pacmd list-sinks | grep -Po "(?<=\* index: )[0-9]+"); do /usr/bin/pactl -- set-sink-mute $i $(pacmd list-sinks | grep -Pqzo "(?s)\* index.*?muted: no.*?(properties)" && echo 1 || echo 0); done'
# play/pause
171 gnome-screensaver-command -q | grep "is active" && bash -c '/usr/bin/pactl -- suspend-sink `pacmd list-sinks | grep -P -o "(?<=\* index: )[0-9]+"` `pacmd list-sinks | grep -P -o "state: RUNNING" | wc -l`'
#
# Add own key mappings
# [ctrl_][shift_][alt_][altgr_]keycode command
""")

def echo_keypresses():
    print('Echoing key presses.')
    print('Press ctrl+c to exit.')
    control_keys = ["Control_R", "Control_L",]
    control = [False]

    def handle_keydown(event):
        print('Key-down:')
        print('\tkey:', event.Key)
        print('\tkey id:', event.KeyID)
        print('\tscan code:', event.ScanCode)
        if event.Key in control_keys:
            control[0] = True
        elif control[0] and event.Key in ('C','c'):
            sys.exit()

    def handle_keyup(event):
        print('Key-up:')
        print('\tkey:', event.Key)
        print('\tkey id:', event.KeyID)
        print('\tscan code:', event.ScanCode)
        if event.Key in control_keys:
            control[0] = False

    hm = HookManager()
    hm.HookKeyboard()
    hm.KeyDown = handle_keydown
    hm.KeyUp = handle_keyup
    hm.start()

#def install_symlink():
#    fqfn = os.path.abspath(__file__)
#    fn = os.path.split(fqfn)[1]
#    installed_fqfn = os.path.join(DEFAULT_BIN_DIR, fn)
#    os.system(
#        '[ ! -f %(installed_fqfn)s ] && ln -s %(fqfn)s %(installed_fqfn)s; chmod +x %(installed_fqfn)s' \
#        % dict(fqfn=fqfn, installed_fqfn=installed_fqfn))
#
#def uninstall_symlink():
#    fqfn = os.path.abspath(__file__)
#    fn = os.path.split(fqfn)[1]
#    installed_fqfn = os.path.join(DEFAULT_BIN_DIR, fn)
#    os.system(
#        'rm -f %(installed_fqfn)s' \
#        % dict(fqfn=fqfn, installed_fqfn=installed_fqfn))

def install_profile_daemon():
    print('Writing %s...' % DEFAULT_PROFILE_SCRIPT)
    open(DEFAULT_PROFILE_SCRIPT, 'w').write(r"""#!/bin/bash
freekey start
""")

def uninstall_profile_daemon():
    print('Removing %s...' % DEFAULT_PROFILE_SCRIPT)
    os.remove(DEFAULT_PROFILE_SCRIPT)

if __name__ == "__main__":
    from optparse import OptionParser
    usage = """usage: %%prog [options] <%s>

Actions:

  echo := Wait and display info for pressed keys.

  install := Installs the script's executable daemon and configuration file.

  restart := Stops and then starts the daemon.

  run := Runs the script in non-daemon mode.

  start := Runs the script in daemon mode.

  stop := Terminates a running daemon.

  uninstall := Removes the scripts executable daemon.""" % ('|'.join(ACTIONS),)
    parser = OptionParser(usage=usage, version=__version__)

    parser.add_option(
        "--pidfile",
        dest="pidfile",
        default=DEFAULT_PIDFILE,
        help="Location of the process identification file storing the " +
            "process identification number while running as a daemon.")

    parser.add_option(
        "--conf",
        dest="conf",
        default=DEFAULT_CONF,
        help="Location of the configuration file.")

    (options, args) = parser.parse_args()

    action = DEFAULT_ACTION
    if args:
        action = args[0]
    if action not in ACTIONS:
        parser.error("Invalid action: %s" % action)
    if action == ECHO:
        echo_keypresses()
    if action == INSTALL:
        write_default_conf(options.conf)
        #install_symlink()
        install_profile_daemon()
    elif action == RESTART:
        daemon = FreeKey(**options.__dict__)
        daemon.restart()
    elif action == RUN:
        daemon = FreeKey(control_c_kill=True, **options.__dict__)
        daemon.run()
    elif action == START:
        daemon = FreeKey(**options.__dict__)
        daemon.start()
    elif action == STOP:
        daemon = FreeKey(**options.__dict__)
        daemon.stop()
    elif action == UNINSTALL:
        #uninstall_symlink()
        uninstall_profile_daemon()
    sys.exit(0)
