import React from 'react';
import Button from '@material-ui/core/Button';
import ButtonGroup from '@material-ui/core/ButtonGroup';
import {connect} from "react-redux";

class ClassLabelsCollection extends React.Component {
    constructor(props) {
      super(props)
      this.keyHandling = this.keyHandling.bind(this);
      this.assignLabel = this.assignLabel.bind(this);
    }

    defaultSelections

    keyHandling(e) {
      const key = parseInt(e.key);
      if (key in this.props.hotKeys)  {
        this.assignLabel(key);
      }
    }

    assignLabel(key) {
      this.props.onClick(key);
    }

    componentDidMount() {     
      window.addEventListener("keyup", this.keyHandling);   
    }        

    componentWillUnmount() {      
      window.removeEventListener("keyup", this.keyHandling);   
    }

    render(){
        const classes = this.props.classes;
        return (
            <ButtonGroup color="primary">
             { Object.entries(this.props.labelClasses).map( (labelClass, key) => 
                   <Button 
                        className={classes.button} 
                        key = {key}
                        onClick={() => this.assignLabel(key)} 
                        variant={(this.props.label === key) ? "contained" : "outlined"}
                    >
                        ({key})
                        {labelClass}
                    </Button>
                  )
              }
            </ButtonGroup>)
    }   
}

function mapStateToProps(state, ownProps?) {
    return { 
      labelClasses: state.labelClasses.data,
      hotKeys: Object.values(state.labelClasses.data).map(lClass => lClass.key),
      annotations: state.annotations,
      label: state.label
    };
}
function mapDispatchToProps(state){
  return {};
}

export default connect(mapStateToProps, mapDispatchToProps)(ClassLabelsCollection);