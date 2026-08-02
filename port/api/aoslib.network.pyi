# Generated from a native module introspection run. Do not edit by hand.
#
# Source: aoslib.network (package)
# Regenerate with tools/oracle/generate_api_reference.py


# Constants
A2011: int  # 1
A2012: int  # 2
A2014: int  # 4
A2015: int  # 0
A2016: int  # 1
A2388: int  # 2
A2390: int  # 8
A2441: int  # 6
A2447: int  # 12
A2450: dict  # {'tdm': 6, 'ugc': 12, 'tut': 10, 'zom': 2, 'vip': 7, 'cctf': 8, 'nor': 0, 'oc': 4, 'mh': 3, 'ctf': 8, 'dem': 1, 'tc': 9, 'dia': 5}
A554: dict  # {0: {0: [2, 1], 1: [8, 60], 2: [12, 13], 3: [11, 32, 72], 4: [0, 8, 7], 5: [5, 23, 22, 30, 25, 26, 30], 6: []}, 1: {0: [0, 1], 1: [18, 19], 2: [17, 53], 3: [20, 56], 4: [1, 8, 7], 5: [5, 23, 22, 30, 2...
Queue: module  # <module 'Queue' from 'C:\Python27-x86\lib\Queue.pyc'>
THREAD_CLOSE: int  # 4
THREAD_DONE_PROCESSING: int  # 3
THREAD_IDLE: int  # 0
THREAD_STATE_FULL_LOCAL: int  # 1
THREAD_STATE_PART_REMOTE: int  # 2
constants: module  # <module 'shared.constants' from 'D:\a\aceofspades_revival\aceofspades_revival\shared\constants.pyc'>
copy: module  # <module 'copy' from 'C:\Python27-x86\lib\copy.pyc'>
enet: module  # <module 'enet' from 'D:\a\aceofspades_revival\aceofspades_revival\enet.pyd'>
json: module  # <module 'json' from 'C:\Python27-x86\lib\json\__init__.pyc'>
lzf: module  # <module 'shared.lzf' from 'D:\a\aceofspades_revival\aceofspades_revival\shared\lzf.pyd'>
map_data_validation: MapDataValidation  # <shared.packet.MapDataValidation object at 0x02CD8A90>
os: module  # <module 'os' from 'C:\Python27-x86\lib\os.pyc'>
pack_response: PackResponse  # <shared.packet.PackResponse object at 0x02CD8A80>
packets: module  # <module 'shared.packet' from 'D:\a\aceofspades_revival\aceofspades_revival\shared\packet.pyd'>
threading: module  # <module 'threading' from 'C:\Python27-x86\lib\threading.pyc'>
time: module  # <module 'time' (built-in)>
zlib: module  # <module 'zlib' (built-in)>

# Functions
def SteamCancelSessionTicket():
    ...

def SteamSendPassword(client, name, ip, port):
    ...

def SteamSendSessionTicket(client):
    ...

def add_ground_color(*args, **kwargs):  # signature not introspectable
    ...

def clamp(*args, **kwargs):  # signature not introspectable
    ...

def game_version():
    ...

def generate_ground_color_table(*args, **kwargs):  # signature not introspectable
    ...

def load_server_packet(*args, **kwargs):  # signature not introspectable
    ...

def make_server_identifier(ip, port=32887):
    ...

def reset_ground_colors(*args, **kwargs):  # signature not introspectable
    ...

def xor_encryption(*args, **kwargs):  # signature not introspectable
    ...

# Classes
class ByteReader(object):
    __init__: wrapper_descriptor  # 
    data_left: method_descriptor  # 
    read: method_descriptor  # 
    read_byte: method_descriptor  # 
    read_float: method_descriptor  # 
    read_int: method_descriptor  # 
    read_pystring: method_descriptor  # 
    read_reader: method_descriptor  # 
    read_short: method_descriptor  # 
    read_string: method_descriptor  # 
    read_uint64: method_descriptor  # 
    rewind: method_descriptor  # 
    seek: method_descriptor  # 
    skip_bytes: method_descriptor  # 
    tell: method_descriptor  # 


