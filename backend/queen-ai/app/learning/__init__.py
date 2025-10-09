"""
Learning Function - Data Collection for Future Model Training

Passively observes and logs interactions for future self-hosted model training.
"""
from app.learning.observer import LearningObserver
from app.learning.bigquery_logger import BigQueryLogger

__all__ = ["LearningObserver", "BigQueryLogger"]
