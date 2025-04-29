import logging
import os

# Basic logger setup
def setup_logger():
    # Create the .logs directory if it doesn't exist
    log_dir = ".logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # Create the log file inside the .logs directory
    log_file = os.path.join(log_dir, 'zap_scan.log')

    # Create the logger
    logger = logging.getLogger("zap_logger")
    logger.setLevel(logging.INFO)

    # Create a file handler that writes the logs to the file
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.INFO)

    # Create a format for the logs
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)

    # Add the handler to the logger
    logger.addHandler(file_handler)

    return logger
