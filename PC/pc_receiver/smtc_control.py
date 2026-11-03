"""
smtc_control.py
================

Windows System Media Transport Controls (SMTC) integration for AudioSync's
Bluetooth (A2DP sink + AVRCP) receiver.

Why this exists
---------------
When the PC acts as a Bluetooth A2DP sink, Windows *also* instantiates an
AVRCP target for that connection. The phone (the AVRCP *controller*) sends
play / pause / next / previous / stop commands which Windows translates and
delivers to the **active media session** through SMTC. By registering
AudioSync as an SMTC media session we get:

  * The Windows "Now playing" card (Action Center / lock screen) shows
    AudioSync while a phone is connected over Bluetooth.
  * Play / Pause / Next / Previous / Stop commands arriving from
      - the phone over AVRCP (the handset's media buttons), **and**
      - the PC's own media keys / hardware buttons
    are delivered to AudioSync through SMTC's ``button_pressed`` event.
  * AudioSync reflects its playback state back to SMTC, which Windows then
    mirrors to the phone over AVRCP (so the handset's play/pause icon stays
    in sync). This is the bidirectional AVRCP bridge.

Design notes
------------
* This module depends only on ``winsdk`` (WinRT) and is framework agnostic.
* WinRT ``button_pressed`` callbacks run on a WinRT-owned thread. To keep
  WinRT mutations safe we never touch SMTC objects from that thread; we just
  enqueue the command and let the host pump it from its main loop via
  :meth:`MediaTransportController.pump`.
* All failures are non-fatal: if SMTC is unavailable the receiver still works
  as a plain Bluetooth speaker.
"""

import json
import queue

from winsdk.windows.media.playback import MediaPlayer
from winsdk.windows.media import (
    SystemMediaTransportControls,
    MediaPlaybackStatus,
    MediaPlaybackType,
    SystemMediaTransportControlsButton,
)


def emit_event(event_type, data=None):
    """Emit a structured event the Electron layer forwards to the UI.

    Uses the ``{"type": ..., "data": ...}`` shape understood by
    ``electron/main.js`` (see the Bluetooth stdout forwarder).
    """
    msg = {"type": event_type}
    if data is not None:
        msg["data"] = data
    print(json.dumps(msg), flush=True)


# WinRT button enum -> (logical command, human label)
_BUTTON_MAP = {
    SystemMediaTransportControlsButton.PLAY: ("play", "Play"),
    SystemMediaTransportControlsButton.PAUSE: ("pause", "Pause"),
    SystemMediaTransportControlsButton.PLAY_PAUSE_TOGGLE: ("toggle", "Play/Pause"),
    SystemMediaTransportControlsButton.STOP: ("stop", "Stop"),
    SystemMediaTransportControlsButton.NEXT: ("next", "Next"),
    SystemMediaTransportControlsButton.PREVIOUS: ("previous", "Previous"),
}


class MediaTransportController:
    """Wraps a WinRT ``MediaPlayer``'s SystemMediaTransportControls."""

    def __init__(self, device_name="AudioSync"):
        self._device_name = device_name or "AudioSync"
        self._player = None
        self._smtc = None
        self._cmd_queue = queue.Queue()
        self._playing = False
        self._enabled = False

    # ------------------------------------------------------------------ #
    # Lifecycle
    # ------------------------------------------------------------------ #
    def start(self):
        """Register with SMTC. Returns True on success."""
        try:
            self._player = MediaPlayer()
        except Exception as e:
            emit_event("smtc_error", {"error": f"MediaPlayer init failed: {e}"})
            return False

        try:
            # We handle transport commands ourselves.
            try:
                self._player.command_manager.is_enabled = False
            except Exception:
                pass

            self._smtc = self._player.system_media_transport_controls
            self._smtc.is_play_enabled = True
            self._smtc.is_pause_enabled = True
            self._smtc.is_play_pause_toggle_enabled = True
            self._smtc.is_next_enabled = True
            self._smtc.is_previous_enabled = True
            self._smtc.is_stop_enabled = True
            self._smtc.add_button_pressed(self._on_button_pressed)

            self.set_metadata("AudioSync Bluetooth Stream", self._device_name)

            self._enabled = True
            self.set_playing(True)  # mark as playing once the sink is live
            emit_event("smtc_ready", {"device": self._device_name})
            return True
        except Exception as e:
            emit_event("smtc_error", {"error": f"SMTC init failed: {e}"})
            self.stop()
            return False

    def stop(self):
        """Tear down SMTC registration."""
        self._enabled = False
        try:
            if self._smtc is not None:
                self._smtc.button_pressed.remove(self._on_button_pressed)
        except Exception:
            pass
        try:
            if self._player is not None:
                self._player.close()
        except Exception:
            pass
        self._player = None
        self._smtc = None

    # ------------------------------------------------------------------ #
    # WinRT event (runs on WinRT thread -> only enqueue)
    # ------------------------------------------------------------------ #
    def _on_button_pressed(self, sender, args):
        try:
            mapping = _BUTTON_MAP.get(args.button)
            if mapping is not None:
                cmd, label = mapping
            else:
                cmd = str(args.button).split(".")[-1].lower()
                label = cmd
        except Exception:
            cmd, label = "unknown", "Unknown"
        self._cmd_queue.put((cmd, label))

    # ------------------------------------------------------------------ #
    # State setters (must be called from the host's main thread)
    # ------------------------------------------------------------------ #
    def set_playing(self, playing):
        if not self._enabled or self._smtc is None:
            return
        try:
            self._playing = bool(playing)
            self._smtc.playback_status = (
                MediaPlaybackStatus.PLAYING if self._playing
                else MediaPlaybackStatus.PAUSED
            )
            emit_event("smtc_status", {"playing": self._playing})
        except Exception as e:
            emit_event("smtc_error", {"error": f"set_playing failed: {e}"})

    def set_metadata(self, title, artist):
        if not self._enabled or self._smtc is None:
            return
        try:
            updater = self._smtc.display_updater
            updater.type = MediaPlaybackType.MUSIC
            updater.music_properties.title = title or "AudioSync"
            updater.music_properties.artist = artist or "AudioSync"
            updater.update()
        except Exception as e:
            emit_event("smtc_error", {"error": f"set_metadata failed: {e}"})

    def is_playing(self):
        return self._playing

    # ------------------------------------------------------------------ #
    # Main-loop pump
    # ------------------------------------------------------------------ #
    def pump(self, handler):
        """Drain queued AVRCP/SMTC commands.

        ``handler(cmd, label)`` runs on the caller's (main) thread, so any
        WinRT mutations it performs stay safe.
        """
        while not self._cmd_queue.empty():
            try:
                cmd, label = self._cmd_queue.get_nowait()
            except queue.Empty:
                break
            try:
                if handler:
                    handler(cmd, label)
            except Exception as e:
                emit_event("smtc_error", {"error": f"command handler error: {e}"})
