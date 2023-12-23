#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import time
import signal
import threading

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk as gtk
from gi.repository import GLib
from gi.repository import Gio
from gi.repository.GdkPixbuf import Pixbuf

FRAME_WIDTH = 1024
FRAME_HEIGHT = 768
FPS = 15

# Exit if no frames received in the next 10 seconds
WATCHDOG_TIMEOUT = 10

FRAMESIZE = FRAME_WIDTH * FRAME_HEIGHT * 3

class InputReader:
	def __init__(self, framestream, framesize):
		self.framestream = framestream
		self.framesize = framesize

	def readFrame(self):
		framedata = self.framestream.read(self.framesize)
		while len(framedata) < self.framesize:
			framedata += self.framestream.read(self.framesize - len(framedata))
		return framedata

def updateScreenThread():
	frameReader = InputReader(sys.stdin.buffer, FRAMESIZE)
	while True:
		# Request a new frame
		print("NEXT")
		sys.stdout.flush()

		# Watchdog timeout
		signal.alarm(WATCHDOG_TIMEOUT)

		# Load and display the new frame
		try:
			framedata = frameReader.readFrame()
			pixbuf = Pixbuf.new_from_data(framedata, 0, False, 8, FRAME_WIDTH, FRAME_HEIGHT, 3 * FRAME_WIDTH)
			GLib.idle_add(updateScreenGtkTask, pixbuf)
		except:
			pass

		# FPS Limit
		time.sleep(1.0 / FPS)

def updateScreenGtkTask(pixbuf):
	screen.set_from_pixbuf(pixbuf)

# Set up the root window
win = gtk.Window()
win.set_title("Qubes OS Cross-Domain Screenshare")

# Add a screen to show the cross-domain window
fixed = gtk.Fixed()
screen = gtk.Image()
fixed.put(screen, 0, 0)
win.add(fixed)
win.show_all()

# Handle the exit signal
win.connect('destroy', lambda *x: gtk.main_quit())

# Run a thread to read raw frames from the remote domain and display them here
tUpdater = threading.Thread(target=updateScreenThread)
tUpdater.daemon = True
tUpdater.start()

# GTK Mainloop
gtk.main()
