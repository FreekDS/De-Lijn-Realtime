from flask import Flask, render_template
from flask_restful import Resource, Api
from flask_cors import CORS
from datetime import datetime, timedelta
from utils import *
from typing import List, Any, Tuple

app = Flask(__name__)
CORS(app)
app.config['TEMPLATES_AUTO_RELOAD'] = True
api = Api(app)


@app.route('/')
def documentation() -> Any:
    """
    Renders the API documentation
    :return: rendered template of index.html
    """
    return render_template("index.html")


class GetEntities(Resource):
    def get(self):
        """
        Get all the entities of "De Lijn".
        :return: Formatted version of the entities. List of objects. Each object has a number and a description.
        """
        raw_data, status = make_lijn_request("GET", "/DLKernOpenData/api/v1/entiteiten")
        if raw_data is None:
            check_status(404, "Please try again")
        check_status(status, "Could not get entities from De Lijn")
        raw_data = raw_data.get("entiteiten")
        return GetEntities.format_data(raw_data), 200

    @staticmethod
    def format_data(raw):
        entities = list()
        for raw_entity in raw:
            entity = dict()
            if raw_entity is None:
                check_status(500, "Entity '{}' from De Lijn is None".format(raw_entity))
            entity['number'] = int(raw_entity.get("entiteitnummer"))
            entity['name'] = raw_entity.get("omschrijving")
            entities.append(entity)
        return entities


class GetVillages(Resource):
    def get(self) -> tuple:
        """
        Send request to De Lijn API for the villages
        Modify received data and only return interesting data
        :return: json array of objects: {id: int, name: string}
        """
        raw_data, status = make_lijn_request("GET", "/DLKernOpenData/api/v1/gemeenten")
        check_status(status, "Cannot get villages from De Lijn")
        raw_data = raw_data.get("gemeenten")
        proc_data = GetVillages.format_data(raw_data)
        return proc_data, 200

    @staticmethod
    def format_name(name: str) -> str:
        """
        Format village name into correct form
        Names start with a capital letter, each part of name separated with '-' or a space start with capital letter
        :param name: incorrect formatted name : string
        :return: correct formatted name : string
        """
        nextUpper = True
        new_name = str()
        for char in name:
            if char == '-' or char == ' ':
                new_name += char
                nextUpper = True
                continue
            if nextUpper:
                new_name += char.upper()
                nextUpper = False
            else:
                new_name += char.lower()
        return new_name

    @staticmethod
    def format_data(raw: dict) -> List[dict]:
        """
        Process received data and delete unnecessary data
        :param raw: raw unprocessed data
        :return: list of dictionaries containing the essential data: id and name
        """
        processed = list()
        for raw_village in raw:
            proc_village = dict()
            proc_village['id'] = raw_village.get('gemeentenummer')
            if proc_village['id'] < 0:
                continue
            proc_village['name'] = GetVillages.format_name(raw_village.get('omschrijving'))
            processed.append(proc_village)
        return processed


class GetAllStops(Resource):
    def get(self):
        """
        Get all stops and clean up the data
        :return: json array of the useful data: {stopNumber, villageID, villageName, desc, latlng}
        """
        raw_data, status = make_lijn_request("GET", "/DLKernOpenData/api/v1/haltes")
        check_status(status, "Cannot get all stops from De Lijn")
        raw_data = raw_data.get("haltes")
        proc_data = GetAllStops.format_data(raw_data)
        return proc_data, 200

    @staticmethod
    def format_data(raw: dict) -> List[dict]:
        """
        Format the raw data in a more useful structure
        :param raw: data as it was received from the 'De Lijn' API
        :return: json array of the useful data
        """
        proc_data = list()
        for raw_stop in raw:
            stop = GetAllStops.format_stop(raw_stop)
            proc_data.append(stop)
        return proc_data

    @staticmethod
    def format_stop(raw_stop: dict) -> dict:
        """
        Format a single stop to a more useful representation
        :param raw_stop: single stop as it was received from the 'De lijn' API
        :return: dictionary of the stop with the useful data
        """

        proc_stop = dict()
        try:
            proc_stop['number'] = int(raw_stop.get('haltenummer'))
            proc_stop['villageName'] = raw_stop.get("omschrijvingGemeente")
            proc_stop['desc'] = raw_stop.get("omschrijving")
            proc_stop["latlng"] = format_latlng(raw_stop.get("geoCoordinaat"))
        except Exception as e:
            print("Error occurred in formatting stop", raw_stop, "Error:", e)

        return proc_stop


