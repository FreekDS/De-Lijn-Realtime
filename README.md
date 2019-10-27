# De-Lijn-Realtime
###### Freek De Sagher S0171876

## Installation
#### Back-end
The back-end of this application is built with Python and the [Flask](https://palletsprojects.com/p/flask/) framework. To install the project, navigate to the WebServices folder. To be able to install the back-end, Python 3 and pip are required. Install the requirements by running

> pip install -r requirements.txt

When this is done, the back-end server can be started with

> python app.py

The webserver will start on 127.0.0.1:5000 by default. Going to this page will show a brief documentation of the API. This documentation is also given in this document.

#### Front-end
The front-end of this application is built with the [React](https://reactjs.org/) framework. To install this part of the project, go to web-services-front. To be able to install the front-end [npm](https://www.npmjs.com/get-npm) is required. Once npm is installed, run

> npm install

To start the development server run

> npm run start

By default, the front end server will start on 127.0.0.1:3000

## API Structure
In this section, all the possible API can be found.

###### Error structure
Sometimes exceptions can occur (De Lijn API doesn't always return things, max calls exceeded...). An http error will be thrown with the following structure
```json
{
    "message": "message",
    "status": 404 (for example)
}
```

###### GET /entities
Get all the entities of De Lijn. Each entity has a number (the identifier of the entity) and a description.
If the function succeeds, the response code will be 200. 
```json
[
    {
        "number": 1,
        "desc": "Antwerpen"
    },
    ...
]
```

## Design choices

## Used tools
#### Back-end

#### Front-end
