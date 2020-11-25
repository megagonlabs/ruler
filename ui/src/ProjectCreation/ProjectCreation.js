// material ui
import Box from "@material-ui/core/Box";
import Button from "@material-ui/core/Button";
import LinearProgress from "@material-ui/core/LinearProgress";
import Paper from "@material-ui/core/Paper";
import Step from "@material-ui/core/Step";
import StepContent from "@material-ui/core/StepContent";
import StepLabel from "@material-ui/core/StepLabel";
import Stepper from "@material-ui/core/Stepper";
import Typography from "@material-ui/core/Typography";

import clsx from "clsx";
import React, { useRef, useEffect } from "react";
import { connect } from "react-redux";
import { Link as RouteLink } from "react-router-dom";
import { Redirect } from "react-router-dom";
import { bindActionCreators } from "redux";

// actions
import { submitLabels } from "../actions/labelClasses";
import launch, { launchStatus } from "../actions/loadingBar";

// components
import DatasetSelect from "./DatasetSelect";
import ModelSelect from "./ModelSelect";
import LabelConfig from "./LabelConfig";
import { useStyles } from "../ProjectGrid";

function LinearProgressWithLabel(props) {
  return (
    <Box display="flex" alignItems="center">
      <Box width="100%" mr={1}>
        <LinearProgress variant="determinate" {...props} />
      </Box>
      <Box minWidth={35}>
        <Typography variant="body2" color="textSecondary">{`${Math.round(
          props.value
        )}%`}</Typography>
      </Box>
    </Box>
  );
}

function VerticalLinearStepper(props) {
  const [activeStep, setActiveStep] = React.useState(0);
  const steps = getSteps();

  const [inProgress, startLoadingBar] = React.useState(false);

  const classes = useStyles(),
    isDrawerOpen = props.isDrawerOpen;

  // this is used for getIdToken for a dummy user object
  const promise1 = new Promise((resolve, reject) => {
    resolve(true);
  });

  const handleNext = () => {
    //TODO If we're on the label creation step, send the labels to server when next is clicked
    setActiveStep((prevActiveStep) => prevActiveStep + 1);
  };

  const handleBack = () => {
    setActiveStep((prevActiveStep) => prevActiveStep - 1);
  };

  const handleReset = () => {
    setActiveStep(0);
  };

  function getSteps() {
    return [
      "Select Dataset",
      "Select Model",
      "Specify Label Classes",
      "Continue to Task",
    ];
  }

  function getStepContent(step) {
    switch (step) {
      case 0:
        return (
          <DatasetSelect
            isDrawerOpen={isDrawerOpen}
            user={{ getIdToken: (arg) => promise1 }}
            classes={classes}
          />
        );
      case 1:
        return (
          <ModelSelect
            isDrawerOpen={isDrawerOpen}
            user={{ getIdToken: (arg) => promise1 }}
            classes={classes}
          />
        );
      case 2:
        return (
          <LabelConfig
            isDrawerOpen={isDrawerOpen}
            user={{ getIdToken: (arg) => promise1 }}
            classes={classes}
          />
        );
      case 3:
        return null;
      default:
        return "Unknown step";
    }
  }

  function getStepButton(step) {
    switch (step) {
      case 2:
        function goToProject() {
          props.submitLabels(props.labelClasses);
          handleNext();
          startLoadingBar();
        }
        return (
          <Button
            variant="contained"
            color="primary"
            onClick={goToProject}
            className={classes.button}
            disabled={props.selected_model === undefined}
          >
            Continue
          </Button>
        );
      case 3:
        return (
          <RouteLink to="/project" classes={classes}>
            Continue to Task
          </RouteLink>
        );
      default:
        return (
          <Button
            variant="contained"
            color="primary"
            onClick={handleNext}
            className={classes.button}
            disabled={props.selected_dataset === undefined}
          >
            Next
          </Button>
        );
    }
  }

  // Once dataset is selected, check status of data preparation at regular intervals.
  const intervalRef = useRef();
  useEffect(() => {
    const id = setInterval(() => {
      if (inProgress) {
        props.getDataPrepProgress(props.selected_dataset);
      }
    }, 1000);
    intervalRef.current = id;
    return () => {
      clearInterval(intervalRef.current);
    };
  });

  // Redirect to project page once preparation is done.
  if (props.launchProgress >= 100) {
    return <Redirect to="/project" />;
  }

  if (inProgress) {
    return (
      <div id="loadingBar">
        <Typography>
          {" "}
          Your project is loading. You will be automatically redirected when it
          is complete.
        </Typography>
        <br />
        <LinearProgressWithLabel
          variant="determinate"
          value={props.launchProgress}
        />
      </div>
    );
  }

  return (
    <div
      className={clsx(classes.content, {
        [classes.contentShift]: isDrawerOpen,
      })}
    >
      <Stepper activeStep={activeStep} orientation="vertical">
        {steps.map((label, index) => (
          <Step key={label}>
            <StepLabel>{label}</StepLabel>
            <StepContent>
              {getStepContent(index)}
              <div className={classes.actionsContainer}>
                <div>
                  <Button
                    disabled={activeStep === 0}
                    onClick={handleBack}
                    className={classes.button}
                  >
                    Back
                  </Button>
                  {getStepButton(index)}
                </div>
              </div>
            </StepContent>
          </Step>
        ))}
      </Stepper>
      {activeStep === steps.length && (
        <Paper square elevation={0} className={classes.resetContainer}>
          <Typography>All steps completed - you&apos;re finished</Typography>
          <Button onClick={handleReset} className={classes.button}>
            Reset
          </Button>
        </Paper>
      )}
    </div>
  );
}

function mapStateToProps(state, ownProps?) {
  return {
    selected_dataset: state.datasets.selected,
    selected_model: state.models.selected,
    labelClasses: state.labelClasses.data,
    launchProgress: state.launchProgress.progress * 100, //convert to a percentage, not a fraction
    inProgress: !(state.launchProgress.thread === null),
    launchThread: state.launchProgress.thread,
  };
}
function mapDispatchToProps(dispatch) {
  return {
    getDataPrepProgress: bindActionCreators(launchStatus, dispatch),
    submitLabels: bindActionCreators(submitLabels, dispatch),
  };
}

export default connect(
  mapStateToProps,
  mapDispatchToProps
)(VerticalLinearStepper);
