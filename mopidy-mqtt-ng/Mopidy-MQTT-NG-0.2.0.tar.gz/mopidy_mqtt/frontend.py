from __future__ import absolute_import
from __future__ import unicode_literals

import logging

import pykka
from mopidy.core import CoreListener
from .mqtt import Comms


log = logging.getLogger(__name__)


VOLUME_MAX = 100
VOLUME_MIN = 0
VOLUME_STEP = 5


class MQTTFrontend(pykka.ThreadingActor, CoreListener):
    def __init__(self, config, core):
        """
        config (dict): The entire Mopidy configuration.
        core (ActorProxy): Core actor for Mopidy Core API.
        """
        super(MQTTFrontend, self).__init__()
        self.core = core
        self.mqtt = Comms(frontend=self, config=config['mqtt'])

    def on_start(self):
        """
        Hook for doing any setup that should be done *after* the actor is
        started, but *before* it starts processing messages.
        """
        log.debug('Starting MQTT frontend: %s', self)
        self.mqtt.start()

    def on_stop(self):
        """
        Hook for doing any cleanup that should be done *after* the actor has
        processed the last message, and *before* the actor stops.
        """
        log.debug('Stopping MQTT frontend: %s', self)
        self.mqtt.stop()

    def on_failure(self, exception_type, exception_value, traceback):
        """
        Hook for doing any cleanup *after* an unhandled exception is raised,
        and *before* the actor stops.
        """
        log.error('MQTT frontend failed: %s', exception_value)

    def playback_state_changed(self, old_state, new_state):
        """
        old_state (mopidy.core.PlaybackState) - the state before the change.
        new_state (mopidy.core.PlaybackState) - the state after the change.
        """
        log.debug('MQTT playback state changed: %s', new_state)
        self.mqtt.publish('state', new_state)

    def stream_title_changed(self, title):
        """
        title (string) - the new stream title.
        """
        log.debug('MQTT title changed: %s', title)
        self.mqtt.publish('nowplaying', title)

    def track_playback_ended(self, tl_track, time_position):
        """
        tl_track (mopidy.models.TlTrack) - the track that was played before
                                           playback stopped.
        time_position (int) - the time position in milliseconds.
        """
        log.debug('MQTT track ended: %s', tl_track.track.name)
        self.mqtt.publish('nowplaying', '')

    def track_playback_started(self, tl_track):
        """
        tl_track (mopidy.models.TlTrack) - the track that just started playing.
        """
        log.debug('MQTT track started: %s', tl_track.track)
        # TODO: Better name construction.
        self.mqtt.publish('nowplaying', str(tl_track.track))

    def volume_changed(self, volume):
        """
        volume (int) - the new volume in the range [0..100].
        """
        log.debug('MQTT volume changed: %s', volume)
        self.mqtt.publish('info', 'volume;{}'.format(self.volume))

    @property
    def volume(self):
        return self.core.mixer.get_volume().get()

    @volume.setter
    def volume(self, value):
        self.core.mixer.set_volume(value)

    def on_action_control(self, value):
        """
        General playback (and volume) control.
        """
        if value == 'stop':
            return self.core.playback.stop()
        if value == 'pause':
            return self.core.playback.pause()
        if value == 'play':
            return self.core.playback.play()
        if value == 'resume':
            return self.core.playback.resume()

        if value == 'next':
            return self.core.playback.next()
        if value == 'previous':
            return self.core.playback.previous()

        if value == 'volplus':
            new_volume = min(self.volume + VOLUME_STEP, VOLUME_MAX)
            self.volume = new_volume
            return

        if value == 'volminus':
            new_volume = max(self.volume - VOLUME_STEP, VOLUME_MIN)
            self.volume = new_volume
            return

        log.warn('Unknown MQTT playback control request: %s', value)

    def on_action_play(self, value):
        """
        Clear tracklist, add specified track by URL, start the playback.
        """
        self.core.tracklist.clear()
        self.core.tracklist.add(
            tracks=None, at_position=None, uri=str(value), uris=None)
        self.core.playback.play()

    def on_action_volume(self, value):
        """
        Absolute volume control.
        """
        try:
            new_volume = int(value)
        except ValueError:
            log.warn('Illegal value for volume: %s', value)
        else:
            self.volume = new_volume

    def on_action_info(self, value):
        """
        Inquiries about status.
        """
        if value == 'state':
            return self.mqtt.publish(
                'state', self.core.playback.get_state().get())

        if value == 'volume':
            return self.mqtt.publish('info', 'volume;{}'.format(self.volume))

        if value == 'list':
            # TODO: Real current playlist info.
            raise NotImplementedError('TODO')
            return

    def on_action_search(self, value):
        """
        Library search.
        """
        raise NotImplementedError('TODO')
