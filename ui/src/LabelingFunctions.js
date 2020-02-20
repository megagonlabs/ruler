import React from 'react';
import {bindActionCreators} from 'redux';
import {connect} from "react-redux";
import { withStyles } from '@material-ui/core/styles';


import ClearIcon from '@material-ui/icons/Clear';
import Divider from '@material-ui/core/Divider';
import IconButton from '@material-ui/core/IconButton';
import LinearProgress from '@material-ui/core/LinearProgress';
import Paper from '@material-ui/core/Paper';
import PublishIcon from '@material-ui/icons/Publish';
import Table from '@material-ui/core/Table';
import TableBody from '@material-ui/core/TableBody';
import TableCell from '@material-ui/core/TableCell';
import TableHead from '@material-ui/core/TableHead';
import TableRow from '@material-ui/core/TableRow';
import TableSortLabel from '@material-ui/core/TableSortLabel';
import Tooltip from '@material-ui/core/Tooltip';
import Typography from '@material-ui/core/Typography';
import WarningIcon from '@material-ui/icons/Warning';

import LFPanel from './LFPanel'

import submitLFs, { getLFstats, deleteLF } from './actions/submitLFs'
import { stableSort, getSorting, style } from './SortingTableUtils'

const FadedTableBody = withStyles(theme => ({
  root: {
    color: "white",
  },
}))(TableBody);

class LabelingFunctions extends React.Component {
    constructor(props) {
        super(props);

        this.state = {
            // if a session starts with a labelling function already defined (for dev mode),
            // the asynchronous calls to get these dicts will likely be too slow 
            // and throw an error. Adding them explicitly for development.
            connective: {"AND": 0,"OR": 1},
            keyType: {"CONCEPT": 1, "NER": 2, "TOKEN": 0},
            order: 'asc',
            orderBy: "Weight"
        };
    }

    componentDidMount() {
        this.props.getLFstats();
    }

    connective(lf) {
        return (
            Object.keys(this.props.connective)
                .filter(c => this.state.connective[c] === lf.Connective)[0]
        );
    }

    label(lf) {
        const label = this.props.labelClasses.filter(c => c.key === lf.Label)
        return (
            label[0] ? label[0].name : "UNK"
        );
    }

