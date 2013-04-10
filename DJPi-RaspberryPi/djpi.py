#!/usr/bin/env python
# -*- coding: utf8 -*-

import cmd
import logging
import os
import sys
import threading
import time

from spotify import Link, SpotifyError
from spotify.audiosink import import_audio_sink
from spotify.manager import (SpotifySessionManager, SpotifyPlaylistManager,
    SpotifyContainerManager)

AudioSink = import_audio_sink()

class QueueManager(threading.Thread):
	
	def __init__(self, player):
		threading.Thread.__init__(self)
		self.player = player
		self.trackQueue = []

	def run(self):
		print "Started Thread"	

		#Load sample queue
		self.trackQueue = ["spotify:track:64pDOeUGiB0vboqmJx2gGp","spotify:track:2lwwrWVKdf3LR9lbbhnr6R","spotify:track:0yp6ui2sosUjCUro1rRk2Q"]
		l = Link.from_string(self.trackQueue[0])
		if not l.type() == Link.LINK_TRACK:
			print "You can only play tracks!"
			return
		self.player.load_track(l.as_track())
		self.player.play()

class PiPlayer(SpotifySessionManager):

	queued = False
	playlist = 2
	track = 0	
	appkey_file = os.path.join(os.path.dirname(__file__), 'spotify_appkey.key')

	def __init__(self, *a, **kw):
		SpotifySessionManager.__init__(self, *a, **kw)
		self.audio = AudioSink(backend=self)
		self.manager = QueueManager(self)
		self.playing = False
		self.trackQueue = []
		self.currentIndex = 0;
		self.track_playing = None
		print "Logging in, please wait..."


	def logged_in(self, session, error):
		if error:
			print error
			return
		print "Logged in!"
		
		if not self.manager.is_alive():
			self.manager.start()
	
	def logged_out(self, session):
		print "Logged out!"
	
	def load_track(self, track):
		print u"Loading track..."
		while not track.is_loaded():
			time.sleep(1)
		
		if track.is_autolinked(): # if linked, load the target track instead
			print "Autolinked track, loading the linked-to track"
	   		return self.load_track(track.playable())
		
		if track.availability() != 1:
   			print "Track not available (%s)" % track.availability()
		
		if self.playing:
   			self.stop()
		self.new_track_playing(track)
		self.session.load(track)
		print "Loaded track: %s" % track.name()
	
	def new_track_playing(self, track):
		self.track_playing = track
	
	def play(self):
	   self.audio.start()
	   self.session.play(1)
	   print "Playing"
	   self.playing = True
	
	def stop(self):
	   self.session.play(0)
	   print "Stopping"
	   self.playing = False
	   self.audio.stop()
	
	def music_delivery_safe(self, *args, **kwargs):
	   return self.audio.music_delivery(*args, **kwargs)
	
	def next(self):
	   self.stop()
	   if self._queue:
	       t = self._queue.pop(0)
	       self.load(*t)
	       self.play()
	   else:
	       self.stop()
	
	def end_of_track(self, sess):
		self.audio.end_of_track()

		#Move to next track in queue
		self.currentIndex += 1
		if self.currentIndex < len(self.manager.trackQueue):
			l = Link.from_string(self.manager.trackQueue[self.currentIndex])
			if not l.type() == Link.LINK_TRACK:
				print "You can only play tracks!"
				return
			self.load_track(l.as_track())

		#Update queue from webserver

## container calllbacks ##
class JukeboxContainerManager(SpotifyContainerManager):
    def container_loaded(self, c, u):
        container_loaded.set()

    def playlist_added(self, c, p, i, u):
        print 'Container: playlist "%s" added.' % p.name()

    def playlist_moved(self, c, p, oi, ni, u):
        print 'Container: playlist "%s" moved.' % p.name()

    def playlist_removed(self, c, p, i, u):
        print 'Container: playlist "%s" removed.' % p.name()


if __name__ == '__main__':
    import optparse
    op = optparse.OptionParser(version="%prog 0.1")
    op.add_option("-u", "--username", help="Spotify username")
    op.add_option("-p", "--password", help="Spotify password")
    op.add_option("-v", "--verbose", help="Show debug information",
        dest="verbose", action="store_true")
    (options, args) = op.parse_args()
    if options.verbose:
        logging.basicConfig(level=logging.DEBUG)
    session_m = PiPlayer(options.username, options.password, True)
    session_m.connect()
