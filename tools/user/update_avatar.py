import io
from collections.abc import Generator
from typing import Any

import requests
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from dify_plugin.file.entities import FileType
from dify_plugin.file.file import File

from wordpress_api_utils import wordpress_api_utils
from wp_db_service import wp_db_service


class WordpressUserTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        print(self.runtime.credentials)
        print(tool_parameters)
        api = wordpress_api_utils(self.runtime.credentials)
        if not api:
            raise Exception("token is required")

        if not tool_parameters.get('userid'):
            raise Exception("userid is required")
        if not tool_parameters.get('avatar_file'):
            raise Exception("avatar_file is required")
        file = tool_parameters.get('avatar_file')
        image: File | None = tool_parameters.get("avatar_file")
        if not image:
            raise ValueError("Got no image")
        if image.type != FileType.IMAGE:
            raise ValueError("Not a valid image")

        image_binary = image.blob
        media = api.uploadMedia(image_binary, "avatar"+image.extension,image.mime_type)


        service = wp_db_service(self.runtime.credentials)
        service.updateMedia(tool_parameters.get('userid'),media['id'])
        result = api.updateUserAvator(tool_parameters.get('userid'), media['id'])

        yield self.create_json_message(result)
