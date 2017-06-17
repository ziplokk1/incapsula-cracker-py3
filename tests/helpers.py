from requests import Response


def make_response(url, content, status_code=200):
    response = Response()
    response.url = url
    response._content = content
    response.status_code = status_code
    return response
