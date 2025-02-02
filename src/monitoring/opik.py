# import json
# import os
# import random
# import tempfile
# from pathlib import Path

# from tqdm import tqdm

# from core.config import settings
# from core.logger_utils import get_logger

# logger = get_logger(__name__)

# try:
#     import opik
#     from comet_ml import Experiment
#     from opik.configurator.configure import OpikConfigurator
# except:
#     logger.info("Could not import Opik and Comet.")


# def configure_opik() -> None:
#     if settings.COMET_API_KEY and settings.COMET_PROJECT:
#         if settings.COMET_WORKSPACE:
#             default_workspace = settings.COMET_WORKSPACE
#         else:
#             try:
#                 client = OpikConfigurator(api_key=settings.COMET_API_KEY)
#                 default_workspace = client._get_default_workspace()
#             except Exception:
#                 logger.warning(
#                     "Default workspace not found. Setting workspace to None and enabling interactive mode."
#                 )
#                 default_workspace = None

#         os.environ["OPIK_PROJECT_NAME"] = settings.COMET_PROJECT

#         opik.configure(
#             api_key=settings.COMET_API_KEY,
#             workspace=default_workspace,
#             use_local=False,
#             force=True,
#         )
#         logger.info("Opik configured successfully.")
#     else:
#         logger.warning(
#             "COMET_API_KEY and COMET_PROJECT are not set. Set them to enable prompt monitoring with Opik (powered by Comet ML)."
#         )


# def create_dataset_from_artifacts(
#     dataset_name: str, artifact_names: list[str]
# ) -> opik.Dataset | None:
#     client = opik.Opik()
#     try:
#         dataset = client.get_dataset(name=dataset_name)
#     except Exception:
#         dataset = None

#     if dataset:
#         logger.warning(
#             f"Dataset '{dataset_name}' already exists. Skipping dataset creation."
#         )

#         return dataset

#     experiment = Experiment(
#         workspace=settings.COMET_WORKSPACE,
#         project_name=settings.COMET_PROJECT,
#         api_key=settings.COMET_API_KEY,
#     )
#     dataset_items = []
#     with tempfile.TemporaryDirectory() as tmp_dir:
#         for artifact_name in tqdm(artifact_names):
#             artifact_dir = Path(tmp_dir) / artifact_name
#             try:
#                 logged_artifact = experiment.get_artifact(artifact_name)
#                 logged_artifact.download(str(artifact_dir))
#                 logger.info(
#                     f"Successfully downloaded  '{artifact_name}' at location '{tmp_dir}'"
#                 )
#             except Exception as e:
#                 logger.error(f"Error retrieving artifact: {str(e)}")

#                 continue

#             testing_artifact_file = list(artifact_dir.glob("*_testing.json"))
#             assert (
#                 len(testing_artifact_file) == 1
#             ), "Expected exactly one testing artifact file."
#             testing_artifact_file = testing_artifact_file[0]

#             logger.info(f"Loading testing data from: {testing_artifact_file}")
#             with open(testing_artifact_file, "r") as file:
#                 items = json.load(file)

#             enhanced_items = [
#                 {**item, "artifact_name": artifact_name} for item in items
#             ]
#             dataset_items.extend(enhanced_items)
#     experiment.end()

#     if len(dataset_items) == 0:
#         logger.warning("No items found in the artifacts. Dataset creation skipped.")

#         return None

#     dataset = create_dataset(
#         name=dataset_name,
#         description="Dataset created from artifacts",
#         items=dataset_items,
#     )

#     return dataset


# def create_dataset(name: str, description: str, items: list[dict]) -> opik.Dataset:
#     client = opik.Opik()

#     dataset = client.get_or_create_dataset(name=name, description=description)
#     dataset.insert(items)

#     dataset = client.get_dataset(name=name)

#     return dataset


# def add_to_dataset_with_sampling(item: dict, dataset_name: str) -> bool:
#     if "1" in random.choices(["0", "1"], weights=[0.3, 0.7]):
#         client = opik.Opik()
#         dataset = client.get_or_create_dataset(name=dataset_name)
#         dataset.insert([item])

