import logging
from pathlib import Path
import copy
import re
import yaml

def load_logging_yaml():
    with open(str(Path(__file__).parent / "log_maker_config.yml")) as stream:
        settings = yaml.safe_load(stream)
    # Enforce all lower case by repeating the dict all lower case.
    return {key.lower(): value for key, value in settings.items()}

class ColoredFormatter(logging.Formatter):
    LOG_FORMAT = "%(asctime)s | %(levelname)8s | %(message)s | %(name)s :: %(filename)s:%(lineno)d"

    RESET = "\033[0m"
    MAGENTA = "\033[35m"
    CYAN = "\033[96m"
    BRACKET_PATTERN = re.compile(
        r"\[((?!96m)[^\]]+)\]"
    )  # ignore cyan coloring for log messages
    COLORS = {
        logging.DEBUG: "\033[38;20m",  # Grey
        logging.INFO: "\033[0;32m",  # Green
        logging.WARNING: "\033[33;20m",  # Yellow
        logging.ERROR: "\033[31;20m",  # Red
        logging.CRITICAL: "\033[31;1m",  # Bold red
    }

    def __init__(self):
        super().__init__()

        self._formatters = {
            level: logging.Formatter(f"{color}{self.LOG_FORMAT}{self.RESET}")
            for level, color in self.COLORS.items()
        }

        self._default_formatter = logging.Formatter(self.LOG_FORMAT)

    def format(self, record):
        # Don't modify the original LogRecord
        copy_record = copy.copy(record)
        level_color = self.COLORS.get(copy_record.levelno, "")
        # Color the whole message cyan
        msg = rf"{self.CYAN}{copy_record.msg:<75}{self.RESET}{level_color}"

        # Then override bracket contents to magenta
        copy_record.msg = self.BRACKET_PATTERN.sub(
            rf"[{self.MAGENTA}\1{self.RESET}{level_color}{self.CYAN}]",
            msg,
        )
        formatter = self._formatters.get(
            copy_record.levelno,
            self._default_formatter,
        )
        return formatter.format(copy_record)

g_log_cfg = load_logging_yaml()
# "global" logger name of an application.
g_logger_name = None


def get_logger(
    name: str = None,
    level: int = None,
    log_file: str | Path | None = None,
) -> logging.Logger:
    """Gets an existing logger or makes a new one by name.

    :param str name: name of logger, defaults to None
    :param int level: logging level, defaults to None (set by yaml file or default to debug if can't use yaml)
    :param str | Path | None log_file: path of logging text file., defaults to None
    :return logging.Logger: logging object
    """
    global g_log_cfg
    global g_logger_name
    if name is None:
        if g_logger_name is not None:
            # No name given, use default one.
            logger = logging.getLogger(g_logger_name)
        else:
            # not name and no default name, so just make one.
            logger = logging.getLogger(__name__)
    else:
        logger = logging.getLogger(name)
        if g_logger_name is None:
            # Store a default logger name by the first logger that trips this (usually the main.py logger)
            g_logger_name = name

    if level is not None:
        # Set level by supplied input
        logger.setLevel(level)
    else:
        # no supplied input try to set logger by yaml file, if can't just make it debug.
        if logger.name.lower() in g_log_cfg.keys():
            logger.setLevel(logging.getLevelNamesMapping().get(g_log_cfg[logger.name.lower()].upper(), logging.DEBUG))
        else:
            logger.setLevel(logging.DEBUG)
    logger.propagate = False

    # Add console handler only once
    if not any(
        isinstance(h, logging.StreamHandler) and not isinstance(h, logging.FileHandler)
        for h in logger.handlers
    ):
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(ColoredFormatter())
        logger.addHandler(console_handler)

    # Optionally add a file handler
    if log_file is not None:
        log_file = Path(log_file)

        # Create parent directory if necessary
        log_file.parent.mkdir(parents=True, exist_ok=True)

        # Don't add the same file twice
        if not any(
            isinstance(h, logging.FileHandler)
            and Path(h.baseFilename) == log_file.resolve()
            for h in logger.handlers
        ):
            file_handler = logging.FileHandler(log_file, encoding="utf-8")
            file_handler.setFormatter(logging.Formatter(ColoredFormatter.LOG_FORMAT))
            logger.addHandler(file_handler)

    return logger
