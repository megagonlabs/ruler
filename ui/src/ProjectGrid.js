import React, {useState} from 'react';
import {bindActionCreators} from 'redux';
import {connect} from "react-redux";
import { label, clear_suggestions, reset_label } from "./actions/labelAndSuggestLF";
import fetchClasses from  './actions/labelClasses'
import { getText } from './actions/getText'
import getStatistics from './actions/getStatistics'
import submitLFs, { getLFstats } from './actions/submitLFs'
import { getKeyTypes, getConnectives } from './actions/connectivesAndKeyTypes'
import { makeStyles } from '@material-ui/core/styles';
import Grid from '@material-ui/core/Grid';
import Fab from '@material-ui/core/Fab';

import ArrowIcon from '@material-ui/icons/ArrowForward';
import AnnotationBuilder from './AnnotationBuilder'
import LabelingFunctions from './LabelingFunctions'
import SuggestedLabelingFunctions from './SuggestedLabelingFunctions'
import clsx from 'clsx';
import StatisticsPane from './StatisticsPane'
import LRStatisticsPane from './LRStatisticsPane'

const drawerWidth = 200;

const useStyles = makeStyles(theme => ({
    card: {
        padding: theme.spacing(2),
        textAlign: 'center',
        color: theme.palette.text.secondary,
        alignItems: "flex-end"
    },
    text: {
        margin: "0px",
        minHeight: '10vh',
        fontSize: 20,
        display: "initial",
    },
    cardActions: {
        margin: theme.spacing(3, 1, 1),
    },
    paper: {
        padding: theme.spacing(2),
        color: theme.palette.text.secondary,
    },
    fab: {
        margin: theme.spacing(1),
    },
    arrowIcon: {
        marginRight: theme.spacing(0),
    },
    content: {
        flexGrow: 1,
        height:'90vh',
        padding: theme.spacing(3),
        transition: theme.transitions.create('margin', {
            easing: theme.transitions.easing.sharp,
            duration: theme.transitions.duration.leavingScreen,
        }),
    },
    contentShift: {
        transition: theme.transitions.create('margin', {
            easing: theme.transitions.easing.easeOut,
            duration: theme.transitions.duration.enteringScreen,
        }),
        marginLeft: drawerWidth,
    },
    root: {
        flexGrow: 1,
        display: 'flex',
        justifyContent: 'center',
        flexWrap: 'wrap',
    },
    chip: {
        margin: theme.spacing(1),
        fontSize: "large",
    },
    input: {
        marginLeft: theme.spacing(0),
        flex: 1,
        variant: "h6",
    },
    link: {
        badge: {
            transform: 'scale(1) translate(0%, -50%)',
        }
    },
    snackbar: {
        top: "100px"
    },
    visuallyHidden: {
        border: 0,
        clip: 'rect(0 0 0 0)',
        height: 1,
        margin: -1,
        overflow: 'hidden',
        padding: 0,
        position: 'absolute',
        top: 20,
        width: 1,
    },
    box: {
        width: "fit-content",
        display: "inline",
    },
}));

const ProjectGrid =  (props) => {

    if ((props.text.length === 0) && !(props.text_pending)) {
        props.fetchNextText();
    }
    if (!props.gll.fetched_keytype) {
        props.getKeyTypes();
    }
    if (!props.gll.fetched_conn) {
        props.getConnectives();
    }
    if (props.labelClassesPending) {
        props.fetchClasses();
    }
    const classes = useStyles(),
        isDrawerOpen = props.isDrawerOpen;
        
    function assignClassLabel(label) {
        // If no annotations have been made, treat it
        // as if the entire text was selected
        var annotations = props.annotations;
        if (annotations.length === 0) {
          annotations = [{
            id: 0, 
            label: 0, 
            start_offset: 0, 
            end_offset: props.text.length, 
            text: props.text,
            link: null
          }];
        }
        const data = {
            "label": label,
            "annotations": annotations,
            "text_origin": props.text
        }
        props.label(data);

    }

    function clickNext(){  
        props.reset_label(); 
        const LF_ids = Object.keys(props.suggestedLF);
        const selected_LFs = LF_ids.reduce( function (selected_LFs, id) {
            let LF = props.suggestedLF[id];
            if (LF.selected) {
                delete LF.selected;
                selected_LFs[id] = LF;
            }
            return selected_LFs;
        }, {});
        
        const LFS_WILL_UPDATE = (Object.keys(selected_LFs).length > 0)
        // TODO this should also be true if a concept has been updated
        if (LFS_WILL_UPDATE) {
            props.submitLFs(selected_LFs);
        } else if (STATS_WILL_UPDATE) {
            props.getLFstats();
        }
        props.fetchNextText(); 
        props.clear_suggestions();

        shouldStatsUpdate(false);
    }

    const FabText = ((props.currentLabel === null) && (props.text.length !== 0)) ? "Skip" : "Next";

    const [STATS_WILL_UPDATE, shouldStatsUpdate] = useState(true);

    return (
        <div className={clsx(classes.content, { [classes.contentShift]: isDrawerOpen })}>
            <Grid container direction={'row'} style={{"paddingBottom":"100px"}}>

                <Grid container item md={12} lg={7} direction={'column'} justify={'flex-start'} alignItems={'stretch'} wrap="nowrap">
                    <Grid item><AnnotationBuilder 
                        text={props.text}
                        classes={classes} 
                        assignClassLabel={assignClassLabel} 
                        shouldStatsUpdate={shouldStatsUpdate}
                    /></Grid>
                    <Grid container item justify={'center'} direction={'row'}>
                        <Fab color="secondary" size="large" variant="extended" onClick={clickNext}>
                            { FabText }
                            <ArrowIcon />
                        </Fab>
                    </Grid>
                    <Grid item>
                        <SuggestedLabelingFunctions 
                        classes={classes} />
                    </Grid>
                </Grid>

                <Grid container item md={12} lg={5} direction={'column'} justify={'flex-start'} alignItems={'stretch'} wrap="nowrap">
                    <Grid item ><StatisticsPane classes={classes} /></Grid>
                    <Grid item ><LRStatisticsPane classes={classes} /></Grid>
                    <Grid item ><LabelingFunctions classes={classes} labelClasses={props.labelClasses}/></Grid>
                </Grid>

            </Grid>
        </div>
    );
};

function mapStateToProps(state, ownProps?) {
    return {
        text: state.text.data,
        text_pending: state.text.pending, 
        concepts: state.concepts, 
        annotations: state.annotations,
        suggestedLF: state.suggestedLF,
        currentLabel: state.label,
        labelClassesPending: state.labelClasses.pending,
        gll: state.gll
    };
}
function mapDispatchToProps(dispatch) {
    return { 
        fetchNextText: bindActionCreators(getText, dispatch), 
        label: bindActionCreators(label, dispatch),
        fetchClasses: bindActionCreators(fetchClasses, dispatch),
        getStatistics: bindActionCreators(getStatistics, dispatch),
        submitLFs: bindActionCreators(submitLFs, dispatch),
        getConnectives: bindActionCreators(getConnectives, dispatch),
        getKeyTypes: bindActionCreators(getKeyTypes, dispatch),
        clear_suggestions: bindActionCreators(clear_suggestions, dispatch),
        reset_label: bindActionCreators(reset_label, dispatch),
        getLFstats: bindActionCreators(getLFstats, dispatch)
    };
}

export default connect(mapStateToProps, mapDispatchToProps)(ProjectGrid);


