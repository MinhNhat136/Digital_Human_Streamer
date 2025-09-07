from pipeline.template_node_pipeline import TemplateNodePipeline
import time

class AudioToTextPipelineV0(TemplateNodePipeline):
    def __init__(self):
        self.audio_buffer = bytearray()
        self.collected_audio = bytearray()
        self.is_speaking = False
        self.last_activity_time = time.time()
        self.is_paused = False  

    def initiate(self):
        pass

    def update(self):
        pass

    def stop(self):
        pass




