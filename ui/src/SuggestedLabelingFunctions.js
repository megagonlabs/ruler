import React from 'react';
import {connect} from "react-redux";
import {bindActionCreators} from 'redux';
import PropTypes from 'prop-types';

import Checkbox from '@material-ui/core/Checkbox';
import InfoIcon from '@material-ui/icons/Info';
import Paper from '@material-ui/core/Paper';
import Table from '@material-ui/core/Table';
import TableBody from '@material-ui/core/TableBody';
import TableCell from '@material-ui/core/TableCell';
import TableHead from '@material-ui/core/TableHead';
import TableRow from '@material-ui/core/TableRow';
import Typography from '@material-ui/core/Typography';
import WarningIcon from '@material-ui/icons/Warning';

import { set_selected_LF } from './actions/labelAndSuggestLF'

class SuggestedLabelingFunctions extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            // if a session starts with a labelling function already defined (for dev mode),
            // the asynchronous calls to get these dicts will likely be too slow 
            // and throw an error. Adding them explicitly for development.
            all_selected: false
        };

    }


    componentDidUpdate(prevProps) {
        if (this.state.all_selected) {
            for (var i = Object.values(this.props.labelingFunctions).length - 1; i >= 0; i--) {
                let lf = Object.values(this.props.labelingFunctions)[i];
                if (lf.selected !== true) {
                    this.setState({all_selected: false})
                }
            }
        }
    }

    connective(lf) {
        return (
            Object.keys(this.props.connective)
                .filter(c => this.props.connective[c] === lf.Connective)[0]
        );
    }

    label(lf) {
        return (
            this.props.labelClasses
                .filter(c => c.key === lf.Label)[0].name
        );    
    }

    keyType(code) {
        return (
            Object.keys(this.props.keyType)
                .filter(c => this.props.keyType[c] === code)[0]
        );    
    }

    conditionToString(condition) {
        let string = Object.keys(condition)[0];
        const keyType = this.keyType(condition[string]);
        if (condition[string] === 0){
            return "\"" + string + "\""
        }
        return string + " (" + keyType + ")";
    }

    conditions(lf) {
        const conditions = lf.Conditions.map(cond => this.conditionToString(cond));
        if (conditions.length > 1) {
            return (
                conditions.join(" " + this.connective(lf) + " ")
            );
        } 
        return conditions.join('');
    }

    LFtoStrings(key, lf) {
        const stringsDict = {
            id: key,
            conditions: this.conditions(lf),
            label: this.label(lf),
            order: lf.Direction.toString(),
            weight: lf.Weight
        };
        return stringsDict;
    }

    selectAllLF(bool_selected) {
        // (de)select all LFs, depending on value of bool_selected
        const LF_names = Object.keys(this.props.labelingFunctions);

        let newLFs = {};
        for (var i = LF_names.length - 1; i >= 0; i--) {
            let LF_key = LF_names[i];
            newLFs[LF_key] = this.props.labelingFunctions[LF_key];
            newLFs[LF_key]['selected'] = bool_selected;
        }
    
        this.setState({all_selected: bool_selected});
        this.props.set_selected_LF(newLFs);
    }

    handleChange(name, event) {
        let updatedLF = this.props.labelingFunctions[name];
        updatedLF['selected'] = !(updatedLF['selected']);
        const newLFs = {
            ...this.props.labelingFunctions,
            [name]: updatedLF 
        };
        this.props.set_selected_LF(newLFs);
    }

    render() {
        const classes = this.props.classes;
        const LFList = Object.keys(this.props.labelingFunctions).map(lf_key => this.LFtoStrings(lf_key, this.props.labelingFunctions[lf_key]));

        var LF_content = <Table size="small" aria-label="suggested labeling functions table">
              <TableHead>
                <TableRow>
                  <TableCell>
                    <Checkbox
                        onChange={(event) => this.selectAllLF(!this.state.all_selected)}
                        checked={this.state.all_selected}
                    /> 
                    { this.state.all_selected ? "Deselect All" : "Select All"}
                  </TableCell>
                  <TableCell align="right">Conditions</TableCell>
                  <TableCell align="right">Assign Label</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {LFList.map(row => (
                  <TableRow key={Object.values(row).join('')}>
                    <TableCell component="th" scope="row">
                      <Checkbox 
                        key={this.props.labelingFunctions[row.id].selected}
                        onChange={(event) => this.handleChange(row.id, event)} 
                        checked={this.props.labelingFunctions[row.id].selected===true}/>
                    </TableCell>
                    <TableCell align="right">{row.conditions}</TableCell>
                    {/*<TableCell align="right">{row.order}</TableCell>*/}
                    <TableCell align="right">{row.label}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>

        return(
          <Paper className={classes.paper}>
            <Typography className={classes.title} variant="h6" id="tableTitle">
                Suggested Labeling Functions
            </Typography>
            { this.props.no_label ? <Typography variant="body1" color="error"><WarningIcon/>{"You must assign a label in order to generate labeling functions!"}</Typography> : "" }
            { (this.props.no_annotations && !(this.props.no_label)) ?  <Typography variant="body1"><InfoIcon/>{"TIP: to improve function suggestions, annotate the parts of the text that guided your decision."}</Typography> : "" }
            {LF_content}
          </Paper>
        );
    }
}

SuggestedLabelingFunctions.propTypes = {
    all_selected: PropTypes.bool
};

function mapStateToProps(state, ownProps?) {

    return { 
        labelingFunctions: state.suggestedLF,
        labelClasses:state.labelClasses.data, 
        connective: state.gll.connective,
        keyType: state.gll.keyType,
        no_annotations: (state.annotations.length < 1),
        no_label: (state.label === null),
    };
}

function mapDispatchToProps(dispatch) {
    return {
        set_selected_LF: bindActionCreators(set_selected_LF, dispatch)
    };
}

export default connect(mapStateToProps, mapDispatchToProps)(SuggestedLabelingFunctions);