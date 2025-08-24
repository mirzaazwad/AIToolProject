"""
Base logger implementation for the agent system.
"""

import logging
from pathlib import Path


class SingletonMeta(type):
    """Metaclass for implementing singleton pattern."""
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


class BaseLogger(metaclass=SingletonMeta):
    """Base logger class with common functionality and singleton pattern."""

    def __init__(self, name: str, log_file: str, level: str = "INFO"):
        """
        Initialize the base logger.

        Args:
            name: Logger name
            log_file: Log file name (will be created in logs/ directory)
            level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        """

        if hasattr(self, '_initialized'):
            return

        self.name = name
        self.log_file = log_file
        self.level = level
        project_root = Path(__file__).parent.parent.parent.parent
        self.logs_dir = project_root / "logs"
        self.logs_dir.mkdir(exist_ok=True)

        self.logger = self._setup_logger()
        self._initialized = True
    
    def _setup_logger(self) -> logging.Logger:
        """Set up and configure the logger."""
        logger = logging.getLogger(self.name)
        logger.setLevel(getattr(logging, self.level.upper()))
        
        logger.handlers.clear()
        
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        log_path = self.logs_dir / self.log_file
        file_handler = logging.FileHandler(log_path)
        file_handler.setFormatter(formatter)
        file_handler.setLevel(getattr(logging, self.level.upper()))
        logger.addHandler(file_handler)

        logger.propagate = False
        
        return logger
    
    def debug(self, message: str) -> None:
        """Log debug message."""
        self.logger.debug(message)
    
    def info(self, message: str) -> None:
        """Log info message."""
        self.logger.info(message)
    
    def warning(self, message: str) -> None:
        """Log warning message."""
        self.logger.warning(message)
    
    def error(self, message: str) -> None:
        """Log error message."""
        self.logger.error(message)
    
    def critical(self, message: str) -> None:
        """Log critical message."""
        self.logger.critical(message)
