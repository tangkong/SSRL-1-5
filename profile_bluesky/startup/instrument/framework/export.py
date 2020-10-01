'''
Batch export functions (csv summaries, primarily)

Since csv doesn't work live.
'''

from itertools import tee
import suitcase.csv as sc
import suitcase.tiff_series as ts
import suitcase.csv

from databroker import Broker

def std_exporter(docs, directory):
    '''
    Batch exporter for data.  

    docs: documents from a Bluesky Run.  

    directory: Parent directory where exported files will be written to.
                Files will be further separated into subdirectories
    '''

    docs1, docs2, docs3 = tee(docs, 3)
    suitcase.csv.export(docs1, directory, 'scan/Scan{start[scan_id]}-')
    suitcase.tiff_series.export(docs2, directory, 'tiff/Scan{start[scan_id]}-')
    suitcase.json_metadata.export(docs3, directory, 'meta/Scan{start[scan_id]}-')

def my_exporter(db, query, parent_directory):
    '''
    Batch exports data, given a database and a query


    Example queries:
    
    my_exporter(db, 'plan_name="scan"', 'export/')
    my_exporter(db, 'motor="s_stage.pz"', 'export/')


    '''
    try:
        for hdr in db(query):
            print(f'-- exporting hdr: {hdr.start["scan_id"]}')
            std_exporter()

    except Exception as e:
        print('Query was ')
        print(e)