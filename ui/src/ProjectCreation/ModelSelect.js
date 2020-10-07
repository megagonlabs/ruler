import React from 'react';
import {bindActionCreators} from 'redux';
import {connect} from "react-redux";

import fetchClasses, {addLabelClass} from '../actions/labelClasses';

import AddIcon from '@material-ui/icons/Add';
import Button from '@material-ui/core/Button';
import FormControl from '@material-ui/core/FormControl';
import Select from '@material-ui/core/Select';
import TextField from '@material-ui/core/TextField';
import Typography from '@material-ui/core/Typography';

import { fetchModels, setSelected, createNewModel } from '../actions/model'

class ModelSelect extends React.Component {
    constructor(props) {
        super(props);

        this.state = {
          newModel: "",
        };
        this.handleSelect = this.handleSelect.bind(this);
        this.createModel = this.createModel.bind(this);
        this.handleInput = this.handleInput.bind(this);
        this.handleKeyPress = this.handleKeyPress.bind(this);

        this.props.fetchModels();
    }

    // MODELS MANAGEMENT
    fetchModels() {
        if ( !this.props.user )
            return;
        this.props.user.getIdToken(true).then((idToken) => {
            this.props.fetchModels(idToken);
        });
    }

    handleSelect(event) {
        const { options } = event.target;
        const value = [];
        for (let i = 0, l = options.length; i < l; i += 1) {
            if (options[i].selected) {
                value.push(options[i].value);
            }
        }
        this.props.setSelected(value[0]);
    }

    handleInput(event){
        this.setState({
            newModel: event.target.value
        });
    }

    createModel(){
        this.props.createNewModel(this.state.newModel);
    }

    handleKeyPress(event){ 
        if (event.key === 'Enter') {
            this.createModel();
        }
    }                  

    render() {
        const model_names = this.props.models;
        const { classes } = this.props;

        return(
            <div>

                <Typography>Load Model</Typography>
                <div className={classes.contents}>
                  <FormControl className={classes.formControl}>
                    <Select multiple native value={this.props.selected_model} onChange={this.handleSelect}>
                      { model_names.map((model) => 
                        <option 
                          value={model} 
                          key={model}
                        >
                          {model}
                        </option>) }
                    </Select>
                  </FormControl>
                </div>
                <Typography>-OR-</Typography>  
                <Typography>Create new model:</Typography>
                <div  className={classes.contents}>
                    <Typography>Model Name</Typography>
                    <TextField  
                        required
                        className={classes.input}
                        placeholder="your new model"
                        value={this.state.newModel}
                        onKeyPress={this.handleKeyPress}
                        onChange={this.handleInput}
                        InputProps={{endAdornment:
                        <Button className={classes.button} size="small" color="primary" aria-label="create a new model" 
                            onClick={this.createModel} disabled={(this.state.newModel==="")} >
                            <AddIcon />
                        </Button>}}
                    />

                </div>
            </div>
        )
    }
}

function mapStateToProps(state, ownProps?) {
    return { 
        models: state.models.data,
        modelsPending: state.models.pending,
    };
}

function mapDispatchToProps(dispatch){
    return {
        addLabel: bindActionCreators(addLabelClass, dispatch),
        fetchClasses: bindActionCreators(fetchClasses, dispatch),
        fetchModels: bindActionCreators(fetchModels, dispatch),
        setSelected: bindActionCreators(setSelected, dispatch),
        createNewModel: bindActionCreators(createNewModel, dispatch)
    };
}

export default connect(mapStateToProps, mapDispatchToProps)(ModelSelect);