#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import signal

from Xlib import display, X
from PIL import Image

DISPLAY_NUM = ":0"
SCREEN_SIZE = (1024, 768)

# Exit if no frames requested in the next 10 seconds
WATCHDOG_TIMEOUT = 10

if len(sys.argv) < 2:
	print("Usage: python3 server.py TARGET_WINDOW_ID")
	sys.exit(1)

TARGET_WINDOW_ID = int(sys.argv[1], 16)

dsp = display.Display(DISPLAY_NUM)
root = dsp.screen().root

selected_window = None
windows = root.query_tree().children
for window in windows:
	if window.id == TARGET_WINDOW_ID:
		selected_window = window

if selected_window is None:
	sys.exit(-1)

# Resize the window to SCREEN_SIZE
selected_window.configure(width=SCREEN_SIZE[0], height=SCREEN_SIZE[1])
selected_window.get_geometry()

# Main loop
while True:
	# Watchdog timeout
	signal.alarm(WATCHDOG_TIMEOUT)

	# Wait for a frame to be requested
	request_line = sys.stdin.readline()
	if "NEXT" != request_line.rstrip():
		break

	# Send the window pixels over STDOUT
	raw = selected_window.get_image(0, 0, SCREEN_SIZE[0], SCREEN_SIZE[1], X.ZPixmap, 0xffffffff)
	image = Image.frombytes("RGB", SCREEN_SIZE, raw.data, "raw", "BGRX")
	sys.stdout.buffer.write(image.tobytes())
	sys.stdout.buffer.flush()
