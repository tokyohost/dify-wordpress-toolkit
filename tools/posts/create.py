from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from wordpress_api_utils import wordpress_api_utils


class WordpressTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        print(self.runtime.credentials)
        api = wordpress_api_utils(self.runtime.credentials)
        if not api:
            raise Exception("token is required")

        if not tool_parameters.get('title'):
            raise Exception("title is required")
        if not tool_parameters.get('content'):
            raise Exception("content is required")

        result = api.create_post(tool_parameters)

        yield self.create_json_message(result)
