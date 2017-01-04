import json
from flask import make_response


class BasicRestApi:
    def __init__(self):
        self.__response = make_response()

    def set_response(self, status=None, data=None):
        self.__response.data = json.dumps(data)
        if status:
            self.__response.status_code = status
        else:
            self.__response.status_code = 200
        self.headers()
        return self.__response

    def headers(self):
        self.__response.headers['Content-Type'] = 'application/json'


class RestApi(BasicRestApi):

    def response(self, status=None, data=None, msg=None):
        if msg:
            data = {
                'data': data,
                'msg': msg
            }
        return self.set_response(status=status, data=data)


class ErrorRestApi(BasicRestApi):

    def response(self, status=None, errors=None):
        data = {
            'errors': []
        }
        for e in errors:
            if type(e) is dict:
                data['errors'].append(e)
            else:
                data['errors'].append({
                    'title': e
                })

        if not status:
            status = 400
        return self.set_response(status=status, data=data)
