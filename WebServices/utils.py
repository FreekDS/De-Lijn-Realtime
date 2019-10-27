import http.client, urllib.request, urllib.parse, urllib.error, base64
import json
from flask_restful import abort
from typing import List
from config import DE_LIJN_API_KEY, WEATHER_API_KEY, TOMTOM_API_KEY

headers = {
    'Ocp-Apim-Subscription-Key': DE_LIJN_API_KEY
}

# TODO Documentation


def make_request(url: str):
    try:
        # Protection against stupid self
        if url[0] != '/':
            url = '/' + url

        # Create connection
        conn = http.client.HTTPSConnection('localhost:5000')

        # Make request
        conn.request("GET", url)
        resp = conn.getresponse()
        status = int(resp.getcode())
        data = resp.read()
        conn.close()
        return json.loads(data), status
    except Exception as e:
        print("Error :'(", e.__str__())


def make_lijn_request(request_type, url, params=None):
    try:
        # Protection against stupid self
        if url[0] != '/':
            url = '/' + url

        # Create connection
        conn = http.client.HTTPSConnection('api.delijn.be')

        # Make request
        if params is None:
            conn.request(request_type, url, "{body}", headers)
        else:
            full_url = url + '?{}'.format(params)  # Format parameters
            conn.request(request_type, full_url, "{body}", headers)
        resp = conn.getresponse()
        status = int(resp.getcode())
        data = resp.read()
        conn.close()
        return json.loads(data), status
    except Exception as e:
        print("Error :'(", e.__str__())


def make_weather_request(lat, lon):
    try:
        conn = http.client.HTTPSConnection("api.openweathermap.org")

        url = "/data/2.5/weather?lat={}&lon={}&appid={}&units=metric".format(lat, lon, WEATHER_API_KEY)
        conn.request("GET", url)
        resp = conn.getresponse()
        data = resp.read()
        status = int(resp.getcode())
        conn.close()
        return json.loads(data), status
    except Exception as e:
        print("Error in fetching weather data", e.__str__())


def make_tomtom_request(lat1, lon1, lat2, lon2):
    try:
        conn = http.client.HTTPSConnection("api.tomtom.com")
        latlon = "{},{}:{},{}".format(lat1, lon1, lat2, lon2)
        url = "/routing/1/calculateRoute/{}/json?key={}&travelMode=bus".format(latlon, TOMTOM_API_KEY)
        conn.request("GET", url)
        resp = conn.getresponse()
        data = resp.read()
        status = int(resp.getcode())
        conn.close()
        return json.loads(data), status
    except Exception as e:
        print("Error in fetching route", e.__str__())


def format_latlng(raw_latlng: dict) -> List[float]:
    """
    The lat lng data is inconsistent in the 'De Lijn' API, convert it to a
    useful structure
    :param raw_latlng: raw lat lng object
    :return: list of the latitude and longitude
    """
    return [float(raw_latlng.get("latitude")), float(raw_latlng.get('longitude'))]


def check_status(status: int, error: str):
    if status == 404:
        abort(status, message="Not Found", error=error, status=status)
    elif status == 400:
        abort(status, message="Bad Request", error=error, status=status)
    elif status == 403:
        abort(status, message="Forbidden", error=error, status=status)
    elif status == 408:
        abort(status, message="Request Timeout", error=error, status=status)
    elif status == 418:
        # just a funny one, found on https://developer.mozilla.org/nl/docs/Web/HTTP/Status/418
        abort(status, message="I'm a teapot", error="The server refuses the attempt to brew coffee with a teapot",
              status=status)
    elif status == 500:
        abort(status, message="Internal Server Error", error=error, status=status)


def get_stop_details(entity_number: int, stop_number: int):
    data, status = make_lijn_request("GET", "DLKernOpenData/api/v1/haltes/{}/{}".format(entity_number,
                                                                                        stop_number))
    check_status(status,
                 "Cannot get stop with number {} for entity {}".format(stop_number, entity_number))

    proc_stop = dict()
    proc_stop["desc"] = data.get("omschrijving")
    proc_stop["entityID"] = data.get("entiteitnummer")
    proc_stop["village"] = data.get("omschrijvingGemeente")
    proc_stop["latlng"] = data.get("geoCoordinaat")
    return proc_stop


def get_entity_from_url(object: dict):
    # Split URL on '/'
    url = object.get("links")[0].get("url").split("/")
    return int(url[len(url) - 2])
