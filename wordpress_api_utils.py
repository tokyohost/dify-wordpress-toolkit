import random
import string
from datetime import datetime

import requests
from dify_plugin.errors.tool import ToolProviderCredentialValidationError
from gevent.testing import params
from requests.auth import HTTPBasicAuth

import rest_api_utils
import utils as utils


class wordpress_api_utils:
    config = {}
    wp_url = ""
    wp_username = ""
    wp_password = ""
    domain = ""

    def __init__(self, config):
        self.config = config
        self.wp_url = self.config['website_host']
        self.domain = self.config['website_host']
        self.wp_username = self.config['rest_api_username']
        self.wp_password = self.config['rest_api_secret_passwd']
        if not self.wp_url:
            raise ToolProviderCredentialValidationError("website_host is required")
        if not self.wp_username:
            raise ToolProviderCredentialValidationError("wp_username is required")
        if not self.wp_password:
            raise ToolProviderCredentialValidationError("wp_password is required")

    def userMe(self):
        wp_url = self.wp_url + "/wp-json/wp/v2/media"
        wp_username = self.wp_username
        wp_password = self.wp_password

        auth = HTTPBasicAuth(wp_username, wp_password)

        response = requests.get(wp_url, auth=auth)

        if response.status_code == 200:
            users = response.json()
            if users:
                return users
            else:
                raise Exception(response.text)
        else:
            raise Exception(response.text)

    def uploadMedia(self, file, filename, mime_type):
        print(filename)
        wp_url = self.wp_url + "/wp-json/wp/v2/media"
        wp_username = self.wp_username
        wp_password = self.wp_password

        auth = HTTPBasicAuth(wp_username, wp_password)
        headers = {
            "Content-Disposition": f'attachment; filename="{filename}"',
        }
        files = {
            "file": (filename, file, mime_type)  # (文件名, 文件内容, MIME 类型)
        }
        response = requests.post(wp_url, auth=auth, headers=headers, files=files)
        response.encoding = "utf-8"

        if response.status_code == 201:
            media_data = response.json()
            return media_data
        else:
            print(response.text)
            raise Exception(response.text)

    def searchUser(self, name):
        self.proxy()
        wp_url = self.wp_url + "/wp-json/wp/v2/users?search=" + name
        wp_username = self.wp_username
        wp_password = self.wp_password

        auth = HTTPBasicAuth(wp_username, wp_password)

        response = requests.get(wp_url, auth=auth)

        if response.status_code == 200:
            users = response.json()
            if users:
                return users[0]
            else:
                raise Exception(response.text)
        else:
            raise Exception(response.text)

    def searchUserById(self, id):
        self.proxy()
        wp_url = self.wp_url + "/wp-json/wp/v2/users/" + str(id)
        wp_username = self.wp_username
        wp_password = self.wp_password

        auth = HTTPBasicAuth(wp_username, wp_password)

        response = requests.get(wp_url, auth=auth)

        if response.status_code == 200:
            users = response.json()
            if users:
                return users
            else:
                raise Exception(response.text)
        else:
            raise Exception(response.text)

    def createUser(self, tool_parameters):
        self.proxy()
        # WordPress 站点信息
        wp_url = self.wp_url + "/wp-json/wp/v2/users"
        wp_username = self.wp_username
        wp_password = self.wp_password
        # 认证
        auth = HTTPBasicAuth(wp_username, wp_password)
        data = self.getUserData(tool_parameters)

        response = requests.post(wp_url, json=data, auth=auth)
        print(response.json())

        if response.status_code == 201:
            user = response.json()
            user["existing"] = "false"
            return user
        elif response.json().get("code") == 'existing_user_login':
            user = self.searchUser(data['name'])
            if user:
                user["existing"] = "true"
                return user
            else:
                raise Exception(response.text)
        else:
            raise Exception(response.text)

    def getUserData(self, tool_parameters):
        data = {}
        if tool_parameters.get('username'):
            data["username"] = tool_parameters.get('username')
        if tool_parameters.get('roles'):
            data["roles"] = [tool_parameters.get('roles')]
        if tool_parameters.get('name'):
            data["name"] = tool_parameters.get('name')
        if tool_parameters.get('last_name'):
            data["last_name"] = tool_parameters.get('last_name')
        if tool_parameters.get('first_name'):
            data["first_name"] = tool_parameters.get('first_name')
        if tool_parameters.get('email'):
            data["email"] = tool_parameters.get('email')
        if not tool_parameters.get('password'):
            tool_parameters['password'] = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
        else:
            data["password"] = tool_parameters.get('password')
        return utils.process_other_parameter(data, tool_parameters)

    def updateUserAvator(self, userid, media_id):

        self.proxy()
        wp_url = self.wp_url + "/wp-json/wp/v2/users/" + str(userid)
        wp_username = self.wp_username
        wp_password = self.wp_password
        auth = HTTPBasicAuth(wp_username, wp_password)

        data = {
            "simple_local_avatar": {
                "media_id": media_id
            }
        }

        result = rest_api_utils.call_rest_api("POST", wp_url, auth=auth, data=data)

        return result

    def proxy(self):
        if "enable_proxy" in self.config:
            enableProxy = self.config["enable_proxy"]
            if enableProxy:
                # print("已开启代理")
                self.proxies = {
                    "http": "socks5h://{}:{}".format(
                        self.config["proxy_host"],
                        self.config["proxy_port"]
                    ),
                    "https": "socks5h://{}:{}".format(
                        self.config["proxy_host"],
                        self.config["proxy_port"]
                    ), }

    def delete_media(self, tool_parameters):
        mediaId = tool_parameters['mediaId']
        force = tool_parameters['force']
        self.proxy()
        wp_url = self.wp_url + "/wp-json/wp/v2/media/" + str(mediaId)
        if force:
            wp_url = wp_url + "?force=true"
        wp_username = self.wp_username
        wp_password = self.wp_password
        params = {}
        params = utils.process_other_parameter(params, tool_parameters)
        auth = HTTPBasicAuth(wp_username, wp_password)
        result = rest_api_utils.call_rest_api("DELETE", wp_url, auth=auth, params=params)
        return result

    def update_user(self, tool_parameters):
        self.proxy()
        # WordPress 站点信息
        wp_url = self.wp_url + "/wp-json/wp/v2/users/" + str(tool_parameters['userId'])
        wp_username = self.wp_username
        wp_password = self.wp_password
        # 认证
        auth = HTTPBasicAuth(wp_username, wp_password)
        data = self.getUserData(tool_parameters)
        result = rest_api_utils.call_rest_api("PUT", wp_url, auth=auth, data=data)
        return result

    def delete_user(self, tool_parameters):
        userId = tool_parameters['userId']
        force = tool_parameters['force']
        reassign = tool_parameters['reassign']

        wp_url = self.wp_url + "/wp-json/wp/v2/users/" + str(userId)
        params = {"force": force, "reassign": reassign}
        if force and force is True:
            wp_url = wp_url + "?force=true"

        params = utils.process_other_parameter(params, tool_parameters)
        wp_username = self.wp_username
        wp_password = self.wp_password
        auth = HTTPBasicAuth(wp_username, wp_password)
        result = rest_api_utils.call_rest_api("DELETE", wp_url, auth=auth, params=params)
        return result

    def query_media(self, tool_parameters):
        mediaId = tool_parameters['mediaId']
        wp_url = self.wp_url + "/wp-json/wp/v2/media"
        if mediaId:
            wp_url = wp_url + "/" + str(mediaId)
        wp_username = self.wp_username
        wp_password = self.wp_password
        params = {}
        params = utils.process_other_parameter(params, tool_parameters)
        auth = HTTPBasicAuth(wp_username, wp_password)
        result = rest_api_utils.call_rest_api("GET", wp_url, auth=auth, params=params)
        return result

    def update_media(self, tool_parameters):
        self.proxy()
        # WordPress 站点信息
        wp_url = self.wp_url + "/wp-json/wp/v2/media/" + str(tool_parameters["mediaID"])
        wp_username = self.wp_username
        wp_password = self.wp_password
        # 认证
        auth = HTTPBasicAuth(wp_username, wp_password)
        MEDIA_DATA = {
            "title": tool_parameters["title"],
            "alt_text": tool_parameters["alt_text"],
            "caption": tool_parameters["caption"],
            "description": tool_parameters["description"]
        }
        MEDIA_DATA = utils.process_other_parameter(MEDIA_DATA, tool_parameters)
        result = rest_api_utils.call_rest_api("POST", wp_url, auth=auth, data=MEDIA_DATA)
        return result

    def query_posts(self, tool_parameters):
        self.proxy()
        # WordPress 站点信息
        wp_url = self.wp_url + "/wp-json/wp/v2/posts"
        if "postsId" in tool_parameters:
            wp_url = wp_url + "/" + str(tool_parameters["postsId"])
        params = {}
        if "categories" in tool_parameters:
            params["categories"] = tool_parameters["categories"]
        params = utils.process_other_parameter(params, tool_parameters)
        wp_username = self.wp_username
        wp_password = self.wp_password
        # 认证
        auth = HTTPBasicAuth(wp_username, wp_password)
        result = rest_api_utils.call_rest_api("GET", wp_url, auth=auth, params=params)
        return result

    def create_post(self, tool_parameters):
        self.proxy()
        wp_url = self.wp_url + "/wp-json/wp/v2/posts"
        wp_username = self.wp_username
        wp_password = self.wp_password

        auth = HTTPBasicAuth(wp_username, wp_password)

        data = self.getPostsData(tool_parameters)

        result = rest_api_utils.call_rest_api("POST", wp_url, auth=auth, data=data)
        return result

    def getPostsData(self, tool_parameters):
        data = {
        }
        if "content" in tool_parameters:
            data["content"] = tool_parameters["content"]
        if "title" in tool_parameters:
            data["title"] = tool_parameters["title"]
        if "status" in tool_parameters:
            data["status"] = tool_parameters["status"]
        if "excerpt" in tool_parameters:
            data["excerpt"] = tool_parameters["excerpt"]
        if "slug" in tool_parameters:
            data["slug"] = tool_parameters["slug"]
        if "date" in tool_parameters:
            dt_obj = datetime.strptime(tool_parameters["date"], "%Y-%m-%d %H:%M:%S")
            # 转换为 "YYYY-MM-DDTHH:MM:SS" 格式
            formatted_date = dt_obj.strftime("%Y-%m-%dT%H:%M:%S")
            data["date"] = formatted_date
        if "author" in tool_parameters:
            data["author"] = tool_parameters["author"]
        if "categories" in tool_parameters:
            idlist = tool_parameters["categories"]
            ids = list(map(int, idlist.split(",")))
            data["categories"] = ids
        if "tags" in tool_parameters:
            idlist = tool_parameters["tags"]
            ids = list(map(int, idlist.split(",")))
            data["tags"] = ids
        if "featured_media" in tool_parameters:
            data["featured_media"] = tool_parameters["featured_media"]
        return utils.process_other_parameter(data, tool_parameters)

    def update_post(self, tool_parameters):
        self.proxy()
        wp_url = self.wp_url + "/wp-json/wp/v2/posts/" + str(tool_parameters["postId"])
        wp_username = self.wp_username
        wp_password = self.wp_password

        auth = HTTPBasicAuth(wp_username, wp_password)

        data = self.getPostsData(tool_parameters)

        result = rest_api_utils.call_rest_api("PUT", wp_url, auth=auth, data=data)
        return result

    def delete_post(self, post_id, force):
        self.proxy()
        wp_url = self.wp_url + "/wp-json/wp/v2/posts/" + str(post_id)
        wp_username = self.wp_username
        wp_password = self.wp_password
        if force:
            wp_url = wp_url + "?force=true"

        auth = HTTPBasicAuth(wp_username, wp_password)

        result = rest_api_utils.call_rest_api("DELETE", wp_url, auth=auth)
        return result

    def create_tag(self, tool_parameters):
        data = self.getTagData(tool_parameters)
        self.proxy()
        wp_url = self.wp_url + "/wp-json/wp/v2/tags"
        wp_username = self.wp_username
        wp_password = self.wp_password

        auth = HTTPBasicAuth(wp_username, wp_password)

        result = rest_api_utils.call_rest_api("POST", wp_url, auth=auth, data=data)
        return result

    def getTagData(self, tool_parameters):
        data = {

        }
        if "name" in tool_parameters:
            data["name"] = tool_parameters["name"]
        if "slug" in tool_parameters:
            data["slug"] = tool_parameters["slug"]
        if "description" in tool_parameters:
            data["description"] = tool_parameters["description"]
        return utils.process_other_parameter(data, tool_parameters)

    def update_tag(self, tool_parameters):
        data = self.getTagData(tool_parameters)
        self.proxy()
        wp_url = self.wp_url + "/wp-json/wp/v2/tags/" + str(tool_parameters["tagId"])
        wp_username = self.wp_username
        wp_password = self.wp_password

        auth = HTTPBasicAuth(wp_username, wp_password)

        result = rest_api_utils.call_rest_api("PUT", wp_url, auth=auth, data=data)
        return result

    def query_tags(self, tool_parameters):
        self.proxy()
        wp_url = self.wp_url + "/wp-json/wp/v2/tags"
        wp_username = self.wp_username
        wp_password = self.wp_password
        params = {

        }
        if "tagName" in tool_parameters:
            params["search"] = tool_parameters["tagName"]
        if "tagId" in tool_parameters:
            wp_url = wp_url + "/" + str(tool_parameters["tagId"])

        auth = HTTPBasicAuth(wp_username, wp_password)

        result = rest_api_utils.call_rest_api("GET", wp_url, auth=auth, params=params)
        return result

    def create_categories(self, tool_parameters):
        data = self.getCategoriesData(tool_parameters)
        self.proxy()
        wp_url = self.wp_url + "/wp-json/wp/v2/categories"
        wp_username = self.wp_username
        wp_password = self.wp_password

        auth = HTTPBasicAuth(wp_username, wp_password)

        result = rest_api_utils.call_rest_api("POST", wp_url, auth=auth, data=data)
        return result

    def getCategoriesData(self, tool_parameters):
        data = {
        }
        if "name" in tool_parameters:
            data["name"] = tool_parameters["name"]
        if "slug" in tool_parameters:
            data["slug"] = tool_parameters["slug"]
        if "description" in tool_parameters:
            data["description"] = tool_parameters["description"]
        return utils.process_other_parameter(data, tool_parameters)

    def update_categories(self, tool_parameters):
        data = self.getCategoriesData(tool_parameters)
        self.proxy()
        wp_url = self.wp_url + "/wp-json/wp/v2/categories/" + str(tool_parameters["categoryId"])
        wp_username = self.wp_username
        wp_password = self.wp_password

        auth = HTTPBasicAuth(wp_username, wp_password)

        result = rest_api_utils.call_rest_api("PUT", wp_url, auth=auth, data=data)
        return result

    def delete_categories(self, categoriesId, force):
        self.proxy()
        wp_url = self.wp_url + "/wp-json/wp/v2/categories/" + str(categoriesId)
        wp_username = self.wp_username
        wp_password = self.wp_password
        if force:
            wp_url = wp_url + "?force=true"

        auth = HTTPBasicAuth(wp_username, wp_password)

        result = rest_api_utils.call_rest_api("DELETE", wp_url, auth=auth)
        return result

    def query_categories(self, tool_parameters):
        self.proxy()
        wp_url = self.wp_url + "/wp-json/wp/v2/categories"
        wp_username = self.wp_username
        wp_password = self.wp_password
        params = {

        }
        if "categoriesId" in tool_parameters:
            wp_url = wp_url + "/" + str(tool_parameters["categoriesId"])

        if "categoriesName" in tool_parameters:
            params["name"] = tool_parameters["categoriesName"]

        auth = HTTPBasicAuth(wp_username, wp_password)

        result = rest_api_utils.call_rest_api("GET", wp_url, auth=auth, params=params)
        return result

    def delete_tag(self, tool_parameters):
        self.proxy()
        tagId = tool_parameters["tagId"]
        wp_url = self.wp_url + "/wp-json/wp/v2/tags/" + str(tagId)
        wp_username = self.wp_username
        wp_password = self.wp_password
        if "force" in tool_parameters and tool_parameters["force"] == "True":
            wp_url = wp_url + "?force=true"

        auth = HTTPBasicAuth(wp_username, wp_password)
        params = {}
        params = utils.process_other_parameter(params, tool_parameters)

        result = rest_api_utils.call_rest_api("DELETE", wp_url, auth=auth,params=params)
        return result

    def create_comments(self, tool_parameters):
        data = self.getCommentsData(tool_parameters)
        self.proxy()
        wp_url = self.wp_url + "/wp-json/wp/v2/comments"
        wp_username = self.wp_username
        wp_password = self.wp_password

        auth = HTTPBasicAuth(wp_username, wp_password)

        result = rest_api_utils.call_rest_api("POST", wp_url, auth=auth, data=data)
        return result

    def getCommentsData(self, tool_parameters):
        data = {}
        if "post" in tool_parameters:
            data["post"] = tool_parameters["post"]
        if "content" in tool_parameters:
            data["content"] = tool_parameters["content"]
        if "author_name" in tool_parameters:
            data["author_name"] = tool_parameters["author_name"]
        if "author_email" in tool_parameters:
            data["author_email"] = tool_parameters["author_email"]
        if "parent" in tool_parameters:
            data["parent"] = tool_parameters["parent"]
        return utils.process_other_parameter(data, tool_parameters)

    def update_comments(self, tool_parameters):
        data = self.getCommentsData(tool_parameters)
        self.proxy()
        wp_url = self.wp_url + "/wp-json/wp/v2/comments/" + str(tool_parameters["commentId"])
        wp_username = self.wp_username
        wp_password = self.wp_password

        auth = HTTPBasicAuth(wp_username, wp_password)

        result = rest_api_utils.call_rest_api("PUT", wp_url, auth=auth, data=data)
        return result

    def query_comments(self, tool_parameters):
        params = self.getCommentsData(tool_parameters)
        wp_url = self.wp_url + "/wp-json/wp/v2/comments"

        self.proxy()
        wp_username = self.wp_username
        wp_password = self.wp_password

        if "commentId" in tool_parameters:
            wp_url = wp_url + "/" + str(tool_parameters["commentId"])

        auth = HTTPBasicAuth(wp_username, wp_password)

        result = rest_api_utils.call_rest_api("GET", wp_url, auth=auth, params=params)
        return result

    def delete_comments(self, tool_parameters):
        self.proxy()
        commentId = tool_parameters["commentId"]
        wp_url = self.wp_url + "/wp-json/wp/v2/comments/" + str(commentId)
        wp_username = self.wp_username
        wp_password = self.wp_password
        if "force" in tool_parameters and tool_parameters["force"] == "True":
            wp_url = wp_url + "?force=true"

        auth = HTTPBasicAuth(wp_username, wp_password)
        params = {}
        params = utils.process_other_parameter(params, tool_parameters)

        result = rest_api_utils.call_rest_api("DELETE", wp_url, auth=auth,params=params)
        return result


if __name__ == '__main__':
    pass
