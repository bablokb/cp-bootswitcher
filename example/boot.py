# ----------------------------------------------------------------------------
# Boot-Switcher for CircuitPython.
#
# This boot.py assumes that you installed your applications to two
# subdirectories in the root of your device, e.g.
#
#   /_app0
#   /_app1
#
# It also needs a GPIO to start either _app0 (GPIO is low) or _app1.
# Note that this will also work if you only want to switch a subset of
# files (use SHARED_FILES for common files, e.g. fonts).
# See the configuration section below.
#
# Author: Bernhard Bablok
# License: GPL3
#
# Website: https://github.com/bablokb/cp-bootswitcher
#
# ----------------------------------------------------------------------------

import board
import os
import digitalio
import storage
import supervisor

# --- configuration   --------------------------------------------------------

PIN_SWITCH = board.D1                       # change as needed
APP_NAMES  = ["FirstApp","SecondApp"]       # change as needed
SHARED_FILES = ["boot.py"]+APP_NAMES        # add (top-level) files as needed

# --- move application-code to top-level   -----------------------------------

def activate(app_nr,app_files):
  """ move given files to top-level directory """

  app_dir = f"/{APP_NAMES[app_nr]}"
  for f in app_files:
    os.rename(f"/{app_dir}/{f}",f"/{f}")
  os.sync()

# --- move application-code to app-directory   -------------------------------

def deactivate(app_nr):
  """ move top-level files back to application-directory """

  source_files = os.listdir("/")
  app_dir = f"/{APP_NAMES[app_nr]}"
  for f in source_files:
    if f in SHARED_FILES:
      continue
    else:
      os.rename(f"/{f}",f"{app_dir}/{f}")
  os.sync()

# --- main program   ---------------------------------------------------------

# query selected app
switch = digitalio.DigitalInOut(PIN_SWITCH)
switch.direction = digitalio.Direction.INPUT
switch.pull      = digitalio.Pull.UP
app_nr           = int(switch.value)
switch.deinit()

# check for files in application-directory
app_files = os.listdir(f"/{APP_NAMES[app_nr]}")
if len(app_files):
  storage.remount("/",False)    # remount rw
  deactivate(1-app_nr)          # deactivate the other app
  activate(app_nr,app_files)    # activate selected app
  storage.remount("/",True)     # remount ro
  
# and start main-code
supervisor.reload()
