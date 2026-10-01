import logging
from inspect import signature

logger = logging.getLogger(__name__)


class BaseDataClass:

    @classmethod
    def from_kwargs(cls, **kwargs):
        """
        @classmethod for instantiating a dataclass that allows unexpected fields

        See https://stackoverflow.com/a/55101438
        """
        # fetch the constructor's signature
        class_fields = {field for field in signature(cls).parameters}

        # split the kwargs into native ones and new ones
        native_args, new_args = {}, {}
        for name, val in kwargs.items():
            if name in class_fields:
                native_args[name] = val
            else:
                new_args[name] = val

        # use the native ones to create the class ...
        instance = cls(**native_args)

        # ... and log any unexpected args
        for new_name, new_val in new_args.items():
            logger.info(f"Unexpected arg parsing response for {cls}: {new_name} = {new_val}")

        return instance
