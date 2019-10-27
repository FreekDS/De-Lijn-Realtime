import React from 'react'

/**
 * Loading icon. Code found on https://loading.io/css/
 * @returns {*} loading icon html
 */
export const Loading = () => {
    return (<div className="lds-spinner" id="spinner">
        <div></div>
        <div></div>
        <div></div>
        <div></div>
        <div></div>
        <div></div>
        <div></div>
        <div></div>
        <div></div>
        <div></div>
        <div></div>
        <div></div>
    </div>);
};