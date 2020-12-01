import axios from 'axios';

export const SAVE_ERROR = "SAVE_ERROR"
export const SAVE_PENDING = "SAVE_PENDING"
export const SAVE_SUCCESS = "SAVE_SUCCESS"

const api = process.env.REACT_APP_SERVER;

function saveSuccess(data) {
    return {
        type: SAVE_SUCCESS,
        data: data,
    }
}

export function savePending() {
    return {
        type: SAVE_PENDING
    }
}

function saveError(error) {
    return {
        type: SAVE_ERROR,
        error: error
    }
}

export function saveModel() { 
    return dispatch => {
        axios.post(`${api}/save`)
        .then(response => {});
    }
}

export function uploadModel() { 
    return dispatch => {
        dispatch(savePending());
        var today = new Date();   
        var data = {"dirname": (today.getMonth()+1)+'-'+today.getDate()+ "_" + today.getHours() + "-" + today.getMinutes() + "-" + today.getSeconds()}
        axios.post(`${api}/save`, data)
        .then(response => {
            if(response.error) {
                throw(response.error);
            }
            dispatch(saveSuccess(response.data));
            return response.data;
        })
        .catch(error => {
            dispatch(saveError(error));
        })
    }
}