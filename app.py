from business import GraphBuilder, StatsBuilder
from dash import Input, Output, State, dcc, html
from dash import Dash
import dash_bootstrap_components as dbc
from dash_iconify import DashIconify

# Initialize app with modern theme
app = Dash(
    __name__, 
    external_stylesheets=[dbc.themes.QUARTZ, 'https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap'],
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}]
)

# Initialize business objects
gb = GraphBuilder()
sb = StatsBuilder()

# Define color scheme
COLORS = {
    "primary": "#6200EA",
    "secondary": "#03DAC5",
    "background": "#121212",
    "surface": "#1E1E1E",
    "text": "#FFFFFF",
    "accent": "#BB86FC",
}

# Custom style components
card_style = {
    "background-color": COLORS["surface"],
    "border-radius": "12px",
    "box-shadow": "0 4px 20px rgba(0, 0, 0, 0.15)",
    "padding": "20px",
    "margin-bottom": "25px",
}

header_style = {
    "color": COLORS["text"],
    "font-family": "Poppins, sans-serif",
    "font-weight": "600",
    "margin-bottom": "20px",
    "padding-bottom": "10px",
    "border-bottom": f"2px solid {COLORS['accent']}",
}

app.layout = dbc.Container(
    [
        dbc.Row(
            dbc.Col(
                html.Div(
                    [
                        html.H1("Experimental Analytics Platform", 
                               style={**header_style, "font-size": "2.5rem", "text-align": "center", "border-bottom": "none"}),
                        html.Div("Analyze demographic data and run statistical experiments", 
                                style={"color": "#B0BEC5", "text-align": "center", "margin-bottom": "30px", "font-family": "Poppins, sans-serif"})
                    ],
                ),
                width=12,
            ),
            style={"margin-top": "30px", "margin-bottom": "20px"},
        ),
        
        # Dashboard tabs - NEW FEATURE: Tabbed interface
        dbc.Tabs(
            [
                # Demographics tab
                dbc.Tab(
                    [
                        dbc.Card(
                            [
                                dbc.CardHeader([
                                    DashIconify(icon="mdi:account-group", width=24, style={"marginRight": "10px"}),
                                    "Enrollment Demographics"
                                ], style={"display": "flex", "align-items": "center", "font-size": "1.2rem", "font-weight": "500"}),
                                dbc.CardBody(
                                    [
                                        dbc.Row(
                                            [
                                                dbc.Col(
                                                    dbc.Select(
                                                        id="demo-plots-dropdown",
                                                        options=[
                                                            {"label": "Nationality Distribution", "value": "Nationality"},
                                                            {"label": "Age Distribution", "value": "Age"},
                                                            {"label": "Education Levels", "value": "Education"},
                                                        ],
                                                        value="Nationality",
                                                        style={"background-color": "#2D2D2D", "border": "none", "color": "#E0E0E0"},
                                                    ),
                                                    lg=4, md=6,
                                                ),
                                                # NEW FEATURE: Download option for the current chart
                                                dbc.Col(
                                                    dbc.Button(
                                                        [DashIconify(icon="mdi:download", width=18, style={"marginRight": "5px"}), "Download Chart"],
                                                        id="download-chart-button",
                                                        outline=True,
                                                        color="info",
                                                        size="sm",
                                                        className="ml-auto",
                                                        style={"float": "right"}
                                                    ),
                                                    lg=8, md=6,
                                                    style={"text-align": "right"}
                                                ),
                                            ],
                                            className="mb-3",
                                        ),
                                        html.Div(id="demo-plots-display"),
                                        dcc.Download(id="download-chart"),
                                    ]
                                ),
                            ],
                            style=card_style,
                        ),
                    ],
                    label="Demographics",
                    tab_id="tab-demographics",
                    label_style={"color": "#FFFFFF"},
                    active_label_style={"color": COLORS["accent"]},
                ),
                
                # Experiment tab
                dbc.Tab(
                    [
                        dbc.Row(
                            [
                                dbc.Col(
                                    dbc.Card(
                                        [
                                            dbc.CardHeader([
                                                DashIconify(icon="mdi:flask", width=24, style={"marginRight": "10px"}),
                                                "Experiment Configuration"
                                            ], style={"display": "flex", "align-items": "center", "font-size": "1.2rem", "font-weight": "500"}),
                                            dbc.CardBody(
                                                [
                                                    html.H5("Effect Size", className="mb-2", style={"color": "#E0E0E0"}),
                                                    dbc.Row(
                                                        [
                                                            dbc.Col(
                                                                dcc.Slider(
                                                                    min=0.1,
                                                                    max=0.8,
                                                                    step=0.1,
                                                                    value=0.2,
                                                                    id="effect-size-slider",
                                                                    marks={i/10: str(i/10) for i in range(1, 9)},
                                                                    tooltip={"placement": "bottom", "always_visible": True},
                                                                    className="mt-1 mb-4",
                                                                ),
                                                                width=10,
                                                            ),
                                                            dbc.Col(
                                                                html.Div(
                                                                    DashIconify(
                                                                        icon="mdi:information-outline",
                                                                        width=20,
                                                                        id="effect-size-info",
                                                                    ),
                                                                    style={"textAlign": "center"},
                                                                ),
                                                                width=2,
                                                            ),
                                                        ],
                                                    ),
                                                    dbc.Tooltip(
                                                        "Effect size is a quantitative measure of the magnitude of the experimental effect. Larger values indicate stronger effects that are easier to detect.",
                                                        target="effect-size-info",
                                                    ),
                                                    html.Div(id="effect-size-display", className="mb-4", 
                                                            style={"padding": "10px", "background": "#2D2D2D", "border-radius": "8px"}),
                                                    
                                                    html.H5("Experiment Duration (Days)", className="mb-2", style={"color": "#E0E0E0"}),
                                                    dbc.Row(
                                                        [
                                                            dbc.Col(
                                                                dcc.Slider(
                                                                    min=1,
                                                                    max=20,
                                                                    step=1,
                                                                    value=1,
                                                                    id="experiment-days-slider",
                                                                    marks={i: str(i) for i in range(1, 21, 2)},
                                                                    tooltip={"placement": "bottom", "always_visible": True},
                                                                    className="mt-1 mb-4",
                                                                ),
                                                                width=10,
                                                            ),
                                                            dbc.Col(
                                                                html.Div(
                                                                    DashIconify(
                                                                        icon="mdi:information-outline",
                                                                        width=20,
                                                                        id="duration-info",
                                                                    ),
                                                                    style={"textAlign": "center"},
                                                                ),
                                                                width=2,
                                                            ),
                                                        ],
                                                    ),
                                                    dbc.Tooltip(
                                                        "Choose how many days your experiment will run. Longer durations typically yield more observations.",
                                                        target="duration-info",
                                                    ),
                                                    html.Div(id="experiment-days-display", className="mb-4", 
                                                            style={"padding": "10px", "background": "#2D2D2D", "border-radius": "8px"}),
                                                    
                                                    dbc.Button(
                                                        [DashIconify(icon="mdi:play", width=20, style={"marginRight": "8px"}), "Begin Experiment"],
                                                        id="start-experiment-button",
                                                        color="primary",
                                                        style={"background-color": COLORS["primary"], "border": "none", "width": "100%", "margin-top": "10px"},
                                                        n_clicks=0,
                                                    ),
                                                ]
                                            ),
                                        ],
                                        style=card_style,
                                    ),
                                    md=5,
                                ),
                                
                                dbc.Col(
                                    dbc.Card(
                                        [
                                            dbc.CardHeader([
                                                DashIconify(icon="mdi:chart-bar", width=24, style={"marginRight": "10px"}),
                                                "Experiment Results"
                                            ], style={"display": "flex", "align-items": "center", "font-size": "1.2rem", "font-weight": "500"}),
                                            dbc.CardBody(
                                                [
                                                    html.Div(
                                                        [
                                                            html.Div(
                                                                DashIconify(
                                                                    icon="mdi:flask-empty-outline",
                                                                    width=64,
                                                                    color="#555555",
                                                                ),
                                                                style={"textAlign": "center", "margin": "40px 0 20px 0"},
                                                                id="placeholder-icon",
                                                            ),
                                                            html.Div(
                                                                "Configure your experiment and click 'Begin Experiment' to see results",
                                                                style={"color": "#888888", "textAlign": "center", "fontSize": "14px", "margin-bottom": "40px"},
                                                                id="placeholder-text",
                                                            ),
                                                            html.Div(id="results-display"),
                                                        ]
                                                    )
                                                ]
                                            ),
                                        ],
                                        style={**card_style, "height": "100%"},
                                    ),
                                    md=7,
                                ),
                            ],
                        ),
                    ],
                    label="Experiment",
                    tab_id="tab-experiment",
                    label_style={"color": "#FFFFFF"},
                    active_label_style={"color": COLORS["accent"]},
                ),
            ],
            id="tabs",
            active_tab="tab-demographics",
        ),
        
        # Footer
        html.Footer(
            dbc.Row(
                dbc.Col(
                    html.Div(
                        [
                            "© 2025 Experimental Analytics Platform ",
                            html.A("Documentation", href="#", style={"color": COLORS["accent"], "text-decoration": "none", "margin-left": "15px"}),
                        ],
                        style={"color": "#888888", "text-align": "center", "padding": "20px 0", "font-size": "0.8rem"}
                    ),
                    width=12
                )
            )
        )
    ],
    fluid=True,
    style={"background-color": COLORS["background"], "color": COLORS["text"], "min-height": "100vh", "padding": "0 25px 25px 25px"},
)


