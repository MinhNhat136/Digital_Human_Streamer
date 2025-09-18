import logging
from typing import Deque, Dict
from collections import deque
from queue import Queue
import time

from entities.entity_audio import AudioData
from components.audio.abstract_tts_generator import AbstractTTSGenerator
from stages.template_node_stage import TemplateNodeStage
from constants.constants_enum import StageStatus, StageExceptionType
from entities.entity_conversation import StopRequest

logger = logging.getLogger(__name__)

class TTSStage(TemplateNodeStage):
    def __init__(self, tts_generator: AbstractTTSGenerator, output_dir: str = None):
        super().__init__()
        self.tts_generator = tts_generator
        self._output_dir = output_dir
        
        self._input_text_deque: Deque[str] = deque()
        self._stop_deque: Deque[StopRequest] = deque()

        self._input_handled_deque = deque()
        
        self._output_audio_deque: Queue[AudioData] = Queue()
        self._exception_deque: Deque[Dict[StageExceptionType, str]] = deque()
        
        self.status = StageStatus.Wait
        self.last_time_generate = 0

    def add_input_text(self, text: str) -> None:
        if not text or len(text.strip()) == 0:
            self._exception_deque.append({StageExceptionType.INVALID_DATA_CONTENT: text})
            return
        
        self._input_text_deque.append(text)

    def add_stop_request(self, stop_request: StopRequest) -> None:
        self._stop_deque.append(stop_request)

    def get_audio_data(self) -> AudioData:
        if self._output_audio_deque.empty():
            return None
        return self._output_audio_deque.get()
    
    def get_exception_data(self) -> Dict[StageExceptionType, str]:
        if len(self._exception_deque) == 0:
            return None
        return self._exception_deque[0]

    def notify_exception_data_handled(self) -> None:
        self._exception_deque.popleft()

    def wait(self) -> None:
        if len(self._exception_deque) != 0:
            self.status = StageStatus.Error
            return
    
        if len(self._input_handled_deque) > 0: 
            self.status = StageStatus.Execute
            return

    def execute(self) -> None:
        if len(self._exception_deque) != 0:
            self.status = StageStatus.Error
            return
        
        if len(self._stop_deque) != 0:
            self.status = StageStatus.Stop
            return

        if len(self._input_handled_deque) == 0:
            self.status = StageStatus.Wait
            return

        try:
            input_handled = self._input_handled_deque.popleft()

            audio_data = self.tts_generator.generate_speech(input_handled)
            
            if self._output_dir:
                self.tts_generator.save_audio(audio_data, format='wav', output_dir=self._output_dir)
            
            self._output_audio_deque.put(audio_data)
        except Exception as e:
            logger.error(f"Error in TTS generation: {e}")
            self._exception_deque.append({StageExceptionType.STAGE_EXECUTE_FAILED: None})

    def stop(self) -> None:
        if len(self._stop_deque) == 0:
            self.status = StageStatus.Wait
            return
        
        # Clear all queues
        self._input_text_deque.clear()
        while not self._output_audio_deque.empty():
            self._output_audio_deque.get()
        
        self.last_time_generate = time.time()

    def error(self) -> None:
        if len(self._exception_deque) == 0: 
            self.status = StageStatus.Wait
            return
        
        self.last_time_generate = time.time()
    
    def loof(self) -> None:
        if len(self._input_text_deque) > 0:
            handled_text = self.tts_generator.prepare_inputs_for_model([self._input_text_deque.popleft()])
            self._input_handled_deque.append(handled_text)
        
        handler = self.status_handlers.get(self.status, lambda: logging.warning("Unknown status"))
        handler()
