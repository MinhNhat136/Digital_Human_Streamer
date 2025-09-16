from abc import ABC, abstractmethod
from entities.entity_audio import AudioData
from entities.entity_visual import FaceExpression
from typing import Iterator, Optional, Dict, Any

class AbstractFaceGenerator(ABC):    
    @abstractmethod
    def generate_face_expression(self, audio_data: AudioData, seed_expression: Optional[FaceExpression] = None) -> FaceExpression:
        """Generate face expression for single audio data."""
        pass

    @abstractmethod
    def save_face_expression(self, face_expression: FaceExpression, format: str = 'json') -> str:
        """Save face expression data to file."""
        pass

    @abstractmethod
    def load_face_expression(self, face_expression_path: str) -> FaceExpression:
        """Load face expression data from file."""
        pass

    @abstractmethod
    def delete_face_expression(self, face_expression_path: str) -> None:
        """Delete face expression data from file."""
        pass
