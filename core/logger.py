import logging
import traceback
from typing import Optional

from colorama import init as colorama_init, Fore, Style

# 初始化 Windows 控制台颜色支持
colorama_init(autoreset=True)


# 颜色定义
LEVEL_COLORS = {
    logging.DEBUG: Fore.BLUE + Style.BRIGHT,
    logging.INFO: Fore.GREEN + Style.BRIGHT,
    logging.WARNING: Fore.YELLOW + Style.BRIGHT,
    logging.ERROR: Fore.RED + Style.BRIGHT,
    logging.CRITICAL: Fore.MAGENTA + Style.BRIGHT,
}

# 其他部分的配色
TIME_COLOR = Fore.CYAN
NAME_COLOR = Fore.MAGENTA + Style.BRIGHT
RESET = Style.RESET_ALL


class ColorizedFormatter(logging.Formatter):
    """
    彩色日志格式化器 + 浅堆栈
    格式: 时间 [级别] logger名:行号 - 消息
    """

    def __init__(self, fmt: Optional[str] = None, datefmt: Optional[str] = None, max_frames: int = 6):
        fmt = fmt or "%(asctime)s [%(levelname)s] %(name)s:%(lineno)d - %(message)s"
        datefmt = datefmt or "%H:%M:%S"
        super().__init__(fmt=fmt, datefmt=datefmt)
        self.max_frames = max_frames

    def format(self, record: logging.LogRecord) -> str:
        # 着色级别
        level_color = LEVEL_COLORS.get(record.levelno, "")
        record.levelname = f"{level_color}{record.levelname}{RESET}"
        # 着色时间
        record.asctime = f"{TIME_COLOR}{self.formatTime(record, self.datefmt)}{RESET}"
        # 着色 logger 名字和行号
        record.name = f"{NAME_COLOR}{record.name}{RESET}"
        return super().format(record)

    def formatException(self, ei) -> str:
        """
        将异常堆栈裁剪到最后 max_frames 帧，并着色异常类型与消息。
        """
        lines = traceback.format_exception(*ei)
        # 找到 Traceback 标识并保留结尾的 max_frames 帧
        try:
            tb_start = next(i for i, l in enumerate(lines) if l.strip().startswith("Traceback"))
        except StopIteration:
            tb_start = 0

        frames = lines[tb_start + 1 : -1]  # 仅帧，不含最后的异常行
        trimmed = frames[-self.max_frames :] if self.max_frames and len(frames) > self.max_frames else frames
        exc_line = lines[-1].strip()

        colored_exc = f"{Fore.RED}{Style.BRIGHT}{exc_line}{RESET}"
        return "".join(["Traceback (most recent call last):\n", *trimmed, colored_exc])


def setup_logging(level: str = "INFO", max_frames: int = 6) -> None:
    """
    初始化根 logger，应用彩色格式器与浅堆栈。
    """
    root = logging.getLogger()
    root.setLevel(level.upper())

    # 清理已有 console handler，避免重复输出
    root.handlers = [h for h in root.handlers if not isinstance(h, logging.StreamHandler)]

    console = logging.StreamHandler()
    console.setFormatter(ColorizedFormatter(max_frames=max_frames))
    root.addHandler(console)


def get_log_config(level: str = "INFO", max_frames: int = 6) -> dict:
    """
    提供给 uvicorn.run 的 dictConfig，用我们自定义的 formatter。
    """
    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "colorized": {
                "()": "core.logger.ColorizedFormatter",
                "fmt": "%(asctime)s [%(levelname)s] %(name)s:%(lineno)d - %(message)s",
                "datefmt": "%H:%M:%S",
                "max_frames": max_frames,
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "colorized",
                "stream": "ext://sys.stdout",
            },
        },
        "loggers": {
            "uvicorn": {"handlers": ["console"], "level": level.upper(), "propagate": False},
            "uvicorn.error": {"handlers": ["console"], "level": level.upper(), "propagate": False},
            "uvicorn.access": {"handlers": ["console"], "level": level.upper(), "propagate": False},
        },
        "root": {"handlers": ["console"], "level": level.upper()},
    }