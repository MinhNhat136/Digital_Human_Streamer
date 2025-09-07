import os
import sys

sys.path.append('src')
from logs import logger
import json
from ensure import ensure_annotations
from box import ConfigBox
from pathlib import Path
from typing import Any
from box.exceptions import BoxValueError
import yaml
import joblib


@ensure_annotations
def read_yaml(path_to_yaml: Path) -> ConfigBox:
    """reads yaml file and returns

    Args:
        path_to_yaml (str): path like input

    Raises:
        ValueError: if yaml file is empty
        e: empty file

    Returns:
        ConfigBox: ConfigBox type
    """
    try:
        with open(path_to_yaml) as yaml_file:
            content = yaml.safe_load(yaml_file)
            logger.info(f"yaml file: {path_to_yaml} loaded successfully")
            return ConfigBox(content)
    except BoxValueError:
        raise ValueError("yaml file is empty")
    except Exception as e:
        raise e


@ensure_annotations
def create_directories(path_to_directories: list, verbose=True):
    """create list of directories

    Args:
        path_to_directories (list): list of path of directories
        ignore_log (bool, optional): ignore if multiple dirs is to be created. Defaults to False.
    """
    for path in path_to_directories:
        os.makedirs(path, exist_ok=True)
        if verbose:
            logger.info(f"created directory at: {path}")


@ensure_annotations
def save_json(path: Path, data: dict):
    """save json data

    Args:
        path (Path): path to json file
        data (dict): data to be saved in json file
    """
    with open(path, "w") as f:
        json.dump(data, f, indent=4)

    logger.info(f"json file saved at: {path}")


@ensure_annotations
def load_json(path: Path) -> ConfigBox:
    """load json files data

    Args:
        path (Path): path to json file

    Returns:
        ConfigBox: data as class attributes instead of dict
    """
    with open(path) as f:
        content = json.load(f)

    logger.info(f"json file loaded succesfully from: {path}")
    return ConfigBox(content)


@ensure_annotations
def save_bin(data: Any, path: Path):
    """save binary file

    Args:
        data (Any): data to be saved as binary
        path (Path): path to binary file
    """
    joblib.dump(value=data, filename=path)
    logger.info(f"binary file saved at: {path}")


@ensure_annotations
def load_bin(path: Path) -> Any:
    """load binary data

    Args:
        path (Path): path to binary file

    Returns:
        Any: object stored in the file
    """
    data = joblib.load(path)
    logger.info(f"binary file loaded from: {path}")
    return data


