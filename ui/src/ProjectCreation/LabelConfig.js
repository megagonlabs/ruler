import React from 'react';
import {bindActionCreators} from 'redux';
import {connect} from "react-redux";

import fetchClasses, {addLabelClass} from '../actions/labelClasses';

import AddIcon from '@material-ui/icons/Add';
import Button from '@material-ui/core/Button';
import TextField from '@material-ui/core/TextField';
import Typography from '@material-ui/core/Typography';

class LabelConfig extends React.Component {

    constructor(props) {
        super(props);
        var new_label_key = Object.keys(props.labelClasses).length;

        this.state = {
          newLabel: "",
          fetched: false,
          new_label_key: new_label_key
        };
        this.handleLabelInput = this.handleLabelInput.bind(this);
        this.handleAdd = this.handleAdd.bind(this);

        this.props.fetchClasses();
    }

    handleLabelInput(event) {
        this.setState({
            newLabel: event.target.value
        });
    }

    handleAdd() {
        const newLabel = this.state.newLabel.trim()
        if (newLabel !== "") {
            this.props.addLabel({[newLabel]: this.state.new_label_key});
            this.setState({
                newLabel: "", 
                new_label_key: this.state.new_label_key + 1
            });
        }
    }

    handleKeyPress(event){ 
        if (event.key === 'Enter') {
            this.handleAdd();
        }
    }                  

    render() {
        const labels = Object.entries(this.props.labelClasses);
        console.log(labels)
        const classes = this.props.classes;
        return(
            <div>
            <Typography>Label Classes</Typography>
            {   labels.map( (item) => {
                    var lname = item[0];
                    var value = item[1];
                    return(
                        <div key={value}>
                        <Button 
                            className={classes.button} 
                            key = {value}
                            variant="outlined"
                        >
                            ({value})
                            {lname}
                        </Button>
                        </div>
                    )
                })
            }
            <TextField
               className={classes.input}
               placeholder="add label class"
               inputProps={{ 'aria-label': 'add label class' }}
               onChange = {this.handleLabelInput}
               value={this.state.newLabel}
               InputProps={{endAdornment:
                <Button className={classes.button} size="small" color="primary" aria-label="add" 
                    onClick={this.handleAdd} disabled={(this.state.newLabel==="")} >
                    <AddIcon />
                </Button>}}
            />
            </div>
        );
    }
}


function mapStateToProps(state, ownProps?) {
    return { 
        labelClasses: state.labelClasses.data,
        labelClassesPending: state.labelClasses.pending,
    };
}

function mapDispatchToProps(dispatch){
    return {
        addLabel: bindActionCreators(addLabelClass, dispatch),
        fetchClasses: bindActionCreators(fetchClasses, dispatch)
    };
}

export default connect(mapStateToProps, mapDispatchToProps)(LabelConfig);