@app.callback(
    Output("demo-plots-display", "children"),
    Input("demo-plots-dropdown", "value")
)
def display_demo_graph(graph_name):
    """Serves applicant demograhic visualization.

    Parameters
    ----------
    graph_name : str
        User input given via 'demo-plots-dropdown'. Name of Graph to be returned.
        Options are 'Nationality', 'Age', 'Education'.

    Returns
    -------
    dcc.Graph
        Plot that will be displayed in 'demo-plots-display' Div.
    """
    if graph_name == "Nationality":
        fig = gb.build_nat_choropleth()
    elif graph_name == "Age":
        fig = gb.build_age_hist()
    else:
        fig = gb.build_ed_bar()
        
    # Update figure layout for better aesthetics
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=20, r=20, t=30, b=20),
        font=dict(family="Poppins, sans-serif", color="#E0E0E0"),
        colorway=[COLORS["primary"], COLORS["secondary"], COLORS["accent"], "#FF4081", "#29B6F6"],
    )
    
    return dcc.Graph(figure=fig, config={"displayModeBar": True, "responsive": True})


@app.callback(
    Output("effect-size-display", "children"),
    Input("effect-size-slider", "value")
)
def display_group_size(effect_size):
    """Serves information about required group size.

    Parameters
    ----------
    effect_size : float
        Size of effect that user wants to detect. Provided via 'effect-size-slider'.

    Returns
    -------
    html.Div
        Text with information about required group size. will be displayed in
        'effect-size-display'.
    """
    n_obs = sb.calculate_n_obs(effect_size)
    
    return html.Div([
        DashIconify(icon="mdi:account-group", width=20, style={"verticalAlign": "middle", "marginRight": "8px"}),
        f"To detect an effect size of ", 
        html.Span(f"{effect_size}", style={"color": COLORS["accent"], "fontWeight": "bold"}), 
        f", you would need ", 
        html.Span(f"{n_obs}", style={"color": COLORS["secondary"], "fontWeight": "bold"}), 
        " observations."
    ])


