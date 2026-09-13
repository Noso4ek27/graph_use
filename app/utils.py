import logging
from datetime import datetime

def setup_logging(level = logging.INFO):
    """
    Note:
        Настраивает базовую конфигурацию логирования для всего приложения

    Args:
        level: уровень логированяи (по умолчанию logging.INFO)
    
    """
    logging.basicConfig(
        level=level
        ,format = "[%(asctime)s] [%(levelname)s] [%(name)s] - %(message)s"
        ,datefmt = "%Y-%m-%d %H:%M:%S"
        ,
    )


def get_logger(name: str) -> logging.Logger:
    """
    Notes:
        Создает и возвращает экземпляр логгера с указанным именем.

    Args:
        name: Имя логгера

    Returns:
        logging.Logger: Настроенный объект логгера
    """
    return logging.getLogger(name)


def json_serializer(obj):
    """
    Note:
        Сериализует объект в JSON-совместимый формат.
    Args:
        obj: Объект для сериализации
    Returns:
        str: JSON-совместимое представление объекта
    """
    if isinstance(obj, datetime):
        return obj.isoformat()
    if hasattr(obj, "model_dump"):
        return obj.model_dump()
    return str(obj)


if __name__ == "__main__":
    setup_logging()
    logger = get_logger(__name__)

    logger.info("Init logger.py")