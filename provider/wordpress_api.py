from typing import Any

from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError

from wordpress_api_utils import wordpress_api_utils
from wp_db_service import wp_db_service


class WordpressUsermanageProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        try:
            post = wordpress_api_utils(credentials)
            me = post.userMe()
            if "db_host" in credentials:
                wordpress_post = wp_db_service(credentials)
        except Exception as e:
            raise ToolProviderCredentialValidationError(str(e))
