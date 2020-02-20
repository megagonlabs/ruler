import React from 'react';
import {connect} from "react-redux";
import PropTypes from 'prop-types';

import Box from '@material-ui/core/Box';
import Link from './Link'
import SelectedSpan from './SelectedSpan'
import Span from './Span'
import Typography from '@material-ui/core/Typography';

export const DEFAULT_LABEL = 0;
// TODO use defaultdict instead of default label?

class AnnotationDisplay extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            mounted: false
        };
    }

    componentDidMount() {
        // Delays rendering of links.
        //      Why? creation of links required detecting where the spans are located. 
        //      to avoid finding this position while the spans are animating (such
        //      as in a modal or badge), we wait to render the links.
        setTimeout(function() {
            this.setState({mounted: true})
        }.bind(this), 100);
    }

    componentWillUnmount() {
        this.setState({mounted: false})
    }

    // returns a dictionary of styling information for each concept
    getStyle() {
        const default_style = {
            id: DEFAULT_LABEL, 
            text_color: 'inherit', 
            background_color: '#D3D3D3'
        };
        // define styling for highlighted spans without assigned concepts (id=DEFAULT_LABEL)
        var getStyle = new Proxy({}, {
          get: (target, name) => name in target ? target[name] : default_style
        })
        const concepts = Object.keys(this.props.concepts);
        for (let i = 0; i < concepts.length; i++) {
            let concept = concepts[i];
            getStyle[concept] = { 
                id: concept,
                text_color: "white", 
                background_color: this.props.concepts[concept]["color"],
            };
        }
        return getStyle;
    }

    addRichText(chunks, highlights) {
        var h_index = 0;
        var highlight = highlights[h_index];
        var rich_texts = [];
        for (var chunk of chunks) {
            var text = [];
            var loc = 0;
            while ((h_index < highlights.length) && (chunk.end_offset > highlight.start_offset)) {
                var bold_start = Math.max(0, highlight.start_offset - chunk.start_offset);
                if (bold_start > 1) {
                    text.push(<React.Fragment key={loc}>{chunk.text.slice(loc, bold_start)}</React.Fragment>);
                }
                var bold_end = Math.min(0, highlight.end_offset - chunk.end_offset) + chunk.text.length;
                text.push(<Box className={this.props.classes.box} fontWeight="fontWeightBold" key={bold_start}>{chunk.text.slice(bold_start, bold_end)}</Box>);
                loc = bold_end;
                h_index++;
                highlight = highlights[h_index];
            }
            if (chunk.text.length > loc) {
                text.push(<React.Fragment key={loc}>{chunk.text.slice(loc, chunk.text.length)}</React.Fragment>);
            }
            rich_texts.push(text);
        }
        return rich_texts;
    }

    chunks(annotations, text) {
        const res = [];
        let left = 0;
        for (let i = 0; i < annotations.length; i++) {
            const e = annotations[i];
            // annotations must be sorted by start offset, and must not overlap!
            if (e.start_offset < left){
                console.error("Annotations are overlapping or out of order.");
                console.error(annotations);
            }

            if (left !== e.start_offset){
                const l = Span(left, e.start_offset, text);
                res.push(l); 
            }
            e.text = text.slice(e.start_offset, e.end_offset);
            res.push(e);
            left = e.end_offset;
        }
        const l = Span(left, text.length, text);
        res.push(l);
        return res;
    }

    createSelectedSpan(s, rich_text=null, divStyle={}) {
        return (
            <SelectedSpan 
                key={s.start_offset} 
                id={ `selection_${s.id}` }
                classes={this.props.classes} 
                style={divStyle}
                text={rich_text ? rich_text : s.text}
                linked={s.link !== null}

                // optional props
                clickSegment = {"clickSegment" in this.props ? () => this.props.clickSegment(s) : undefined}
                clickLinkButton = {"clickLinkButton" in this.props ? () => this.props.clickLinkButton(s) : undefined }
                onDelete = {"onDelete" in this.props ? () => this.props.onDelete(s.start_offset) : undefined } 
            />);
    }

    render() {
        const getStyle = this.getStyle();
        const classes = this.props.classes;

        let annotations = this.props.annotations || [];
        let highlights = this.props.highlights || [];

        let segments = this.chunks(annotations, this.props.text, highlights);
        let rich_texts = this.addRichText(segments, highlights);

        let links = {};
        let tags = segments.map(
            (s, index) => {
                if (s.label !== null) {
                    let divStyle = {
                        color: getStyle[s.label].text_color,
                        backgroundColor: getStyle[s.label].background_color,
                    };

                    if (s.link !== null) {
                        if (!(s.link in links)) {
                            links[s.link] = [];
                        }
                        links[s.link].push(s);
                    }

                    return (this.createSelectedSpan(s, rich_texts[index], divStyle));
                }
                return (
                <Typography 
                    component="div"
                    className={classes.text}
                    key={s.id+'raw'}
                >{rich_texts[index]}</Typography> )
            }
        );


        if (this.state.mounted) {
            links = Object.values(links).map( link => {
                const from=`selection_${link[0].id}`;
                const to=`selection_${link[1].id}`;
                return(<Link 
                    key={["link", "from", from, "to", to].join("_")} 
                    from={from} 
                    to={to}
                    classes={classes}
                    className={classes.link}
                />);
            });
        } else {
            links = [];
        }

        return (
        <React.Fragment>
        <div className={this.props.classes.text} 
            id='text-to-label' 
            onMouseUp={this.props.onMouseUp}
            ref={this.props.textAreaRef}>
            <br/>
            {tags}
            <br/>
        </div>
        {links}
        </React.Fragment>
    )}
}

AnnotationDisplay.propTypes = {
    text: PropTypes.string.isRequired,
    annotations: PropTypes.array,
    highlights: PropTypes.array,
    onMouseUp: PropTypes.func,
    classes: PropTypes.object,
};

function mapStateToProps(state, ownProps?) {
    return { 
        concepts: state.concepts.data
    }
}
function mapDispatchToProps(dispatch) {
    return {}
}

export default connect(mapStateToProps, mapDispatchToProps)(AnnotationDisplay)