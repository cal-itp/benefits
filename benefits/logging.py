def get_config(level="INFO", enable_azure=False):
    config = {
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
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "default",
            },
        },
        "root": {
            "handlers": ["console"],
            "level": level,
        },
        "loggers": {
            "django": {
                "handlers": ["console"],
                "propagate": False,
            },
        },
    }

    if enable_azure:
        # enable Azure Insights logging

        # https://docs.microsoft.com/en-us/azure/azure-monitor/app/opencensus-python#configure-logging-for-django-applications
        config["handlers"]["azure"] = {
            "class": "opencensus.ext.azure.log_exporter.AzureLogHandler",
            # send all logs
            "logging_sampling_rate": 1.0,
        }

        # create custom logger
        # https://github.com/census-instrumentation/opencensus-python/issues/1130#issuecomment-1161898856
        config["loggers"]["azure"] = {
            "handlers": ["azure"],
            "level": level,
        }

    return config
