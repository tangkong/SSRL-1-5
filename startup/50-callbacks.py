from bluesky.callbacks import CallbackBase
from bluesky.callbacks.broker import LiveImage

import time

import os
import os.path

import uuid

import yaml

import threading

from PIL import Image

##################
# Taken from NSLS-II-PDF for now
####################
print('-------------------50-callbacks.py startup file')
class SoftLinkCallBack(CallbackBase):
    ''' Create data soft links.

        This callback creates softlinks of your data.
    '''
    def __init__(self, db, data_keys, data_info_keys=None, root='/SHARE/user_data'):
        '''
            db : the database to read from
            data_keys : data keys to create soft links for
            data_info_keys : data that you want to save into filename
        '''
        self.db = db
        self.start_uid = None
        self.start_doc = None
        self.descriptors = dict()
        self.data_keys = data_keys
        self.data_info_keys = data_info_keys
        self.root = root
        if data_info_keys is None:
            data_info_keys=[ 
                ('start', 'Proposal ID')
                ('start', 'sample_name')
                ('start', 'wavelength')
                ('event', 'data', 'Det_1_Z')
            ]
        self.data_info_keys = data_info_keys


    def start(self, doc):
        self.start_doc = doc 
        self.start_uid = doc['uid']

    def descriptor(self, doc):
        self.descriptors[doc['uid']] = dict(doc)

    def event(self, doc):
        data_dict = doc['data'] 
        descriptor_uid = doc['descriptor']

        docs = dict(start=self.start_doc,
                    descriptor=self.descriptors[descriptor_uid],
                    event=doc)
        root = self.root
        prefix = root + "/"

        stream_name = self.descriptors[descriptor_uid]['name']
        
        # print("Got name : {}".format(stream_name))
        # print("data dict : {}".format(data_dict))
        for data_key in self.data_keys:
            # print("looking for {}".format(data_key))
            if data_key in data_dict:
                datum_id = data_dict[data_key]
                file_list = get_file_list(datum_id, db)
                for filepath in file_list:
                    suffix = os.path.splitext(filepath)[1]
                    src = filepath
                    dst = filename_from_info(docs, self.data_info_keys, prefix, suffix=suffix)
                    num, dst = check_name_collision(dst)
                    # TODO : Add these
                    dirname = os.path.dirname(dst)
                    os.makedirs(dirname, exist_ok=True)
                    os.symlink(src, dst)
                    prefix, ext = os.path.splitext(dst)
                    dst_md = prefix + ".txt"  
                    yaml.dump(self.start_doc, open(dst_md, "w"), default_flow_style=False)
                    print("Soft linking {} to {}".format(src, dst))
                    print("Writing metadata to {}".format(dst_md))

    def stop(self, doc):
        ''' clear the start data.'''
        self.start_uid = None
        self.start_doc = None
        self.descriptors = dict()


def check_name_collision(dst):
    ''' takes a filename and appends extra sequence number 
        if exists. Keeps looping until it reaches a non-existing seq number.

        assumes an extension present and removes

        Just to avoid collisions.
    '''
    prefix, suffix = os.path.splitext(dst)

    # checking file existence
    num = 0
    if os.path.isfile(prefix+suffix):
        collision = True
        while(collision):
            new_dst = prefix + "." + str(num) + "." + suffix
            collision = os.path.isfile(new_dst)
            # print("check_name_collision: collision")
            num += 1 
        dst = new_dst

    return num, dst


def filename_from_info(docs, data_info_keys, prefix, suffix):
    '''
        from docs (dict of start, descriptor and event docs)
            create a filename according to data_info_keys template

        data_info_keys=[ 
            ('start', 'sample_name')
            ('start', 'wavelength')
            ('event', 'data', 'Det_1_Z')
        ]

        filename_from_info(docs, data_info_keys, root, ".tiff")
    '''
    filename = ""
    first = True
    for key in data_info_keys:
        if isinstance(key, str):
            filename = filename + key
            first = True
        else: 
            # print("key {} ".format(key))
            # root
            node = docs
            # walk down to key
            for subkey in key:
                # print("subkey : {}".format(subkey))
                if subkey not in node:
                    node = "NULL"
                    break
                node = node[subkey] 
    
            #filename = f"{filename}_{node}"
            if not first:
                node = "_" + str(node)
            else:
                node = str(node)
                first = False
            filename = filename + node

    #filename = f"{prefix}{filename}{suffix}"
    filename = prefix + filename + suffix

    return filename
   
