import { ANNOTATE, HIGHLIGHT, HIGHLIGHT_ERROR, SELECT_LINK } from '../actions/annotate';

function annotations(state=[], action ){
    switch (action.type) {
        case ANNOTATE:
            return action.data
        default:
            return state
    }
}

export default annotations;

export function highlights(state={data: [], error: null}, action ){
    switch (action.type) {
        case HIGHLIGHT:
            return {
                ...state, 
                data: action.data, 
                error: null
            }
        case HIGHLIGHT_ERROR:
            return {
                ...state, 
                error: action.error
            }
        default:
            return state
    }
}

export function selectedLink(state={type: null}, action) {
    switch (action.type) {
        case SELECT_LINK: 
            return action.data
        default: 
            return state
    }
 }