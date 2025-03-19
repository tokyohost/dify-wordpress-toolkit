import random
import string
from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from dify_plugin.file.entities import FileType
from dify_plugin.file.file import File

from wordpress_api_utils import wordpress_api_utils


class WordpressTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        print(self.runtime.credentials)
        print(tool_parameters)
        api = wordpress_api_utils(self.runtime.credentials)
        if not api:
            raise Exception("token is required")

        if not tool_parameters.get('file'):
            raise Exception("file is required")
        image: File | None = tool_parameters.get("file")
        if not image:
            raise ValueError("Got no image")
        # if image.type != FileType.IMAGE:
        #     raise ValueError("Not a valid image")

        image_binary = image.blob
        media = api.uploadMedia(image_binary, image.filename, image.mime_type)

        yield self.create_json_message(media)
