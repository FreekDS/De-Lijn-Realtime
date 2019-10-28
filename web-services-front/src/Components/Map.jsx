import L from 'leaflet'
import 'leaflet-routing-machine'
import '../dist/L.Routing.TomTom'
import React, {Component} from 'react'
import {TOMTOM_API_KEY} from "../config";

/**
 * Types of the Leaflet markers. Contains the icon, sizes and anchors.
 * @type {{BUS: {name: string, icon: *}, STOP: {name: string, icon: *}}}
 */
const markerTypes = {
    STOP: {
        name: "stop",
        icon: L.icon({
            iconUrl: process.env.PUBLIC_URL + 'stop.png',
            iconSize: [38, 38],
            iconAnchor: [19, 38],
            popupAnchor: [0, -40]
        })
    },
    BUS: {
        name: "bus",
        icon: L.icon({
            iconUrl: process.env.PUBLIC_URL + "bus.svg",
            iconSize: [20, 20],
            iconAnchor: [10, 10]
        })
    }
};


/**
 * This React component show the Leaflet OpenStreetMap to the screen. The props received from the parent are
 *  1. stop_markers: the array of stop objects.
 *  2. bus_markers: the array of bus objects
 *  3. api: the APIhandler class
 * The React state of this class consists of:
 *  1. map: the Leaflet map instance (L.map)
 *  2. markers: an array which will be populated with the marker objects (L.marker)
 *  3. markerLayer: a LayerGroup object (L.layerGroup) where the stop markers will be stored for future use
 *  4. busLayer: a layerGroup object (L.layerGroup) where the bus markers will be put on
 *  5. routingControl: routing control used for drawing the routes (L.Control)
 */
class OpenMap extends Component {
    constructor(props) {
        super(props);

        // Initialize the React state
        this.state = {
            map: null,
            markerLayer: null,
            busLayer: null,
            routingControl: null
        }
    }

    /**
     * This function gets called when the component mounts.
     * The map will be initialized with a layer group for the markers.
     */
    componentDidMount() {
        // Create leaflet map
        let map = L.map("map", {
            center: [50.85045, 4.34878],
            zoom: 9,
            useCache: true,
            layers: [
                // Tile provider for the map tiles
                L.tileLayer("https://a.tile.openstreetmap.org/{z}/{x}/{y}.png", {
                    attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors',
                })
            ]
        });
        let markerLayer = L.layerGroup().addTo(map);    // create marker layer group
        let busLayer = L.layerGroup().addTo(map);
        map.invalidateSize();   // Updates size of the map
        this.setState({map, markerLayer, busLayer});  // Updates the state of the component
    }

    /**
     * Updates the popup of the marker after fetching the weather data.
     * @param marker: the marker of which the popup needs to be updated
     * @param generalData: general marker data. This is the data of the stops as it was returned from the API
     * @param weatherData: weather data as it was returned from the API
     */
    updateMarkerPopup(marker, generalData, weatherData) {
        let popupData = "<div><b>" + generalData.desc.toString() + "</b><p>Place: " + generalData.village.toString() +
            "<br> Weather: " + weatherData.desc.toString() + "<br> Temperature: " + weatherData.temp.toString(10) +
            "°C <br>Wind speed: " + weatherData.windspeed.toString(10) + "m/s <br>Humidity: " + weatherData.humidity.toString() +
            "%<br>Cloud coverage: " + weatherData.clouds + "%</p></div>";
        marker._popup.setContent(popupData);
    }

    /**
     * Clears the old markers and add the new markers to the map. This function is also calls the function to
     * display the route.
     * @param data: stop data in the form it was returned from the API
     * @param markerLayer: layer group the markers are attached to
     */
    updateStopMarkers(data, markerLayer) {
        let list = data.stops;      // Get the stops data from all the returned data
        let markers = [];

        if (list === undefined)     // Sometimes the data is undefined. If so, do nothing in this function
            return;
        markerLayer.clearLayers();  // Remove old markers from the map
        for (const obj of list) {
            let latlng = {
                lat: obj.latlng[0],
                lng: obj.latlng[1]
            };
            let marker = L.marker(latlng, {icon: markerTypes.STOP.icon}).addTo(markerLayer);    // Create marker object
            marker.bindPopup('<b>' + obj.desc.toString() + "</b>", {autoClose: false}); // Bind popup to marker
            marker.on('click', () => {                                  // Add click listener
                this.props.api.getWeather(obj.latlng)                            // On click: fetch weather and update
                    .then(res =>                                                 // and stop marker
                        this.updateMarkerPopup(marker, obj, res.data)
                    )
                    .catch(err => console.error(err))
            });
            markers.push(marker);   // Add markers to the marker list
        }
        this.setState({markers});

        // Do some routing
        this.updateRoute(data.route);
    }

    /**
     * Update the bus route
     * @param route {Array} array of lat lng objects. Gotten from API call
     */
    updateRoute(route) {
        // Get variables from the state
        let {routingControl, map} = this.state;

        if (routingControl !== undefined && routingControl !== null) // If the routing control has been set before, remove it
            map.removeControl(routingControl);

        try {
            // Create routing control (leaflet routing machine and TomTom routing)
            let control = L.Routing.control({
                router: new L.Routing.TomTom(TOMTOM_API_KEY),
                waypoints: route,
                show: false,
                waypointMode: 'snap',
                addWaypoints: false,
                createMarker: function () {     // empty callback function so that no markers get created
                }
            }).addTo(map);
            control.hide(); // Hide the direction details
            this.setState({routingControl: control, map}) // Update the state
        } catch (e) {
            console.error("Problem trying to create route", e)
        }
    }

    updateBusMarkers(locations, busLayer) {
        if (locations === undefined || locations === null)
            return;
        busLayer.clearLayers();
        for (const location of locations) {
            L.marker({lat: location[0], lng: location[1]}, {icon: markerTypes.BUS.icon}).addTo(busLayer);
        }
    }

    /**
     * This function gets called when the component gets updated (the props or the state get updated)
     * @param prevProps The previous props from before the update
     * @param prevState The state from before the update
     * @param snapshot A snapshot from before the update
     */
    componentDidUpdate(prevProps, prevState, snapshot) {
        // Only call updateStopMarkers if the prev props are different from the new ones
        if (prevProps !== this.props) {
            if (prevProps.stop_markers !== this.props.stop_marker) {
                this.updateStopMarkers(this.props.stop_markers, this.state.markerLayer);
                let {busLayer} = this.state;
                busLayer.clearLayers();
            }
            if (prevProps.bus_markers !== this.props.bus_markers) {
                this.updateBusMarkers(this.props.bus_markers, this.state.busLayer);
            }
        }
    }

    /**
     * Renders the map
     * @returns {*} it really just renders the map
     */
    render() {
        return <React.Fragment>
            <div id="map"/>
        </React.Fragment>;
    }

}

// Export component
export default OpenMap;