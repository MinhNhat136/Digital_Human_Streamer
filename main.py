import stages_backbone
from stages.motion_stage import MotionStage
from components.visual.camn_motion_generator import CamnMotionGenerator


motion_generator = CamnMotionGenerator()
motion_stage = MotionStage()

stage_backbone = stages_backbone.StageBackbone()
stage_backbone.add_stage(motion_stage)

is_execute = False

if __name__ == "__main__":

    stage_backbone.initiate_all_stages()
    stage_backbone.start_all_stages()
    stage_backbone.execute_all_stages()

    while True:
        stage_backbone.loop_all_stages()

        if is_execute:
            stage_backbone.execute_all_stages()
    

