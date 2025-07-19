"""
通用日志记录器配置模块
使用方式：
from common.logger import get_logger
logger = get_logger(__name__)
"""
import os
import logging
from logging.handlers import RotatingFileHandler

from config.config import LOG_ROOT


def get_logger(
        name: str,
        log_dir: str = LOG_ROOT,
        log_file: str = None,
        level: int = logging.INFO,
        console: bool = True,
        file: bool = True,
        max_bytes: int = 10 * 1024 * 1024,
        backup_count: int = 5,
        fmt: str = "[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s",
        datefmt: str = "%Y-%m-%d %H:%M:%S"
) -> logging.Logger:
    """
    获取并配置一个 Logger 实例。

    参数:
        name (str): Logger 名称，通常传入 __name__。
        log_dir (str): 日志文件所在目录，默认为项目根下的 "logs" 目录。
        log_file (str): 日志文件名，默认使用 "{name}.log"。若指定了完整路径，则直接使用该路径。
        level (int): 日志级别，默认为 INFO。
        console (bool): 是否输出到控制台，默认开启。
        file (bool): 是否输出到文件，默认开启。
        max_bytes (int): 单个日志文件的最大大小（字节），超过后会滚动，默认 10MB。
        backup_count (int): 保留的备份文件数量，默认 5。
        fmt (str): 日志输出格式，默认 "[时间] [级别] [名称]: 内容"。
        datefmt (str): 时间格式，默认 "%Y-%m-%d %H:%M:%S"。

    返回:
        logging.Logger: 配置好的 Logger 对象。
    """

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.propagate = False  # 避免重复输出

    # 如果已经添加过 Handler，就直接返回（保证多次调用不会重复添加处理器）
    if logger.handlers:
        return logger

    formatter = logging.Formatter(fmt=fmt, datefmt=datefmt)

    # 控制台 Handler
    if console:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    # 文件 Handler（滚动文件）
    if file:
        # 如果没指定 log_file，则使用 name + ".log"
        if not log_file:
            log_filename = f"{name}.log"
        else:
            log_filename = log_file

        # 如果传入的是相对路径或不包含目录，则放到 log_dir 中
        if not os.path.isabs(log_filename) or os.path.dirname(log_filename) == "":
            # 确保日志目录存在
            os.makedirs(log_dir, exist_ok=True)
            log_filepath = os.path.join(log_dir, log_filename)
        else:
            # 传入了绝对路径，直接使用
            log_filepath = log_filename
            os.makedirs(os.path.dirname(log_filepath), exist_ok=True)

        file_handler = RotatingFileHandler(
            filename=log_filepath,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding="utf-8"
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger
