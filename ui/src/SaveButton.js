import IconButton from "@material-ui/core/IconButton";
import SaveIcon from '@material-ui/icons/Save';

import React from "react";
import { bindActionCreators } from "redux";
import { connect } from "react-redux";
import { saveModel } from "./actions/save";

const SaveButton = (props) => {
    return (
        <IconButton aria-label="download" onClick={props.save} color="inherit">
            <SaveIcon/>
        </IconButton>
    );
};

function mapStateToProps(state, ownProps?) {
    return {};
}

function mapDispatchToProps(dispatch) {
    return {
        save: bindActionCreators(saveModel, dispatch),
    };
}

export default connect(mapStateToProps, mapDispatchToProps)(SaveButton);
