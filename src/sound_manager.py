import random
from pathlib import Path
from PyQt6.QtCore import QUrl
from PyQt6.QtMultimedia import QAudioOutput, QMediaPlayer


class SoundManager:
    def __init__(self):
        base_dir = Path(__file__).resolve().parent.parent
        self.tracks_dir = base_dir / "assets" / "sound" / "photon_tracks"

        self.audio_output = QAudioOutput()
        self.player = QMediaPlayer()
        self.player.setAudioOutput(self.audio_output)
        self.audio_output.setVolume(0.8)

        self.last_track = None

    def play_random_start_track(self):
        tracks = list(self.tracks_dir.glob("*.mp3"))
        if not tracks:
            print("No tracks found in photon_tracks")
            return

        if len(tracks) > 1:
            available_tracks = [track for track in tracks if track != self.last_track]
            if available_tracks:
                tracks = available_tracks

        chosen = random.choice(tracks)
        self.last_track = chosen

        self.player.setSource(QUrl.fromLocalFile(str(chosen.resolve())))
        self.player.play()
        print(f"Playing: {chosen.name}")

    def stop(self):
        self.player.stop()
