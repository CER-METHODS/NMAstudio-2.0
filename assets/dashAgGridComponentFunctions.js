

var dagfuncs = window.dashAgGridFunctions = window.dashAgGridFunctions || {};

dagfuncs.rowSpan = function (params) {
    var Ref = params.data ? params.data.Reference : undefined;

    if (Ref !== '') {
        // have selected in column ref of height of 2*lenth rows
        return 10;
        
    } else {
        // all other rows should be just normal
        return 0;
    }
}



// var dagcomponentfuncs = window.dashAgGridComponentFunctions = window.dashAgGridComponentFunctions || {};

// dagcomponentfuncs.DCC_GraphClickData = function (props) {
//     const {setData} = props;
//     function setProps() {
//         const graphProps = arguments[0];
//         if (graphProps['clickData']) {
//             setData(graphProps);
//         }
//     }
//     return React.createElement(window.dash_core_components.Graph, {
//         figure: props.value,
//         setProps,
//         style: {height: '100%'},
//         config: {displayModeBar: false},
//     });
// };

var dagcomponentfuncs = window.dashAgGridComponentFunctions = window.dashAgGridComponentFunctions || {};

dagcomponentfuncs.DCC_GraphClickData = function (props) {
    const { setData, value } = props;
    
    // Check if the value is a figure (you may need to adjust this condition)
    const isFigure = typeof value === 'object' && value.hasOwnProperty('data') && value.hasOwnProperty('layout');
    
    // If it's a figure, render the graph; otherwise, render the cell value
    if (isFigure) {
        return React.createElement(window.dash_core_components.Graph, {
            figure: value,
            setProps: (graphProps) => {
                if (graphProps['clickData']) {
                    setData(graphProps);
                }
            },
            style: { height: '100%' },
            config: { displayModeBar: false, scrollZoom : false},
        });
    } else {
        return String(value);
    }
};





// dagcomponentfuncs.CustomTooltip = function (props) {
//     info = [
//         React.createElement('h4', {}, "Certainty of evidence:"+ props.data.Certainty),
//         React.createElement('div', { style: { marginBottom: 8 } }, ''),
//         React.createElement('div', {}, 'Risk of bias: Not serious'),
//         React.createElement('div', {}, 'Inconsistency: Not serious'),
//         React.createElement('div', {}, 'Publication Bias: Not serious'),
//         React.createElement('div', {}, 'Imprecision:: Not serious'),
//         React.createElement('div', {}, 'Intransitivity: Not serious'),
//     ];
//     return React.createElement(
//         'div',
//         {
//             style: {
//                 border: '1pt solid white',
//                 backgroundColor: props.color || 'grey',
//                 padding: 10,
//                 lineHeight: '20px' 
//             },
//         },
//         info
//     );
// };

// dagcomponentfuncs.CustomTooltiptreat = function (props) {
//     return React.createElement(
//         'div',
//         {
//             style: {
//                 border: '5px',
//                 backgroundColor: props.color || 'grey',
//                 padding: 10,
//             },
//         },
//         [
//             React.createElement('b', {}, 'Click a cell to see the details of the corresponding comparison')
//         ]
//     );
// };







dagcomponentfuncs.CustomTooltip = function (props) {
    const certainty = props.data.Certainty;
    const withinstudy = props.data.within_study;
    const reporting = props.data.reporting;
    const indirectness = props.data.indirectness;
    const imprecision = props.data.imprecision;
    const heterogeneity = props.data.heterogeneity;
    const incoherence = props.data.incoherence;


    const backgroundColor = getBackgroundColorForCertainty(certainty);

    const info = [
        React.createElement('h4', {}, "Certainty of evidence: " + certainty),
        React.createElement('div', { style: { marginBottom: 8 } }, ''),
        React.createElement('div', {}, 'Within-study bias: '+ withinstudy),
        React.createElement('div', {}, 'Reporting bias: '+reporting),
        React.createElement('div', {}, 'Indirectness: '+indirectness),
        React.createElement('div', {}, 'Imprecision: '+imprecision),
        React.createElement('div', {}, 'Heterogeneity: '+heterogeneity),
        React.createElement('div', {}, 'Incoherence: '+incoherence),

    ];

    return React.createElement(
        'div',
        {
            style: {
                border: '1pt solid white',
                backgroundColor: backgroundColor,
                padding: 10,
                lineHeight: '20px',
            },
        },
        info
    );
};

