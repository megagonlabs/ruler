import React from 'react';
import {bindActionCreators} from 'redux';
import {connect} from "react-redux";

import CircularProgress from '@material-ui/core/CircularProgress';
import Container from '@material-ui/core/Container';
import Divider from '@material-ui/core/Divider';
import Grid from '@material-ui/core/Grid';
import IconButton from '@material-ui/core/IconButton';
import InfoIcon from '@material-ui/icons/Info';
import Paper from '@material-ui/core/Paper';
import Popover from '@material-ui/core/Popover';
import Table from '@material-ui/core/Table';
import TableBody from '@material-ui/core/TableBody';
import TableCell from '@material-ui/core/TableCell';
import TableRow from '@material-ui/core/TableRow';
import Typography from '@material-ui/core/Typography';
import WarningIcon from '@material-ui/icons/Warning';

import AnnotationDisplay from './AnnotationDisplay'
import { style } from './SortingTableUtils'
import { getLFexamples } from './actions/submitLFs'
import { getInteraction, deleteInteraction } from './actions/interaction'

class LFPanel extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            anchorEl: null
        };
    }

    handleOpen(event) {
        this.setState({anchorEl: event.currentTarget});
        this.props.getLFexamples(this.props.lf.id);
        //this.props.getInteraction(this.props.lf.interaction_idx);
    }
    handleClose() {
        this.setState({anchorEl: null});
    }

    render() { 
        var classes = this.props.classes;
        const anchorEl = this.state.anchorEl;
        const open = Boolean(anchorEl)

        var fields_to_display = ["conditions", "label", "Weight", "Coverage", "Conflicts", "dev_set_accuracy", "dev_set_coverage"]
        return (
            <React.Fragment>
                <IconButton onClick={this.handleOpen.bind(this)} size="small"><InfoIcon/></IconButton>

                <Popover
                    aria-labelledby="Labeling Function Description"
                    open={open}
                    onClose={this.handleClose.bind(this)}
                    anchorEl={anchorEl}
                    //marginThreshold={50}
                >
                    <Container maxWidth="md">
                    <Grid
                      className={classes.grid}
                      container
                      direction="row"
                      spacing={5}
                    >
                    
                        <Grid item xs={6} className={classes.grid}>
                        <Paper className={classes.paper}>

                            <Typography variant="h6">Statistics</Typography>
                            <Typography variant="body1">Computed over the training data unless otherwise noted. For further explanation of these calculations, please see the <a href="https://snorkel.readthedocs.io/en/v0.9.3/packages/_autosummary/labeling/snorkel.labeling.LFAnalysis.html">Snorkel LFAnalysis Documentation.</a></Typography>
                            <Table size="small" aria-label="Statistics for this LF"><TableBody>
                                {fields_to_display.map(key => 
                                    <TableRow key={key}>
                                        <TableCell ><Typography variant="button">{key}</Typography></TableCell> 
                                        <TableCell padding="none" align="right">{key in this.props.lf ? style(this.props.lf[key]) : "?" }</TableCell>
                                    </TableRow>
                                )}
                            </TableBody></Table>    
                        </Paper>
                        <Paper className={classes.paper}>
                            <Typography variant="h6"> False Positives ({this.props.mistakes.length})</Typography>
                            <Typography variant="body1">Up to 5 examples from the development set that are INCORRECTLY labeled by this function. </Typography>

                            <br/>
                            {this.props.mistakes.map((example_dict, idx) => 
                                <Grid item key={idx}>
                                <Divider/>
                                <WarningIcon color={"error"}/>
                                {this.props.pending ? < CircularProgress/> : 
                                                                <AnnotationDisplay 
                                                                    text={example_dict.text || ""}
                                                                    annotations={example_dict.annotations || []}
                                                                    classes={classes}
                                                                />}
                                </Grid>
                                )}
                            {/*{this.props.pending ? < CircularProgress/> : <AnnotationDisplay 
                                classes={classes}
                                annotations={annotations}
                                text={this.props.interaction.text_origin}
                            /> */}
                        </Paper>
                        </Grid>
                        <Grid container item xs={6} className={classes.grid} direction={'column'} justify={'flex-start'}>
                            <Paper className={classes.paper}>
                            <Typography variant="h6"> Matches ({this.props.examples.length})</Typography>
                            <Typography variant="body1">Examples from the training data that are labeled by this function. </Typography>

                            <br/>
                            {this.props.examples.map((example_dict, idx) => 
                                <Grid item xs={12} key={idx}>
                                <Divider/>
                                {this.props.pending ? < CircularProgress/> : 
                                                                <AnnotationDisplay 
                                                                    text={example_dict.text || ""}
                                                                    annotations={example_dict.annotations || []}
                                                                    classes={classes}
                                                                />}
                                </Grid>
                                )}
                            {/*{this.props.pending ? < CircularProgress/> : <AnnotationDisplay 
                                classes={classes}
                                annotations={annotations}
                                text={this.props.interaction.text_origin}
                            /> */}
                            </Paper>
                        </Grid>
                    
                    </Grid></Container>
                
                </Popover>
            </React.Fragment>
        );
    }
}

function mapStateToProps(state, ownProps?) {
    return {
        interaction: state.interactionHistory.data,
        pending: false, //TODO add pending field to labelExamples
        examples: state.labelExamples.examples,
        mistakes: state.labelExamples.mistakes
    }
}

function mapDispatchToProps(dispatch) {
    return {
        getInteraction: bindActionCreators(getInteraction, dispatch),
        deleteInteraction: bindActionCreators(deleteInteraction, dispatch),
        getLFexamples: bindActionCreators(getLFexamples, dispatch)
    };
}

export default connect(mapStateToProps, mapDispatchToProps)(LFPanel);