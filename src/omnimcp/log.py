import logging
import sys


class ColorFormatter(logging.Formatter):
    """Formatter with ANSI colors for terminal output."""

    COLORS = {
        'DEBUG': '\033[36m',     # Cyan
        'INFO': '\033[32m',      # Green
        'WARNING': '\033[33m',   # Yellow
        'ERROR': '\033[31m',     # Red
        'CRITICAL': '\033[35m',  # Magenta
    }
    RESET = '\033[0m'

    def format(self, record):
        color = self.COLORS.get(record.levelname, self.RESET)
        record.levelname = f"{color}{record.levelname}{self.RESET}"
        return super().format(record)


handler = logging.StreamHandler(sys.stderr)
handler.setFormatter(ColorFormatter('%(asctime)s │ %(levelname)-17s │ %(message)s', datefmt='%H:%M:%S'))

logger = logging.getLogger('omnimcp')
logger.setLevel(logging.INFO)
logger.addHandler(handler)
logger.propagate = False

logging.getLogger('httpx').setLevel(logging.WARNING)


