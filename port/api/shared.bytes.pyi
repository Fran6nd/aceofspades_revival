# Generated from a native module introspection run. Do not edit by hand.
#
# Source: shared.bytes (package)
# Regenerate with tools/oracle/generate_api_reference.py


"""Reads/writes bytes"""

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


class NoDataLeft(Exception):
    __init__: wrapper_descriptor  # 
    args: getset_descriptor  # <attribute 'args' of 'exceptions.BaseException' objects>
    message: getset_descriptor  # <attribute 'message' of 'exceptions.BaseException' objects>
