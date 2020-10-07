import { SAVE_SUCCESS, SAVE_PENDING, SAVE_ERROR} from '../actions/save'

export default function projectReducer(state = {}, action)
{
    switch (action.type) {
        case SAVE_ERROR :
            return {...state,
                error: action.error};
        default:
            return state;
    }
    return state;

}