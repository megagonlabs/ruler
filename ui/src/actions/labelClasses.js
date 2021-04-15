import axios from 'axios';

export const GET_CLASSES_SUCCESS="GET_CLASSES_SUCCESS";
export const GET_CLASSES_PENDING="GET_CLASSES_PENDING";
export const GET_CLASSES_ERROR="GET_CLASSES_ERROR";
export const ADD_CLASS_SUCCESS="ADD_CLASS_SUCCESS";

const api = process.env.REACT_APP_SERVER;

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

function addClassSuccess(data) {
    return {
        type: ADD_CLASS_SUCCESS,
        data: data
    }
}

function dataFromResponse(response_data) {
    return response_data;
    /*return Object.keys(response_data).map(k => {
        return {
            name: k, 
            key: response_data[k]
        }
    })*/
}

export function submitLabels(labelClasses) {
    return dispatch => {
        dispatch(pending());
        axios.post(`${api}/label`,
            {
                labels: labelClasses,
            }
        )
        .then(response => {
            if (response.error) {
                throw(response.error);
            }
            const data = dataFromResponse(response.data);
            dispatch(getClassesSuccess(data));
        })
        .catch(error => {
            dispatch(raiseError(error));
        })
    }
}

export function addLabelClass(labelClassObj) {
    return dispatch => {
        dispatch(addClassSuccess(labelClassObj));   
    }
}

function fetchClasses() {
    return dispatch => {
        dispatch(pending());
        axios.get(`${api}/label`)
        .then(response => {
            if(response.error) {
                throw(response.error);
            }
            var data = dataFromResponse(response.data);
            if (data.labels) {
                data = data.labels;
            }
            console.log(data);
            dispatch(getClassesSuccess(data));
        })
        .catch(error => {
            dispatch(raiseError(error));
        })
    }
}

export default fetchClasses;