@app.callback(
    Output("experiment-days-display", "children"),
    Input("effect-size-slider", "value"),
    Input("experiment-days-slider", "value")
)
def display_cdf_pct(effect_size, days):
    """Serves probability of getting desired number of obervations.

    Parameters
    ----------
    effect_size : float
        The effect size that user wants to detect. Provided via 'effect-size-slider'.
    days : int
        Duration of the experiment. Provided via 'experiment-days-slider'.

    Returns
    -------
    html.Div
        Text with information about probabilty. Goes to 'experiment-days-display'.
    """
    # Calculate number of observations
    n_obs = sb.calculate_n_obs(effect_size)

    # Calculate percentage
    pct = round(sb.calculate_cdf_pct(n_obs, days), 2)
    
    # Set color based on probability
    if pct < 30:
        color = "#F44336"  # Red
    elif pct < 70:
        color = "#FFC107"  # Amber
    else:
        color = "#4CAF50"  # Green

    # Create text
    return html.Div([
        DashIconify(icon="mdi:percent", width=20, style={"verticalAlign": "middle", "marginRight": "8px"}),
        f"The probability of getting ", 
        html.Span(f"{n_obs}", style={"color": COLORS["secondary"], "fontWeight": "bold"}), 
        f" observations in ", 
        html.Span(f"{days} day{'s' if days > 1 else ''}", style={"color": COLORS["accent"], "fontWeight": "bold"}), 
        " is ",
        html.Span(f"{pct}%", style={"color": color, "fontWeight": "bold"}),
    ])


