import os
import logging
import stages_backbone
from omegaconf import OmegaConf
import time
from stages.tts_stage import TTSStage
from stages.face_stage import FaceStage
from stages.motion_stage import MotionStage

from components.audio.bark_tts_generator import BarkTTSGenerator
from components.visual.nvidia_face_generator import NvidiaFaceGenerator
from components.visual.camn_motion_generator import CamnMotionGenerator

def load_config():
    config = OmegaConf.load('configs/config_path.yml')
    return config

def initialize_components(config):
    tts_generator = BarkTTSGenerator({})
    face_generator = NvidiaFaceGenerator({})
    motion_generator = CamnMotionGenerator({})
    
    return tts_generator, face_generator, motion_generator

def initialize_stages(config, tts_generator, face_generator, motion_generator):
    tts_stage = TTSStage(
        tts_generator=tts_generator,
        output_dir=config.text_to_speech.output_dir
    )
    
    face_stage = FaceStage(
        face_generator=face_generator,
        output_dir=config.audio_to_face.output_dir
    )
    
    motion_stage = MotionStage(
        motion_generator=motion_generator,
        input_dir=config.audio_to_gesture.output_dir,
        output_dir=config.audio_to_gesture.output_dir
    )
    
    return tts_stage, face_stage, motion_stage

# Initialize everything
config = load_config()
tts_generator, face_generator, motion_generator = initialize_components(config)
tts_stage, face_stage, motion_stage = initialize_stages(
    config,
    tts_generator,
    face_generator,
    motion_generator
)

# Setup stage backbone
stage_backbone = stages_backbone.StageBackbone()
stage_backbone.add_stage(tts_stage)
stage_backbone.add_stage(face_stage)
stage_backbone.add_stage(motion_stage)


if __name__ == "__main__":
    while True:
        stage_backbone.loop_stage()
        print("looping")
        time.sleep(2)

    
    

