import axios from 'axios';
import api from './api'
import { annotate, select_link } from './annotate'
import { reset_label } from "./labelAndSuggestLF";

export const GET_TEXT_PENDING = "GET_TEXT_PENDING";
export const GET_TEXT_SUCCESS = 'GET_TEXT_SUCCESS';
export const GET_TEXT_ERROR = "GET_TEXT_ERROR";

function getTextPending() {
    return {
        type: GET_TEXT_PENDING,
    }
}

function newText(data){
   return {
        type: GET_TEXT_SUCCESS, 
        data
    }
}

function getTextError(error) {
    return {
        type: GET_TEXT_ERROR,
        error
    }
}

export function getText(){
    return dispatch => {
        dispatch(getTextPending());
        axios.get(`${api}/interaction`)
        .then(response => {
            if (response.error) {
                throw(response.error);
            }
            _getTextHelper(response, dispatch);
            return response.data.text
        })
        .catch(error => {
            dispatch(getTextError(error));
        })
    }
}

// Set the new text, and reset all state related to the previous text
function _getTextHelper(response, dispatch){
    //change the text
    dispatch(newText(response.data.text));

    //reset annotations
    let annotations = [];
    if ("annotations" in response.data) {
        annotations = response.data.annotations;
    }
    dispatch(annotate(annotations));

    //reset selected span to link
    dispatch(select_link({type: null}));

    //reset selected label
    dispatch(reset_label());
}