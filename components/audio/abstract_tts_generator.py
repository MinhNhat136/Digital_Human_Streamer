from abc import ABC, abstractmethod
from entities.entity_audio import AudioData
from typing import Optional, Dict, Any

class AbstractTTSGenerator(ABC):
    @abstractmethod
    def prepare_inputs_for_model(self, texts) -> Dict[str, Any]:
        pass

    @abstractmethod
    def generate_speech(self, inputs) -> AudioData:
        pass

    @abstractmethod
    def save_audio(self, audio_data: AudioData, format: str = 'wav') -> str:
        pass

    @abstractmethod
    def load_audio(self, audio_path: str) -> AudioData:
        pass

    @abstractmethod
    def delete_audio(self, audio_path: str) -> None:
        pass 

    