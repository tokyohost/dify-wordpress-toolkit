import random
import string
from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from wordpress_api_utils import wordpress_api_utils


class WordpressUserTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        print(self.runtime.credentials)
        print(tool_parameters)
        api = wordpress_api_utils(self.runtime.credentials)
        if not api:
            raise Exception("token is required")

        if not tool_parameters.get('userId'):
            raise Exception("userId is required")


        result = api.update_user(tool_parameters)

        yield self.create_json_message(result)
