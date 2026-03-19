

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
    // outcomeIndex should be set depending on which outcome column is hovered
    const outcomeIndex = props.outcomeIndex || 1; // default to 1 if not provided

    const certainty = props.data[`Certainty_out${outcomeIndex}`];
    const withinstudy = props.data[`within_study_out${outcomeIndex}`];
    const reporting = props.data[`reporting_out${outcomeIndex}`];
    const indirectness = props.data[`indirectness_out${outcomeIndex}`];
    const imprecision = props.data[`imprecision_out${outcomeIndex}`];
    const heterogeneity = props.data[`heterogeneity_out${outcomeIndex}`];
    const incoherence = props.data[`incoherence_out${outcomeIndex}`];

    const backgroundColor = getBackgroundColorForCertainty(certainty);

    const info = [
        React.createElement('h4', {}, "Certainty in evidence: " + certainty),
        React.createElement('div', { style: { marginBottom: 8 } }, ''),
        React.createElement('div', {}, 'Within-study bias: ' + withinstudy),
        React.createElement('div', {}, 'Reporting bias: ' + reporting),
        React.createElement('div', {}, 'Indirectness: ' + indirectness),
        React.createElement('div', {}, 'Imprecision: ' + imprecision),
        React.createElement('div', {}, 'Heterogeneity: ' + heterogeneity),
        React.createElement('div', {}, 'Incoherence: ' + incoherence),
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

// helper function for background color
function getBackgroundColorForCertainty(certainty) {
    switch (certainty) {
        case 'Low':
            return '#B85042';
        case 'Moderate':
            return 'rgb(248, 212, 157)';
        case 'High':
            return 'rgb(90, 164, 105)';
        default:
            return 'lightgrey';
    }
};


dagcomponentfuncs.CustomTooltip2 = function (props) {
    const certainty = props.data.Certainty;
    const withinstudy = props.data.within_study;
    const reporting = props.data.reporting;
    const indirectness = props.data.indirectness;
    const imprecision = props.data.imprecision;
    const heterogeneity = props.data.heterogeneity;
    const incoherence = props.data.incoherence;


    const backgroundColor = getBackgroundColorForCertainty(certainty);

    const info = [
        React.createElement('h4', {}, "Certainty in evidence: " + certainty),
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



// dagcomponentfuncs.CustomTooltip2 = function (props) {
//     const certainty = props.data.Certainty_out1;
//     const withinstudy = props.data.within_study_out1;
//     const reporting = props.data.reporting_out1;
//     const indirectness = props.data.indirectness_out1;
//     const imprecision = props.data.imprecision_out1;
//     const heterogeneity = props.data.heterogeneity_out1;
//     const incoherence = props.data.incoherence_out1;


//     const backgroundColor = getBackgroundColorForCertainty(certainty);

//     const info = [
//         React.createElement('h4', {}, "Certainty of evidence: " + certainty),
//         React.createElement('div', { style: { marginBottom: 8 } }, ''),
//         React.createElement('div', {}, 'Within-study bias: '+ withinstudy),
//         React.createElement('div', {}, 'Reporting bias: '+reporting),
//         React.createElement('div', {}, 'Indirectness: '+indirectness),
//         React.createElement('div', {}, 'Imprecision: '+imprecision),
//         React.createElement('div', {}, 'Heterogeneity: '+heterogeneity),
//         React.createElement('div', {}, 'Incoherence: '+incoherence),

//     ];

//     return React.createElement(
//         'div',
//         {
//             style: {
//                 border: '1pt solid white',
//                 backgroundColor: backgroundColor,
//                 padding: 10,
//                 lineHeight: '20px',
//             },
//         },
//         info
//     );
// };


// dagcomponentfuncs.CustomTooltip3 = function (props) {
//     const certainty = props.data.Certainty_out2;
//     const withinstudy = props.data.within_study_out2;
//     const reporting = props.data.reporting_out2;
//     const indirectness = props.data.indirectness_out2;
//     const imprecision = props.data.imprecision_out2;
//     const heterogeneity = props.data.heterogeneity_out2;
//     const incoherence = props.data.incoherence_out2;


//     const backgroundColor = getBackgroundColorForCertainty(certainty);

//     const info = [
//         React.createElement('h4', {}, "Certainty of evidence: " + certainty),
//         React.createElement('div', { style: { marginBottom: 8 } }, ''),
//         React.createElement('div', {}, 'Within-study bias: '+ withinstudy),
//         React.createElement('div', {}, 'Reporting bias: '+reporting),
//         React.createElement('div', {}, 'Indirectness: '+indirectness),
//         React.createElement('div', {}, 'Imprecision: '+imprecision),
//         React.createElement('div', {}, 'Heterogeneity: '+heterogeneity),
//         React.createElement('div', {}, 'Incoherence: '+incoherence),

//     ];

//     return React.createElement(
//         'div',
//         {
//             style: {
//                 border: '1pt solid white',
//                 backgroundColor: backgroundColor,
//                 padding: 10,
//                 lineHeight: '20px',
//             },
//         },
//         info
//     );
// };





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

        // swap treatment and reference
        props.node.data.Treatment = temp.Reference;
        props.node.data.Reference = temp.Treatment;

        data = props.node.data;

        // find all outcomes: RR_outX, OR_outX, MD_outX, SMD_outX
        const outcomes = [];
        Object.keys(data).forEach(k => {
            const m = k.match(/^(RR|OR|MD|SMD)_out(\d+)$/);
            if (m) outcomes.push({ type: m[1], index: m[2] });
        });

        outcomes.forEach(({ type, index }) => {
            const valKey = `${type}_out${index}`;
            const loKey = `CI_lower_out${index}`;
            const hiKey = `CI_upper_out${index}`;
            const labelKey = `${type}_out${index}_label`;

            let main = parseFloat(data[valKey]);
            let lo = parseFloat(data[loKey]);
            let hi = parseFloat(data[hiKey]);

            if (type === "RR" || type === "OR") {
                // invert
                main = 1 / main;
                lo = 1 / lo;
                hi = 1 / hi;
            } else {
                // flip sign MD / SMD
                const newLo = -hi;
                const newHi = -lo;
                main = -main;
                lo = newLo;
                hi = newHi;
            }

            // apply updates directly to row data
            props.node.data[valKey] = main;
            props.node.data[loKey] = lo;
            props.node.data[hiKey] = hi;

            props.node.data[labelKey] =
                `${main.toFixed(2)} \n(${lo.toFixed(2)}, ${hi.toFixed(2)})`;
        });

        // refresh the grid row
        props.api.refreshCells({ rowNodes: [props.node], force: true });

        setData();
    }

    // icon as before
    let icon;
    if (props.icon) {
        icon = React.createElement(window.dash_iconify.DashIconify, {
            icon: props.icon,
            style: { color: props.color, fontSize: "24px" }
        });
    }

    return React.createElement(
        "div",
        {
            onClick,
            style: {
                background: "none",
                border: "none",
                cursor: "pointer",
                display: "flex",
                justifyContent: "center",
                alignItems: "center"
            }
        },
        icon
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





// Keep AG Grid column menu available: add a small menu button that calls
// the grid-provided `showColumnMenu` function with the clicked element.
// dagcomponentfuncs.HeaderWithIcon = function (props) {
//     const [hover, setHover] = React.useState(false);
//     const iconId = "info-icon-" + props.column.colId;
//     // small menu button handler — AG Grid expects the target element to anchor the menu
//     function onMenuClick(e) {
//         if (typeof props.showColumnMenu === 'function') {
//             // use the currentTarget so AG Grid anchors correctly
//             props.showColumnMenu(e.currentTarget);
//             e.stopPropagation();
//         }
//     }

//     return React.createElement(
//         "div",
//         {
//             style: {
//                 display: "flex",
//                 alignItems: "center",
//                 gap: "6px",
//                 paddingRight: "4px",
//                 width: '100%',
//                 boxSizing: 'border-box'
//             }
//         },
//         [
//             React.createElement("span", { key: "label", style: { flex: 1, textAlign: 'center' } }, props.displayName),
//             React.createElement(
//                 "span",
//                 {
//                     key: "info",
//                     id: iconId,
//                     onMouseEnter: () => setHover(true),
//                     onMouseLeave: () => setHover(false),
//                     style: {
//                         cursor: "pointer",
//                         fontSize: "16px",
//                         color: hover ? "rgb(228, 28, 2)" : "rgb(184, 80, 67)",
//                         fontWeight: hover ? "bolder" : "bold",
//                         marginLeft: "4px"
//                     },
//                 },
//                 "ⓘ"
//             ),
//             // Menu button: only render when the grid/column allows it. AG Grid
//             // columns can set `suppressHeaderMenuButton: true` (or the grid-level
//             // default can be set). If suppression is requested, do not render
//             // the menu button here so the header stays clean.
//             (props.suppressHeaderMenuButton ? null : React.createElement(
//                 "span",
//                 {
//                     key: "menu",
//                     className: "ag-header-icon ag-header-cell-menu-button",
//                     title: "Column menu",
//                     onClick: onMenuClick,
//                     style: {
//                         cursor: 'pointer',
//                         padding: '0 6px',
//                         fontSize: '14px',
//                         color: '#666'
//                     }
//                 },
//                 "⋮"
//             ))
//         ]
//     );
// };


dagcomponentfuncs.HeaderWithIcon = function (props) {
    const [hover, setHover] = React.useState(false);
    const iconId = "info-icon-" + props.column.colId;

    // Function to open column menu (AG Grid standard)
    function onMenuClick(e) {
        if (typeof props.showColumnMenu === 'function') {
            props.showColumnMenu(e.currentTarget);
            e.stopPropagation();
        }
    }

    // Auto-set column width based on header text + icon
    React.useEffect(() => {
        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d');
        // Match the font style used in your header
        ctx.font = 'bold 14px Arial';
        const textWidth = ctx.measureText(props.displayName).width;

        const iconWidth = 20; // approximate width for your info icon + gap
        const padding = 16;   // header padding/margin
        const totalWidth = Math.ceil(textWidth + iconWidth + padding);

        // Set column width dynamically
        if (props.columnApi) {
            props.columnApi.setColumnWidth(props.column.colId, totalWidth);
        }
    }, [props.displayName, props.columnApi, props.column.colId]);

    return React.createElement(
        "div",
        {
            style: {
                display: "flex",
                alignItems: "center",
                gap: "6px",
                paddingRight: "4px",
                boxSizing: 'border-box',
                width: 'auto',  // allow container to fit content
            }
        },
        [
            // Header label
            React.createElement(
                "span",
                {
                    key: "label",
                    style: {
                        textAlign: 'center',
                        whiteSpace: 'nowrap', // prevent wrapping
                    }
                },
                props.displayName
            ),

            // Info icon
            React.createElement(
                "span",
                {
                    key: "info",
                    id: iconId,
                    onMouseEnter: () => setHover(true),
                    onMouseLeave: () => setHover(false),
                    style: {
                        cursor: "pointer",
                        fontSize: "16px",
                        color: hover ? "rgb(228, 28, 2)" : "rgb(184, 80, 67)",
                        fontWeight: hover ? "bolder" : "bold",
                        marginLeft: "4px"
                    },
                },
                "ⓘ"
            ),

            // Menu button (optional, based on AG Grid suppressHeaderMenuButton)
            (!props.suppressHeaderMenuButton ? React.createElement(
                "span",
                {
                    key: "menu",
                    className: "ag-header-icon ag-header-cell-menu-button",
                    title: "Column menu",
                    onClick: onMenuClick,
                    style: {
                        cursor: 'pointer',
                        padding: '0 6px',
                        fontSize: '14px',
                        color: '#666'
                    }
                },
                "⋮"
            ) : null)
        ]
    );
};

