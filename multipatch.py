import mock


def patch(target=''):
    collection = PatchCollection()
    collection = collection.patch(target)
    return collection

class PatchCollection(object):

    def __init__(self):
        self.__isPatched = False
        self.__patches = {}
        self.__patchers = {}

    def patch(self, target):
        # ignore blank targets
        if not target.strip():
            return self

        # blow up on duplicate names

        name = self.__getName(target)

        newCollection = PatchCollection()
        newCollection.__patches = self.__patches.copy()
        newCollection.__patches[name] = mock.patch(target)
        return newCollection

    def __getName(self, target):
        name = target
        index = name.rfind('.')
        if index != -1:
            name = name[(index + 1):]
        return name

    def start(self):
        if not self.__isPatched:
            self.__isPatched = True
            for name in self.__patches:
                patch = self.__patches[name]
                patcher = patch.start()
                self.__patchers[name] = patcher

    @property
    def isStarted(self):
        return self.__isPatched

    def stop(self):
        if self.__isPatched:
            for name in self.__patches:
                patch = self.__patches[name]
                patch.stop()
            self.__patchers.clear()
            self.__isPatched = False

    def __enter__(self):
        self.start()
        return self
    
    def __exit__(self, ExceptionType, exception, traceback):
        self.stop()

    def __getattr__(self, name):
        if not self.__isPatched or name not in self.__patchers:
            return super(PatchCollection, self).__getattr__()
        patcher = self.__patchers[name]
        return patcher
