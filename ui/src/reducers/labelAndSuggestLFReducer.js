import { 
    NEW_LF,
    LABEL,
} from '../actions/labelAndSuggestLF';


export function label (state = null, action ) {
    switch (action.type) {
        case LABEL:
            return action.data.label
        default:
            return state
    }
}

export function suggestedLF (state = {}, action) {
    switch (action.type) {
        case NEW_LF:
            return action.data;
        default:
            return state;
    }
}