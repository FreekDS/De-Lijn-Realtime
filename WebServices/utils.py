import http.client, urllib.request, urllib.parse, urllib.error, base64
import json
from flask_restful import abort
from typing import List
from config import DE_LIJN_API_KEY, WEATHER_API_KEY, TOMTOM_API_KEY

headers = {
    'Ocp-Apim-Subscription-Key': DE_LIJN_API_KEY
}


def make_lijn_request(request_type, url, params=None):
    """
    Makes a request to the De Lijn API.
    :param request_type: The type of the request, usually 'GET'
    :param url: The url of the request
    :param params: The additional parameters of the request
    :return: a tuple of a json object and a HTTP status code
    """
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
    """
    Makes a request for the OpenWeather API.
    :param lat: latitude of the location to get the weather of. This is a positive float
    :param lon: longitude of the location to get the weather of. This is a positive float
    :return: a json object and an HTTP status code
    """
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
    """
    Make a request for the TomTom Routing API
    :param lat1: latitude of first point of route
    :param lon1: longitude of first point of route
    :param lat2: latitude of second point of route
    :param lon2: longitude of second point of route
    :return: a tuple of a json object and a HTTP status code
    """
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
    Convert the lat lng data to a useful structure
    :param raw_latlng: raw lat lng object
    :return: list of the latitude and longitude
    """
    return [float(raw_latlng.get("latitude")), float(raw_latlng.get('longitude'))]


def check_status(status: int, error: str):
    """
    Check the status code of an HTTP request and abort the request
    :param status: status code of the request
    :param error: additional error message
    :return: Nothing
    """
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
    """
    Get the details of a stop of De Lijn
    :param entity_number: entity number of the stop
    :param stop_number: number of the stop
    :return: a json object with the data of the stop
    """
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


def get_entity_from_url(object: dict) -> int:
    """
    Get the entity number from an object received from De Lijn API.
    :param object: object that contains reference url's
    :return: entity number of the object
    """
    # Split URL on '/'
    url = object.get("links")[0].get("url").split("/")
    return int(url[len(url) - 2])
