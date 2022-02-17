from flask import current_app
from json import JSONDecodeError
import requests
from urllib.parse import urlsplit, urlunsplit
from ..utils.exceptions import APIException


def query_katsu(endpoint, id=None, query=None):
    c = current_app.config
    katsu_base_url = c["KATSU_BASE_URL"]
    verify_certificates = not c["BENTO_DEBUG"]
    timeout = current_app.config["KATSU_TIMEOUT"]

    # construct request url 
    url_components = urlsplit(katsu_base_url)
    id_param = "/" + id if id is not None else ""
    query_url = urlunsplit((
        url_components.scheme,
        url_components.netloc,   
        url_components.path + endpoint + id_param,
        url_components.query,
        url_components.fragment
        ))

    print("before request")

    try:
        r = requests.get(
            query_url,
            verify=verify_certificates,
            timeout=timeout
        )
        katsu_response = r.json()    

    except JSONDecodeError:
        # katsu "bad request" repsonse is html, not json
        # todo: logging
        raise APIException()  

    return katsu_response



# katsu "not found" responses:

# for, eg, "/biosamples/id" when id not found: { "detail": "Not found." }

# for search endpoints, eg "/biosamples" when query return no results:
#     {
#       "count": 0,
#       "next": null,
#       "previous": null,
#       "results": []
#      }
