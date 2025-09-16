import time
from typing import Dict, Any, Optional
import torch
import librosa
import logging
import json
import pandas as pd

from entities.entity_audio import AudioData
from entities.entity_visual import MotionData
from components.visual.abstract_motion_generator import AbstractMotionGenerator
from models.audio2gesture import CamnAudioModel

logger = logging.getLogger(__name__)

class CamnMotionGenerator(AbstractMotionGenerator):    
    def __init__(self, config: Dict[str, Any]):
        self.config = config

        self.pretrained_model_path = config.get('path', 'H-Liu1997/camn_audio')
        self.device = torch.device(config.get('device', 'cuda' if torch.cuda.is_available() else 'cpu'))
        self.pose_fps = config.get('pose_fps', 30)
        self.seed_frames = config.get('seed_frames', 10)
        
        self._init_model()
        
        logger.info(f"MotionGenerator initialized successfully")
    
    def _init_model(self) -> None:
        try:
            self.model = CamnAudioModel.from_pretrained(self.pretrained_model_path).to(self.device)
            self.model.eval()
                        
        except Exception as e:
            logger.error(f"Failed to initialize CAMN model: {e}")
            raise
    
    def generate_motion(self, input_dir: str, audio_data: AudioData, seed_motion: Optional[MotionData] = None) -> MotionData:
        try:
            audio_path = f"{input_dir}/{audio_data.name}"
            motion_result = self._inference_model(audio_path, audio_data.sample_rate, seed_motion)
            poses_result = motion_result['poses'].tolist()
            motion_data_name = audio_data.name.split('.')[0]

            motion_data = MotionData(
                audio_name=motion_data_name,
                poses=poses_result,
                timestamp= time.time(),
                duration= audio_data.duration,
                frame_count= len(poses_result)
                )
                        
            return motion_data
            
        except Exception as e:
            raise e
    
    def _inference_model(self, audio_path: str, audio_sr: int, seed_motion: Optional[MotionData] = None) -> Dict[str, Any]:
        try:
            audio, _ = librosa.load(audio_path, sr=audio_sr)
            audio_tensor = torch.from_numpy(audio).to(self.device).unsqueeze(0)
            speaker_id = torch.zeros(1, 1).long().to(self.device)
            
            if seed_motion is not None:
                seed_motion_tensor = torch.from_numpy(seed_motion.poses).to(self.device).unsqueeze(0)
            else:
                seed_motion_tensor = None
                
            with torch.no_grad():
                motion_pred = self.model(
                    audio_tensor, 
                    speaker_id, 
                    seed_frames=self.seed_frames, 
                    seed_motion=seed_motion_tensor
                )["motion_axis_angle"]
            
            t = motion_pred.shape[1]
            motion_pred = motion_pred.cpu().numpy().reshape(t, -1)
            
            return {
                'poses': motion_pred,
                'duration': t / self.pose_fps,
                'frame_count': t
            }
            
        except Exception as e:
            raise
    
    def save_motion_data(self, motion_data: MotionData, format: str = 'csv', output_dir: str = None) -> str:
        try:
            output_path = f"{output_dir}/{motion_data.audio_name}.{format}"
            
            if format == 'csv':
                df = pd.DataFrame(motion_data.poses)
                df.to_csv(output_path, index=False)
            elif format == 'json':
                data = {
                    'poses': motion_data.poses,
                    'audio_name': motion_data.audio_name,
                    'timestamp': motion_data.timestamp,
                    'duration': motion_data.duration,
                    'frame_count': motion_data.frame_count
                }
                with open(output_path, 'w') as f:
                    json.dump(data, f, indent=2)
            else:
                raise ValueError(f"Unsupported format: {format}")
            
            return str(output_path)
            
        except Exception as e:
            raise

    def load_motion_data(self, motion_data_path: str) -> MotionData:
        pass

    def delete_motion_data(self, motion_data_path: str) -> None:
        pass

    
    