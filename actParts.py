import requests
import io
import datetime
import dash  # (version 1.12.0)
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.graph_objects as go
import traceback

###break###
def load_data():
    url = "https://telemetry-query-imperial-factory.platform.quix.ai/parameters/data"
    token = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6Ik1qVTBRVE01TmtJNVJqSTNOVEpFUlVSRFF6WXdRVFF4TjBSRk56SkNNekpFUWpBNFFqazBSUSJ9.eyJodHRwczovL3F1aXguYWkvcm9sZXMiOiIiLCJodHRwczovL3F1aXguYWkvb3JnX2lkIjoiaW1wZXJpYWwiLCJpc3MiOiJodHRwczovL2xvZ2ljYWwtcGxhdGZvcm0uZXUuYXV0aDAuY29tLyIsInN1YiI6ImF1dGgwfDJkYjcwYjIzLTc5YTktNGI2NS1hYmQ4LTFiYzJlYWNjNzAwMiIsImF1ZCI6WyJxdWl4IiwiaHR0cHM6Ly9sb2dpY2FsLXBsYXRmb3JtLmV1LmF1dGgwLmNvbS91c2VyaW5mbyJdLCJpYXQiOjE2MjA5MDg5NTEsImV4cCI6MTYyMzUwMDk1MSwiYXpwIjoiMHptV2ZKZGtpdUdQaUpXeXBTQ0E4ckthVnZmUERLTEkiLCJzY29wZSI6Im9wZW5pZCBwcm9maWxlIGVtYWlsIiwicGVybWlzc2lvbnMiOltdfQ.OlhgnRi5dy5BLkkLtAkor69zSRa36F08HwmjBPcz41LPeEGj4jbc-kom74yOqlr84TOTjUh_oOrmkOrvDDqExSGOtC175wPoPUiL85VJckhYpV5ZNXiGoQzWqAaOSRNr4FdzUWjRk1EY9cVXt3ZNV_C5FpkfGGm-3_EhTV-bBZupLTzs15ZR1JKqmO932N8rsD_VbaYvwTTn3FdY1cZmK-9i8MSqq0nhEiK_NoxjpbH4Vj5Mhju8_mEtCClZ0-DYiLU8QSBcs5oJKPcKi_auXFG4IhoLtgSKrhJvL139GZOI98T5RfNKxaDxdVhkFtK8GdlNyRuIr9uj6xh75GqkcQ"
    head = {'Authorization': 'Bearer {}'.format(token), 'Accept': "application/csv"}
    payload = {
        'from': 1620834013410371300,
        'to': 1620935102264000000,
        'numericParameters': [
            {
                'parameterName': 'actParts',
                'aggregationType': 'None'
            }
        ],
        'stringParameters': [],
        'streamIds': [
            '78e7dd30-02e2-442a-9b3e-eeb4e5b8eeb0'
        ],
        'groupBy': []
    }

    response = requests.post(url, headers=head, json=payload)

    df = pd.read_csv(io.StringIO(response.content.decode('utf-8')))

    # with pd.option_context('display.max_rows', None, 'display.max_columns', None):
    #     print(df)
    if df.size > 0:
        # We convert nanoseconds epoch to datetime for better readability.
        df["Timestamp"] = df["Timestamp"].apply(lambda x: str(datetime.datetime.fromtimestamp(x / 1000000000)))
    return df

###break###
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div(children=[
    html.H1(children='Dashboard'), #title
    html.Div(children='''
        actParts
    '''), #subtitle
    dcc.Graph(
        id='graph',

    ),
    dcc.Interval(
        id='interval_component',
        interval=5000,
        n_intervals=0,

    )
])


###break###
@app.callback(Output('graph', 'figure'), [Input('interval_component', 'n_intervals')])
def update_data(n_intervals):
    try:
        data = load_data()

        scatter = go.Scatter(x=data["Timestamp"].to_numpy(), y=data["actParts"].to_numpy()) #param name

        fig = go.Figure(
            data=[scatter]
        )
        return fig

    except Exception:
        print(traceback.format_exc())


###break###
if __name__ == '__main__':
    app.run_server(debug=True, host="0.0.0.0", port=80)
