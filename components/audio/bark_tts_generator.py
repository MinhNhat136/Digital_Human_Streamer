import time
import torch
import logging
import numpy as np
from typing import Dict, Any, Optional, List
from transformers import AutoProcessor, AutoModel

from entities.entity_audio import AudioData
from components.audio.abstract_tts_generator import AbstractTTSGenerator
from constants.constants_enum import AudioFormat

logger = logging.getLogger(__name__)

class BarkTTSGenerator(AbstractTTSGenerator):    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        
        self.model_name = config.get('model_name', 'suno/bark-small')
        self.voice_preset = config.get('voice_preset', 'v2/en_speaker_9')
        self.device = torch.device(config.get('device', 'cuda' if torch.cuda.is_available() else 'cpu'))
        self.sample_rate = config.get('sample_rate', 24000)
        
        self._init_model()
    
    def _init_model(self) -> None:
        try:
            self.processor = AutoProcessor.from_pretrained(self.model_name)
            self.model = AutoModel.from_pretrained(
                self.model_name,
                dtype=torch.float16
            ).to(self.device).eval()
            
            if torch.cuda.is_available():
                torch.backends.cuda.matmul.allow_tf32 = True
                torch.backends.cudnn.allow_tf32 = True
            
        except Exception as e:
            logger.error(f"Failed to initialize Bark model: {e}")
            raise
    
    def generate_speech(self, inputs) -> AudioData:
        try:
            speech_result = self._inference_model(inputs)
            
            audio_data = AudioData(
                data=speech_result['audio_data'],
                format=AudioFormat.WAV,
                name=f"{int(time.time())}.wav",
                timestamp=time.time(),
                sample_rate=self.sample_rate,
                duration=speech_result['duration'],
            )
            
            return audio_data
            
        except Exception as e:
            logger.error(f"Error generating speech: {e}")
            raise
    
    def prepare_inputs_for_model(self, texts: list[str]) -> Dict[str, Any]:
        inputs = self.processor(
            text=texts,
            voice_preset=self.voice_preset,
        ).to(self.device)
        
        return inputs
    
    def _inference_model(self, inputs) -> Dict[str, Any]:
        try:        
            with torch.inference_mode():
                speech_values = self.model.generate(
                    **inputs,
                    do_sample=True,
                    fine_temperature=0.4,
                    coarse_temperature=0.8,
                    pad_token_id=self.processor.tokenizer.pad_token_id
                )
            
            audio_data = speech_values.cpu().numpy().squeeze()
            duration = len(audio_data) / self.sample_rate
            
            return {
                'audio_data': audio_data,
                'duration': duration
            }
            
        except Exception as e:
            logger.error(f"Error in model inference: {e}")
            raise
    
    def save_audio(self, audio_data: AudioData, format: str = 'wav', output_dir: Optional[str] = None) -> str:
        try:
            import soundfile as sf
            
            output_path = f"{output_dir}/{audio_data.name}" if output_dir else audio_data.name
            sf.write(output_path, audio_data.data, audio_data.sample_rate)
            
            return str(output_path)
            
        except Exception as e:
            logger.error(f"Error saving audio: {e}")
            raise
    
    def load_audio(self, audio_path: str) -> AudioData:
        try:
            import soundfile as sf
            
            audio_data, sample_rate = sf.read(audio_path)
            duration = len(audio_data) / sample_rate
            
            return AudioData(
                name=audio_path.split('/')[-1],
                data=audio_data,
                sample_rate=sample_rate,
                duration=duration,
                text=None
            )
            
        except Exception as e:
            logger.error(f"Error loading audio: {e}")
            raise
    
    def delete_audio(self, audio_path: str) -> None:
        try:
            import os
            if os.path.exists(audio_path):
                os.remove(audio_path)
        except Exception as e:
            logger.error(f"Error deleting audio: {e}")
            raise
