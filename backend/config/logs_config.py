import logging

# Configuración básica del logger
def setup_logger():
    # Crear el logger
    logger = logging.getLogger("zap_logger")
    logger.setLevel(logging.INFO)

    # Crear un manejador de archivo que escribe los logs en un archivo
    file_handler = logging.FileHandler('zap_scan.log')
    file_handler.setLevel(logging.INFO)

    # Crear un formato para los logs
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)

    # Agregar el manejador al logger
    logger.addHandler(file_handler)

    return logger
