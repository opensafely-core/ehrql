import logging
import logging.config
import os
import textwrap


# It's not great that our logging utilities need to know about how the logs get
# formatted, but this makes a big difference to the readability of the logs.
LOG_INDENT = " " * 10


class EHRQLFormatter(logging.Formatter):
    def format(self, record):
        record.levelname_lower = record.levelname.lower()
        return logging.Formatter.format(self, record)


CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "formatter": {
            "()": EHRQLFormatter,
            "format": "[{levelname_lower:<7}] {message}",
            "datefmt": "%Y-%m-%d %H:%M:%S",
            "style": "{",
        }
    },
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "formatter",
        }
    },
    "root": {
        "handlers": ["console"],
        "level": os.getenv("LOG_LEVEL", "CRITICAL"),
    },
    "loggers": {
        "sqlalchemy.engine": {
            "level": "INFO" if os.getenv("LOG_SQL") else "WARN",
        },
    },
}


def init_logging():
    logging.config.dictConfig(CONFIG)


def kv(kv_pairs):
    """Generate a string of kv pairs in space separated k=v format."""
    return " ".join("{}={}".format(k, v) for k, v in kv_pairs.items())


def indent(s, prefix=LOG_INDENT):
    """
    Indent subsequent lines so they align correctly given the length of the log line
    prefix
    """
    first_line, sep, rest = s.partition("\n")
    return first_line + sep + textwrap.indent(rest, prefix)