function getBackgroundColorForCertainty(certainty) {
    switch (certainty) {
        case 'Low':
            return '#B85042';
        case 'Moderate':
            return 'rgb(248, 212, 157)';
        case 'High':
            return 'rgb(90, 164, 105)';
        default:
            return 'lightgrey'; // Default background color
    }
};





dagcomponentfuncs.CustomTooltip2 = function (props) {
    const certainty = props.data.Certainty_out1;
    const withinstudy = props.data.within_study_out1;
    const reporting = props.data.reporting_out1;
    const indirectness = props.data.indirectness_out1;
    const imprecision = props.data.imprecision_out1;
    const heterogeneity = props.data.heterogeneity_out1;
    const incoherence = props.data.incoherence_out1;


    const backgroundColor = getBackgroundColorForCertainty(certainty);

    const info = [
        React.createElement('h4', {}, "Certainty of evidence: " + certainty),
        React.createElement('div', { style: { marginBottom: 8 } }, ''),
        React.createElement('div', {}, 'Within-study bias: '+ withinstudy),
        React.createElement('div', {}, 'Reporting bias: '+reporting),
        React.createElement('div', {}, 'Indirectness: '+indirectness),
        React.createElement('div', {}, 'Imprecision: '+imprecision),
        React.createElement('div', {}, 'Heterogeneity: '+heterogeneity),
        React.createElement('div', {}, 'Incoherence: '+incoherence),

    ];

    return React.createElement(
        'div',
        {
            style: {
                border: '1pt solid white',
                backgroundColor: backgroundColor,
                padding: 10,
                lineHeight: '20px',
            },
        },
        info
    );
};


dagcomponentfuncs.CustomTooltip3 = function (props) {
    const certainty = props.data.Certainty_out2;
    const withinstudy = props.data.within_study_out2;
    const reporting = props.data.reporting_out2;
    const indirectness = props.data.indirectness_out2;
    const imprecision = props.data.imprecision_out2;
    const heterogeneity = props.data.heterogeneity_out2;
    const incoherence = props.data.incoherence_out2;


    const backgroundColor = getBackgroundColorForCertainty(certainty);

    const info = [
        React.createElement('h4', {}, "Certainty of evidence: " + certainty),
        React.createElement('div', { style: { marginBottom: 8 } }, ''),
        React.createElement('div', {}, 'Within-study bias: '+ withinstudy),
        React.createElement('div', {}, 'Reporting bias: '+reporting),
        React.createElement('div', {}, 'Indirectness: '+indirectness),
        React.createElement('div', {}, 'Imprecision: '+imprecision),
        React.createElement('div', {}, 'Heterogeneity: '+heterogeneity),
        React.createElement('div', {}, 'Incoherence: '+incoherence),

    ];

    return React.createElement(
        'div',
        {
            style: {
                border: '1pt solid white',
                backgroundColor: backgroundColor,
                padding: 10,
                lineHeight: '20px',
            },
        },
        info
    );
};





function getBackgroundColorForCertainty(certainty) {
    switch (certainty) {
        case 'Low':
            return '#B85042';
        case 'Moderate':
            return 'rgb(248, 212, 157)';
        case 'High':
            return 'rgb(90, 164, 105)';
        default:
            return 'lightgrey'; // Default background color
    }
};






