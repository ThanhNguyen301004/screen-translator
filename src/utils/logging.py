# src/utils/logging.py
import logging
import os

LOG_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'logs', 'app.log')

def setup_logging():
    if not os.path.exists(os.path.dirname(LOG_PATH)):
        os.makedirs(os.path.dirname(LOG_PATH))
    logging.basicConfig(filename=LOG_PATH, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

logger = logging.getLogger(__name__)