class DarkSubCallback(LiveImage):
    '''Try extending Live image.  Take dark array and live plot subtracted plot
    Live image is broken????
    '''

    def __init__(self, dark_arr, *args, **kwargs):
        self.dark = dark_arr
        super().__init__(*args, **kwargs)

    def event(self, doc):
        super().event(doc)
        data = doc['data'][self.field] - self.dark
        # this will break horribly if you don't be nice
        self.update(data)

class DarkSubtractionCallback(CallbackBase):
    def __init__(self, cbs, image_key="dexela_image", primary_stream="primary",
                 dark_stream="dark", db=None, root='/SHARE/user_data',
                 data_info_keys=[], suffix=".tiff"):
        '''
            Initializes a dark subtraction callback

            This will perform dark subtraction and then save to file.

            cb : callbacks to send result to
            primary_stream : the primary stream name
            dark_stream : the dark stream name
`           db : a Broker instance

            
        '''
        # the names of the primary and dark streams
        if db is None:
            raise ValueError("Error, Broker instance (db) is required. Got None")
        self.pstream = primary_stream
        self.dstream = dark_stream
        self._outputs = cbs
        self.image_key = image_key
        self.data_info_keys = data_info_keys
        self.suffix = suffix
        self.root = root
        self.clear()


    def start(self, doc):
        self.start_doc = doc 
        self.start_uid = doc['uid']

    def descriptor(self, doc):
        ''' stash the up and down stream descriptors'''
        if doc['name'] in [self.pstream, self.dstream]:
            self.descriptors[doc['uid']] = doc


    def event(self, doc):
        data_dict = doc['data'] 
        descriptor_uid = doc['descriptor']
        
        #added by DO to fix crash where streams not relevant to xpdac exist (like baseline)
        try:
            stream_name = self.descriptors[descriptor_uid]['name'] #original line
        except KeyError:
            #print ('tacos')
            return None

        # check it's a prim or dark stream and the key matches the image key
        # desired
        if (stream_name in [self.pstream, self.dstream] and
            self.image_key in doc['data']):
            event_filled = list(db.fill_events([doc], [self.descriptors[descriptor_uid]]))[0]
           
            self.images[stream_name] = event_filled['data'][self.image_key].astype(np.int32)

            # now check if there is an entry in both
            # TODO : Allow for multiple images
            if self.pstream in self.images and self.dstream in self.images:
                dsub_image = self.images[self.pstream] - self.images[self.dstream]
                self.clear_images()
                # print("Sending images to callbacks")
                # print(dsub_image)
                docs = dict()
                docs['start'] = self.start_doc
                docs['descriptor'] = self.descriptors[descriptor_uid].copy()
                # fix to get real stream name in
                docs['descriptor']['name'] = 'bgsub'
                docs['event'] = doc
                prefix = self.root + "/"
                suffix = "_bgsub.tiff"
                filepath = filename_from_info(docs, self.data_info_keys, prefix, suffix)
                im = Image.fromarray(dsub_image.astype(np.int32))

                # make sure dir exists
                dirname = os.path.dirname(filepath)
                os.makedirs(dirname, exist_ok=True)

                im.save(filepath)
                prefix, ext = os.path.splitext(filepath)
                dst_md = prefix + ".txt"  
                yaml.dump(self.start_doc, open(dst_md, "w"), default_flow_style=False)
                # print("Filepath: {}".format(filepath))
                #for nds in self.create_docs(dsub_image):
                    #for cb in self.cbs:
                        #cb(nds)

    def save_to_file(self, filename, data):
        # TODO : play with mode
        im = Image.fromarray(data, mode="I;16")
        im.save(filename)
 
    def create_docs(self, data):
        '''        
            Custom doc creation script for bg subbed image.
            Outputs only one image for now.
        '''        
        start_doc = self.start_doc.copy()
        start_doc['uid'] = str(uuid.uuid4())
        start_doc['time'] = time.time()
        yield ('start', start)
        old_desc = self.descriptors[self.pstream]
        new_desc = dict()
        new_desc['data_keys'] = dict()
        new_desc['data_keys'][self.image_key] = \
            old_desc['data_keys'][self.image_key].copy()
        new_desc['name'] = 'bgsub' 
        new_desc['run_start'] = start_doc['uid']
        new_desc['time'] = time.time()
        new_desc['uid'] = str(uuid.uuid4())
        new_desc['timestamps'] = {self.image_key: time.time}
        yield ('descriptor', new_desc)
        new_event = dict()
        new_event['data'] = {self.image_key: data}
        new_event['descriptor'] = new_desc['uid']
        # always one event for now
        new_event['seq_num'] = 1
        new_event['time'] = time.time()
        new_event['timestamps'] = {self.image_key : time.time()}
        new_event['uid'] = str(uuid.uuid4())
        yield ('event', new_event)
        new_stop = dict()
        new_stop['uid'] = str(uuid.uuid4())
        new_stop['exit_status'] = 'success'
        new_stop['num_events'] = {'bgsub' : 1}
        new_stop['run_start'] = start_doc['uid']
        new_stop['time'] = time.time()
        yield ('stop', new_stop)

                    
    def clear_images(self):
        self.images = dict()


    def stop(self, doc):
        self.clear()

    def clear(self):
        ''' clear the state.'''
        self.start_uid = None
        self.start_doc = None
        self.descriptors = dict()
        # TODO : Allow for multiple images
        #self.images = dict()
        self.clear_images()