dagcomponentfuncs.DMC_Button = function (props) {
    var { setData, data } = props;

    function onClick() {   
        const temp = structuredClone(data);
        props.node.setDataValue( "Treatment", temp.Reference);
        props.node.setDataValue( "Reference", temp.Treatment);
        data = props.node.data;
        // const tempRR = data.RR;
        // props.node.setDataValue("RR", parseFloat((1 / data.RR).toFixed(2)))
        // props.node.setDataValue("RR_out2", parseFloat((1 / data.RR_out2).toFixed(2)));

        // const temp3 = data.RR_out2;
        // props.node.setDataValue("RR_out2", data.RR_inv2);
        // props.node.setDataValue("RR_inv2", temp3);
        
        const rrParts = data.RR.match(/([\d.]+)\n\(([\d.]+) to ([\d.]+)\)/);
        if (rrParts) {
            const mainRR = parseFloat(rrParts[1]);
            const ciLower = parseFloat(rrParts[2]);
            const ciUpper = parseFloat(rrParts[3]);

            const invertedMainRR = (1 / mainRR).toFixed(2);
            const invertedCiLower = (1 / ciLower).toFixed(2);
            const invertedCiUpper = (1 / ciUpper).toFixed(2);

            // Reformat the RR string with inverted values
            const newRR = `${invertedMainRR}\n(${invertedCiLower} to ${invertedCiUpper})`;
            props.node.setDataValue("RR", newRR);
        }
        
        const rrParts2 = data.RR_out2.match(/([\d.]+)\n\(([\d.]+) to ([\d.]+)\)/);
        if (rrParts2) {
            const mainRR2 = parseFloat(rrParts2[1]);
            const ciLower2 = parseFloat(rrParts2[2]);
            const ciUpper2 = parseFloat(rrParts2[3]);

            const invertedMainRR2 = (1 / mainRR2).toFixed(2);
            const invertedCiLower2 = (1 / ciLower2).toFixed(2);
            const invertedCiUpper2 = (1 / ciUpper2).toFixed(2);

            // Reformat the RR string with inverted values
            const newRR2 = `${invertedMainRR2}\n(${invertedCiLower2} to ${invertedCiUpper2})`;
            props.node.setDataValue("RR_out2", newRR2);
        }

        setData();
    }

    // Create the icon element
    let icon;
    if (props.icon) {
        icon = React.createElement(window.dash_iconify.DashIconify, {
            icon: props.icon,
            style: {
                color: props.color, // Apply color directly to the icon
                fontSize: '24px' // Adjust size as needed
            },
        });
    }

    // Return a minimal button with no background or borders
    return React.createElement(
        "div", // Change from a button to a div or span for no button appearance
        {
            onClick,
            style: {
                background: 'none',   // No background
                border: 'none',       // No border
                cursor: 'pointer',    // Pointer cursor for clickability
                display: 'flex',
                justifyContent: 'center',
                alignItems: 'center',
            },
        },
        icon // Use only the icon as content
    );
};



// dagcomponentfuncs.StudyLink = function (props) {
//     return React.createElement(
//         'a',
//         {
//             href: props.node.data.link,
//             target: "_blank"
//         },
//         props.value
//     );
// };


dagcomponentfuncs.StudyLink = function (props) {
    return React.createElement(
        'a',
        {
            href: props.node.data.link,
            target: "_blank",
            style: {
                color: 'gray',
                textDecoration: 'none'
            },
            onMouseEnter: (e) => e.target.style.color = 'green',
            onMouseLeave: (e) => e.target.style.color = 'gray'
        },
        props.value
    );
};



dagcomponentfuncs.HeaderWithIcon = function (props) {
    const [hover, setHover] = React.useState(false);
    // make an ID based on the header name (safe for HTML)
    const iconId = "info-icon-" + props.column.colId;
    
    return React.createElement(
        "div",
        {
            style: {
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                gap: "4px"
            }
        },
        [
            React.createElement("span", { key: "label" }, props.displayName),
            React.createElement(
                "span",
                {
                    id: iconId,  // must match Popover target
                    onMouseEnter: () => setHover(true),
                    onMouseLeave: () => setHover(false),
                    style: {
                        cursor: "pointer",
                        fontSize: "16px",
                        color: hover ? "rgb(228, 28, 2)" : "rgb(184, 80, 67)",
                        fontWeight: hover ? "bold" : "normal",
                        marginLeft: "4px"
                    },
                },
                "ⓘ"   // info icon
            )
        ]
    );
};



