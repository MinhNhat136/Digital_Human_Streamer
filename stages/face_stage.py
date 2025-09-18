import logging

from entities.entity_audio import AudioData
from entities.entity_visual import FaceExpression
from components.visual.abstract_face_generator import AbstractFaceGenerator
from stages.template_node_stage import TemplateNodeStage
from constants.constants_enum import StageStatus, AudioFormat, StageExceptionType
from entities.entity_conversation import StopRequest
from typing import Deque, Dict
from collections import deque
from constants.constants_value import MIN_AUDIO_SIZE, MAX_AUDIO_SIZE
from queue import Queue
import asyncio
from concurrent.futures import ThreadPoolExecutor
import time
logger = logging.getLogger(__name__)


class FaceStage(TemplateNodeStage):
    def __init__(self, face_generator: AbstractFaceGenerator, output_dir: str = None):
        super().__init__()
        self.face_generator = face_generator
        
        self._input_audio_deque: Deque[AudioData] = deque()
        self._stop_deque: Deque[StopRequest] = deque()

        self._output_face_deque: Queue[FaceExpression] = Queue()
        self._exception_deque: Deque[Dict[StageExceptionType, AudioData]] = deque()
        
        self.status = StageStatus.Wait
        self.executor = ThreadPoolExecutor(max_workers=1)

    def add_input_audio_data(self, audio_data: AudioData) -> None:
        exception = self._is_resource_exception(audio_data)
        if exception is not None:
            self._exception_deque.append(exception, audio_data)
            return
        
        self._input_audio_deque.append(audio_data)

    def add_stop_request(self, stop_request: StopRequest) -> None:
        self._stop_deque.append(stop_request)

    def get_face_expression(self) -> FaceExpression:
        if self._output_face_deque.empty():
            return None
        return self._output_face_deque.get()
    
    def get_exception_data(self) -> Dict[StageExceptionType, AudioData]:
        if len(self._exception_deque) == 0:
            return None
        return self._exception_deque[0]

    def notify_exception_data_handled(self) -> None:
        self._exception_deque.popleft()

    def wait(self) -> None:
        if len(self._exception_deque) != 0:
            self.status = StageStatus.Error
            return

        if len(self._input_audio_deque) > 0: 
            self.status = StageStatus.Execute
            return

    def execute(self) -> None:
        if len(self._exception_deque) != 0:
            self.status = StageStatus.Error
            return
        
        if len(self._stop_deque) != 0:
            self.status = StageStatus.Stop
            return

        if len(self._input_audio_deque) == 0:
            self.status = StageStatus.Wait
            return

        try:
            audio_data = self._input_audio_deque.popleft()
            
            def run_async():
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                return loop.run_until_complete(
                    self.face_generator.generate_face_expression(audio_data)
                )
            
            future = self.executor.submit(run_async)
            face_expression = future.result(timeout=30)
            self._output_face_deque.put(face_expression)

            if self._output_dir:
                self.face_generator.save_face_expression(face_expression, format='json', output_dir=self._output_dir)

        except Exception as e:
            logger.error(f"Error in face generation: {e}")
            self._exception_deque.append({StageExceptionType.EXECUTION_FAILED: None})

    def stop(self) -> None:
        if len(self._stop_deque) == 0:
            self.status = StageStatus.Wait
            return
        
    def error(self) -> None:
        if len(self._exception_deque) == 0: 
            self.status = StageStatus.Wait
            return
    
    def loof(self) -> None:
        handler = self.status_handlers.get(self.status, lambda: logging.warning("Unknown status"))
        handler()

    def _is_resource_exception(self, audio_data: AudioData) -> StageExceptionType:
        if not audio_data or not audio_data.data:
            return StageExceptionType.INVALID_DATA_CONTENT
            
        if len(audio_data.data) < MIN_AUDIO_SIZE:
            return StageExceptionType.INVALID_DATA_SIZE

        if len(audio_data.data) > MAX_AUDIO_SIZE:
            return StageExceptionType.INVALID_DATA_SIZE

        if audio_data.format is not AudioFormat.WAV:
            return StageExceptionType.INVALID_DATA_FORMAT

        if audio_data.sample_rate != 16000:
            return StageExceptionType.INVALID_DATA_FORMAT

        if not (0.1 <= audio_data.duration <= 30.0):
            return StageExceptionType.INVALID_DATA_SIZE

        if audio_data.timestamp <= 0:
            return StageExceptionType.INVALID_DATA_CONTENT

        return None
