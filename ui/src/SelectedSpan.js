import React from 'react';
import PropTypes from 'prop-types';
import {connect} from "react-redux";

import Badge from '@material-ui/core/Badge';
import Box from '@material-ui/core/Box';
import CancelIcon from '@material-ui/icons/Cancel';
import IconButton from '@material-ui/core/IconButton';
import LinkIcon from '@material-ui/icons/Link';
import LinkOffIcon from '@material-ui/icons/LinkOff';
import Typography from '@material-ui/core/Typography';

import { DIR_LINK, UNDIR_LINK } from './AnnotationBuilder'

class SelectedSpan extends React.Component {
    constructor(props){
        super(props);

        this.handleClick = this.handleClick.bind(this);
        this.handleMouseHover = this.handleMouseHover.bind(this);
        this.state = {
            isHovering: false,
        };
    }

    handleMouseHover(newState) {
        this.setState({isHovering: newState});
    }

    handleClick(){
        this.props.annotate();
    }

    render(){
        const classes = this.props.classes;
        const linkVisible = ((this.state.isHovering) || (this.props.selectedLink.type===UNDIR_LINK));
        let style = this.props.style;

        const innerSpan = (
                    <Box style={style} className={classes.box} boxShadow={1}>              
                    <Typography 
                        component="div"
                        className={ classes.text } 
                        onClick={ ("clickSegment" in this.props) ? this.props.clickSegment : ()=>{} }
                        onMouseEnter={() => this.handleMouseHover(true)}
                        onMouseLeave={() => this.handleMouseHover(false)}
                        id={this.props.id}
                        display="inline">
                    {this.props.text}
                    </Typography> 
                    </Box>
        );

        if ((this.props.clickLinkButton) && (this.props.onDelete)) {
            return(
                <Badge 
                    invisible={!this.state.isHovering} 
                    anchorOrigin={{vertical: 'top',horizontal: 'right'}}
                    badgeContent={
                        <IconButton 
                            size="small"
                            onMouseEnter={() => this.handleMouseHover(true)}
                            onMouseLeave={() => this.handleMouseHover(false)} 
                            onClick={this.props.onDelete}><CancelIcon/></IconButton>
                    }
                >
                <Badge 
                    style={{width: "-webkit-fill-available"}}
                    invisible={!linkVisible} 
                    anchorOrigin={{vertical: 'top',horizontal: 'left'}}
                    badgeContent={
                        <IconButton 
                            size="small"
                            onMouseEnter={() => this.handleMouseHover(true)}
                            onMouseLeave={() => this.handleMouseHover(false)} 
                            onClick={ this.props.clickLinkButton }>
                                {this.props.linked ? <LinkOffIcon/> : <LinkIcon/>}
                        </IconButton>
                    }>  
                {innerSpan}
                </Badge>
                </Badge>
            )
        } else {
            return innerSpan;
        }
    }
}

SelectedSpan.propTypes = {
    annotate: PropTypes.func,
    clickLinkButton: PropTypes.func,
    onDelete: PropTypes.func,
    classes: PropTypes.object,
    clickSegment: PropTypes.func

}

function mapStateToProps(state, ownProps?) {
    return { selectedLink: state.selectedLink };
}
function mapDispatchToProps(dispatch) {
    return {};
}

export default connect(mapStateToProps, mapDispatchToProps)(SelectedSpan);