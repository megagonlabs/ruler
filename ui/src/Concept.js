import React from 'react';
import {bindActionCreators} from 'redux';
import {connect} from "react-redux";

import AddIcon from '@material-ui/icons/Add';
import Button from '@material-ui/core/Button';
import Chip from '@material-ui/core/Chip';
import CloseIcon from '@material-ui/icons/Close';
import IconButton from '@material-ui/core/IconButton';
import MenuItem from '@material-ui/core/MenuItem';
import Popover from '@material-ui/core/Popover';
import Select from '@material-ui/core/Select';
import Table from '@material-ui/core/Table';
import TableBody from '@material-ui/core/TableBody';
import TableCell from '@material-ui/core/TableCell';
import TableRow from '@material-ui/core/TableRow';
import TextField from '@material-ui/core/TextField';
import Typography from '@material-ui/core/Typography';

import { conceptEditors, select_concept } from './actions/concepts'
import { highlight_regex, highlight_string, highlight, annotate } from './actions/annotate'

class Concept extends React.Component {
    constructor(props) {
        super(props);

        this.availableKeyTypes = {}; // create a mapping {key_code: key_name}
        for (var i = ["TOKEN", "REGEXP"].length - 1; i >= 0; i--) {
            let keytype_name = ["TOKEN", "REGEXP"][i];
            this.availableKeyTypes[this.props.keyType[keytype_name]] = keytype_name;
        }
        const default_keytype = "TOKEN";

        this.state = {
            anchorEl: null,
            new_token: "",
            new_keytype: default_keytype
        }
        this.handleInput = this.handleInput.bind(this);
        this.handleKeyPress = this.handleKeyPress.bind(this);
        this.handleAdd = this.handleAdd.bind(this);
        this.openMenu = this.openMenu.bind(this);
        this.handleClose = this.handleClose.bind(this);
        this.handleRemove = this.handleRemove.bind(this);
        this.handleClick = this.handleClick.bind(this);
        this.updateConcept = this.updateConcept.bind(this);
    } 

    handleInput(event) {
        const new_token = event.target.value;
        this.setState({
            new_token
        });
        // TODO annotate
        if (new_token.trim().length > 0) {
            if (this.state.new_keytype === "TOKEN") {
                this.props.highlight_string(new_token, this.props.text);
            } if (this.state.new_keytype === "REGEXP") {
                this.props.highlight_regex(new_token, this.props.text);
            }
        } else {
            this.resetHighlights();
        }
    }

    canAdd(new_token) {
        return ((new_token !== "") && !(new_token in this.props.tokens) && !(this.props.error))
    }

    handleAdd() {
        const new_token = this.state.new_token.trim();
        if (this.canAdd(new_token)) {
            this.setState({
                new_token: ""
            })
            var current_tokens = this.props.tokens;
            current_tokens[new_token] = this.props.keyType[this.state.new_keytype];
            this.updateConcept(current_tokens);
            // annotate the text with the new condition, if applicable
            const hlights = this.props.highlights.map(hlight => {
                hlight.id = hlight.start_offset;
                hlight.label = this.props.concept;
                return hlight;
            });
            this.props.annotate(this.props.addAnnotations(hlights));
            this.resetHighlights();            
        }
    }

    resetHighlights() {
        this.props.highlight([]);
    }

    changeKeytype(token_to_change, new_keytype) {
        var current_tokens = this.props.tokens;
        current_tokens[token_to_change] = this.props.keyType[new_keytype];
        this.updateConcept(current_tokens);
        // TODO annotate text with new token/keytype
    }

    handleRemove(old_token) {
        var current_tokens = this.props.tokens;
        delete current_tokens[old_token];
        this.updateConcept(current_tokens);
    }

    updateConcept(tokens) {
        this.props.conceptEditors.updateConcept(
            this.props.concept,
            tokens
        );
        this.props.shouldStatsUpdate(true);
    }

    handleKeyPress(event){ 
        if (event.key === 'Enter') {
            this.handleAdd();
        }
    }
    
    openMenu(event){
        this.setState({anchorEl: event.currentTarget});
    }

    handleClick(event){
        if (this.props.selectedConcept===this.props.concept) {
            this.props.select_concept(null);
        } else {
            this.props.select_concept(this.props.concept);

        }
    }

    handleClose(){
        this.setState({anchorEl: null});
        this.resetHighlights();
    }