#         return True

#     return False

import json
import time
from typing import Any, Dict, Optional

from comet_ml import Experiment
from fastapi import FastAPI, Request
from fastapi.responses import Response
from loguru import logger

from src.entity.config_ent import MonitoringConfig

class LLMMonitoring:
    def __init__(self, config: MonitoringConfig):
        self.experiment = Experiment(
            api_key=config.comet_api_key,
            project_name=config.comet_project,
            workspace=config.comet_workspace
        )
        self.experiment.set_name("noob-busts-scams-monitoring")
        
    def log_llm_request(
        self,
        prompt: str,
        completion: str,
        model: str,
        tokens: Dict[str, int],
        duration: float,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Log LLM request details"""
        try:
            # Log prompt and completion
            self.experiment.log_text(prompt, "prompt")
            self.experiment.log_text(completion, "completion")
            
            # Log model details
            self.experiment.log_parameter("model", model)
            self.experiment.log_parameter("prompt_tokens", tokens.get("prompt_tokens", 0))
            self.experiment.log_parameter("completion_tokens", tokens.get("completion_tokens", 0))
            self.experiment.log_parameter("total_tokens", tokens.get("total_tokens", 0))
            
            # Log performance metrics
            self.experiment.log_metric("response_time", duration)
            
            # Log additional metadata
            if metadata:
                self.experiment.log_parameters(metadata)
                
        except Exception as e:
            logger.error(f"Failed to log LLM request: {str(e)}")

    def log_search(self, phone_number: str, results_count: int):
        """Log search operations"""
        try:
            self.experiment.log_parameter("search_query", phone_number)
            self.experiment.log_metric("results_count", results_count)
            self.experiment.log_metric("search_timestamp", time.time())
        except Exception as e:
            logger.error(f"Failed to log search: {str(e)}")

    def log_user_activity(self, user_id: str, action: str, metadata: Optional[Dict[str, Any]] = None):
        """Log user activities"""
        try:
            self.experiment.log_parameter("user_id", user_id)
            self.experiment.log_parameter("action", action)
            self.experiment.log_metric("activity_timestamp", time.time())
            
            if metadata:
                self.experiment.log_parameters(metadata)
        except Exception as e:
            logger.error(f"Failed to log user activity: {str(e)}")

# Create global monitoring instance
_monitor: Optional[LLMMonitoring] = None

def get_monitor(config: MonitoringConfig) -> LLMMonitoring:
    """Get or create monitoring instance"""
    global _monitor
    if _monitor is None:
        _monitor = LLMMonitoring(config)
    return _monitor

def setup_monitoring(app: FastAPI, config: MonitoringConfig) -> None:
    """Setup monitoring middleware for FastAPI"""
    if not config.enable_monitoring:
        logger.info("Monitoring is disabled")
        return
        
    monitor = get_monitor(config)
    
    @app.middleware("http")
    async def monitoring_middleware(request: Request, call_next) -> Response:
        start_time = time.time()
        
        body = None
        if request.method in ["POST", "PUT"]:
            try:
                body = await request.json()
            except:
                pass
                
        response = await call_next(request)
        
        try:
            duration = time.time() - start_time
            
            monitor.experiment.log_parameter("endpoint", str(request.url))
            monitor.experiment.log_parameter("method", request.method)
            monitor.experiment.log_metric("response_time", duration)
            monitor.experiment.log_metric("status_code", response.status_code)
            
            if body:
                monitor.experiment.log_text(json.dumps(body), "request_body")
                
        except Exception as e:
            logger.error(f"Failed to log request: {str(e)}")
            
        return response

# Convenience functions for external use
def log_search(phone_number: str, results_count: int):
    """Convenience function to log searches"""
    if _monitor:
        _monitor.log_search(phone_number, results_count)

def log_user_activity(user_id: str, action: str, metadata: Optional[Dict[str, Any]] = None):
    """Convenience function to log user activities"""
    if _monitor:
        _monitor.log_user_activity(user_id, action, metadata)