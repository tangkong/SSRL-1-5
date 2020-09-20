"""
live_export.py

Set up callback to live export data as they are collected.  
"""

from ..framework.initialize import RE, callback_db

from itertools import tee

import suitcase.tiff_series as st
import suitcase.csv as sc
import suitcase.json_metadata as sj

from event_model import RunRouter
from databroker.core import discover_handlers

__all__ = ['csv_rr', 'tiff_rr', 'meta_rr']

def csv_factory(name, start_doc):
    serializer = sc.Serializer( 
        '/home/b_spec/export/csv/', file_prefix='Scan{start[scan_id]}-' )

    def cb(name, doc):
        serializer(name, doc) 

    return [cb], []

csv_rr = RunRouter([csv_factory])

callback_db['csv_rr'] = RE.subscribe(csv_rr)

def tiff_factory(name, start_doc):
    serializer = st.Serializer( 
        '/home/b_spec/export/tiff/', file_prefix='Scan{start[scan_id]}-' )

    def cb(name, doc):
        serializer(name, doc) 

    return [cb], []

tiff_rr = RunRouter([tiff_factory], discover_handlers())

callback_db['tiff_rr'] = RE.subscribe(tiff_rr)


def meta_factory(name, start_doc):
    serializer = sj.Serializer( 
        '/home/b_spec/export/meta/', file_prefix='Scan{start[scan_id]}-' )

    def cb(name, doc):
        serializer(name, doc) 

    return [cb], []

meta_rr = RunRouter([meta_factory])

callback_db['meta_rr'] = RE.subscribe(meta_rr)