@ensure_annotations
def load_config(config_path: Path = Path("config/config.yaml")):
    """Load configuration từ YAML file và convert sang DigitalHumanConfig entity
    
    Args:
        config_path (Path): đường dẫn đến file config.yaml
        
    Returns:
        DigitalHumanConfig: configuration object
    """
    try:
        from entity.config_entity import (
            DigitalHumanConfig, DataCollectionConfig, DataValidationConfig,
            DataTransformationConfig, DataAnalysisConfig, TarotKnowledgeConfig,
            LLMConfig, RetrievalConfig, MonitoringConfig, ExperimentTrackingConfig,
            DataSourceConfig, CollectionParamsConfig, ValidationRulesConfig,
            QualityMetricsConfig, ProcessingStepConfig, AnalysisTypeConfig,
            VisualizationConfig, ReportsConfig, CardCategoriesConfig,
            InterpretationConfig, SpreadsConfig, GenerationParamsConfig,
            PromptsConfig, VectorDBConfig, RetrievalParamsConfig,
            KnowledgeSourcesConfig, MetricsConfig, PerformanceConfig
        )
        
        # Load raw YAML content
        config_data = read_yaml(config_path)
        
        # Parse data collection config
        data_collection_data = config_data.get("data_collection", {})
        
        # Parse tarot sources
        kaggle_datasets = [
            DataSourceConfig(**ds) for ds in data_collection_data.get("tarot_sources", {}).get("kaggle_datasets", [])
        ]
        huggingface_datasets = [
            DataSourceConfig(**ds) for ds in data_collection_data.get("tarot_sources", {}).get("huggingface_datasets", [])
        ]
        web_scraping = [
            DataSourceConfig(**ds) for ds in data_collection_data.get("tarot_sources", {}).get("web_scraping", [])
        ]
        manual_sources = data_collection_data.get("tarot_sources", {}).get("manual_sources", {})
        collection_params = CollectionParamsConfig(**data_collection_data.get("collection_params", {}))
        
        data_collection = DataCollectionConfig(
            root_dir=data_collection_data.get("root_dir", "artifacts/data_collection"),
            kaggle_datasets=kaggle_datasets,
            huggingface_datasets=huggingface_datasets,
            web_scraping=web_scraping,
            manual_sources=manual_sources,
            collection_params=collection_params
        )
        
        # Parse data validation config
        data_validation_data = config_data.get("data_validation", {})
        validation_rules = ValidationRulesConfig(**data_validation_data.get("validation_rules", {}))
        quality_metrics = QualityMetricsConfig(**data_validation_data.get("quality_metrics", {}))
        
        data_validation = DataValidationConfig(
            root_dir=data_validation_data.get("root_dir", "artifacts/data_validation"),
            validation_rules=validation_rules,
            quality_metrics=quality_metrics,
            status_file=data_validation_data.get("status_file", "artifacts/data_validation/validation_status.txt"),
            quality_report=data_validation_data.get("quality_report", "artifacts/data_validation/quality_report.json"),
            issues_log=data_validation_data.get("issues_log", "artifacts/data_validation/data_issues.log")
        )
        
        # Parse data transformation config
        data_transformation_data = config_data.get("data_transformation", {})
        processing_steps = [
            ProcessingStepConfig(**step) for step in data_transformation_data.get("processing_steps", [])
        ]
        
        data_transformation = DataTransformationConfig(
            root_dir=data_transformation_data.get("root_dir", "artifacts/data_transformation"),
            processing_steps=processing_steps,
            processed_dataset=data_transformation_data.get("processed_dataset", "artifacts/data_transformation/processed_tarot_data.json"),
            embeddings_file=data_transformation_data.get("embeddings_file", "artifacts/data_transformation/tarot_embeddings.pkl"),
            vocabulary_file=data_transformation_data.get("vocabulary_file", "artifacts/data_transformation/tarot_vocabulary.json")
        )
        
        # Parse data analysis config
        data_analysis_data = config_data.get("data_analysis", {})
        analysis_types = data_analysis_data.get("analysis_types", {})
        
        statistical = AnalysisTypeConfig(
            enabled=analysis_types.get("statistical", {}).get("enabled", True),
            metrics=analysis_types.get("statistical", {}).get("metrics", [])
        )
        semantic = AnalysisTypeConfig(
            enabled=analysis_types.get("semantic", {}).get("enabled", True),
            methods=analysis_types.get("semantic", {}).get("methods", [])
        )
        quality = AnalysisTypeConfig(
            enabled=analysis_types.get("quality", {}).get("enabled", True),
            checks=analysis_types.get("quality", {}).get("checks", [])
        )
        
        visualization = VisualizationConfig(**data_analysis_data.get("visualization", {}))
        reports = ReportsConfig(**data_analysis_data.get("reports", {}))
        
        data_analysis = DataAnalysisConfig(
            root_dir=data_analysis_data.get("root_dir", "artifacts/data_analysis"),
            statistical=statistical,
            semantic=semantic,
            quality=quality,
            visualization=visualization,
            reports=reports
        )
        
        # Parse tarot knowledge config
        tarot_knowledge_data = config_data.get("tarot_knowledge", {})
        card_categories = CardCategoriesConfig(**tarot_knowledge_data.get("card_categories", {}))
        interpretation = InterpretationConfig(**tarot_knowledge_data.get("interpretation", {}))
        spreads = SpreadsConfig(**tarot_knowledge_data.get("spreads", {}))
        
        tarot_knowledge = TarotKnowledgeConfig(
            dataset_path=tarot_knowledge_data.get("dataset_path", "datas/tarot_dataset.json"),
            knowledge_base_path=tarot_knowledge_data.get("knowledge_base_path", "knowledges/"),
            card_categories=card_categories,
            interpretation=interpretation,
            spreads=spreads
        )
        
        # Parse LLM config
        llm_config_data = config_data.get("llm_config", {})
        generation_params = GenerationParamsConfig(**llm_config_data.get("generation_params", {}))
        prompts_config = PromptsConfig(**llm_config_data.get("prompts_config", {}))
        
        llm_config = LLMConfig(
            primary_model=llm_config_data.get("primary_model", "gpt-3.5-turbo"),
            backup_model=llm_config_data.get("backup_model", "gpt-4"),
            generation_params=generation_params,
            prompts_config=prompts_config
        )
        
        # Parse retrieval config
        retrieval_config_data = config_data.get("retrieval_config", {})
        vector_db = VectorDBConfig(**retrieval_config_data.get("vector_db", {}))
        retrieval_params = RetrievalParamsConfig(**retrieval_config_data.get("retrieval_params", {}))
        knowledge_sources = KnowledgeSourcesConfig(**retrieval_config_data.get("knowledge_sources", {}))
        
        retrieval_config = RetrievalConfig(
            root_dir=retrieval_config_data.get("root_dir", "artifacts/retrieval"),
            vector_db=vector_db,
            retrieval_params=retrieval_params,
            knowledge_sources=knowledge_sources
        )
        
        # Parse monitoring config
        monitoring_data = config_data.get("monitoring", {})
        metrics = MetricsConfig(**monitoring_data.get("metrics", {}))
        performance = PerformanceConfig(**monitoring_data.get("performance", {}))
        
        monitoring = MonitoringConfig(
            enable_logging=monitoring_data.get("enable_logging", True),
            log_level=monitoring_data.get("log_level", "INFO"),
            log_file=monitoring_data.get("log_file", "logs/digital_human.log"),
            metrics=metrics,
            performance=performance
        )
        
        # Parse experiment tracking config
        experiment_tracking_data = config_data.get("experiment_tracking", {})
        experiment_tracking = ExperimentTrackingConfig(
            enable_mlflow=experiment_tracking_data.get("enable_mlflow", True),
            mlflow_uri=experiment_tracking_data.get("mlflow_uri", "http://localhost:5000"),
            experiment_name=experiment_tracking_data.get("experiment_name", "digital_human_tarot"),
            track_params=experiment_tracking_data.get("track_params", []),
            track_metrics=experiment_tracking_data.get("track_metrics", [])
        )
        
        # Create main config object
        config = DigitalHumanConfig(
            artifacts_root=config_data.get("artifacts_root", "artifacts"),
            logs_root=config_data.get("logs_root", "logs"),
            models_root=config_data.get("models_root", "models"),
            data_collection=data_collection,
            data_validation=data_validation,
            data_transformation=data_transformation,
            data_analysis=data_analysis,
            tarot_knowledge=tarot_knowledge,
            llm_config=llm_config,
            retrieval_config=retrieval_config,
            monitoring=monitoring,
            experiment_tracking=experiment_tracking
        )
        
        logger.info(f"Configuration loaded successfully from: {config_path}")
        return config
        
    except Exception as e:
        logger.error(f"Error loading configuration: {e}")
        raise e