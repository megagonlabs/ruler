export const ANNOTATE = "ANNOTATE";
export const HIGHLIGHT = "HIGHLIGHT";
export const HIGHLIGHT_ERROR = "HIGHLIGHT_ERROR"
export const SELECT_LINK = "SELECT_LINK";

export function annotate(data) {
    /* data is an array of annotations, for example
     [{
      id: 11,
      label: 0,
      start_offset: 11,
      end_offset: 17,
      text: 'Russia',
      link: null
    }]
  ] */
    return dispatch => {
        dispatch({
            type: ANNOTATE, 
            data
        })
    }
}

export function highlight(data) {
    /* data is an array of annotations, for example
     [{
      id: 11,
      label: 0,
      start_offset: 11,
      end_offset: 17,
      text: 'Russia',
      link: null
    }]
  ] */
    return dispatch => {
        dispatch({
            type: HIGHLIGHT, 
            data
        })
    }
}

export function highlight_regex(regex, text) {
    var data = [];
    var matches = [];
    try {
        matches = text.matchAll(regex);
    } 
    catch (err) {
        return dispatch => dispatch({type: HIGHLIGHT_ERROR, error: err.toString()});
    }

    for (const match of matches) {
        data.push({
            id: `${match.index}_pending`, // 'pending' because this annotation will not necessarily be submitted
            label: 'pending',
            start_offset: match.index,
            end_offset: match.index + match[0].length,
            link: null,
        });
    }
    return highlight(data);
}

export function highlight_string(string, text) {
    string = string.toLowerCase();
    text = text.toLowerCase();
    var data = [];
    let position = text.indexOf(string);
    while (position !== -1) {
        data.push({
            id: `${position}_pending`, // 'pending' because this annotation will not necessarily be submitted
            label: 'pending',
            start_offset: position,
            end_offset: position + string.length,
            link: null,
        });
        position = text.indexOf(string, position + 1);
    }
    return highlight(data);
}

export function select_link(data){
    /* EXAMPLE DATA 
    {
    type: 'Undirected Link',
    segment: {
      id: 11,
      label: 0,
      start_offset: 11,
      end_offset: 15,
      text: 'Ever',
      link: null
    }
  }
  */
    return dispatch => {
        dispatch({
            type: SELECT_LINK, 
            data
        })
    }
}