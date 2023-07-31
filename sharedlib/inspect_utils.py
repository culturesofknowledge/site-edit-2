import inspect


def issubclass_safe(target_cls, check_cls):
    if not target_cls or not inspect.isclass(target_cls):
        return False

    return issubclass(target_cls, check_cls)
