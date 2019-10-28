import React from 'react';
import './style/App.css';
import RealtimeFeature from './Components/RealtimeFeature'

/**
 * Main component for the React app.
 */
export const App = () => {
    return (
        <div className="container-fluid">
            <RealtimeFeature/>
        </div>
    );
};
