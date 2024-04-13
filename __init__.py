from .nodes import MTB_LygiaProgram, MTB_LygiaUniforms
from server import PromptServer
from aiohttp import web

NODE_CLASS_MAPPINGS = {
    "LygiaProgram": MTB_LygiaProgram,
    "LygiaUniforms": MTB_LygiaUniforms,
}
NODE_DISPLAY_NAME_MAPPINGS = {
    "LygiaProgram": "Lygia Program",
    "LygiaUniforms": "Lygia Uniforms",
}

WEB_DIRECTORY = "./web"

__version__ = "0.2.0"

if hasattr(PromptServer, "instance"):

    @PromptServer.instance.routes.post("/shaders/build")
    async def build(request):
        json_data = await request.json()
        source = json_data.get("source")
        if source:
            info = utils.get_shader_info(source)
            compiled = utils.load_source(source)
            return web.json_response(
                {
                    "compiled": compiled,
                    "info": {
                        "uniform_names": info.uniform_names,
                    },
                }
            )
        return web.json_response({"error": "No source code provided"})
