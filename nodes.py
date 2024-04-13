import moderngl
import numpy as np
from .utils import pil2tensor, load_source
from PIL import Image

# for now vertices and vertex shader are hardcoded.
# need to first think of the logic more precisely
VERTICES = np.array(
    [-1.0, -1.0, 1.0, -1.0, -1.0, 1.0, 1.0, -1.0, -1.0, 1.0, 1.0, 1.0], dtype="f4"
)

VERTEX_SHADER = """
#version 330
in vec2 in_vert;
out vec2 vert_pos;
void main() {
    // normalize vert position from [-1,1] to [0,1]
    vert_pos = 0.5*(in_vert + 1.0);
    gl_Position = vec4(in_vert, 0.0, 1.0);
}
"""

from typing import Any


class MTB_LygiaUniforms:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "shader": (
                    "STRING",
                    {"default": "", "multiline": True, "dynamicPrompts": False},
                ),
            },
        }

    RETURN_TYPES = ("UNIFORMS", "STRING")
    RETURN_NAMES = ("uniforms", "compiled_shader")
    CATEGORY = "shaders"
    FUNCTION = "parse"

    def parse(self, shader: str, **kwargs):
        compiled = load_source(shader)

        return (kwargs, compiled)


class MTB_LygiaProgram:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "frag_shader": (
                    "STRING",
                    {
                        "default": "",
                    },
                ),
                "width": ("INT", {"default": 512}),
                "height": ("INT", {"default": 512}),
                "frame_count": ("INT", {"default": 100}),
                "uniforms": ("UNIFORMS",),
            },
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)
    CATEGORY = "shaders"
    FUNCTION = "render"

    def render(
        self,
        frag_shader: str,
        width: int,
        height: int,
        frame_count: int,
        uniforms: dict[str, Any],
    ):
        ctx = moderngl.create_standalone_context()

        # TODO: this should be safe, but maybe enforce it before being passed to the program..
        frag = frag_shader  # load_source(frag_shader)
        print("\n".join([f"{i} - {x}" for i, x in enumerate(frag.splitlines())]))
        prog = ctx.program(vertex_shader=VERTEX_SHADER, fragment_shader=frag)

        # for uniform in uniforms:
        #    prog[uniform].value = uniforms[uniform]

        prog["u_resolution"].value = (height, width)
        time = prog["u_time"]

        time.value = 0.0

        vbo = ctx.buffer(VERTICES.astype("f4").tobytes())
        vao = ctx.simple_vertex_array(prog, vbo, "in_vert")
        fbo = ctx.simple_framebuffer((width, height))
        fbo.use()
        imgs = []

        for i in range(frame_count):
            time.value += 0.1

            fbo.clear(0.0, 0.0, 0.0, 1.0)

            vao.render(moderngl.TRIANGLE_STRIP)

            imgs.append(
                Image.frombytes("RGB", fbo.size, fbo.read(), "raw", "RGB", 0, -1)
            )

        return (pil2tensor(imgs),)