@app.callback(
    [
        Output("results-display", "children"),
        Output("placeholder-icon", "style"),
        Output("placeholder-text", "style"),
    ],
    Input("start-experiment-button", "n_clicks"),
    State("experiment-days-slider", "value")
)
def display_results(n_clicks, days):
    """Serves results from experiment.

    Parameters
    ----------
    n_clicks : int
        Number of times 'start-experiment-button' button has been pressed.
    days : int
        Duration of the experiment. Provided via 'experiment-days-display'.

    Returns
    -------
    html.Div
        Experiment results. Goes to 'results-display'.
    dict
        Style for placeholder icon.
    dict
        Style for placeholder text.
    """
    hide_style = {"display": "none"}
    show_style = {"textAlign": "center", "margin": "40px 0 20px 0"}
    text_style = {"color": "#888888", "textAlign": "center", "fontSize": "14px", "margin-bottom": "40px"}
    
    if n_clicks == 0:
        return html.Div(), show_style, text_style
    else:
        # Run experiment
        sb.run_experiment(days)
        # Create side-by-side bar chart
        fig = gb.build_contingency_bar()
        # Update figure layout for better aesthetics
        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=20, r=20, t=30, b=20),
            font=dict(family="Poppins, sans-serif", color="#E0E0E0"),
            colorway=[COLORS["primary"], COLORS["secondary"], COLORS["accent"], "#FF4081"],
        )
        # Run chi-square
        result = sb.run_chi_square()
        
        # Determine significance level
        p_value = result.pvalue
        if p_value < 0.01:
            sig_text = "Highly Significant"
            sig_color = "#4CAF50"  # Green
            sig_icon = "mdi:check-circle"
        elif p_value < 0.05:
            sig_text = "Significant"
            sig_color = "#8BC34A"  # Light Green
            sig_icon = "mdi:check"
        elif p_value < 0.1:
            sig_text = "Marginally Significant"
            sig_color = "#FFC107"  # Amber
            sig_icon = "mdi:alert"
        else:
            sig_text = "Not Significant"
            sig_color = "#F44336"  # Red
            sig_icon = "mdi:close-circle"
        
        # Return Results
        return html.Div(
            [
                html.H4("Observations", className="mb-3", style={"color": "#E0E0E0"}),
                dcc.Graph(
                    figure=fig,
                    config={"displayModeBar": True, "responsive": True},
                    style={"height": "300px"},
                ),
                html.Div(
                    [
                        html.H4("Statistical Analysis", className="mb-3", style={"color": "#E0E0E0"}),
                        dbc.Row(
                            [
                                dbc.Col(
                                    dbc.Card(
                                        [
                                            html.H6("Chi-Square Test", className="card-subtitle mb-2", style={"color": "#B0BEC5"}),
                                            html.P(f"χ² = {result.statistic.round(3)}", className="card-text", style={"fontSize": "1.2rem"}),
                                        ],
                                        body=True,
                                        style={"backgroundColor": "#2D2D2D", "border": "none", "borderRadius": "8px", "textAlign": "center"},
                                    ),
                                    md=4,
                                ),
                                dbc.Col(
                                    dbc.Card(
                                        [
                                            html.H6("Degrees of Freedom", className="card-subtitle mb-2", style={"color": "#B0BEC5"}),
                                            html.P(f"df = {result.df}", className="card-text", style={"fontSize": "1.2rem"}),
                                        ],
                                        body=True,
                                        style={"backgroundColor": "#2D2D2D", "border": "none", "borderRadius": "8px", "textAlign": "center"},
                                    ),
                                    md=4,
                                ),
                                dbc.Col(
                                    dbc.Card(
                                        [
                                            html.H6("P-value", className="card-subtitle mb-2", style={"color": "#B0BEC5"}),
                                            html.P(f"p = {result.pvalue.round(5)}", className="card-text", style={"fontSize": "1.2rem"}),
                                        ],
                                        body=True,
                                        style={"backgroundColor": "#2D2D2D", "border": "none", "borderRadius": "8px", "textAlign": "center"},
                                    ),
                                    md=4,
                                ),
                            ],
                            className="mb-3",
                        ),
                        dbc.Card(
                            [
                                dbc.CardBody(
                                    [
                                        html.Div(
                                            [
                                                DashIconify(icon=sig_icon, width=28, color=sig_color, style={"marginRight": "10px"}),
                                                html.Span(sig_text, style={"color": sig_color, "fontSize": "1.2rem", "fontWeight": "500"}),
                                            ],
                                            style={"display": "flex", "alignItems": "center", "justifyContent": "center"},
                                        ),
                                        html.P(
                                            f"Based on {days} day{'s' if days > 1 else ''} of data collection",
                                            className="text-center mt-2",
                                            style={"color": "#B0BEC5", "fontSize": "0.9rem"},
                                        ),
                                    ]
                                ),
                            ],
                            style={"backgroundColor": "#2D2D2D", "border": "none", "borderRadius": "8px"},
                        ),
                    ],
                    style={"marginTop": "25px"},
                ),
            ]
        ), hide_style, hide_style


# NEW FEATURE: Chart download callback
@app.callback(
    Output("download-chart", "data"),
    Input("download-chart-button", "n_clicks"),
    State("demo-plots-dropdown", "value"),
    prevent_initial_call=True,
)
def download_chart(n_clicks, graph_name):
    """Generates a downloadable file for the current chart.
    
    Parameters
    ----------
    n_clicks : int
        Number of times 'download-chart-button' has been pressed.
    graph_name : str
        The type of graph currently displayed.
        
    Returns
    -------
    dict
        Dictionary containing downloadable file information.
    """
    if n_clicks is None:
        return None
        
    if graph_name == "Nationality":
        fig = gb.build_nat_choropleth()
    elif graph_name == "Age":
        fig = gb.build_age_hist()
    else:
        fig = gb.build_ed_bar()
    
    # Update figure layout for better aesthetics
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="white",
        plot_bgcolor="white",
        font=dict(family="Poppins, sans-serif", color="black"),
        colorway=[COLORS["primary"], COLORS["secondary"], COLORS["accent"], "#FF4081", "#29B6F6"],
    )
    
    return dcc.send_data_frame(fig.to_html, f"{graph_name.lower()}_demographics.html")


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8050, debug=True)