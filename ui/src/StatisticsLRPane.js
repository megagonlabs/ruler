import React from 'react';
import {connect} from "react-redux";
import {bindActionCreators} from 'redux';

import ArrowDropUpIcon from '@material-ui/icons/ArrowDropUp';
import ArrowDropDownIcon from '@material-ui/icons/ArrowDropDown';
import Divider from '@material-ui/core/Divider';
import LinearProgress from '@material-ui/core/LinearProgress';
import Paper from '@material-ui/core/Paper';
import RefreshIcon from '@material-ui/icons/Refresh';
import Table from '@material-ui/core/Table';
import TableBody from '@material-ui/core/TableBody';
import TableCell from '@material-ui/core/TableCell';
import TableRow from '@material-ui/core/TableRow';
import Typography from '@material-ui/core/Typography';

import { getLRStatistics } from './actions/getStatistics'
import { style } from './SortingTableUtils'


class LRStatisticsPane extends React.Component {
    componentDidUpdate(prevProps, prevState) {
      if ((prevProps.statistics !== this.props.statistics) && (Object.keys(prevProps.statistics).length > 0)) {
        this.setState({prevStats: prevProps.statistics});
      }
    }

    statDelta(key) {
      if ((this.state) && ("prevStats" in this.state)) {
        const delta = this.props.statistics[key] - this.state.prevStats[key];
        let cellContent = delta;
        if (delta > 0.0){
          cellContent = <span style={{color:"green"}}><ArrowDropUpIcon/> {style(delta)} </span>
        } else if (delta < -0.0) {
          cellContent = <span style={{color:"red"}}><ArrowDropDownIcon/> {style(delta)}</span>
        } 
        return(<TableCell>{cellContent}</TableCell>)
      }
    }

    render(){
        const classes = this.props.classes;
        const prevStats = ((this.state) && ("prevStats" in this.state));
        return(
          <Paper className={classes.paper}>
            
            <Typography className={classes.title} variant="h6" id="tableTitle">
                <RefreshIcon onClick={this.props.getLRStatistics} disabled={this.props.pending}></RefreshIcon>Trained Model Statistics
            </Typography>
            <Typography variant="body1">Train a logistic regression model with bag-of-words features on your training set.</Typography>

            {this.props.pending ? <LinearProgress/> : <Divider/>}

            <Table stickyHeader className={classes.table} size="small" aria-label="labeling statistics">
              <TableBody>
                {["accuracy", "micro_f1"].map(key => { 
                  if (key in this.props.statistics) {
                      return (<TableRow key={key}>
                          <TableCell>{key}</TableCell>
                          <TableCell align="right">{style(this.props.statistics[key])}</TableCell>
                          {this.statDelta(key)}
                        </TableRow>)
                  } else { return null}
                })}</TableBody>
                </Table>
            <br/>
            <Typography className={classes.title} variant="h6" id="tableTitle">
                Class-Specific Statistics
            </Typography>
                <Table>
                <TableBody>
                  <TableRow key="class_headers">
                    <TableCell><Typography variant="h6">Class0</Typography></TableCell>
                    <TableCell/>
                    {prevStats ? (<TableCell/>) : null}
                    <TableCell><Typography variant="h6">Class1</Typography></TableCell>
                    <TableCell/>
                  </TableRow>
                  {["precision", "recall"].map(key => { 
                    if (key+"_0" in this.props.statistics) {
                      return (<TableRow key={key}>
                          <TableCell>{key+"_0"}</TableCell>
                          <TableCell align="right">{style(this.props.statistics[key+"_0"])}</TableCell>
                          {this.statDelta(key+"_0")}
                          <TableCell>{key+"_1"}</TableCell>
                          <TableCell align="right">{style(this.props.statistics[key+"_1"])}</TableCell>
                          {this.statDelta(key+"_1")}
                        </TableRow>)
                    } return null
                  })}
              </TableBody>
            </Table>
          </Paper>        )
    }
}

function mapStateToProps(state, ownProps?) {
    return { 
      statistics: state.statistics_LRmodel.data,
      pending: state.statistics_LRmodel.pending
    };
}
function mapDispatchToProps(dispatch) {
    return {
      getLRStatistics: bindActionCreators(getLRStatistics, dispatch)
    };
}
export default connect(mapStateToProps, mapDispatchToProps)(LRStatisticsPane);