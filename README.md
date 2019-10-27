# De-Lijn-Realtime
###### By Freek De Sagher S0171876

## Contents
1. [Installation](#installation)
    1. [Back end](#back-end)
    2. [Front end](#front-end)
2. [Configuration](#configuration)
3. [API structure](#api-structure)
4. [Design choices](#design-choices)
5. [Used Tools](#used-tools)


## Installation
#### Back-end
The back-end of this application is built with Python and the [Flask](https://palletsprojects.com/p/flask/) framework. To install the project, navigate to the WebServices folder. To be able to install the back-end, Python 3 and pip are required. Install the requirements by running

> pip install -r requirements.txt

When this is done, the back-end server can be started with

> python app.py

The webserver will start on 127.0.0.1:5000 by default. Going to this page will show a brief documentation of the API. This documentation is also given in this document.

#### Front-end
The front-end of this application is built with the  [React](https://reactjs.org/) framework. To install this part of the project, go to web-services-front. To be able to install the front-end  [npm](https://www.npmjs.com/get-npm) is required. Once npm is installed, run

> npm install

To start the development server run

> npm run start

By default, the front end server will start on 127.0.0.1:3000

## Configuration

## API Structure
In this section, all the possible API can be found.

### Error structure
Sometimes exceptions can occur (De Lijn API doesn't always return things, max calls exceeded...). An http error will be thrown with the following structure
```
{
    "message": "message",
    "status": 404 (for example)
}
```

### GET /entities
Get all the entities of De Lijn. Each returned entity has a number (the identifier of the entity) and a description.
If the function succeeds, the response code will be 200. 
```
Example URL: 127.0.0.1:5000/entities
[
    {
        "number": 1,
        "desc": "Antwerpen"
    },
    ...
]
```

### GET /lines
Get all lines of De Lijn. Each line has a number, an entity number (for example 1 = Antwerp), a description, a type ("tram" or "bus") and a service type. If the function succeeds, the response code will be 200.
```
Example URL: 127.0.0.1:5000/lines
[
    {
        "number": 2,
        "entityNumber": 1,
        "desc": "Hoboken - P+R Merksem",
        "type": "tram",
        "serviceType": "normaal"
    },
    ...
]
```

### GET /villages
Get all villages of De Lijn. Each village has an id and a name. If this function succeeds, the response code will be 200.
```
Example URL: 127.0.0.1:5000/villages
[
    ...
    {
        "id": 553,
        "name": "Sint-Katelijne-Waver"
    },
    {
        "id": 554,
        "name": "Oppuurs"
    },
    {
        "id": 555,
        "name": "Sint-Amands"
    },
    ...
]
```
### GET /stops
Get all tram and bus stops of De Lijn. This function takes a lot of time (~40 seconds). If the function succeeds, the response code will be 200.
```
Example URL: 127.0.0.1:5000/stops
[
    {
        "number": "101000",
        "villageName": "Wilrijk",
        "desc": "A. Chantrainestraat",
        "latlng": [
        51.16388937021345,
        4.392073389160737
    ]
    },
    ...
]
```

### GET /lines/{entity_number}/{line_number}/{direction} 
This function returns all stops of a certain line. <br>
<b>Parameters</b>
* entity_number: positive integer; represents the entities of De Lijn. The accepted numbers are \[1, 5\]
* line_number: positive integer; represents the line number, ex. 32
* direction: string; can only be 'HEEN' or 'TERUG'

If this function succeeds, the response code will be 200.
```
Example URL: 127.0.0.1:5000/lines/1/253/HEEN
[
    ...
    {
        "number": 107809,
        "desc": "Kerkhof",
        "village": "Oppuurs",
        "latlng": [
            51.07022693785234,
            4.252991607174736
        ]
    },
    {
        "number": 104449,
        "desc": "Zeutestraat",
        "village": "Puurs",
        "latlng": [
            51.07329594009163,
            4.266924020775759
        ]
    },
    ...
]
```

### GET /weather/{latitude}/{longitude} 
Get the weather of a certain geolocation. <br>
<b>Parameters</b>
* latitude: positive float; the latitude of the geolocation.
* longitude: positive float; the longitude of the geolocation.

<b>Return types</b>
* clouds: percentage
* humidity: percentage
* windspeed: float in m/s
* temp: float in Celsius

If this function succeeds, the response code will be 200.

```
Example URL: 127.0.0.1:5000/weather/51.4/4.4
{
    "clouds": 88,
    "humidity": 58,
    "windspeed": 8.92,
    "desc": "overcast clouds",
    "temp": 18.76
}
```

### GET /vehicles/{entity_number}/{line_number}/{direction} 
Get the geo locations of the vehicles of a certain line. <br>
<b>Parameters</b>
* entity_number: positive integer
* line_number: positive integer
* direction: string; can only be 'HEEN' or 'TERUG'

<b>Return types</b>
* First list item: latitude
* Second list item: longitude


```
Example URL: 127.0.0.1:5000/vehicles/1/32/HEEN
[
  [51.15562, 4.43622],
  [51.19465, 4.42364],
  [51.21025, 4.41818]
]
```


## Design choices

## Used tools
#### Back-end
* [De Lijn API](https://data.delijn.be/) for the bus and tram data
* [TomTom Routing API](https://developer.tomtom.com/routing-api) for routing
* [OpenWeatherMap](https://reactjs.org/) for the weather data
* [Flask Restful](https://flask-restful.readthedocs.io/en/latest/) to create the rest API.
* [Flask Cors](https://flask-cors.readthedocs.io/en/latest/) to configure CORS on the API
#### Front-end
* [Leaflet](https://leafletjs.com/) for map creation
* [Leaflet Routing Machine](https://www.liedman.net/leaflet-routing-machine/) for route calculation and display
* [LRM TomTom](https://github.com/mrohnstock/lrm-tomtom) package to use TomTom api with leaflet routing machine
* [Axios](https://github.com/axios/axios) for http requests
* [React](https://reactjs.org/) core framework used for the front end
* [OpenStreetMap data](https://openstreetmap.org) data used to display the Leaflet map
