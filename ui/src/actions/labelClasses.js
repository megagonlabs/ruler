import axios from 'axios';
import api from './api'

export const GET_CLASSES_SUCCESS="GET_CLASSES_SUCCESS";
export const GET_CLASSES_PENDING="GET_CLASSES_PENDING";
export const GET_CLASSES_ERROR="GET_CLASSES_ERROR";

function pending() {
    return {
        type: GET_CLASSES_PENDING
    }
}

function getClassesSuccess(data) {
    return {
        type: GET_CLASSES_SUCCESS,
        data: data
    }
}

function raiseError(error) {
    return {
        type: GET_CLASSES_ERROR,
        error: error
    }
}

function dataFromResponse(response) {
    return Object.keys(response.data).map(k => {
        return {
            name: k, 
            key: response.data[k]
        }
    })
}

function fetchClasses() {
    return dispatch => {
        dispatch(pending());
        axios.get(`${api}/label`)
        .then(response => {
            if(response.error) {
                throw(response.error);
            }
            const data = dataFromResponse(response);
            dispatch(getClassesSuccess(data));
        })
        .catch(error => {
            dispatch(raiseError(error));
        })
    }
}

export default fetchClasses;