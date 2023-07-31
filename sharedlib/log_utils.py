import logging
import re


class ColorCodes:
    grey = '\u001b[38;5;250m'
    black = '\u001b[38;5;232m'
    bg_blue = '\u001b[44m'
    bg_yellow = '\u001b[43m'
    bg_red = '\u001b[41m'
    bg_purple = '\u001b[45m'
    reset = "\u001b[0m"


class ColorFormatter(logging.Formatter):
    level_to_color = {
        logging.DEBUG: ColorCodes.grey,
        logging.INFO: f'{ColorCodes.bg_blue}{ColorCodes.black}',
        logging.WARNING: f'{ColorCodes.bg_yellow}{ColorCodes.black}',
        logging.ERROR: f'{ColorCodes.bg_red}{ColorCodes.black}',
        logging.CRITICAL: f'{ColorCodes.bg_purple}{ColorCodes.black}',
    }

    def __init__(self, fmt, *args, **kwargs):
        super().__init__(fmt, *args, **kwargs)
        self.fmt = fmt

    def format(self, record):
        lv_color = self.level_to_color[record.levelno]

        new_fmt = re.sub(r"(%\((levelname|levelno)\).*?s)", f"{lv_color}\\1{ColorCodes.reset}", self.fmt)
        formatter = logging.Formatter(new_fmt, datefmt=self.datefmt)

        formatted = formatter.format(record)
        return formatted


detailed_web_fmt = '%(asctime)s %(levelname).4s [\x1b[1;32m%(threadName)s\x1b[0m] - %(message)s \t\x1b[1;36m--- [%(name)s--%(module)s.%(funcName)s:%(lineno)d]\x1b[0m'
detailed_web_formatter = ColorFormatter(detailed_web_fmt, '%Y%m%d %H%M%S')


