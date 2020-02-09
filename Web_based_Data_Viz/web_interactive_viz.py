import dash
import dash_core_components as dcc
import dash_html_components as html
from portfolio_optimization import portfolio
import plotly.figure_factory as ff
from dash.dependencies import Output, Input, State
import dash_bootstrap_components as dbc


# textwrap.dedent(your_string)
def separate_positive_negative(values, names):
    negative_ = {"val": [], "name": []}
    positive_ = {"val": [], "name": []}
    for num, el in enumerate(values):
        if el < 0:
            negative_["val"].append(el)
            negative_["name"].append(names[num])
        else:
            positive_["val"].append(el)
            positive_["name"].append(names[num])
    return positive_, negative_


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server
data_path = "Data.xlsx"
data_dict, returns_df, dates = portfolio(data_path, 3)
cov_matrix = returns_df.corr().round(4)
x = [name for name in cov_matrix]
y = x

fig1 = ff.create_annotated_heatmap(z=cov_matrix.to_numpy(), x=x, y=y, showscale=True)

fig1.update_layout(
    title={
        'text': "Portfolio Correlation Matrix",
        'y': 0.9,
        'x': 0.5,
        'xanchor': 'center',
        'yanchor': 'top'}
)
# fig1.add_annotation(
#     go.layout.Annotation(align="center"))
debug = 1
# html.H1('Heading', style={'backgroundColor':'blue'}),
colors = {
    'background': '#61566f',
    'text': '#7FDBFF'
}

