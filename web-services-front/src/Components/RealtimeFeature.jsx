import React, {Component} from "react";
import OpenMap from "./Map";
import APIhandler from "./APIhandler";
import LineSelector from './LineSelector'
import {Loading} from './Loading'
import {INTERVAL} from "../config";

/**
 * Container of the application. This React component contains all the necessary components for a working application.
 * This component renders a loading screen, the line selector form, and the OpenStreetMap map.
 * This component holds the API handler, and a React state in its state.
 * The React state of this component consists of:
 *  1. stops: this array that will be populated with the stops of the currently selected line.
 *  2. buses: this array will be populated with the buses that are on the selected line
 *  3. loading: boolean that will be true if the application is in a loading state. The loading state will be active
 *     when the application is fetching the line. This takes some time.
 *  4. currentLine: an object that holds the currently selected line.
 */
export default class RealtimeFeature extends Component {
    /**
     * Constructor of the RealTimeFeature component
     * @param props: props received from the parent component
     */
    constructor(props) {
        super(props);
        this.api = new APIhandler();

        // React state
        this.state = {
            stops: [],
            buses: [],
            loading: false,
            intervalHandler: null,
            currentLine: {
                region: -1,
                line: -1,
                dir: 'NONE'
            }
        };
        // Bind methods to this component. If we dont do this, we can't pass the methods as props to child components
        // without them knowing they are attached to an instance of this class
        this.selectLine = this.selectLine.bind(this);
        this.updateBusRealTime = this.updateBusRealTime.bind(this);
    }

    /**
     * Select a line. This function will set the React state loading property to true when it starts.
     * An API call will be made with the APIhandler in the state. This usually takes some time. When the line
     * data has been received, the loading state will be set to false again and the stops property of the React state
     * will be populated with the stops data.
     * @param regionNumber: Region number of the line. ex. Antwerp = 1
     * @param lineNumber: The number of the line. ex. 253
     * @param direction: The direction of the line. This can either be 'HEEN' or 'TERUG'
     */
    selectLine(regionNumber, lineNumber, direction) {
        let {intervalHandler} = this.state;
        if (intervalHandler) {
            // If an update procedure is running, cancel it.
            clearInterval(intervalHandler)
        }

        let currentLine = {
            region: regionNumber,
            line: lineNumber,
            direction: direction
        };

        this.setState({loading: true, currentLine});
        this.api.getLineStops(regionNumber, lineNumber, direction).then(res => {
            this.setState({stops: res.data, loading: false});
        })
            .catch(error => {
                console.error("Cannot get line, please try again...", error.message);
                // Setting state to other current line will cancel bus update
                this.setState({loading: false, currentLine: {region: -1, line: -1, direction: 'NONE'}});
            });
        this.api.getVehicles(regionNumber, lineNumber, direction).then(res => {
            // Start update procedure only if no error occurred in function above
            let {currentLine} = this.state;
            if (currentLine.region === regionNumber && currentLine.direction === direction && currentLine.line === lineNumber) {
                let interval = setInterval(() => this.updateBusRealTime(regionNumber, lineNumber, direction), INTERVAL);
                this.setState({buses: res.data, intervalHandler: interval});
            }
        })
            .catch(error => {
                console.error("Cannot get buses, please try again...", error.message);
            })
    }

    /**
     * This function will be called periodically to update the bus locations. The visual update will only happen if
     * the user didn't pick another line in the meantime.
     * @param regionNumber {number} The number of the region
     * @param lineNumber {number} The number of the line
     * @param direction {string} The direction of the line (HEEN or TERUG)
     */
    updateBusRealTime(regionNumber, lineNumber, direction) {
        let {intervalHandler} = this.state;
        this.api.getVehicles(regionNumber, lineNumber, direction).then(res => {
            let {currentLine} = this.state;
            if (currentLine.region === regionNumber && currentLine.direction === direction && currentLine.line === lineNumber)
                this.setState({buses: res.data});
            else
                clearInterval(intervalHandler)
        })
    }

    /**
     * Render function of the component. Renders the loading screen if needed, the LineSelector component
     * and the OpenMap component
     * @returns {*}: html structure of the component
     */
    render() {
        // Get necessary data from the state
        const {stops, buses, loading} = this.state;
        return (
            <React.Fragment>
                <div className="row">
                    {loading && <div id="loading"><Loading/></div>}
                    <LineSelector className="col" api={this.api} selector={this.selectLine} loading={loading}/>
                    <OpenMap className="col" stop_markers={stops} bus_markers={buses}
                             api={this.api}/>
                </div>
            </React.Fragment>
        );
    }
}