def get_handler(datum_id, db):
    '''
        Get a file handler from the database.

        datum_id : the datum uid (from db.table() usually...)
        db : the databroker instance (db = Broker.named("pdf") for example)

    '''
    resource = db.reg.resource_given_datum_id(datum_id)
    datums = list(db.reg.datum_gen_given_resource(resource))
    handler = db.reg.get_spec_handler(resource['uid'])
    return handler


def get_file_list(datum_id, db):
    resource = db.reg.resource_given_datum_id(datum_id)
    datums = db.reg.datum_gen_given_resource(resource)
    handler = db.reg.get_spec_handler(resource['uid'])
    datum_kwarg_list = [datum['datum_kwargs'] for datum in datums if datum['datum_id'] == datum_id]

    return handler.get_file_list(datum_kwarg_list)




# this call back will create soft links for PE
# the format is a list
# each item can be one of the following:
# 1. a tuple ('start', 'cycle')
#data_keys = [pe1.image.name]
data_keys = ["pe1_image"]
#data_info_keys = ["Det_1_Z"]#Det_1_Z.name]
data_info_keys_softlink = [ 
    ('start', 'cycle'),
    "/",
    ('start', 'Proposal ID'),
    "/",
    ('descriptor', 'name'),
    "/",
    ('event', 'data', 'Det_1_Z_user_setpoint'),
    "/",
    ('start', 'sample_name'),
    ('start', 'wavelength'),
    ('start', 'scan_id'),
    ('event', 'data', 'Det_1_Z'),
    ('event', 'data', 'cryostream_T'),
    ('descriptor', 'name'),
]

data_info_keys_bgsub=[ 
    ('start', 'cycle'),
    "/",
    ('start', 'Proposal ID'),
    "/",
    ('descriptor', 'name'),
    "/",
    ('event', 'data', 'Det_1_Z_user_setpoint'),
    "/",
    ('start', 'sample_name'),
    ('start', 'wavelength'),
    ('start', 'scan_id'),
    ('event', 'data', 'Det_1_Z'),
    ('event', 'data', 'cryostream_T'),
    #('event', 'data', ''),
]

soft_link_callback = SoftLinkCallBack(db, data_keys, data_info_keys_softlink, root='/SHARE/user_data')

# RE.subscribe(soft_link_callback)
# background subtraction callback
bgsub_callback =  DarkSubtractionCallback([],
                                          image_key = "dexela_image",
                                          primary_stream="primary",
                                          dark_stream="dark", db=db,
                                          data_info_keys=data_info_keys_bgsub)



# RE.subscribe(bgsub_callback)