class GetAllLines(Resource):
    def get(self) -> tuple:
        """
        Get all the lines of De Lijn API in a useful format
        :return: tuple: (processed data, status code)
        """
        raw_data, status = make_lijn_request('GET', "/DLKernOpenData/api/v1/lijnen")
        check_status(status, "Cannot get all the lines from De Lijn")
        raw_data = raw_data.get("lijnen")
        proc_data = GetAllLines.format_data(raw_data)
        return proc_data, 200

    @staticmethod
    def format_data(raw_data: dict) -> List[dict]:
        """
        Format data in a useful format
        :param raw_data: raw un-edited data
        :return: List of dictionaries containing the lines. A line has a number, entity number, description, type
        and service type
        """
        proc_lines = list()
        for raw_line in raw_data:
            proc_line = dict()
            proc_line['number'] = int(raw_line.get("lijnnummer"))
            proc_line['entityNumber'] = int(raw_line.get("entiteitnummer"))
            proc_line['desc'] = raw_line.get("omschrijving")
            proc_line['type'] = raw_line.get("vervoertype").lower()
            proc_line['serviceType'] = raw_line.get("bedieningtype").lower()
            proc_lines.append(proc_line)
        return proc_lines


class GetStopsOfLine(Resource):
    def get(self, entity_number: int, line_number: int, direction: str) -> tuple:
        """
        Gets all the stops of a certain line in a certain direction.
        :param entity_number: number of the region
        :param line_number: number of the line
        :param direction: direction of the line, can either be 'HEEN' or 'TERUG'
        :return: tuple: (formatted data, status code). De returned data is a dictionary containing 1. stops: the stops
        of the line and 2. route: a list of lat lng lists, the coordinates of the stops
        """
        # Correctness checking
        try:
            entity_number = int(entity_number)
        except Exception as e:
            check_status(400, "Entity number has to be an integer")
        try:
            line_number = int(line_number)
        except Exception as e:
            check_status(400, "Line number has to be an integer")
        if entity_number < 1:
            check_status(400, "Entity number has to be an integer >= 1, got {}".format(entity_number))
        if line_number < 1:
            check_status(400, "Line number has to be an integer >= 1, got {}".format(line_number))
        if direction != "HEEN" and direction != "TERUG":
            check_status(400, "Direction can only be 'HEEN' or 'TERUG', got {}".format(direction))

        today = datetime.today()
        last_monday = (today - timedelta(days=today.weekday())).strftime("%Y-%m-%d")
        url = "DLKernOpenData/api/v1/lijnen/{}/{}/lijnrichtingen/{}/dienstregelingen?datum={}" \
            .format(entity_number,
                    line_number,
                    direction,
                    last_monday)
        raw_data, status = make_lijn_request("GET", url)
        check_status(status, "Cannot get stops of line with entity number {}, line number {}, and direction {}".format(
            entity_number, line_number, direction))
        raw_data = raw_data.get("ritDoorkomsten")[0].get("doorkomsten")
        proc_data = GetStopsOfLine.format_data(raw_data)
        route = self.createRoute(proc_data)

        result = {
            "stops": proc_data,
            "route": route
        }
        return result, 200

    def createRoute(self, stops: List[dict]) -> List[list]:
        """
        Create a route list based on the received data. The data is expected to be processed by GetStopsOfLine.format_data
        :param stops: List of dictionaries containing the processed stops
        :return: List of lat lng lists: the coordinates of the stops
        """
        locations = list()
        for stop in stops:
            latlng = stop.get("latlng")
            locations.append([latlng[0], latlng[1]])
        return locations

    @staticmethod
    def format_data(raw: List[dict]) -> List[dict]:
        """
        Formats the raw data in a more useful format
        :param raw: Raw data as it was received by the De Lijn API
        :param entity_number: number of the region
        :return: List of dictionaries that describe a stop. Stops have a number, description, village description and
        lat lng list
        """
        proc_data = list()
        for raw_stop in raw:
            proc_stop = dict()
            proc_stop["number"] = int(raw_stop.get("haltenummer"))

            # Get the entity number
            entity_number = get_entity_from_url(raw_stop)

            if entity_number < 1 or entity_number is None:
                check_status(500,
                             "Cannot get stop with number {}: there is no entity number {}".format(proc_stop["number"],
                                                                                                   entity_number))

            stop_details = get_stop_details(entity_number, proc_stop["number"])

            proc_stop["desc"] = stop_details.get("desc")
            proc_stop["village"] = stop_details.get("village")
            proc_stop["latlng"] = format_latlng(stop_details.get("latlng"))
            proc_data.append(proc_stop)
        return proc_data


