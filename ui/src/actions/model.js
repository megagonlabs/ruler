import axios from 'axios';

export const SUCCESS = "GET_MODELS_SUCCESS"
export const PENDING = "GET_MODELS_PENDING"
export const ERROR = "GET_MODELS_ERROR"
export const SELECT = "MODEL_SELECT"

const api = process.env.REACT_APP_SERVER;

function UploadError(error) {
    return {
        type: ERROR,
        error: error
    }
}

function selectModel(data) {
    return {
        type:SELECT,
        data: data
    }
}

function UploadPending() {
    return {
        type: PENDING
    }
}

function UploadSuccess(data) {
    return {
        type: SUCCESS,
        data: data
    }
}

export function fetchModels(idToken) {
    return dispatch => {
        dispatch(UploadPending());
        axios.get(`${api}/models`, 
            { 
                headers: {
                    'Authorization': 'Bearer ' + idToken
                }
            }
        )
        .then(response => {
            if(response.error) {
                dispatch(UploadError());
                throw(response.error);
            }
            dispatch(UploadSuccess(response.data));
            return response.data;
        })
        .catch(error => {
            dispatch(UploadError(error));
        })
    }
}

export function setSelected(model_name, idToken=0) {

    return dispatch => {
        axios.post(`${api}/models`, 
            {model_name: model_name},
            { 
                headers: {
                'Authorization': 'Bearer ' + idToken
                }
            }
        )
        .then(response => {
            if (response.error) {
                throw(response.error);
            }
            dispatch(selectModel(model_name));
        })
    }
}

export function createNewModel(model_name=0, formData={}, idToken=0) {
    return dispatch => {
        dispatch(UploadPending());
        console.log(formData);
        axios.post(`${api}/models/${model_name}`, 
            formData, 
            { 
                headers: {
                'Content-Type': 'multipart/form-data',
                'Authorization': 'Bearer ' + idToken
                }
            }
        )
        .then(response => {
            if(response.error) {
                dispatch(UploadError());
                throw(response.error);
            }
            dispatch(UploadSuccess(response.data));
            dispatch(selectModel(model_name));
            return response.data;
        })
        .catch(error => {
            dispatch(UploadError(error));
        })
    }
}