# Generated from a native module introspection run. Do not edit by hand.
#
# Source: shared.lzf (package)
# Regenerate with tools/oracle/generate_api_reference.py


# Functions
def compress(*args, **kwargs):  # signature not introspectable
    """compress(input, max_length=None)
    	
    	return the compressed string, or None if it doesn't compress to smaller 
    	than the original
    	
    	takes an optional second parameter, for specifying a maximum compressed 
    	length (default is one less than the length of the original)
    """
    ...

def decompress(*args, **kwargs):  # signature not introspectable
    """decompress(input, max_length)
    	
    	return the decompressed string
    	
    	will return None if the string doesn't decompress to within max_length bytes
    """
    ...

def decompress_client(*args, **kwargs):  # signature not introspectable
    """decompress_client(input, max_length)
    	
    	return the decompressed string
    	
    	will return None if the string doesn't decompress to within max_length bytes
    """
    ...