class ByteWriter(object):
    __init__: wrapper_descriptor  # 
    pad: method_descriptor  # 
    rewind: method_descriptor  # 
    tell: method_descriptor  # 
    write: method_descriptor  # 
    write_byte: method_descriptor  # 
    write_float: method_descriptor  # 
    write_int: method_descriptor  # 
    write_pystring: method_descriptor  # 
    write_short: method_descriptor  # 
    write_string: method_descriptor  # 
    write_string_size: method_descriptor  # 
    write_uint64: method_descriptor  # 


class GameClient(NetworkClient):
    def __init__(*args, **kwargs):  # signature not introspectable
        ...
    def apply_ground_colors(*args, **kwargs):  # signature not introspectable
        ...
    def attempt_local_map_open(*args, **kwargs):  # signature not introspectable
        ...
    def attempt_local_map_save(*args, **kwargs):  # signature not introspectable
        ...
    blocked_network_count: int  # 0
    def calculate_blocked_map_progress(*args, **kwargs):  # signature not introspectable
        ...
    def close(*args, **kwargs):  # signature not introspectable
        ...
    def disconnect(*args, **kwargs):  # signature not introspectable
        ...
    disconnected: bool  # False
    def finished_connecting(*args, **kwargs):  # signature not introspectable
        ...
    def flush(*args, **kwargs):  # signature not introspectable
        ...
    id: NoneType  # None
    map: NoneType  # None
    map_data: NoneType  # None
    map_percentage: float  # 0.0
    map_texture_quality: int  # 2
    def on_connect(*args, **kwargs):  # signature not introspectable
        ...
    def on_disconnect(*args, **kwargs):  # signature not introspectable
        ...
    pack_percentage: float  # 0.0
    pack_writer: NoneType  # None
    def packet_received(*args, **kwargs):  # signature not introspectable
        ...
    def process_current_data(*args, **kwargs):  # signature not introspectable
        ...
    def send_map_validation(*args, **kwargs):  # signature not introspectable
        ...
    def send_packet(*args, **kwargs):  # signature not introspectable
        ...
    def start_processing_map(*args, **kwargs):  # signature not introspectable
        ...
    def start_processing_map_sync(*args, **kwargs):  # signature not introspectable
        ...
    sync_data: NoneType  # None
    timeout: int  # 5
    ugc_data: NoneType  # None
    ugc_mode_editing: NoneType  # None
    ugc_split_loading_bar: bool  # False
    def update(*args, **kwargs):  # signature not introspectable
        ...


class NetworkClient(object):
    def __init__(*args, **kwargs):  # signature not introspectable
        ...
    blocked_network_count: int  # 0
    def close(*args, **kwargs):  # signature not introspectable
        ...
    def disconnect(*args, **kwargs):  # signature not introspectable
        ...
    disconnected: bool  # False
    def flush(*args, **kwargs):  # signature not introspectable
        ...
    def on_connect(*args, **kwargs):  # signature not introspectable
        ...
    def on_disconnect(*args, **kwargs):  # signature not introspectable
        ...
    def packet_received(*args, **kwargs):  # signature not introspectable
        ...
    def process_current_data(*args, **kwargs):  # signature not introspectable
        ...
    def send_packet(*args, **kwargs):  # signature not introspectable
        ...
    timeout: int  # 5
    def update(*args, **kwargs):  # signature not introspectable
        ...


