import React, {Component} from 'react'

/**
 * This class is a React component that will handle the selection form of the lines.
 * The props this class received from its parent are:
 *  1. api: APIhandler class
 *  2. selector: the selectLine function of the RealTimeFeature component, used to select the chosen line
 *  3. loading: the loading state of the application (bool)
 * The React state of this class consists of:
 *  1. entities: array where the entities will be stored in upon loading this component
 */
export default class LineSelector extends Component {
    /**
     * Constructor for the LineSelector
     * @param props Props received from the parent Component (RealTimeFeature)
     */
    constructor(props) {
        super(props);

        // Initialize the react state
        this.state = {
            entities: []
        };

        // Bind function to this class so react knows that the function is bound to the instance of this class
        this.handleSubmit = this.handleSubmit.bind(this);
    }

    /**
     * This function will be called when the component mounts.
     * This function will use the APIHandler of the props to get the entities.
     * The entities are used in the form.
     */
    componentDidMount() {
        this.props.api.getEntities().then(res => this.setState({entities: res.data}))
            .catch(error => {
                console.error("Cannot get entities from API, please reload page", error.message);
            });
    }

    /**
     * Handles the submission of the form. Calls the selector passed with the props.
     * @param event
     */
    handleSubmit(event) {
        event.preventDefault();
        let regionValue = event.target.region.value;
        if (regionValue === "Loading...")
            return;
        let lineNumber = event.target.line.value;
        let direction = event.target.direction.value;
        this.props.selector(regionValue, lineNumber, direction);
    }

    render() {
        const {entities} = this.state;
        console.log(entities);
        const {loading} = this.props;
        const entityOptions = entities.map(entity => {
            return (<option key={entity.number} value={entity.number}>{entity.name}</option>);
        });
        const loading_entities = (<option>Loading...</option>);
        return (
            <div className="col" onSubmit={this.handleSubmit}>
                <form>
                    <div className="form-group">
                        <label>Region</label>
                        <select name="region" id="selectInput" placeholder="Loading..." className="form-control"
                                required>
                            {entities.length !== 0 ? entityOptions : loading_entities}
                        </select>
                    </div>
                    <div className="form-group">
                        <label>Line number</label>
                        <input type="number" min="1" name="line" id="line" placeholder="Enter number"
                               className="form-control" required/>
                    </div>
                    <div className="form-group">
                        <label>Direction</label>
                        <select name="direction" className="form-control" required>
                            <option value="HEEN">Heen</option>
                            <option value="TERUG">Terug</option>
                        </select>
                    </div>
                    <button type="submit" className="btn btn-dark" disabled={loading}>Search</button>
                </form>
            </div>
        )
            ;
    }
}