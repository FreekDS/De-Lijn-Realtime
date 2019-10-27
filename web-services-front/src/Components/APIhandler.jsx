import {API_BASE} from "../config";
import axios from 'axios'

/**
 * This class makes all the calls to the De Lijn Real-Time API.
 */
export default class APIhandler {

    /**
     * Get all the lines.
     * @returns {Promise<AxiosResponse<T>>} A promise that will eventually return all line data.
     */
    getLines() {
        return axios.get(API_BASE + "lines")
    }

    /**
     * Gets the stops of a line
     * @param regionNumber: region number of the line
     * @param lineNumber: number of the line
     * @param direction: direction of the line. This can either be 'HEEN' or 'TERUG'
     * @returns {Promise<AxiosResponse<T>>} A promise that will eventually return the data of the stops of the line
     */
    getLineStops(regionNumber, lineNumber, direction = "HEEN") {
        return axios.get(API_BASE + "lines/" + regionNumber.toString() + "/" + lineNumber.toString() + "/" + direction)
    }

    /**
     * Gets the weather from a location
     * @param location {Array<number>|Object} The location can either be an array of the form [lat, lng] where lat and lng are floats, or an
     * object of the form {lat: <float>, lng: <float>}. The location represents the latitude and longitude
     * @returns {Promise<AxiosResponse<T>>} A promise that will eventually return the weather data of the location
     */
    getWeather(location) {
        console.log(location);
        if (Array.isArray(location))
            return axios.get(API_BASE + "weather/" + location[0] + "/" + location[1]);
        return axios.get(API_BASE + "weather/" + location.lat + "/" + location.lng);
    }

    /**
     * Gets the entities (= regions) from 'De Lijn'
     * @returns {Promise<AxiosResponse<T>>} A promise that will eventually return the entity data
     */
    getEntities() {
        return axios.get(API_BASE + "entities");
    }

    /**
     * Get the vehicles of a line.
     * @param entityNumber {number} Number of the entity of the line
     * @param lineNumber {number} Number of the line itself.
     * @param direction {string} Direction of the line (can only be 'HEEN' or 'TERUG')
     * @returns {Promise<AxiosResponse<T>>} A promise that will eventually return the vehicle locations
     */
    getVehicles(entityNumber, lineNumber, direction) {
        return axios.get(API_BASE + "vehicles/" + entityNumber.toString(10) + "/" + lineNumber.toString(10) + "/" + direction);
    }
}