class NetworkThread(Thread):
    def _Thread__bootstrap(self):
        ...
    def _Thread__bootstrap_inner(self):
        ...
    def _Thread__delete(self):
        """Remove current thread from the dict of currently running threads."""
        ...
    def _Thread__exc_clear(*args, **kwargs):  # signature not introspectable
        """exc_clear() -> None
        
        Clear global information on the current exception.  Subsequent calls to
        exc_info() will return (None,None,None) until another exception is raised
        in the current thread or the execution stack returns to a frame where
        another exception is being handled.
        """
        ...
    def _Thread__exc_info(*args, **kwargs):  # signature not introspectable
        """exc_info() -> (type, value, traceback)
        
        Return information about the most recent exception caught by an except
        clause in the current stack frame or in an older stack frame.
        """
        ...
    _Thread__initialized: bool  # False
    def _Thread__stop(self):
        ...
    def __init__(*args, **kwargs):  # signature not introspectable
        ...
    _block: property  # <property object at 0x02DD5810>
    def _note(self, format, *args):
        ...
    def _reset_internal_locks(self):
        ...
    def _set_daemon(self):
        ...
    def _set_ident(self):
        ...
    daemon: property  # <property object at 0x02DD58D0>
    def getName(self):
        ...
    ident: property  # <property object at 0x02DD5840>
    def isAlive(self):
        """Return whether the thread is alive.
        
                This method returns True just before the run() method starts until just
                after the run() method terminates. The module function enumerate()
                returns a list of all alive threads.
        """
        ...
    def isDaemon(self):
        ...
    def is_alive(self):
        """Return whether the thread is alive.
        
                This method returns True just before the run() method starts until just
                after the run() method terminates. The module function enumerate()
                returns a list of all alive threads.
        """
        ...
    def join(self, timeout=None):
        """Wait until the thread terminates.
        
                This blocks the calling thread until the thread whose join() method is
                called terminates -- either normally or through an unhandled exception
                or until the optional timeout occurs.
        
                When the timeout argument is present and not None, it should be a
                floating point number specifying a timeout for the operation in seconds
                (or fractions thereof). As join() always returns None, you must call
                isAlive() after join() to decide whether a timeout happened -- if the
                thread is still alive, the join() call timed out.
        
                When the timeout argument is not present or None, the operation will
                block until the thread terminates.
        
                A thread can be join()ed many times.
        
                join() raises a RuntimeError if an attempt is made to join the current
                thread as that would cause a deadlock. It is also an error to join() a
                thread before it has been started and attempts to do so raises the same
                exception.
        """
        ...
    name: property  # <property object at 0x02DD5870>
    def run(*args, **kwargs):  # signature not introspectable
        ...
    def setDaemon(self, daemonic):
        ...
    def setName(self, name):
        ...
    def start(self):
        """Start the thread's activity.
        
                It must be called at most once per thread object. It arranges for the
                object's run() method to be invoked in a separate thread of control.
        
                This method will raise a RuntimeError if called more than once on the
                same thread object.
        """
        ...


class QueryClient(object):
    def __init__(*args, **kwargs):  # signature not introspectable
        ...
    local: bool  # False
    def query(*args, **kwargs):  # signature not introspectable
        ...
    def query_local(*args, **kwargs):  # signature not introspectable
        ...
    def receive_callback(*args, **kwargs):  # signature not introspectable
        ...
    def send_query(*args, **kwargs):  # signature not introspectable
        ...
    def stop(*args, **kwargs):  # signature not introspectable
        ...
    def update(*args, **kwargs):  # signature not introspectable
        ...


class ServerEntry(object):
    """Strict boundary object consumed by the recovered Choose Match menu."""
    def __init__(self, value):
        ...


