import logging
import termcolor
from . import info

_logger = None


class ColoredFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord):
        color = {
            logging.DEBUG: 'white',
            logging.INFO: 'green',
            logging.WARNING: 'yellow',
            logging.ERROR: 'red',
            logging.CRITICAL: 'red',
        }[record.levelno]
        return termcolor.colored(f"[{record.name}] {record.levelname}: {record.msg}", color)


def get_logger():
    global _logger
    if _logger:
        return _logger
    else:
        _logger = logging.getLogger(info.name)
        _logger.setLevel(logging.DEBUG)

        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        ch.setFormatter(ColoredFormatter())

        _logger.addHandler(ch)
        return _logger
