import copy
from event_model import DocumentRouter, RunRouter


class Selector(DocumentRouter):
    def __init__(self, exclude=None, **kwargs):
        self._exclude = exclude or []
        super().__init__(**kwargs)

    def start(self, doc):
        print('---start')
        self.emit('start', doc)

    def descriptor(self, doc):
        print('---descriptor')
        edited = copy.deepcopy(doc)
        for key in self._exclude:
            edited['data_keys'].pop(key, None)
        self.emit('descriptor', edited)

    def event(self, doc):
        print('---event')
        edited = copy.deepcopy(doc)
        for key in self._exclude:
            edited['data'].pop(key, None)
            edited['timestamps'].pop(key, None)
        print(self.emit)
        print(edited)
        self.emit('event', edited)
    
    def stop(self, doc):
        print('---stop')
        self.emit('stop', doc)

# Test

from suitcase.tiff_series import Serializer


# def factory1(name, doc):
#     "This is expected to write TIFFs."
#     serializer = Serializer('test_without_selector')
#     return [serializer], []

    
def factory2(name, doc):
    "This is expected to write TIFFs."
    serializer = Serializer('test_with_selector')
    selector = Selector(exclude=None, emit=serializer)

    selector._stashed_hard_ref_to_serializer = serializer
    return [selector], []


import databroker
from ophyd.sim import img
from bluesky import RunEngine
from bluesky.plans import count

rr = RunRouter([factory2], databroker.core.discover_handlers())
RE = RunEngine()
RE.subscribe(rr)
RE(count([img]))

# Now the directory test_without_selector contains TIFFs. The directory test_without_selector isn't even created.