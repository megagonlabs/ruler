import React from 'react';
import Button from '@material-ui/core/Button';
import AddIcon from '@material-ui/icons/Add';
import InputBase from '@material-ui/core/InputBase';
import PropTypes from 'prop-types';
import {conceptEditors, select_concept} from './actions/concepts'
import {bindActionCreators} from 'redux';
import {connect} from "react-redux";
import Concept from './Concept'


class ConceptCollection extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      conceptName: "",
      fetched: false,
    };
    this.handleInput = this.handleInput.bind(this);
    this.handleKeyPress = this.handleKeyPress.bind(this);
    this.handleAdd = this.handleAdd.bind(this);
  }

  componentDidMount() {
      if (!this.state.fetched) {
        this.props.conceptEditors.fetchConcepts();
        this.setState({fetched: true});
      }
  }

  handleInput(event) {
    this.setState({
      conceptName: event.target.value
    });
  }

  handleAdd() {
    const newConcept = this.state.conceptName.trim()
    if (newConcept !== "") {
      this.setState({conceptName: ""});
      this.props.conceptEditors.addConcept(newConcept);
      this.props.select_concept(newConcept);
    }
  }

  handleKeyPress(event){ 
      if (event.key === 'Enter') {
          this.handleAdd();
      }
  }

  render() {
    const conceptNames = Object.keys(this.props.concepts);
    const classes = this.props.classes;

    return (
       <div>
           { conceptNames.map( (concept) =>
                 <Concept key={concept} concept={concept} classes={classes} addAnnotations={this.props.addAnnotations} shouldStatsUpdate={this.props.shouldStatsUpdate}/>
              )
            }

           <InputBase
               className={classes.input}
               placeholder="add new concept"
               inputProps={{ 'aria-label': ' ' }}
               onKeyPress = {this.handleKeyPress}
               onChange = {this.handleInput}
               value={this.state.conceptName}
           />
            <Button className={classes.button} size="small" color="primary" aria-label="add" 
                onClick={this.handleAdd} disabled={(this.state.conceptName==="")} >
                <AddIcon />
            </Button>
       </div>
    );
  }
}

ConceptCollection.propTypes = {
  addAnnotations: PropTypes.func,
  classes: PropTypes.object.isRequired,
  conceptEditors: PropTypes.object.isRequired
};

function mapStateToProps(state, ownProps?) {
    return { concepts: state.concepts.data };
}

function mapDispatchToProps(dispatch) {
    return { 
      conceptEditors: bindActionCreators(conceptEditors, dispatch),
      select_concept: bindActionCreators(select_concept, dispatch) 
    };
}

export default connect(mapStateToProps, mapDispatchToProps)(ConceptCollection);
