# Generated from a native module introspection run. Do not edit by hand.
#
# Source: aoslib.kv6 (package)
# Regenerate with tools/oracle/generate_api_reference.py


# Constants
MAGIC: str  # 'Kvxl'
PALETTE_MAGIC: str  # 'SPal'
random: module  # <module 'random' from 'C:\Python27-x86\lib\random.pyc'>

# Functions
def crc32(*args, **kwargs):  # signature not introspectable
    """crc32(string[, start]) -- Compute a CRC-32 checksum of string.
    
    An optional starting value can be specified.  The returned checksum is
    a signed integer.
    """
    ...

def set_kv6_default_color(*args, **kwargs):  # signature not introspectable
    ...

# Classes
class Enum(object):
    __init__: wrapper_descriptor  # 


class KV6(object):
    __init__: wrapper_descriptor  # 
    add_points: method_descriptor  # 
    destroy_kv6: method_descriptor  # 
    draw: method_descriptor  # 
    get_adjacent_points: method_descriptor  # 
    get_bounding_box_sizes: method_descriptor  # 
    get_bounds: method_descriptor  # 
    get_crc: method_descriptor  # 
    get_max_z_size: method_descriptor  # 
    get_pivots: method_descriptor  # 
    get_points: method_descriptor  # 
    get_scale: method_descriptor  # 
    get_sizes: method_descriptor  # 
    offset_pivots: method_descriptor  # 
    replace: method_descriptor  # 
    reset_prefab_pivots: method_descriptor  # 
    save: method_descriptor  # 
    set_adjacent_points: method_descriptor  # 


class _memoryviewslice(memoryview):
    T: getset_descriptor  # <attribute 'T' of 'aoslib.kv6.memoryview' objects>
    __init__: wrapper_descriptor  # 
    __pyx_getbuffer: PyCapsule  # <capsule object "getbuffer(obj, view, flags)" at 0x03861758>
    base: getset_descriptor  # <attribute 'base' of 'aoslib.kv6._memoryviewslice' objects>
    copy: method_descriptor  # 
    copy_fortran: method_descriptor  # 
    is_c_contig: method_descriptor  # 
    is_f_contig: method_descriptor  # 
    itemsize: getset_descriptor  # <attribute 'itemsize' of 'aoslib.kv6.memoryview' objects>
    nbytes: getset_descriptor  # <attribute 'nbytes' of 'aoslib.kv6.memoryview' objects>
    ndim: getset_descriptor  # <attribute 'ndim' of 'aoslib.kv6.memoryview' objects>
    shape: getset_descriptor  # <attribute 'shape' of 'aoslib.kv6.memoryview' objects>
    size: getset_descriptor  # <attribute 'size' of 'aoslib.kv6.memoryview' objects>
    strides: getset_descriptor  # <attribute 'strides' of 'aoslib.kv6.memoryview' objects>
    suboffsets: getset_descriptor  # <attribute 'suboffsets' of 'aoslib.kv6.memoryview' objects>


class array(object):
    __init__: wrapper_descriptor  # 
    __pyx_getbuffer: PyCapsule  # <capsule object "getbuffer(obj, view, flags)" at 0x03861728>
    memview: getset_descriptor  # <attribute 'memview' of 'aoslib.kv6.array' objects>


class memoryview(object):
    T: getset_descriptor  # <attribute 'T' of 'aoslib.kv6.memoryview' objects>
    __init__: wrapper_descriptor  # 
    __pyx_getbuffer: PyCapsule  # <capsule object "getbuffer(obj, view, flags)" at 0x03861740>
    base: getset_descriptor  # <attribute 'base' of 'aoslib.kv6.memoryview' objects>
    copy: method_descriptor  # 
    copy_fortran: method_descriptor  # 
    is_c_contig: method_descriptor  # 
    is_f_contig: method_descriptor  # 
    itemsize: getset_descriptor  # <attribute 'itemsize' of 'aoslib.kv6.memoryview' objects>
    nbytes: getset_descriptor  # <attribute 'nbytes' of 'aoslib.kv6.memoryview' objects>
    ndim: getset_descriptor  # <attribute 'ndim' of 'aoslib.kv6.memoryview' objects>
    shape: getset_descriptor  # <attribute 'shape' of 'aoslib.kv6.memoryview' objects>
    size: getset_descriptor  # <attribute 'size' of 'aoslib.kv6.memoryview' objects>
    strides: getset_descriptor  # <attribute 'strides' of 'aoslib.kv6.memoryview' objects>
    suboffsets: getset_descriptor  # <attribute 'suboffsets' of 'aoslib.kv6.memoryview' objects>


class state:
    value: int  # 0
