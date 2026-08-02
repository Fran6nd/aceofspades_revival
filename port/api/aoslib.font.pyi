# Generated from a native module introspection run. Do not edit by hand.
#
# Source: aoslib.font (package)
# Regenerate with tools/oracle/generate_api_reference.py


# Constants
ALIGN_BOTTOM: int  # 2
ALIGN_CENTER: int  # 1
ALIGN_JUSTIFY: int  # 2
ALIGN_LEFT: int  # 0
ALIGN_RIGHT: int  # 2
ALIGN_TOP: int  # 0
DEFAULT_WINDOW_HEIGHT: float  # 600.0
DEFAULT_WINDOW_WIDTH: float  # 800.0
FONT_MAX_PT_SIZE: int  # 119
FONT_MIN_PT_SIZE: int  # 4
GLOBAL_FONT_SCALE: float  # 1.0
GLOBAL_MUL: float  # 1.0
GLOBAL_WINDOW_HEIGHT: float  # 600.0
GLOBAL_WINDOW_WIDTH: float  # 800.0
font_map_aldo: dict  # {4: {'pixel_size': 4.462890625}, 5: {'pixel_size': 5.57861328125}, 6: {'pixel_size': 6.6943359375}, 7: {'pixel_size': 7.81005859375}, 8: {'pixel_size': 8.92578125}, 9: {'pixel_size': 10.0415039062}, 1...
font_map_edo: dict  # {4: {'pixel_size': 4.9439997673}, 5: {'pixel_size': 6.17999982834}, 6: {'pixel_size': 7.41599988937}, 7: {'pixel_size': 8.65200042725}, 8: {'pixel_size': 9.88799953461}, 9: {'pixel_size': 11.123999595...
font_map_standard_bold: dict  # {4: {'pixel_size': 4.57999992371}, 5: {'pixel_size': 5.72499990463}, 6: {'pixel_size': 6.86999988556}, 7: {'pixel_size': 8.01500034332}, 8: {'pixel_size': 9.15999984741}, 9: {'pixel_size': 10.30500030...
font_map_standard_med: dict  # {4: {'pixel_size': 4.56799983978}, 5: {'pixel_size': 5.71000003815}, 6: {'pixel_size': 6.85200023651}, 7: {'pixel_size': 7.99399995804}, 8: {'pixel_size': 9.13599967957}, 9: {'pixel_size': 10.27799987...
font_map_standard_tuffy_bold: dict  # {4: {'pixel_size': 5.931640625}, 5: {'pixel_size': 7.41455078125}, 6: {'pixel_size': 8.8974609375}, 7: {'pixel_size': 10.3803710938}, 8: {'pixel_size': 11.86328125}, 9: {'pixel_size': 13.3461914062}, ...
os: module  # <module 'os' from 'C:\Python27-x86\lib\os.pyc'>
sys: module  # <module 'sys' (built-in)>

# Functions
def get_font_pixel_size(*args, **kwargs):  # signature not introspectable
    ...

def get_font_point_size(*args, **kwargs):  # signature not introspectable
    ...

# Classes
class Font(object):
    __init__: wrapper_descriptor  # 
    contains_character: method_descriptor  # 
    draw: method_descriptor  # 
    draw_3d: method_descriptor  # 
    draw_multi: method_descriptor  # 
    draw_multi_stroke: method_descriptor  # 
    draw_stroke: method_descriptor  # 
    enable_resize: getset_descriptor  # <attribute 'enable_resize' of 'aoslib.font.Font' objects>
    filename: getset_descriptor  # <attribute 'filename' of 'aoslib.font.Font' objects>
    get_advance_width: method_descriptor  # 
    get_ascender: method_descriptor  # 
    get_char_height: method_descriptor  # 
    get_content_width: method_descriptor  # 
    get_descender: method_descriptor  # 
    get_font_scale: method_descriptor  # 
    get_line_height: method_descriptor  # 
    get_line_width: method_descriptor  # 
    global_font_scale: getset_descriptor  # <attribute 'global_font_scale' of 'aoslib.font.Font' objects>
    load_font_for_generation: method_descriptor  # 
    name: getset_descriptor  # <attribute 'name' of 'aoslib.font.Font' objects>
    original_size: getset_descriptor  # <attribute 'original_size' of 'aoslib.font.Font' objects>
    ratio: getset_descriptor  # <attribute 'ratio' of 'aoslib.font.Font' objects>
    resize_font: method_descriptor  # 
    scale: getset_descriptor  # <attribute 'scale' of 'aoslib.font.Font' objects>
    scale_fix: getset_descriptor  # <attribute 'scale_fix' of 'aoslib.font.Font' objects>
    size: getset_descriptor  # <attribute 'size' of 'aoslib.font.Font' objects>


class FontContainer(object):
    __init__: wrapper_descriptor  # 


class FontError(Exception):
    __init__: wrapper_descriptor  # 
    args: getset_descriptor  # <attribute 'args' of 'exceptions.BaseException' objects>
    message: getset_descriptor  # <attribute 'message' of 'exceptions.BaseException' objects>


class Layout(object):
    __init__: wrapper_descriptor  # 
    delete: method_descriptor  # 
    draw: method_descriptor  # 
    height: getset_descriptor  # <attribute 'height' of 'aoslib.font.Layout' objects>
    pFont: getset_descriptor  # <attribute 'pFont' of 'aoslib.font.Layout' objects>
    scale: getset_descriptor  # <attribute 'scale' of 'aoslib.font.Layout' objects>
    set_horizontal_align: method_descriptor  # 
    set_line_spacing: method_descriptor  # 
    set_scale: method_descriptor  # 
    set_vertical_align: method_descriptor  # 
    width: getset_descriptor  # <attribute 'width' of 'aoslib.font.Layout' objects>
