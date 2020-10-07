import React from "react";
import PropTypes from "prop-types";
import { connect } from "react-redux";

import CancelIcon from "@material-ui/icons/Cancel";
import IconButton from "@material-ui/core/IconButton";
import LinkIcon from "@material-ui/icons/Link";
import LinkOffIcon from "@material-ui/icons/LinkOff";
import Typography from "@material-ui/core/Typography";

import { InlineBox } from "./RichTextUtils";
import { DIR_LINK, UNDIR_LINK } from "./AnnotationBuilder";

import { styled } from "@material-ui/core/styles";
import Badge from "@material-ui/core/Badge";

const DeleteBadge = styled(Badge)({
    width: "fit-content",
    display: "inline",
    left: 10,
});

const LinkBadge = styled(Badge)({
    width: "fit-content",
    display: "inline",
    //top: 5
});

class SelectedSpan extends React.Component {
    constructor(props) {
        super(props);

        this.handleClick = this.handleClick.bind(this);
        this.handleMouseHover = this.handleMouseHover.bind(this);
        this.state = {
            isHovering: false,
        };
    }

    handleMouseHover(newState) {
        this.setState({ isHovering: newState });
    }

    delayMouseLeave() {
        setTimeout(
            function () {
                this.setState({ isHovering: false });
            }.bind(this),
            1000
        );
    }

    handleClick() {
        this.props.annotate();
    }

    render() {
        const classes = this.props.classes;
        const linkVisible =
            this.state.isHovering ||
            this.props.selectedLink.type === UNDIR_LINK;
        let style = this.props.style;

        const text = this.props.text;

        const innerSpan = (
            <InlineBox
                style={style}
                className={classes.box}
                boxShadow={1}
                onMouseEnter={() => this.handleMouseHover(true)}
                onMouseLeave={() => this.handleMouseHover(false)}
                onClick={
                    "clickSegment" in this.props
                        ? this.props.clickSegment
                        : () => {}
                }
            >
                <Typography
                    ref={this.textspan}
                    component="div"
                    className={classes.text}
                    id={this.props.id}
                    display="inline"
                >
                    {text}
                </Typography>
            </InlineBox>
        );

        if (this.props.clickLinkButton && this.props.onDelete) {
            return (
                <>
                    <LinkBadge
                        invisible={!linkVisible}
                        //anchorOrigin={{vertical: 'bottom',horizontal: 'left'}}
                        badgeContent={
                            <IconButton
                                size="small"
                                onMouseEnter={() => this.handleMouseHover(true)}
                                //onMouseLeave={() => this.handleMouseHover(false)}
                                onClick={this.props.clickLinkButton}
                            >
                                {this.props.linked ? (
                                    <LinkOffIcon />
                                ) : (
                                    <LinkIcon />
                                )}
                            </IconButton>
                        }
                    >
                        {""}
                    </LinkBadge>
                    {innerSpan}
                    <DeleteBadge
                        invisible={!this.state.isHovering}
                        badgeContent={
                            <IconButton
                                size="small"
                                onMouseEnter={() => this.handleMouseHover(true)}
                                //onMouseLeave={() => this.handleMouseHover(false)}
                                onClick={this.props.onDelete}
                            >
                                <CancelIcon />
                            </IconButton>
                        }
                    >
                        {""}
                    </DeleteBadge>
                </>
            );
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
    clickSegment: PropTypes.func,
};

function mapStateToProps(state, ownProps?) {
    return { selectedLink: state.selectedLink };
}
function mapDispatchToProps(dispatch) {
    return {};
}

export default connect(mapStateToProps, mapDispatchToProps)(SelectedSpan);
