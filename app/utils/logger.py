import logging
import sys

# Configure basic logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)

_logger = logging.getLogger("flowforge.ai")

def log_info(msg: str, *args, **kwargs):
    _logger.info(msg, *args, **kwargs)

def log_warning(msg: str, *args, **kwargs):
    _logger.warning(msg, *args, **kwargs)

def log_error(msg: str, *args, **kwargs):
    _logger.error(msg, *args, **kwargs)

def get_logger(name: str):
    return logging.getLogger(f"flowforge.ai.{name}")