    deleteSelf() {
        this.props.select_concept(null);
        this.props.conceptEditors.deleteConcept(this.props.concept);
    }

    render() {
        const classes = this.props.classes;
        const concept = this.props.concept;
        const color = this.props.color;

        const isSelected = (this.props.selectedConcept===this.props.concept);
        let style = {}
        let variant = null;
        if (isSelected) {
            style["backgroundColor"] = color;
            style["color"] = "white";
            variant = "outlined";
        } else {
            style["backgroundColor"] = "white";
            style["border"] = "2px solid " + color;
            variant = "default";
        }

        return(
            <>
                <Chip
                    aria-label={concept}
                    size="medium"
                    className={ classes.chip }
                    key = {concept}
                    id = {concept}
                    onClick = {this.handleClick}
                    label = { concept }
                    style = { style }
                    variant={ variant }
                    onDelete={this.deleteSelf.bind(this)} 
                    avatar={
                        <IconButton 
                            size="small" 
                            onClick={this.openMenu} 
                            aria-label="edit this concept" 
                            children=<Typography variant="button">{Object.keys(this.props.tokens).length}</Typography>
                            color="inherit"
                        />
                    }
                />
                <Popover 
                    open={Boolean(this.state.anchorEl)}
                    anchorEl={this.state.anchorEl}
                    onClose={this.handleClose}
                    anchorOrigin={{
                    vertical: 'bottom',
                    horizontal: 'right',
                    }}
                    transformOrigin={{
                    vertical: 'bottom',
                    horizontal: 'right',
                    }}
                >
                    <Table><TableBody>
                    {Object.keys(this.props.tokens).map((str) => {
                        var keytype = this.availableKeyTypes[this.props.tokens[str]];
                        return (
                        <TableRow key={str}>
                            <TableCell><Typography variant="h6">{str}</Typography></TableCell>
                            <TableCell><Select
                                value={keytype}
                                onChange={(event) => this.changeKeytype(str, event.target.value)}>
                                {Object.values(this.availableKeyTypes).map((ktype) => 
                                    <MenuItem key={ktype} value={ktype}>{ktype}</MenuItem>
                                )}
                            </Select></TableCell>
                            <TableCell><Button  
                                className={classes.button} size="small" 
                                color="primary" 
                                aria-label="add" >
                                <CloseIcon onClick={() => this.handleRemove(str)}/>
                            </Button></TableCell>
                        </TableRow>
                        )
                    })}
                        <TableRow key="inputField">
                            
                            <TableCell><TextField 
                                className={classes.input}
                                placeholder = "new string"
                                onKeyPress = {this.handleKeyPress} 
                                value={this.state.new_token}
                                onChange = {this.handleInput}
                                error={(this.props.error !== null)}
                                helperText={this.props.error}>
                            </TextField></TableCell>
                            <TableCell><Select
                                value={this.state.new_keytype}
                                onChange={(event) => {
                                    this.setState({
                                        new_keytype: event.target.value
                                    })
                                }}>
                                {Object.values(this.availableKeyTypes).map((ktype) => 
                                    <MenuItem key={ktype} value={ktype}>{ktype}</MenuItem>
                                )}
                            </Select></TableCell>                            
                            <TableCell><Button 
                                onClick={this.handleAdd}
                                className={classes.button} 
                                size="small" 
                                color="primary" 
                                aria-label="add" 
                                disabled={!(this.canAdd(this.state.new_token.trim()))}>
                                <AddIcon />
                            </Button></TableCell>  
                                         
                        </TableRow>
                    </TableBody></Table>
                </Popover>
            </>
        );
    }
}

function mapStateToProps(state, ownProps?) {
    let concept = state.concepts.data[ownProps.concept];
    return { 
        ...concept,
        selectedConcept: state.selectedConcept,
        keyType: state.gll.keyType,
        text: state.text.data,
        error: state.highlights.error,
        highlights: state.highlights.data
    };
}

function mapDispatchToProps(dispatch) {
    return { 
        annotate: bindActionCreators(annotate, dispatch), 
        highlight: bindActionCreators(highlight, dispatch),
        highlight_regex: bindActionCreators(highlight_regex, dispatch),
        highlight_string: bindActionCreators(highlight_string, dispatch),
        conceptEditors: bindActionCreators(conceptEditors, dispatch), 
        select_concept: bindActionCreators(select_concept, dispatch)
    };
}

export default connect(mapStateToProps, mapDispatchToProps)(Concept);
