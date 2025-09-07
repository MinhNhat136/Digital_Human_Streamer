from pipeline.template_node_pipeline import TemplateNodePipeline
from pipeline.asr.audio_to_text_pipeline import AudioToTextPipelineV0
from logs import logger


def execute_stage(stage: TemplateNodePipeline):
    try:
        logger.info(f">>>>>> stage {stage.stage} started <<<<<<")
        stage.initiate()
        logger.info(f">>>>>> stage {stage.stage} completed <<<<<<\n\nx==========x")
    except Exception as e:
        logger.exception(e)
        raise e

asr_pipeline = AudioToTextPipelineV0()

pipeline = [asr_pipeline]



for stage in pipeline:
    execute_stage(stage)
