import threading

from rest_api_utils import get_page_info, clear_page_info


class ResultTool:

    def queryResult(self,data):
        return {"data":data,
                "page_info":self.__totalHeader__()}

    def updateResult(self,data):
        return {"data":data}

    def deleteResult(self,data):
        return {"data":data}

    def createResult(self,data):
        return {"data":data}
    def __totalHeader__(self):
        try:
            pageInfo = get_page_info()
            return pageInfo
        finally:
            clear_page_info()