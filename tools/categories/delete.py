import random
import string
from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from dify_plugin.file.entities import FileType
from dify_plugin.file.file import File

from ResultTool import ResultTool
from wordpress_api_utils import wordpress_api_utils


class WordpressTool(Tool,ResultTool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        print(self.runtime.credentials)
        print(tool_parameters)
        api = wordpress_api_utils(self.runtime.credentials)
        if not api:
            raise Exception("token is required")

        if not tool_parameters.get('categoriesId'):
            raise Exception("categoriesId is required")

        result = api.delete_categories(tool_parameters.get('categoriesId'),tool_parameters.get('force'))

        yield self.create_json_message(self.deleteResult(result))
