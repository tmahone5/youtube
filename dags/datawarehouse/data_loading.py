import json
from datetime import date
import logging

logger = logging.getLogger(__name__)

# Load JSON data from the daily YouTube data file
def load_path():
    # Build path to today’s data file
    file_path = f'./data/YT_data_{date.today()}.json'

    try:
        logger.info(f'Processing file: YT_data_{date.today()}')

        with open(file_path, 'r', encoding='utf-8') as raw_data:
            data = json.load(raw_data)

   

        return data
    
    except FileNotFoundError:
        logger.error(f'File not found:{file_path}')
        raise
    except json.JSONDecodeError:
        logger.error(f'Invalid JSON')
        raise