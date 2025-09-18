import logging

from entities.entity_audio import AudioData
from entities.entity_visual import MotionData
from components.visual.abstract_motion_generator import AbstractMotionGenerator
from stages.template_node_stage import TemplateNodeStage
from constants.constants_enum import StageStatus, AudioFormat, StageExceptionType
from entities.entity_conversation import StopRequest
from typing import Deque, Dict
from collections import deque
from constants.constants_value import MIN_AUDIO_SIZE, MAX_AUDIO_SIZE
from queue import Queue
import time

logger = logging.getLogger(__name__)


class MotionStage(TemplateNodeStage):
    def __init__(self, motion_generator: AbstractMotionGenerator, input_dir, output_dir):
        super().__init__()
        self.motion_generator = motion_generator
        self._input_dir = input_dir
        self._output_dir = output_dir
        
        self._input_audio_deque: Deque[AudioData] = deque()
        self._stop_deque: Deque[StopRequest] = deque()

        self._output_motion_deque: Queue[MotionData] = Queue()
        self._exception_deque: Deque[(StageExceptionType, AudioData)] = deque()
        
        self.status = StageStatus.Wait
        self.seed_motion = None
        self.last_time_generate = 0
    
    def add_input_audio_data(self, audio_data: AudioData) -> None:
        exception = self._is_resource_exception(audio_data)
        if exception is not None:
            self._exception_deque.append((exception, audio_data))
            return
        
        self._input_audio_deque.append(audio_data)

    def add_stop_request(self, stop_request: StopRequest) -> None:
        self._stop_deque.append(stop_request)

    def get_motion_data(self) -> MotionData:
        if self._output_motion_deque.empty():
            return None
        return self._output_motion_deque.popleft()
    
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
        
        if time.time() - self.last_time_generate > 10:
            self.seed_motion = None


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
            motion_data = self.motion_generator.generate_motion(audio_data=audio_data, seed_motion=self.seed_motion)
            
            if self._output_dir is not None:
                self.motion_generator.save_motion_data(motion_data=motion_data, format='csv', output_dir=self._output_dir)
            
            self._output_motion_deque.put(motion_data)
            self.seed_motion = motion_data
            self.last_time_generate = time.time()

        except Exception as e:
            self._exception_deque.append((StageExceptionType.STAGE_EXECUTE_FAILED, None))
            print("execute exception", e)

    def stop(self) -> None:
        if len(self._stop_deque) == 0:
            self.status = StageStatus.Wait
            return
        
        self.last_time_generate = time.time()

    def error(self) -> None:
        if len(self._exception_deque) == 0: 
            self.status = StageStatus.Wait
            return
        
        self.last_time_generate = time.time()
    
    def loof(self) -> None:
        handler = self.status_handlers.get(self.status, lambda: logging.warning("Unknown status"))
        handler()

    def _is_resource_exception(self, audio_data: AudioData):
        # if not audio_data or not audio_data.data:
        #     return StageExceptionType.INVALID_DATA_CONTENT
            
        # if len(audio_data.data) < MIN_AUDIO_SIZE:
        #     return StageExceptionType.INVALID_DATA_SIZE

        # if len(audio_data.data) > MAX_AUDIO_SIZE:
        #     return StageExceptionType.INVALID_DATA_SIZE

        # if audio_data.format is not AudioFormat.WAV:
        #     return StageExceptionType.INVALID_DATA_FORMAT

        # if audio_data.sample_rate is not 16000:
        #     return StageExceptionType.INVALID_DATA_FORMAT

        # if not (0.1 <= audio_data.duration <= 30.0):
        #     return StageExceptionType.INVALID_DATA_SIZE

        # if audio_data.timestamp <= 0:
        #     return StageExceptionType.INVALID_DATA_CONTENT

        return None