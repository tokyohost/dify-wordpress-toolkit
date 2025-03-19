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


        user = api.query_posts(tool_parameters)

        yield self.create_json_message(user)
