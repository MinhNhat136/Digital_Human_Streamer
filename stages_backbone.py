from stages.template_node_stage import TemplateNodeStage

class StageBackbone:
    def __init__(self):
        self.stages = []
        
    def add_stage(self, stage: TemplateNodeStage):
        self.stages.append(stage)
        
    def loop_stage(self):
        for stage in self.stages:
            stage.loof()
    
    def remove_stage(self, stage: TemplateNodeStage):
        self.stages.remove(stage)
    

      