class VXL(object):
    __init__: wrapper_descriptor  # 
    add_point: method_descriptor  # 
    add_static_light: method_descriptor  # 
    change_thread_state: method_descriptor  # 
    check_only: method_descriptor  # 
    chunk_to_pointlist: method_descriptor  # 
    cleanup: method_descriptor  # 
    clear_checked_geometry: method_descriptor  # 
    color_block: method_descriptor  # 
    create_spot_shadows: method_descriptor  # 
    destroy: method_descriptor  # 
    done_processing: method_descriptor  # 
    draw: method_descriptor  # 
    draw_sea: method_descriptor  # 
    draw_spot_shadows: method_descriptor  # 
    erase_prefab_from_world: method_descriptor  # 
    generate_vxl: method_descriptor  # 
    get_color: method_descriptor  # 
    get_color_tuple: method_descriptor  # 
    get_ground_colors: method_descriptor  # 
    get_max_modifiable_z: method_descriptor  # 
    get_overview: method_descriptor  # 
    get_point: method_descriptor  # 
    get_prefab_touches_world: method_descriptor  # 
    get_solid: method_descriptor  # 
    has_neighbors: method_descriptor  # 
    is_space_to_add_blocks: method_descriptor  # 
    minimap_texture: getset_descriptor  # <attribute 'minimap_texture' of 'aoslib.vxl.VXL' objects>
    place_prefab_in_world: method_descriptor  # 
    post_load_draw_setup: method_descriptor  # 
    refresh_ground_colors: method_descriptor  # 
    remove_point: method_descriptor  # 
    remove_point_nochecks: method_descriptor  # 
    remove_static_light: method_descriptor  # 
    set_max_modifiable_z: method_descriptor  # 
    set_point: method_descriptor  # 
    set_shadow_char_height: method_descriptor  # 
    update_static_light_colour: method_descriptor  # 


class ugc_data(object):
    DATA_CHUNK_SIZE: int  # 1048
    ZERO_LENGTH_SKIPS_PER_FRAME: int  # 50
    def __init__(*args, **kwargs):  # signature not introspectable
        ...
    def attempt_local_ugc_open(*args, **kwargs):  # signature not introspectable
        ...
    def attempt_local_vxl_open(*args, **kwargs):  # signature not introspectable
        ...
    def begin_sending_vxl_data(*args, **kwargs):  # signature not introspectable
        ...
    def check_baseplate(*args, **kwargs):  # signature not introspectable
        ...
    def continue_sending_vxl_data(*args, **kwargs):  # signature not introspectable
        ...
    data: NoneType  # None
    def ensure_required_members(*args, **kwargs):  # signature not introspectable
        ...
    entities_not_being_edited: list  # []
    external_publish_finished_callback: NoneType  # None
    def get_ground_colors(*args, **kwargs):  # signature not introspectable
        ...
    def get_path(*args, **kwargs):  # signature not introspectable
        ...
    def get_skybox_name(*args, **kwargs):  # signature not introspectable
        ...
    def get_water_color(*args, **kwargs):  # signature not introspectable
        ...
    def load_png(*args, **kwargs):  # signature not introspectable
        ...
    local_filename: NoneType  # None
    local_vxl_data: NoneType  # None
    network: NoneType  # None
    ongoing_map_data: NoneType  # None
    png_data: NoneType  # None
    preview_image_updated: bool  # False
    def publish(*args, **kwargs):  # signature not introspectable
        ...
    def save_ground_colors(*args, **kwargs):  # signature not introspectable
        ...
    def save_map_author(*args, **kwargs):  # signature not introspectable
        ...
    def save_map_title(*args, **kwargs):  # signature not introspectable
        ...
    def save_png(*args, **kwargs):  # signature not introspectable
        ...
    def save_skybox_name(*args, **kwargs):  # signature not introspectable
        ...
    def save_ugc(*args, **kwargs):  # signature not introspectable
        ...
    def save_vxl(*args, **kwargs):  # signature not introspectable
        ...
    def send_map_info(*args, **kwargs):  # signature not introspectable
        ...
    def send_ugc_entities(*args, **kwargs):  # signature not introspectable
        ...
    def set_aos_ugc_handle(*args, **kwargs):  # signature not introspectable
        ...
    def set_tags_from_supported_gamemodes(*args, **kwargs):  # signature not introspectable
        ...
    def ugc_data_publish_finished_callback(*args, **kwargs):  # signature not introspectable
        ...
    ugc_prefab_sets: NoneType  # None
    def use_custom_preview_image(*args, **kwargs):  # signature not introspectable
        ...
    use_overhead_image: bool  # True