app.layout = html.Div([
    html.Div(
        [html.H2(
            children=['Data Visualization Assignment : Static view of our Interactive webpage'],
            style={
                'color': "white",
                'backgroundColor': colors['background']
            }), ]
    ),
    html.Div(
        dcc.Markdown('''
This Python web application can be used to optimize a portfolio of assets and display interactively the results. To get interactive plots the user should run our python scripts. But Installing python libraries can be difficult, to alleviate this problem we created a Software (binary file or .Exe) that runs on Windows [MIPOpti](https://github.com/MivieMng/Web-based-Interactive-visualization-of-Portfolio-optimization-results/releases).
We used two visualization libraries [plotly](https://plot.ly/) and [dash](https://plot.ly/dash/), and one optimization library [cvxopt](https://cvxopt.org/).
This webpage was entirely created using Dash, no html template was used.
We downloaded the returns data of 10 stocks from [the website of the University of Pennsylvania](https://wrds-www.wharton.upenn.edu/).

 ***
''', style={'backgroundColor': 'white'})),
    html.Div([html.H4(
        children='Encountered difficulties:  ',
        style={
            'color': "black"}),
        dcc.Markdown('''
* Mastering Dash and plotly to produce high quality graphs
  *  handling the properties of plot objects to render nice figures
  * Advanced concepts like "Callbacks" : callbacks enable the update of figures as the inputs change
  * Updating multiple figures by creating multiple callbacks
  * Writing html instructions from Dash
 ***
''', style={'backgroundColor': 'white'})]),
    # dcc.Markdown("**weights**", id="Mark-down", style={"white-space": "pre"}),
    html.H4(
        children='User Inputs ',
        style={
            'color': "black"}),
    html.Label("Choose the stocks you want to analyze : use at least two"),
    dcc.Checklist(
        id="check",
        options=[
            {'label': 'COG', 'value': 'COG'},
            {'label': 'BR', 'value': 'BR'},
            {'label': 'CPB', 'value': 'CPB'},
            {'label': 'CHRW', 'value': 'CHRW'},
            {'label': 'COF', 'value': 'COF'},
            {'label': 'CAH', 'value': 'CAH'},
            {'label': 'KORS', 'value': 'KORS'},
            {'label': 'CDNS', 'value': 'CDNS'},
            {'label': 'BF', 'value': 'BF'},
            {'label': 'KMX', 'value': 'KMX'},
        ],
        value=["COG", "BR", "CPB", "CHRW", "COF", "CAH", "KORS", "CDNS", "BF", "KMX"],
        labelStyle={'display': 'inline-block'}
    ),
    # dcc.Dropdown(
    #     id="drawdown",
    #     options=[
    #         {'label': 'New York City', 'value': 'NYC'},
    #         {'label': 'Montreal', 'value': 'MTL'},
    #         {'label': 'San Francisco', 'value': 'SF'}
    #     ],
    #     searchable=False
    # ),
    html.Label("Choose your risk aversion"),
    dcc.Slider(
        id='year--slider',
        min=1,
        max=10,
        step=1,
        value=3,
        marks={str(year + 1): str(year + 1) for year in range(10)},

    ),
    dcc.Markdown('''
 ***
''', style={'backgroundColor': 'white'}),
    html.Div([html.H4(
        children='Historical returns of a basket of assets',
        style={
            'color': "black"}),
        dcc.Graph(
            id='life-exp-vs-gdp',
        ),
        html.Label(),
        dcc.Markdown('''
            
            **Interpretation** : The monthly returns of the assets show their performances. Assets with high variations can yield higher returns, but they are more volatile and therefore riskier.
            
            ***
        ''', style={'backgroundColor': 'white'})]),
    html.Div([html.H4(
        children='Linear relationships between assets returns',
        style={
            'color': "black"}),
        dcc.Graph(
            figure=fig1,
        ),
        dcc.Markdown('''
                **Interpretation** : The correlation matrix highlights the correlations (linear relationships) between the returns of all pair of assets in the portfolio. The higher the correlation the more the assets change (increase or decrease) in the same way.
                A good portfolio should contain less correlated assets (close to zero or less than one). The correlation matrix is used as the main input in the optimization of a portfolio.

                ***
            ''', style={'backgroundColor': 'white'})
    ]),
    html.Div([
        html.H4(
        children='Solution of the optimization of a portfolio',
        style={
            'color': "black"}),
        dcc.Graph(
            id='Eff',
        ),
        dcc.Markdown('''
                **Interpretation** : The efficient frontier (blue discrete points on the figure) is the solution of the optimization of a portfolio. For each risk level the higher return is a point that belongs to the efficient frontier. The capital allocation line  can be used to determine how to 
                share a bugdet between risky and a risk-free asset.
                ***
            ''', style={'backgroundColor': 'white'})]
    ),
    html.Div([
        html.H4(
        children='Budget Allocation between risky and risk-free assets',
        style={
            'color': "black"}),
        dcc.Graph(
            id='bar',
        ),
        dcc.Markdown('''
                **Interpretation** : The allocation of a bugdet of 10k euros between risky and one risk free asset. Assets with good risk-return (i.e. BR, CDN, BF, risk-free) trade-offs have positive allocation. 
                
            ''', style={'backgroundColor': 'white'})]
    ),
    # dcc.Markdown("**weights**", id="Mark-down")

])


