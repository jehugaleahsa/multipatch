import sys
version = sys.version_info
if version < (3, 3):
    import contextlib2 as contextlib
else:
    import contextlib


def multipatch(*multipatches, **patches):
    """
    Builds a collection of `mock.patch`es that are managed
    all within the same context.

    Args:
        multipatches: other `multipatch`es to merge with.
        patches: named instances of `mock.patch` to incorporate.
    Returns:
        a context manager that will start/stop the contained patches.
    Raises:
        ValueError: the same name is being used for multiple patches.
    Remarks:
        Another multipatch can be treated like a patch by giving it a name.
        The start and stop functions can be used to manage the context
        manually.
    """
    collection = _PatchCollection()

    # aggregate other multipatchers
    for other in multipatches:
        collection._copyPatches(other)

    # add new patches
    for name in patches:
        patch = patches[name]
        collection._addPatch(name, patch)

    return collection


class _PatchCollection(object):
    def __init__(self):
        self.__patches = []
        self.__mocks = {}
        self.__stack = None

    def _addPatch(self, name, patch):
        if name in self.__mocks:
            format = 'A patch with the same name already exists: {0}.'
            message = format.format(name)
            raise ValueError(message)
        self.__patches.append((name, patch))
        self.__mocks[name] = None

    def _copyPatches(self, other):
        for name, patch in other.__patches:
            self._addPatch(name, patch)

    def start(self):
        if self.__stack is None:
            self.__stack = contextlib.ExitStack()
            for name, patch in self.__patches:
                self.__mocks[name] = self.__stack.enter_context(patch)
        return self

    def stop(self):
        if self.__stack is not None:
            for name in self.__mocks:
                self.__mocks[name] = None
            self.__stack.close()
            self.__stack = None

    def __enter__(self):
        return self.start()

    def __exit__(self, ExceptionType, exception, traceback):
        self.stop()

    def __getattr__(self, name):
        if self.__stack is None or name not in self.__mocks:
            format = 'There was no mock with the given name: {0}'
            message = format.format(name)
            raise AttributeError(message)
        return self.__mocks[name]
