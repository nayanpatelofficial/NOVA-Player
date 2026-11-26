from dataclasses import dataclass

@dataclass
class PlaybackState:
    media: str | None = None
    position: float = 0.0
    paused: bool = False
    volume: int = 70
    subtitle: str | None = None
    subtitle_offset: float = 0.0

def handoff(state, target):
    """Return a complete snapshot for an independent target player instance."""
    return PlaybackState(state.media, max(0.0, state.position), state.paused, state.volume,
                         state.subtitle, state.subtitle_offset)