@app.callback(
    [Output(component_id='life-exp-vs-gdp', component_property='figure'),
     Output(component_id='Eff', component_property='figure'),
     Output(component_id='bar', component_property='figure')],
    [Input(component_id='check', component_property='value'),
     Input(component_id='year--slider', component_property='value')]
)
def update_figure(stocks_names, risk_aversion):
    if len(stocks_names) < 2:
        stocks_names = ["BF", "BR"]

    ####
    data_dict, returns_df, dates = portfolio(data_path, risk_aversion, stocks_names)
    positive, negative = separate_positive_negative(data_dict["risky_alloc"], data_dict["symbol"])

    data_eff = [
        dict(
            x=data_dict['EF_10_with_short'][0],
            y=data_dict['EF_10_with_short'][1],
            text="EF with short",
            mode='markers+line',
            opacity=1,
            marker={
                'size': 13,
                'line': {'width': 0.5, 'color': 'white'}
            },
            name="Efficient Frontier with short",
            showlegend=True
        ),
        dict(
            x=data_dict['CAL_10_stocks_with_short'][0],
            y=data_dict['CAL_10_stocks_with_short'][1],
            text="CAL with short",
            mode='lines',
            opacity=1,
            marker={
                'size': 11,
                'line': {'width': 0.5, 'color': 'white'}
            },
            name="Capital Allocation Line with short"
        )
    ]
    data_eff_no_short = [
        dict(
            x=data_dict['EF_10_without_short'][0],
            y=data_dict['EF_10_without_short'][1],
            text="EF with short",
            mode='markers+line',
            opacity=1,
            marker={
                'size': 13,
                'line': {'width': 0.5, 'color': 'white'}
            },
            name="Efficient Frontier no short",
            showlegend=True
        ),
        dict(
            x=data_dict['CAL_10_stocks_without_short'][0],
            y=data_dict['CAL_10_stocks_without_short'][1],
            text="CAL no short",
            mode='lines',
            opacity=1,
            marker={
                'size': 11,
                'line': {'width': 0.5, 'color': 'white'}
            },
            name="Capital Allocation Line no short"
        )
    ]

    stocks = [
        dict(
            x=[data_dict["risk"][i]],
            y=[data_dict["mean_return"][i]],
            text="",
            mode='markers',
            opacity=0.7,
            marker={
                'size': 9,
                'line': {'width': 0.5, 'color': 'white'}
            },
            name=stocks_names[i]
        ) for i in range(len(data_dict["mean_return"]))
    ]

    # data_eff_all = stocks + data_eff+data_eff_no_short
    data_eff_all = stocks + data_eff

    return {
               'data': [
                   dict(
                       x=dates,
                       y=returns_df[i],
                       text="",
                       mode='markers+lines',
                       opacity=0.7,
                       marker={
                           'size': 8,
                           'line': {'width': 0.5, 'color': 'white'}
                       },
                       name=i
                   ) for i in returns_df

               ],
               'layout': dict(
                   xaxis={'title': 'date', 'tickformat': '%Y-%m-%d'},
                   yaxis={'title': "return", "size": 30},
                   # margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
                   legend={'x': 10, 'y': 1},
                   hovermode='closest',
                   title="Portfolio Monthly returns",
                   font=dict(
                       # family="Courier New, monospace",
                       size=18,
                       # color="#7f7f7f"
                   )
               )
           }, \
           {
               'data': data_eff_all,
               'layout': dict(
                   xaxis={'type': 'linear', 'title': 'risk'},
                   yaxis={'title': 'return'},
                   # margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
                   legend={'x': 10, 'y': 1},
                   hovermode='closest',
                   title="Efficient Frontier and Capital Allocation Line"
               )
           }, \
           {'data':
               [dict(
                   x=positive["name"],
                   y=positive["val"],
                   text="",
                   mode='markers+lines',
                   opacity=0.7,
                   marker={
                       'size': 8,
                       'line': {'width': 0.5, 'color': 'white'}
                   },
                   type="bar",
                   name="positive allocation"
               ),
                   dict(
                       x=negative["name"],
                       y=negative["val"],
                       text="negative positive (or short sell)",
                       mode='markers+lines',
                       opacity=0.7,
                       marker={
                           'size': 8,
                           'line': {'width': 0.5, 'color': 'white'}
                       },
                       type="bar",
                       name="negative allocation (or short sell)"
                   )
               ],

               'layout': dict(
                   xaxis={'title': 'stock'},
                   yaxis={'title': 'Capital Investment (euros) '},
                   # margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
                   # legend={'x': 10, 'y': 1},
                   hovermode='closest',
                   title="Allocation of 10k€ between risky assets and one risk-free asset"
               )
           }


if __name__ == '__main__':
    app.run_server(debug=False)
