# from quixstreaming import *
# Run this app with `python app.py` and
# visit http://127.0.0.1:80/ in your web browser.

import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import pandas as pd
import requests
import io
import datetime
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import signalrcore
from signalrcore.hub_connection_builder import HubConnectionBuilder
import logging
from signalrcore.hub_connection_builder import HubConnectionBuilder
from dash.dependencies import Input, Output, State
import plotly

streamId = '78e7dd30-02e2-442a-9b3e-eeb4e5b8eeb0'
token = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6Ik1qVTBRVE01TmtJNVJqSTNOVEpFUlVSRFF6WXdRVFF4TjBSRk56SkNNekpFUWpBNFFqazBSUSJ9.eyJodHRwczovL3F1aXguYWkvcm9sZXMiOiJhZG1pbiIsImh0dHBzOi8vcXVpeC5haS9vcmdfaWQiOiJpbXBlcmlhbCIsImlzcyI6Imh0dHBzOi8vbG9naWNhbC1wbGF0Zm9ybS5ldS5hdXRoMC5jb20vIiwic3ViIjoiYXV0aDB8NDI2NzVkODAtYWFjMi00YTBjLWEzMGMtYWZhYzZhODJmOGJiIiwiYXVkIjpbInF1aXgiLCJodHRwczovL2xvZ2ljYWwtcGxhdGZvcm0uZXUuYXV0aDAuY29tL3VzZXJpbmZvIl0sImlhdCI6MTYyMTI3MTI3MSwiZXhwIjoxNjIzODYzMjcxLCJhenAiOiIwem1XZkpka2l1R1BpSld5cFNDQThyS2FWdmZQREtMSSIsInNjb3BlIjoib3BlbmlkIHByb2ZpbGUgZW1haWwiLCJwZXJtaXNzaW9ucyI6W119.WzKojwdPVgILqh9JIFhKJDj3v6hvgA8JwdPbozfDU1FbzR_YI7C0InIK3HEYvNk-BpNc6F90NX3zI5rKkkAWvsnPJUUP65kWhbVsgrivzv8zwFQ5PpowmgN8ckKFdNHpAfwrcup61hUWBtQnhU4zqrb3vs7VRboTYtTbvU_FGOpXGJVdzdInh84lOulB8oug_UN4YzuuxsI0jxcJjBquOw50QeqrfFgr_E1465OFa6s7s9w4au4vuTZU2FeZiwT8ek-wpdtUJZpA9uwu3aucizOg4m9oBtfAmYRgGfHE69MFxQj_7V4Ud99uecEcmKHsDgz3AiHfgR2AV8mhuU4XwQ"
topic_name = "imperial-opc-ua"
server_url = "wss://reader-imperial-factory.platform.quix.ai/hub"

hub_connection = HubConnectionBuilder()\
    .with_url(server_url, options={"access_token_factory": lambda : token,  })\
    .build()

hub_connection.on_open(print("Connection opened."))
hub_connection.on_close(lambda: on_close_handler())

def subscribeToStream(streamId):
    if not streamId:
        print("No streamId specified!")
    else:
        print("Subscribing to stream: {}".format(streamId))
        hub_connection.send("SubscribeToParameter", [topic_name, streamId, "actProgNetTime"])
        hub_connection.send("SubscribeToParameter", [topic_name, streamId, "actParts"])
        hub_connection.send("SubscribeToParameter", [topic_name, streamId, "progStatus"])
        print("Subscribed to stream: {}".format(streamId))

def on_close_handler():
    print("Connection closed.")
    global streamId
    if streamId:
        print("Reconnecting...")
        hub_connection.start()
        print("Connection restarted.")
        subscribeToStream(streamId)


actProgNetTime = []
actParts = []
progStatus = []
timestamps = []
def on_data(payload):
    for data in payload:
        for row in range(len(data['numericValues']['actProgNetTime'])):
            timestamps.append(str(datetime.datetime.fromtimestamp(data['timestamps'][row] / 1000000000)))
            actProgNetTime.append(data['numericValues']['actProgNetTime'][row])
            actParts.append(data['numericValues']['actParts'][row])
            progStatus.append(data['numericValues']['progStatus'][row])

hub_connection.on("ParameterDataReceived", on_data)
hub_connection.start()

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# We add secondary y axe to accommodate second parameter.
fig = make_subplots(specs=[[{"secondary_y": True}]])

# Add series into plot for actProgNetTime.
fig.add_trace(
    go.Scatter(x=timestamps, y=actProgNetTime, name="actProgNetTime", ),
    secondary_y=False,
)




fig1 = make_subplots(specs=[[{"secondary_y": True}]])

# Add series into plot for actParts
fig1.add_trace(
    go.Scatter(x=timestamps, y=actParts, name="actParts", ),
    secondary_y=False,
)





fig2 = make_subplots(specs=[[{"secondary_y": True}]])

# Add series into plot for actProgNetTime.
fig2.add_trace(
    go.Scatter(x=timestamps, y=progStatus, name="progStatus", ),
    secondary_y=False,
)

@app.callback(Output('example-graph', 'extendData'), [Input('interval', 'n_intervals')])
def update_data(n_intervals):
    global actProgNetTime
    global timestamps

    res = dict(x=[timestamps], y=[actProgNetTime])

    actProgNetTime = []
    timestamps = []
    return res

@app.callback(Output('example-graph1', 'extendData'), [Input('interval', 'n_intervals')])
def update_data(n_intervals):
    global actParts
    global timestamps

    res = dict(x=[timestamps], y=[actParts])

    actParts = []
    timestamps = []
    return res

@app.callback(Output('example-graph2', 'extendData'), [Input('interval', 'n_intervals')])
def update_data(n_intervals):
    global progStatus
    global timestamps

    res = dict(x=[timestamps], y=[progStatus])

    progStatus = []
    timestamps = []
    return res


app.layout = html.Div(children=[
    html.H1(children='Hello from Quix'),
    dcc.Input(
            id="input",
            type="text",
            value=streamId
    ),
    html.Div(children='''
        actProgNetTime
    '''),

    dcc.Graph(
        animate = True,
        id='example-graph',
        figure=fig
    ),
    html.Div(children='''
            actParts
    '''),
    dcc.Graph(
        animate = True,
        id='example-graph1',
        figure=fig1
    ),
    html.Div(children='''
            progStatus
    '''),
    dcc.Graph(
        animate = True,
        id='example-graph2',
        figure=fig2
    ),
    dcc.Interval(id="interval", interval=1000),

    html.Div(id="out-all-types")
])

@app.callback(
    Output("out-all-types", "children"),
    [Input("input", "value")]
)
def cb_render(value):
    global streamId
    streamId = value
    subscribeToStream(streamId)


if __name__ == '__main__':
    app.run_server(debug=True, host="0.0.0.0", port=80)
