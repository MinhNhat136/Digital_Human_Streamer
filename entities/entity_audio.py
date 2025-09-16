from dataclasses import dataclass
from constants.constants_enum import AudioFormat

@dataclass
class AudioData:
    data: bytes
    format: AudioFormat
    name: str
    timestamp: float
    sample_rate: int
    duration: float
