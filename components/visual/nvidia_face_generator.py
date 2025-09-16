import time
import logging
import numpy
from typing import Dict, Any, Optional

from entities.entity_audio import AudioData
from entities.entity_visual import FaceExpression
from components.visual.abstract_face_generator import AbstractFaceGenerator
from models.audio2face.scripts.audio2face_api_client.a2f.client import service
import asyncio
from nvidia_ace.services.a2f_controller.v1_pb2_grpc import A2FControllerServiceStub
from models.audio2face.scripts.audio2face_api_client.a2f.client import auth

logger = logging.getLogger(__name__)

class NvidiaFaceGenerator(AbstractFaceGenerator):
    """Audio2Face generator using NVIDIA Audio2Face API."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        
        self.api_key = config.get('api_key', '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')
        self.function_id = config.get('function_id', '0961a6da-fb9e-4f2e-8491-247e5fd7bf8d')
        self.face_config_path = config.get('face_config_path', 'configs/config_face/config_claire.yml')
        
        logger.info(f"Audio2FaceGenerator initialized successfully")
    
    async def generate_face_expression(self, audio_data: AudioData) -> FaceExpression:
        """Generate face expression for single audio data."""
        try:
            face_result = await self._inference_model(audio_data)
            
            frame_count_result = len(face_result['animation_data'])
            audio_name_result = audio_data.name.split('.')[0]

            face_expression = FaceExpression(
                audio_name=audio_name_result,
                blend_shapes=face_result['animation_data'],
                emotion=face_result['emotion_data'],
                timestamp=time.time(),
                duration=audio_data.duration,
                frame_count= frame_count_result
            )
            
            return face_expression
            
        except Exception as e:
            logger.error(f"Error generating face expression: {e}")
            raise
    
    async def _inference_model(self, audio_data: AudioData) -> Dict[str, Any]:
        metadata_args = [("function-id", self.function_id), ("authorization", "Bearer " + self.api_key)]
        channel = auth.create_channel(uri="grpc.nvcf.nvidia.com:443", use_ssl=True, metadata=metadata_args)
                
        stub = A2FControllerServiceStub(channel)

        audio_np = numpy.frombuffer(audio_data.data, dtype=numpy.int16)

        stream = stub.ProcessAudioStream()
        write = asyncio.create_task(service.write_to_stream_with_data(stream, self.face_config_path, audio_np, audio_data.sample_rate))
        read = asyncio.create_task(service.read_stream_data_only(stream))

        await write
        return await read
   
    
    def save_face_expression(self, face_expression: FaceExpression, format: str = 'json') -> str:
        pass

    def load_face_expression(self, face_expression_path: str) -> FaceExpression:
        """Load face expression data from file."""
        return self.load_seed_expression(face_expression_path)
    
    def delete_face_expression(self, face_expression_path: str) -> None:
        """Delete face expression data from file."""
        pass

