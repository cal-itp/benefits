def get_config(level):
    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": "[{asctime}] {levelname} {name}:{lineno} {message}",
                "datefmt": "%d/%b/%Y %H:%M:%S",
                "style": "{",
            },
        },
        "handlers": {
            "default": {
                "class": "logging.StreamHandler",
                "formatter": "default",
            },
        },
        "root": {
            "handlers": ["default"],
            "level": level,
        },
        "loggers": {
            "django": {
                "handlers": ["default"],
                "propagate": False,
            },
        },
    }
