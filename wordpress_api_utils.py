import random
import string
from datetime import datetime

import requests
from dify_plugin.errors.tool import ToolProviderCredentialValidationError
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
    def queryUser(self, tool_parameters):
        self.proxy()
        wp_url = self.wp_url + "/wp-json/wp/v2/users"
        wp_username = self.wp_username
        wp_password = self.wp_password
        params = {
        }
        if tool_parameters.get('username'):
            params['search'] = tool_parameters.get('username')

        if tool_parameters.get("id"):
            wp_url = wp_url + "/" + str(tool_parameters.get('id'))
        params = utils.process_other_parameter(params, tool_parameters)
        auth = HTTPBasicAuth(wp_username, wp_password)

        result = rest_api_utils.call_rest_api("GET", wp_url, auth=auth, params=params)
        return result

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
        self.proxy()
        mediaId = tool_parameters['mediaId']
        wp_url = self.wp_url + "/wp-json/wp/v2/media/" + str(mediaId)
        params = {}
        if "force" in tool_parameters:
            force = tool_parameters['force']
            params["force"] = force.lower()


        wp_username = self.wp_username
        wp_password = self.wp_password

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
        params = {}
        if 'force' in tool_parameters:
            force = tool_parameters['force']
            params["force"] = force.lower()
        if 'reassign' in tool_parameters:
            reassign = tool_parameters['reassign']
            params["reassign"] = reassign


        wp_url = self.wp_url + "/wp-json/wp/v2/users/" + str(userId)


        params = utils.process_other_parameter(params, tool_parameters)
        wp_username = self.wp_username
        wp_password = self.wp_password
        auth = HTTPBasicAuth(wp_username, wp_password)
        result = rest_api_utils.call_rest_api("DELETE", wp_url, auth=auth, params=params)
        return result

    def query_media(self, tool_parameters):

        wp_url = self.wp_url + "/wp-json/wp/v2/media"
        if tool_parameters.get("mediaId"):
            mediaId = tool_parameters['mediaId']
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
        wp_url = self.wp_url + "/wp-json/wp/v2/media/" + str(tool_parameters["mediaId"])
        wp_username = self.wp_username
        wp_password = self.wp_password
        auth = HTTPBasicAuth(wp_username, wp_password)
        data = {
            # "title": tool_parameters["title"],
            # "alt_text": tool_parameters["alt_text"],
            # "caption": tool_parameters["caption"],
            # "description": tool_parameters["description"]
        }
        data.update(tool_parameters)
        data = utils.process_other_parameter(data, tool_parameters)
        result = rest_api_utils.call_rest_api("POST", wp_url, auth=auth, data=data)
        return result

    def query_posts(self, tool_parameters):
        self.proxy()
        wp_url = self.wp_url + "/wp-json/wp/v2/posts"
        if "postsId" in tool_parameters:
            wp_url = wp_url + "/" + str(tool_parameters["postsId"])
        params = {}
        if "categories" in tool_parameters:
            params["categories"] = tool_parameters["categories"]
        params = utils.process_other_parameter(params, tool_parameters)
        wp_username = self.wp_username
        wp_password = self.wp_password

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
        if  tool_parameters.get("content"):
            data["content"] = tool_parameters["content"]
        if tool_parameters.get("title"):
            data["title"] = tool_parameters["title"]
        if  tool_parameters.get("status"):
            data["status"] = tool_parameters["status"]
        if  tool_parameters.get("excerpt"):
            data["excerpt"] = tool_parameters["excerpt"]
        if  tool_parameters.get("slug"):
            data["slug"] = tool_parameters["slug"]
        if tool_parameters.get("date"):
            dt_obj = datetime.strptime(tool_parameters["date"], "%Y-%m-%d %H:%M:%S")
            # 转换为 "YYYY-MM-DDTHH:MM:SS" 格式
            formatted_date = dt_obj.strftime("%Y-%m-%dT%H:%M:%S")
            data["date"] = formatted_date
        if  tool_parameters.get("author"):
            data["author"] = tool_parameters["author"]
        if tool_parameters.get("categories"):
            idlist = tool_parameters["categories"]
            ids = list(map(int, idlist.split(",")))
            data["categories"] = ids
        if tool_parameters.get("tags"):
            idlist = tool_parameters["tags"]
            ids = list(map(int, idlist.split(",")))
            data["tags"] = ids
        if tool_parameters.get("featured_media"):
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

    def delete_post(self, tool_parameters):
        self.proxy()
        post_id = tool_parameters.get('postId')
        force = tool_parameters.get('force')
        wp_url = self.wp_url + "/wp-json/wp/v2/posts/" + str(post_id)
        wp_username = self.wp_username
        wp_password = self.wp_password
        params = {}
        if force:
            params["force"] = force.lower()
        auth = HTTPBasicAuth(wp_username, wp_password)
        params = utils.process_other_parameter(params, tool_parameters)

        result = rest_api_utils.call_rest_api("DELETE", wp_url, auth=auth,params=params)
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
        if  tool_parameters.get("name"):
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
        wp_url = self.wp_url + "/wp-json/wp/v2/categories/" + str(tool_parameters.get("categoriesId"))
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
        params = {}
        if force:
            params["force"] = force.lower()

        auth = HTTPBasicAuth(wp_username, wp_password)

        result = rest_api_utils.call_rest_api("DELETE", wp_url, auth=auth,params=params)
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
            params["search"] = tool_parameters["categoriesName"]

        auth = HTTPBasicAuth(wp_username, wp_password)

        result = rest_api_utils.call_rest_api("GET", wp_url, auth=auth, params=params)
        return result

    def delete_tag(self, tool_parameters):
        self.proxy()
        tagId = tool_parameters["tagId"]
        wp_url = self.wp_url + "/wp-json/wp/v2/tags/" + str(tagId)
        wp_username = self.wp_username
        wp_password = self.wp_password
        params = {}
        if "force" in tool_parameters:
            params["force"] = tool_parameters["force"].lower()

        auth = HTTPBasicAuth(wp_username, wp_password)

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
        params = {}
        if "force" in tool_parameters and tool_parameters["force"] == "true":
            params["force"] = tool_parameters["force"].lower()

        auth = HTTPBasicAuth(wp_username, wp_password)

        params = utils.process_other_parameter(params, tool_parameters)

        result = rest_api_utils.call_rest_api("DELETE", wp_url, auth=auth,params=params)
        return result


if __name__ == '__main__':
    pass
