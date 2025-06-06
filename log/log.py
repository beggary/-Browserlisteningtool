import logging
from datetime import datetime
from logging.handlers import RotatingFileHandler

def setup_logger(name: str) -> logging.Logger:
    save_time = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
    log_name = f"{name}{save_time}.log"

    # 创建 Logger 实例
    logger = logging.getLogger(log_name)
    logger.setLevel(logging.INFO)
    logger.propagate = False

    if not logger.handlers:
        # 创建滚动文件处理器
        handler = RotatingFileHandler(
            filename=log_name,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=1000,
            encoding='utf-8'
        )

        # 设置格式
        formatter = logging.Formatter(
            # 方法调用 必须按这个str写法
            fmt="%(asctime)s [%(levelname)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        handler.setFormatter(formatter)

        # 添加 handler 到 logger
        logger.addHandler(handler)

    return logger
