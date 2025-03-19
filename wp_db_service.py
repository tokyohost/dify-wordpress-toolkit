import json
from datetime import date, datetime

import mysql.connector
from dify_plugin.errors.tool import ToolProviderCredentialValidationError

import utils


class wp_db_service:
    config = {}
    cursor = None
    conn = None
    def __init__(self,config):
        self.config = config
        self.initDb(config)
        pass
    def initDb(self,config):

        if "db_host" not in config:
            raise ToolProviderCredentialValidationError("db_host is required")

        if "db_user" not in config:
            raise ToolProviderCredentialValidationError("db_user is required")

        if "db_port" not in config:
            raise ToolProviderCredentialValidationError("db_port is required")

        if "db_password" not in config:
            raise ToolProviderCredentialValidationError("db_password is required")

        if "db_database" not in config:
            raise ToolProviderCredentialValidationError("db_database is required")


        # 连接 MySQL
        self.conn = mysql.connector.connect(
            host=config["db_host"],  # MySQL 服务器地址，例如 localhost
            user=config["db_user"],  # 用户名
            port=config["db_port"],  # port
            password=config["db_password"],  # 密码
            database=config["db_database"]  # 数据库名称
        )

        self.cursor = self.conn.cursor()
    def updateMedia(self,userId,mediaId):
        """
                更新 WordPress 媒体（附件）的归属用户
                :param mediaId: 附件的 ID (wp_posts 表中的 ID)
                :param userId: 新的用户 ID (wp_users 表中的 ID)
                """
        try:
            sql = "UPDATE wp_posts SET post_author = %s WHERE ID = %s"
            self.cursor.execute(sql, (userId, mediaId))
            self.conn.commit()

            if self.cursor.rowcount > 0:
                print(f"✅ 更新成功：媒体 ID {mediaId} 的归属用户修改为 {userId}")
            else:
                print(f"⚠️ 更新失败：没有找到 ID {mediaId} 的附件或用户 ID {userId} 无效")
                raise Exception("⚠️ 更新失败：没有找到 ID {mediaId} 的附件或用户 ID {userId} 无效")

        except mysql.connector.Error as err:
            print(f"❌ 数据库错误: {err}")
            self.conn.rollback()
            raise err


    def close(self):
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()

    def execute(self, sql):
        sql_type = utils.get_sql_type_regex(sql)  # 获取 SQL 类型
        cursor = None
        try:
            cursor = self.conn.cursor(dictionary=True) if sql_type == "SELECT" else self.conn.cursor()
            cursor.execute(sql)

            if sql_type == "SELECT":
                result = cursor.fetchall()
                return {"success":True,"data":result} if result else None
            elif sql_type in ("INSERT", "UPDATE", "DELETE"):
                self.conn.commit()
                return {"success":True,"affected_rows":cursor.rowcount}
            else:
                raise ValueError(f"Unsupported SQL type: {sql_type}")

        except mysql.connector.Error as err:
            print(err)
            self.conn.rollback()
            raise err
        finally:
            if cursor:
                cursor.close()



