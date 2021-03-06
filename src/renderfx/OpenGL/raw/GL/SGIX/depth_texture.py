'''Autogenerated by get_gl_extensions script, do not edit!'''
from OpenGL import platform as _p
from OpenGL.GL import glget
EXTENSION_NAME = 'GL_SGIX_depth_texture'
_p.unpack_constants( """GL_DEPTH_COMPONENT16_SGIX 0x81A5
GL_DEPTH_COMPONENT24_SGIX 0x81A6
GL_DEPTH_COMPONENT32_SGIX 0x81A7""", globals())


def glInitDepthTextureSGIX():
    '''Return boolean indicating whether this extension is available'''
    from OpenGL import extensions
    return extensions.hasGLExtension( EXTENSION_NAME )
