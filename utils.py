import torch

from PIL import Image
import numpy as np
import re

from pathlib import Path
from glsl_shaderinfo import get_info as glsl_info


def get_shader_info(shader):
    return glsl_info(shader)


# adapted from from https://gist.github.com/patriciogonzalezvivo/9a50569c2ef9b08058706443a39d838e
def load_source(
    code: str, folder: str | None = None, dependencies: list[str] | None = None
) -> str:
    if dependencies is None:
        dependencies = []

    source = "\n"
    here = Path(__file__).parent
    if folder:
        lygia = here / "lygia" / folder
    else:
        lygia = here
    lines: list[str] = []
    lines = code.splitlines(keepends=False)
    for line in lines:
        if line.strip().startswith("//"):
            continue
        if match := re.search(
            r'^#include\s*["|<](.*.[glsl|hlsl|metal])["|>]', line, re.IGNORECASE
        ):
            # print(match)
            new_folder = lygia / Path(match.group(1)).parent
            new_dep = Path(match.group(1)).name
            # print(Path(match.group(1)))
            # print((new_folder / new_dep).as_posix())
            new_src = (new_folder / new_dep).read_text(encoding="utf-8")
            source += load_source(new_src, new_folder.as_posix(), dependencies) + "\n"

            # source += load_source(new_folder.as_posix(), new_dep, dependencies)
        else:
            source += line + "\n"

    # print(source)
    return source


def tensor2pil(image: torch.Tensor) -> list[Image.Image]:
    """Convert PyTorch tensor to PIL image."""
    batch_count = image.size(0) if len(image.shape) > 3 else 1
    if batch_count > 1:
        out: list[Image.Image] = []
        for i in range(batch_count):
            out.extend(tensor2pil(image[i]))
        return out

    return [
        Image.fromarray(
            np.clip(255.0 * image.cpu().numpy().squeeze(), 0, 255).astype(np.uint8)
        )
    ]


def pil2tensor(image: Image.Image | list[Image.Image]) -> torch.Tensor:
    """Convert PIL image to PyTorch tensor."""
    if isinstance(image, list):
        return torch.cat([pil2tensor(img) for img in image], dim=0)

    return torch.from_numpy(np.array(image).astype(np.float32) / 255.0).unsqueeze(0)