class WeatherChecker(Resource):
    def get(self, lat: str, lon: str) -> Tuple[Any, int]:
        """
        Gets the weather for a certain geolocation. This function aborts if the input data is not correct or if
        an internal API returned an incorrect result. This function returns a dictionary with the weather details
        and 200 (HTTP OK)
        :param lat: Latitude of geolocation
        :param lon: longitude of geolocation
        :return: Weather details:
        {clouds: float (percentage), humidity: float (percentage), windspeed: float, desc: str, temp: float (in Celsius)}
        and 200 (HTTP OK)
        :exception: An internal API failed
        :rtype: tuple
        """
        # Check input variables
        try:
            lat = float(lat)
            if lat < 0:
                raise Exception
        except Exception:
            check_status(400, "Latitude must be a positive float, got {}".format(lat))

        try:
            lon = float(lon)
            if lon < 0:
                raise Exception
        except Exception:
            check_status(400, "Longitude must be a positive float, got {}".format(lon))

        # Make request
        raw_data, status = make_weather_request(lat, lon)

        # Check response
        if raw_data is None:
            check_status(404, "Cannot find location ({}, {})".format(lat, lon))
        check_status(status, "Cannot fetch weather from location ({},{})".format(lat, lon))

        # Format data
        data = self.format_data(raw_data)

        # return result
        return data, 200

    def format_data(self, raw_weather: dict) -> dict:
        """
        Formats the weather response
        :param raw_weather: response data
        :return: formatted form of weather
        :rtype: dict
        """
        if raw_weather is None:
            check_status(500, "Unexpected result from weather api")

        formatted = dict()
        formatted['clouds'] = float(raw_weather.get("clouds").get('all'))
        formatted['humidity'] = float(raw_weather.get('main').get('humidity'))
        formatted['windspeed'] = float(raw_weather.get('wind').get('speed'))
        formatted['desc'] = raw_weather.get("weather")[0].get("description")
        celsius = float(raw_weather.get('main').get('temp'))
        formatted['temp'] = celsius
        return formatted


