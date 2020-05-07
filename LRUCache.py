from collections import OrderedDict


class LRUCache:
    dictCache = None
    maxSize = None

    def __init__(self, maxSize=1):
        self.dictCache = OrderedDict()
        self.maxSize = maxSize

    def __getitem__(self, key):
        # check if item is in the dict
        if key in self.dictCache:
            retVal = self.dictCache[key]
            self.dictCache.move_to_end(key)
            return retVal
        else:
            return None

    def __setitem__(self, key, value):
        if key in self.dictCache:
               self.dictCache.__getitem__(key)
        self.dictCache.__setitem__(key, value)
        if len(self.dictCache) > self.maxSize:
            last = next(iter(self.dictCache))
            del self.dictCache[last]
