import inspect


def ensure_loaded(fn):
    """Checks that the `_object` of the method's class is fetched before
    perfomign operations on it.

    Args:
        fn: method of `NotionPage` or `NodtionDatabase` or other class
            that has `_object` attribute.
    """
    is_coroutine = inspect.iscoroutinefunction(fn)

    def check_object(obj):
        if obj is None:
            raise Exception(
                f"Can't call {fn} because the object is not loaded."
                "Do object.load() first"
            )

    def sync_wrapper(self, *args, **kwargs):
        check_object(self._object)
        return fn(self, *args, **kwargs)

    async def async_wrapper(self, *args, **kwargs):
        check_object(self._object)
        return await fn(self, *args, **kwargs)

    if is_coroutine:
        return async_wrapper
    else:
        return sync_wrapper
