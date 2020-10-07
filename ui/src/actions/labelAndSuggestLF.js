import axios from 'axios';

export const LABEL = 'LABEL'
export const NEW_LF = 'NEW_LF'

const api = process.env.REACT_APP_SERVER;

export function reset_label(){
    return dispatch => {
        dispatch({type: LABEL, data: {label: null}});
    }
}

export function label(data){
    return dispatch => {
        dispatch({type: LABEL, data: data});
        axios.post(`${api}/interaction`, data)
        .then( response => {
            dispatch({type: NEW_LF, data: response.data})
        })
    }      
}

export function set_selected_LF(data){
    return dispatch => dispatch({type: NEW_LF, data: data});
}

export function clear_suggestions(){
    return dispatch => dispatch({type: NEW_LF, data: {}})
}