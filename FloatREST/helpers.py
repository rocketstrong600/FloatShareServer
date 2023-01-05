from flask import Response

def jsonRes(response):
    respond = Response(response=response, status=200, mimetype="application/json")
    respond.headers["Content-Type"] = "application/json; charset=utf-8"
    return respond