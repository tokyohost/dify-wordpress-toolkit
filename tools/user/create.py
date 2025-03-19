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

        if not tool_parameters.get('username'):
            raise Exception("username is required")
        if not tool_parameters.get('roles'):
            raise Exception("roles is required")
        if not tool_parameters.get('roles'):
            raise Exception("roles is required")
        if not tool_parameters.get('name'):
            raise Exception("name is required")
        if not tool_parameters.get('last_name'):
            raise Exception("last_name is required")
        if not tool_parameters.get('first_name'):
            raise Exception("first_name is required")
        if not tool_parameters.get('email'):
            raise Exception("email is required")
        if not tool_parameters.get('password'):
            tool_parameters['password'] = ''.join(random.choices(string.ascii_letters + string.digits, k=10))


        user = api.createUser(tool_parameters)

        yield self.create_json_message(user)