    keyType(code) {
        return (
            Object.keys(this.props.keyType)
                .filter(c => this.state.keyType[c] === code)[0]
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
/*        let strings = ["IF text contains "];
        strings.push(this.conditions(lf));
        if (lf.Direction){
            strings.push(", in that order,")
        }
        strings.push(" THEN label == " + this.label(lf));
        strings.push(" with weight " + lf.Weight);
        return strings;*/

        const strings = {
            ...lf,
            id: key,
            conditions: this.conditions(lf),
            label: this.label(lf),
            order: lf.Direction.toString()
        }
        return strings
    }

    duplicateCell(dupeString) {
        if (dupeString !== null) {
            let msg = "labeling signature same as ".concat(dupeString)
            return(
                <Tooltip title={msg}><WarningIcon color={"error"}/></Tooltip>
            )
        }
    }

    render() {

        const headCells = [
          { id: 'conditions', numeric: false, disablePadding: false, label: 'Conditions' },
          //{ id: 'order', numeric: false, disablePadding: true, label: 'In Order' },
          { id: 'label', numeric: false, disablePadding: true, label: 'Label' },
          { id: 'dev_set_accuracy', numeric: true, disablePadding: true, label: 'Est. Accuracy' },
          { id: 'Coverage', numeric: true, disablePadding: true, label: 'Coverage' },
          { id: 'Conflicts', numeric: true, disablePadding: true, label: 'Conflicts' },
        ];

        const { classes } = this.props;
        const createSortHandler = property => event => {
            const isDesc = orderBy === property && order === 'desc';
            this.setState({
                order: isDesc ? 'asc' : 'desc',
                orderBy: property
            });
        };

        const order = this.state.order;
        const orderBy = this.state.orderBy;

        var LFList = Object.keys(this.props.labelingFunctions).map(lf_key => this.LFtoStrings(lf_key, this.props.labelingFunctions[lf_key]));
        const inactive = LFList.filter(LF => !LF.active);
        LFList = LFList.filter(LF => LF.active);
        let any_dupes = false;
        if (LFList.some(lf => lf["Duplicate"])) {
            any_dupes = true;
            headCells.push({ id: 'Duplicate', numeric: false, disablePadding: true, label: 'Duplicate' },
)
        }

        return(
          <Paper className={classes.paper}>
            <Typography className={classes.title} variant="h6" id="tableTitle">
                Selected Labeling Functions ({LFList.length}) 
            </Typography>
            {any_dupes ? <Typography color="error"><WarningIcon/><br/>Some of your functions have duplicate labeling signatures. Consider deleting the indicated functions.</Typography> : ""}
            {this.props.pending ? <LinearProgress/> : <Divider/>}
            <Table size="small" aria-label="Selected labeling functions table">
              <TableHead>
                  <TableRow>
                      <TableCell></TableCell>

                    {headCells.map(headCell => (
                      <TableCell
                        key={headCell.id}
                        align='right'
                        padding="none"
                        sortDirection={orderBy === headCell.id ? order : false}
                      >
                        <TableSortLabel
                          active={orderBy === headCell.id}
                          direction={order}
                          onClick={createSortHandler(headCell.id)}
                        >
                          {headCell.label}
                          {orderBy === headCell.id ? (
                            <span className={classes.visuallyHidden}>
                              {order === 'desc' ? 'sorted descending' : 'sorted ascending'}
                            </span>
                          ) : null}
                        </TableSortLabel>
                      </TableCell>
                    ))}
                    <TableCell></TableCell>
                  </TableRow>
              </TableHead>
              <TableBody>

                {stableSort(LFList, getSorting(order, orderBy))
                    .map(row => (
                  <TableRow key={row.id}>
                    <TableCell><LFPanel {...this.props} lf={row}/></TableCell>
                    <TableCell>{row.conditions}</TableCell>
                    {/*<TableCell>{row.order}</TableCell>*/}
                    <TableCell>{row.label}</TableCell>
                    <TableCell align="right">{"dev_set_accuracy" in row    ? style(row.dev_set_accuracy)    : "..."}</TableCell> 
                    <TableCell align="right">{"Coverage" in row  ? style(row.Coverage)  : "..."}</TableCell> 
                    <TableCell align="right">{"Conflicts" in row ? style(row.Conflicts) : "..."}</TableCell> 
                    {any_dupes ? <TableCell align="right">{this.duplicateCell(row.Duplicate)}</TableCell> : ""}                     
                    <TableCell><IconButton onClick={() => this.props.deleteLF([row.id])} size="small"><ClearIcon/></IconButton></TableCell>

                  </TableRow>
                ))}
            </TableBody>
            </Table>

            { inactive.length > 0 ? <Typography className={classes.title} variant="h6" id="tableTitle">Inactive Functions ({inactive.length})</Typography> : ""}
            <Table>
            <FadedTableBody>
               {inactive.map(row => (
                  <TableRow key={row.id}>
                    <TableCell>{/*<LFPanel {...this.props} lf={row}/>*/}</TableCell>
                    <TableCell>{row.conditions}</TableCell>
                    {/*<TableCell>{row.order}</TableCell>*/}
                    <TableCell>{row.label}</TableCell>
                    <TableCell align="right">{"dev_set_accuracy" in row    ? style(row.dev_set_accuracy)    : "..."}</TableCell> 
                    <TableCell align="right">{"Coverage" in row  ? style(row.Coverage)  : "..."}</TableCell> 
                    <TableCell align="right">{"Conflicts" in row ? style(row.Conflicts) : "..."}</TableCell> 
                    <TableCell><IconButton onClick={
                        () => this.props.submitLFs({[row.id]: row})
                    } size="small"><PublishIcon/></IconButton></TableCell>
                  </TableRow>
                ))}

            </FadedTableBody>
            </Table>
          </Paper>
        );
    }
}

function mapStateToProps(state) {
    return { 
        labelingFunctions: state.selectedLF.data,
        pending: state.selectedLF.pending,
        labelClasses: state.labelClasses.data,
        connective: state.gll.connective,
        keyType: state.gll.keyType,
        stats: state.selectedLF.stats //to force update when statistics come in
    };
}

function mapDispatchToProps(dispatch) {
    return {
        getLFstats: bindActionCreators(getLFstats, dispatch),
        deleteLF: bindActionCreators(deleteLF, dispatch),
        submitLFs: bindActionCreators(submitLFs, dispatch)
    }
}

export default connect(mapStateToProps, mapDispatchToProps)(LabelingFunctions);