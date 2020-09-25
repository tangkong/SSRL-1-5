"""
live_export.py

Set up callback to live export data as they are collected.  
"""

from ..framework.initialize import RE, callback_db

import copy

import suitcase.tiff_series as st
import suitcase.csv as sc
import suitcase.json_metadata as sj

from event_model import RunRouter, DocumentRouter
from event_model import Filler
from databroker.core import discover_handlers

__all__ = ['csv_rr', 'tiff_rr', 'meta_rr']
hands = discover_handlers()
hands.pop("XSP3")

def csv_factory(name, start_doc):
    serializer = sc.Serializer( 
        '/home/b_spec/export/csv/', file_prefix='Scan{start[scan_id]}-' )

    def cb(name, doc):
        f(name,doc)
        serializer(name, doc) 

    return [cb], []

csv_rr = RunRouter([csv_factory])

#callback_db['csv_rr'] = RE.subscribe(csv_rr)

class Selector(DocumentRouter):
    def __init__(self, exclude=None, **kwargs):
        self._exclude = exclude or []
        super().__init__(**kwargs)

    def start(self, doc):
        #print('---start')
        self.emit('start', doc)

    def descriptor(self, doc):
        #print('---desc')
        edited = copy.deepcopy(dict(doc))
        for key in self._exclude:
            edited['data_keys'].pop(key, None)
        self.emit('descriptor', edited)

    def event(self, doc):
        #print('---event')
        #print(doc)
        edited = copy.deepcopy(dict(doc))
        for key in self._exclude:
            edited['data'].pop(key, None)
            edited['timestamps'].pop(key, None)
            edited.get('filled', {}).pop(key, None)
        #print('---event: emitting to serializer')
        self.emit('event', edited)

    def resource(self, doc):
        self.emit('resource', doc)

    def datum(self, doc):
        self.emit('datum', doc)

    def stop(self, doc):
        self.emit('stop', doc)

def tiff_factory(name, start_doc):
    serializer = st.Serializer( 
        '/home/b_spec/export/tiff/', file_prefix='Scan{start[scan_id]}-')

    f = Filler(hands)
    #serializer('start', start_doc)
    def cb(name, doc):
        name_, doc_, = f(name, doc)
        serializer(name_, doc_)

    selector = Selector(exclude=['xsp3_channel1', 'xsp3_channel2'], 
                        emit=cb)
    
    selector._stashed_hard_ref_to_serializer = serializer
    selector._stashed_hard_ref_to_filler = f 
    selector._stashed_hard_ref_to_cb = cb
    return [selector], []

assert 'AD_TIFF' in hands
tiff_rr = RunRouter([tiff_factory])

callback_db['tiff_rr'] = RE.subscribe(tiff_rr)

def meta_factory(name, start_doc):
    serializer = sj.Serializer( 
        '/home/b_spec/export/meta/', file_prefix='Scan{start[scan_id]}-' )

    def cb(name, doc):
        serializer(name, doc) 

    return [cb], []

meta_rr = RunRouter([meta_factory])

callback_db['meta_rr'] = RE.subscribe(meta_rr)