class GetVehicleLocations(Resource):
    def get(self, entity_number: str, line_number: str, direction: str) -> Tuple[Any, int]:
        """
        Get the geo locations of the vehicles on the selected line. This function aborts if the input parameters are
        incorrect or if an internal API doesn't behave as expected. This function returns the vehicle locations (a list
        of lists) and 200 (HTTP OK)
        :param entity_number: region number of the line
        :param line_number: number of the line
        :param direction: direction of the line ('HEEN' or 'TERUG')
        :return: the locations of the vehicles (list of lists: each list has 2 entries, the first one is the latitude,
        the second is the longitude) and 200 (HTTP OK)
        """
        # Try converting the input to there correct form
        try:
            entity_number = int(entity_number)
        except Exception as e:
            check_status(400, "Entity number has to be an integer")
        try:
            line_number = int(line_number)
        except Exception as e:
            check_status(400, "Line number has to be an integer")

        # Check for correct values of the parameters
        if entity_number < 1:
            check_status(400, "Entity number has to be an integer >= 1, got {}".format(entity_number))
        if line_number < 1:
            check_status(400, "Line number has to be an integer >= 1, got {}".format(line_number))
        if direction != "HEEN" and direction != "TERUG":
            check_status(400, "Direction can only be 'HEEN' or 'TERUG', got {}".format(direction))

        # Create URL
        url = "/DLKernOpenData/api/v1/lijnen/{}/{}/lijnrichtingen/{}/dienstregelingen".format(entity_number,
                                                                                              line_number, direction)

        # Make the request and check the status
        raw_data, status = make_lijn_request("GET", url
                                             .format(entity_number, line_number, direction))
        check_status(status, "Cannot get real time location for entity number {}, line number {} and direction {}"
                     .format(entity_number, line_number, direction))
        # Sometimes De Lijn returns nothing
        if raw_data is None:
            check_status(500, "Cannot get real time location, De Lijn API didn't return anything")
        raw_data = raw_data.get("ritDoorkomsten")
        # Format data
        return self.format_data(raw_data), 200

    def format_data(self, raw_data: dict) -> List[List[float]]:
        """
        Format the data in a useful format. (List of lists)
        :param raw_data: the data received from De Lijn API
        :return: formatted data
        """
        result = list()
        for ride in raw_data:
            vehicle_loc = self.get_vehicle_from_ride(ride)
            if vehicle_loc is not None:
                result.append(vehicle_loc)
        return result

    def get_vehicle_from_ride(self, ride: dict) -> List[float] or None:
        """
        Get the location of a vehicle from the ride details.
        :param ride: the ride details
        :return: location of the vehicle. None if the location could not be determined or if there is no location to
        provide.
        """
        last_stop = None  # Stores the stop the vehicle just passed
        next_stop = None  # Stores the stop the vehicle will pass next
        transits = ride.get("doorkomsten")
        now = datetime.now()
        for stop in transits:
            time_str = stop.get("dienstregelingTijdstip")
            # If there is no timetable, go to next stop
            if time_str is None:
                continue
            # convert to date time object
            time = datetime.strptime(time_str, '%Y-%m-%dT%H:%M:%S')

            # Update the last stop or the next stop
            if last_stop is not None and time < now:
                last_stop = stop
            elif last_stop is not None and time > now:
                # We found the last stop
                next_stop = stop
                break
            else:
                last_stop = stop
                continue

        # If there is no next stop, the vehicle finished the ride
        if next_stop is None:
            return None

        # Get timetable times of the stops
        last_time = datetime.strptime(last_stop.get("dienstregelingTijdstip"), "%Y-%m-%dT%H:%M:%S")
        next_time = datetime.strptime(next_stop.get("dienstregelingTijdstip"), "%Y-%m-%dT%H:%M:%S")

        # Calculate the percentage of the route the vehicle covered
        percentage = self.calculate_percentage(last_time, next_time)
        if percentage is None:
            return None

        # Get number of the stop
        last_number = last_stop.get("haltenummer")
        next_number = next_stop.get("haltenummer")

        # Get geolocation of both stops
        entity_number = get_entity_from_url(last_stop)
        latlng_last = get_stop_details(entity_number, last_number).get("latlng")
        entity_number = get_entity_from_url(next_stop)
        latlng_next = get_stop_details(entity_number, next_number).get("latlng")

        # Calculate route between the two geo locations
        lat1, lng1 = latlng_last.get("latitude"), latlng_last.get("longitude")
        lat2, lng2 = latlng_next.get("latitude"), latlng_next.get("longitude")
        resp, status = make_tomtom_request(lat1, lng1, lat2, lng2)
        check_status(status, "Cannot get route from TomTom API")

        # Get route and get the location of the current vehicle
        route = resp["routes"][0]["legs"][0]["points"]
        index = int(len(route) * percentage)
        return [float(route[index]["latitude"]), float(route[index]["longitude"])]

    def calculate_percentage(self, last_time: datetime, next_time: datetime) -> float or None:
        """
        Calculate the percentage the vehicle has driven on the route.
        :param last_time: the time of the last stop
        :param next_time: the expected time of the next stop
        :return: percentage (float) or None if the percentage could not be calulated
        """
        now = datetime.now()
        time_since_last = now - last_time
        time_between = next_time - last_time  # Time in between the two stops
        # Avoid division by 0
        if time_between == 0:
            percentage = 0
        else:
            percentage = time_since_last.seconds / time_between.seconds
        # If percentage is incorrect, return None
        if percentage > 1 or percentage < 0:
            return None
        return percentage


# Create the REST API resources
api.add_resource(GetEntities, "/entities")
api.add_resource(GetAllLines, "/lines")
api.add_resource(GetVillages, "/villages")
api.add_resource(GetAllStops, "/stops")
api.add_resource(GetStopsOfLine, "/lines/<entity_number>/<line_number>/<direction>")
api.add_resource(WeatherChecker, "/weather/<lat>/<lon>")
api.add_resource(GetVehicleLocations, "/vehicles/<entity_number>/<line_number>/<direction>")

# TODO check error handling
# TODO testing
# TODO update documentation

if __name__ == '__main__':
    app.run(debug=True)
