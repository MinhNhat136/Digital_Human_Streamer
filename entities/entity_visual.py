from dataclasses import dataclass
from typing import List, Dict

@dataclass
class FaceExpression:
    audio_name: str
    blend_shapes: List[List[float]]
    emotion: List[List[float]]
    timestamp: float
    duration: float
    frame_count: int

@dataclass
class MotionData:
    audio_name: str
    poses: List[List[float]]  
    timestamp: float
    duration: float
    frame_count: int
    
@dataclass
class VisualOutput:
    audio_name: str
    face_expressions: FaceExpression
    motion_data: MotionData