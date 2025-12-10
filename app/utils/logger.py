import logging
import sys
import traceback
from logging.handlers import RotatingFileHandler
from typing import Optional

from colorama import Fore, Style, init

init(autoreset=True)
from app.core import settings

class ColoredFormatter(logging.Formatter):
    COLORS = {
        'DEBUG': Fore.CYAN,
        'INFO': Fore.GREEN,
        'WARNING': Fore.YELLOW,
        'ERROR': Fore.RED,
        'CRITICAL': Fore.MAGENTA + Style.BRIGHT,
    }

    def __init__(self, fmt: Optional[str] = None, datefmt: Optional[str] = None, style='%'):
        effective_fmt = fmt or settings.log.format
        effective_datefmt = datefmt or settings.log.date_format
        super().__init__(fmt=effective_fmt, datefmt=effective_datefmt, style=style)

    def format(self, record):
        # ... (此部分与之前相同，用于处理常规日志的颜色) ...
        original_exc_info = record.exc_info
        original_exc_text = record.exc_text

        if record.exc_info and settings.log.exceptions:
            record.exc_text = self.formatException(record.exc_info)

        log_message = super().format(record)
        
        record.exc_info = original_exc_info
        record.exc_text = original_exc_text

        level_color = self.COLORS.get(record.levelname, '')
        colored_level = f"{level_color}{record.levelname}{Style.RESET_ALL}"

        # 优化：只在格式字符串中包含行号时，才尝试替换它
        # 这使得同一个 Formatter 可以处理带和不带行号的格式
        if self._fmt and "%(lineno)d" in self._fmt:
            colored_module_line = f"{Fore.BLUE}{record.name}:{record.lineno}{Style.RESET_ALL}"
            # 使用更精确的替换，避免误伤
            placeholder = f"{record.name}:{record.lineno}"
            if placeholder in log_message:
                log_message = log_message.replace(placeholder, colored_module_line, 1)
        log_message = log_message.replace(record.levelname, colored_level, 1)
        
        return log_message

    def formatException(self, ei) -> str:
        """
        格式化异常堆栈，并根据配置限制其深度。
        """
        if not settings.log.exceptions or settings.log.stack_trace_level <= 0:
            # 如果不记录异常或层级为0，则只记录异常类型和消息
            return "".join(traceback.format_exception_only(ei[0], ei[1]))

        tb = ei[2]
        extracted_list = []
        # traceback.walk_tb 从内到外遍历堆栈
        for frame, line_no in traceback.walk_tb(tb):
            if len(extracted_list) >= settings.log.stack_trace_level:
                break
            extracted_list.append((frame.f_code.co_filename, line_no, frame.f_code.co_name, 'line'))
        
        # 反转列表以获得从外到内的正确顺序
        extracted_list.reverse()

        # 格式化堆栈和异常信息
        formatted_stack = traceback.format_list(extracted_list)
        formatted_exception = traceback.format_exception_only(ei[0], ei[1])
        full_trace = "".join(formatted_stack) + "".join(formatted_exception)

        # 为整个堆栈信息添加颜色
        colored_full_trace = "".join([f"{Fore.RED}{line}{Style.RESET_ALL}" for line in full_trace])
        
        return colored_full_trace

def setup_logging():
    """
    根据配置设置全局日志处理器，并强制禁用 Uvicorn 的访问日志。
    """
    root_logger = logging.getLogger()
    root_logger.setLevel(settings.log.level.upper())
    root_logger.handlers.clear()

    # --- 控制台处理器 ---
    if settings.log.handler in ["console", "both"]:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(settings.log.level.upper())
        console_formatter = ColoredFormatter()
        console_handler.setFormatter(console_formatter)
        root_logger.addHandler(console_handler)

    # --- 文件处理器 ---
    if settings.log.handler in ["file", "both"]:
        file_handler = RotatingFileHandler(
            str(settings.log.file_path),
            maxBytes=settings.log.file_max_size_mb * 1024 * 1024,
            backupCount=settings.log.file_backup_count,
            encoding='utf-8'
        )
        file_handler.setLevel(settings.log.level.upper())
        file_formatter = logging.Formatter(fmt=settings.log.format, datefmt=settings.log.date_format)
        file_handler.setFormatter(file_formatter)
        root_logger.addHandler(file_handler)

    # # --- 应用第三方库日志级别覆盖 ---
    # for logger_name, level_name in settings.log.override_loggers.items():
    #     logging.getLogger(logger_name).setLevel(level_name.upper())

    # ==============================================================================
    # === 强制管理 Uvicorn 日志 ===
    # ==============================================================================
    # 1. 彻底禁用 uvicorn.error 日志
    uvicorn_error_logger = logging.getLogger("uvicorn.error")
    uvicorn_error_logger.handlers.clear()
    uvicorn_error_logger.propagate = False
    # 设置一个极高的级别，作为双重保险
    uvicorn_error_logger.setLevel(logging.CRITICAL + 1)

    # 2. 静默 uvicorn 根 logger
    # 这可以捕获一些未被 uvicorn.error 处理的杂项日志。
    # uvicorn_logger = logging.getLogger("uvicorn")
    # uvicorn_logger.handlers.clear()
    # uvicorn_logger.propagate = False
    # uvicorn_logger.setLevel(logging.CRITICAL + 1)
    
    # 1. 阻止sqlalchemy日志传播到根 logger，消除重复输出
    sqlalchemy_logger = logging.getLogger("sqlalchemy.engine")
    sqlalchemy_logger.propagate = False

def get_logger(name: Optional[str] = None) -> logging.Logger:
    return logging.getLogger(name)

def cleanup_logging():
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        handler.close()
        root_logger.removeHandler(handler)