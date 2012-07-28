import mock


def multipatch(*multipatches, **patches):
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
        self.__isStarted = False
        self.__patches = {}
        self.__mocks = {}

    def _addPatch(self, name, patch):
        if name in self.__patches:
            format = 'A patch with the same name already exists: {0}.'
            message = format.format(name)
            raise ValueError(message)
        self.__patches[name] = patch

    def _copyPatches(self, other):
        for name in other.__patches:
            patch = other.__patches[name]
            self._addPatch(name, patch)

    def start(self):
        if not self.__isStarted:
            self.__isStarted = True
            for name in self.__patches:
                patch = self.__patches[name]
                self.__mocks[name] = patch.start()
        return self

    def stop(self):
        if self.__isStarted:
            for name in self.__patches:
                patch = self.__patches[name]
                patch.stop()
            self.__mocks.clear() # not born from a unit test
            self.__isStarted = False

    def __enter__(self):
        return self.start()

    def __exit__(self, ExceptionType, exception, traceback):
        self.stop()

    def __getattr__(self, name):
        if not self.__isStarted or name not in self.__mocks:
            raise AttributeError()
        return self.__mocks[name]
