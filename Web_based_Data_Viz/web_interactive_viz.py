import dash
import dash_core_components as dcc
import dash_html_components as html
from portfolio_optimization import portfolio
import plotly.figure_factory as ff
from dash.dependencies import Output, Input, State


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
data_path = "Data.xlsx"
data_dict, returns_df, dates = portfolio(data_path, 3)
cov_matrix = returns_df.cov().round(4)
x = [name for name in cov_matrix]
y = x

fig1 = ff.create_annotated_heatmap(z=cov_matrix.to_numpy(), x=x, y=y, showscale=True)

fig1.update_layout(
    title={
        'text': "Portfolio Covariance Matrix",
        'y': 0.9,
        'x': 0.5,
        'xanchor': 'center',
        'yanchor': 'top'}
)
# fig1.add_annotation(
#     go.layout.Annotation(align="center"))
debug = 1
app.layout = html.Div([
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
    dcc.Graph(
        id='life-exp-vs-gdp',

    ),
    dcc.Graph(
        figure=fig1,
    ),
    dcc.Graph(
        id='Eff',
    ),
    dcc.Graph(
        id='bar',
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
            text="EF without short",
            mode='markers',
            opacity=1,
            marker={
                'size': 13,
                'line': {'width': 0.5, 'color': 'white'}
            },
            name="Efficient Frontier without short",
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
            name="Capital Allocation Line"
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
                   yaxis={'title': "returns"},
                   # margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
                   legend={'x': 10, 'y': 1},
                   hovermode='closest',
                   title="Portfolio Monthly returns"
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
                   name = "positive allocation"
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
                   title="Allocation of 10k€ between your stocks"
               )
           }


if __name__ == '__main__':
    app.run_server(debug=False)
