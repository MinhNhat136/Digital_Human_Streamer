from abc import ABC, abstractmethod
from entities.entity_audio import AudioData
from entities.entity_visual import MotionData
from typing import Optional

class AbstractMotionGenerator(ABC):
    @abstractmethod
    def generate_motion(self, audio_data: AudioData, seed_motion: Optional[MotionData] = None) -> MotionData:
        pass

    @abstractmethod
    def save_motion_data(self, motion_data: MotionData, format: str = 'csv') -> str:
        pass

    @abstractmethod
    def load_motion_data(self, motion_data_path: str) -> MotionData:
        pass

    @abstractmethod
    def delete_motion_data(self, motion_data_path: str) -> None:
        pass