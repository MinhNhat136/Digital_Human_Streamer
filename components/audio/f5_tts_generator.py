import logging
import requests
import time
from typing import Dict, Any, Optional
import json
import os

from entities.entity_audio import AudioData
from constants.constants_enum import AudioFormat

logger = logging.getLogger(__name__)

class F5TTSGenerator:
    """Text-to-Speech generator using F5 TTS API."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        
        # Load config
        self.api_key = config.get('api_key')
        self.api_url = config.get('api_url', 'https://api.f5.com/v1/tts')
        self.voice_id = config.get('voice_id', 'default')
        self.output_format = config.get('output_format', 'wav')
        self.sample_rate = config.get('sample_rate', 16000)
        
        # Validate config
        if not self.api_key:
            raise ValueError("API key is required")
            
        logger.info(f"F5TTSGenerator initialized with voice_id: {self.voice_id}")

    def generate_speech(self, text: str, voice_config: Optional[Dict[str, Any]] = None) -> AudioData:
        """Generate speech from text using F5 TTS API.
        
        Args:
            text: Text to convert to speech
            voice_config: Optional voice configuration to override defaults
            
        Returns:
            AudioData object containing the generated audio
        """
        try:
            # Prepare request
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            # Merge voice configs
            voice_params = {
                'voice_id': self.voice_id,
                'output_format': self.output_format,
                'sample_rate': self.sample_rate
            }
            if voice_config:
                voice_params.update(voice_config)
                
            data = {
                'text': text,
                'voice_params': voice_params
            }
            
            # Make API call
            response = requests.post(
                self.api_url,
                headers=headers,
                json=data
            )
            response.raise_for_status()
            
            # Get audio data
            audio_bytes = response.content
            
            # Create AudioData object
            audio_data = AudioData(
                data=audio_bytes,
                format=AudioFormat.WAV,
                name=f"tts_{int(time.time())}.wav",
                timestamp=time.time(),
                sample_rate=self.sample_rate,
                duration=len(audio_bytes) / (self.sample_rate * 2)  # 16-bit audio = 2 bytes per sample
            )
            
            return audio_data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            raise
        except Exception as e:
            logger.error(f"Error generating speech: {e}")
            raise
            
    def save_audio(self, audio_data: AudioData, output_path: str) -> str:
        """Save audio data to file.
        
        Args:
            audio_data: AudioData object to save
            output_path: Directory to save the file in
            
        Returns:
            Path to saved file
        """
        try:
            os.makedirs(output_path, exist_ok=True)
            file_path = os.path.join(output_path, audio_data.name)
            
            with open(file_path, 'wb') as f:
                f.write(audio_data.data)
                
            logger.info(f"Audio saved to {file_path}")
            return file_path
            
        except Exception as e:
            logger.error(f"Error saving audio: {e}")
            raise
            
    def load_audio(self, file_path: str) -> AudioData:
        """Load audio data from file.
        
        Args:
            file_path: Path to audio file
            
        Returns:
            AudioData object
        """
        try:
            with open(file_path, 'rb') as f:
                audio_bytes = f.read()
                
            # Get filename and creation time
            filename = os.path.basename(file_path)
            creation_time = os.path.getctime(file_path)
            
            # Create AudioData object
            audio_data = AudioData(
                data=audio_bytes,
                format=AudioFormat.WAV,
                name=filename,
                timestamp=creation_time,
                sample_rate=self.sample_rate,
                duration=len(audio_bytes) / (self.sample_rate * 2)
            )
            
            return audio_data
            
        except Exception as e:
            logger.error(f"Error loading audio: {e}")
            raise
            
    def set_voice(self, voice_id: str) -> None:
        """Change the voice ID.
        
        Args:
            voice_id: New voice ID to use
        """
        self.voice_id = voice_id
        logger.info(f"Voice changed to {voice_id}")
        
    def get_available_voices(self) -> Dict[str, Any]:
        """Get list of available voices from F5 API.
        
        Returns:
            Dictionary containing voice information
        """
        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}'
            }
            
            response = requests.get(
                f"{self.api_url}/voices",
                headers=headers
            )
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            logger.error(f"Error getting voices: {e}")
            raise
