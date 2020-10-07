import React from "react";
import { bindActionCreators } from "redux";
import { connect } from "react-redux";
import clsx from "clsx";

// actions
import { label } from "./actions/labelAndSuggestLF";
import fetchClasses from "./actions/labelClasses";
import { getKeyTypes } from "./actions/connectivesAndKeyTypes";
import { makeStyles } from "@material-ui/core/styles";
import { getText } from "./actions/getText";

// material UI
import Grid from "@material-ui/core/Grid";

// sub components
import AnnotationBuilder from "./AnnotationBuilder";
import LabelingFunctionsSelected from "./LabelingFunctionsSelected";
import LabelingFunctionsSuggested from "./LabelingFunctionsSuggested";
import Navigation from "./Navigation";
import StatisticsPane from "./StatisticsPane";
import StatisticsLRPane from "./StatisticsLRPane";

const drawerWidth = 200;

export const useStyles = makeStyles((theme) => ({
    title: {
        fontWeight: "bold",
        marginRight: "10px",
    },
    description: {
        fontStyle: "italic",
    },
    toolbarItem: {
        marginRight: "10px",
    },
    drawerDiv: {
        padding: "10px",
    },
    badge: {
        margin: "10px",
        cursor: "pointer",
    },
    contents: {
        margin: "20px",
    },
    icon: {
        marginRight: theme.spacing(0.5),
        width: 24,
        height: 24,
        verticalAlign: "text-bottom",
    },
    card: {
        padding: theme.spacing(1),
        textAlign: "center",
        color: theme.palette.text.secondary,
        alignItems: "flex-end",
    },
    text: {
        margin: "0px",
        minHeight: "15vh",
        fontSize: 20,
        display: "initial",
        lineHeight: 2.0,
    },
    cardActions: {
        margin: theme.spacing(1, 1, 1),
    },
    paper: {
        padding: theme.spacing(2),
        color: theme.palette.text.secondary,
    },
    grid: {
        padding: theme.spacing(1),
    },
    fab: {
        margin: theme.spacing(1),
    },
    arrowIcon: {
        marginRight: theme.spacing(0),
    },
    content: {
        flexGrow: 1,
        height: "90vh",
        padding: theme.spacing(1),
        transition: theme.transitions.create("margin", {
            easing: theme.transitions.easing.sharp,
            duration: theme.transitions.duration.leavingScreen,
        }),
        marginBottom: "100px",
    },
    contentShift: {
        transition: theme.transitions.create("margin", {
            easing: theme.transitions.easing.easeOut,
            duration: theme.transitions.duration.enteringScreen,
        }),
        marginLeft: drawerWidth,
        marginBottom: "100px",
    },
    root: {
        flexGrow: 1,
        display: "flex",
        justifyContent: "center",
        flexWrap: "wrap",
    },
    chip: {
        margin: theme.spacing(1),
        fontSize: "large",
        cursor: "pointer",
    },
    input: {
        marginLeft: theme.spacing(0),
        flex: 1,
        variant: "h6",
    },
    link: {
        badge: {
            transform: "scale(1) translate(0%, -50%)",
        },
    },
    snackbar: {
        top: "100px",
    },
    visuallyHidden: {
        border: 0,
        clip: "rect(0 0 0 0)",
        height: 1,
        margin: -1,
        overflow: "hidden",
        padding: 0,
        position: "absolute",
        top: 20,
        width: 1,
    },
    box: {
        width: "fit-content",
        display: "inline",
    },
}));

const ProjectGrid = (props) => {
    if (props.text.length === 0 && !props.text_pending) {
        props.fetchNextText();
    }
    if (!props.gll.fetched_keytype) {
        props.getKeyTypes();
    }
    if (props.labelClassesPending) {
        props.fetchClasses();
    }
    const classes = useStyles(),
        isDrawerOpen = props.isDrawerOpen;

    function assignClassLabel(label) {
        var annotations = props.annotations;
        const data = {
            label: label,
            annotations: annotations,
            text: props.text,
            index: props.index,
        };
        props.label(data);
    }

    return (
        <div
            className={clsx(classes.content, {
                [classes.contentShift]: isDrawerOpen,
            })}
        >
            <Grid container direction={"row"}>
                <Grid
                    container
                    item
                    md={12}
                    lg={7}
                    direction={"column"}
                    justify={"flex-start"}
                    alignItems={"stretch"}
                    wrap="nowrap"
                >
                    <Grid item>
                        <AnnotationBuilder
                            text={props.text}
                            classes={classes}
                            assignClassLabel={assignClassLabel}
                        />
                    </Grid>
                    <Grid container item justify={"center"} direction={"row"}>
                        <Navigation />
                    </Grid>
                    <Grid item>
                        <LabelingFunctionsSuggested classes={classes} />
                    </Grid>
                </Grid>
                <Grid
                    container
                    item
                    md={12}
                    lg={5}
                    direction={"column"}
                    justify={"flex-start"}
                    alignItems={"stretch"}
                    wrap="nowrap"
                >
                    <Grid item>
                        <StatisticsPane classes={classes} />
                    </Grid>
                    <Grid item>
                        <StatisticsLRPane classes={classes} />
                    </Grid>
                    <Grid item>
                        <LabelingFunctionsSelected
                            classes={classes}
                            labelClasses={props.labelClasses}
                        />
                    </Grid>
                </Grid>
            </Grid>
        </div>
    );
};

function mapStateToProps(state, ownProps?) {
    return {
        text: state.text.data,
        index: state.text.index,
        text_pending: state.text.pending,
        annotations: state.annotations,
        labelClassesPending: state.labelClasses.pending,
        gll: state.gll,
    };
}
function mapDispatchToProps(dispatch) {
    return {
        fetchNextText: bindActionCreators(getText, dispatch),
        label: bindActionCreators(label, dispatch),
        fetchClasses: bindActionCreators(fetchClasses, dispatch),
        getKeyTypes: bindActionCreators(getKeyTypes, dispatch),
    };
}

export default connect(mapStateToProps, mapDispatchToProps)(ProjectGrid);
