import random
import string
from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from dify_plugin.errors.tool import ToolProviderCredentialValidationError
from dify_plugin.file.entities import FileType
from dify_plugin.file.file import File

from wordpress_api_utils import wordpress_api_utils
from wp_db_service import wp_db_service


class WordpressTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        print(self.runtime.credentials)
        print(tool_parameters)

        if not self.runtime.credentials.get("db_host"):
            raise ToolProviderCredentialValidationError("If you want to use this feature, configure the database connection information in advance")

        service = wp_db_service(self.runtime.credentials)
        if not tool_parameters.get("sql"):
            raise Exception(f"sql parameter is required")
        try:
            result = service.execute(tool_parameters.get("sql"))
            yield self.create_json_message(result)
        except Exception as e:
            raise e

