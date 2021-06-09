import requests
import operator
import io
import datetime
from datetime import date, timedelta
from datetime import datetime
import dash
import numpy as np
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import traceback
import requests
import pandas as pd
import io


'''
TO DO LIST: Fix Load All Issue  original where it doesn't load all correctly at the start when clicking button straight away
'''
def greater_than(a, b):
    #if any in b are greater than a
    shorter_len = 0
    a_len = len(a)
    b_len = len(b)
    if b_len >= a_len:
        shorter_len = a_len
    else:
        shorter_len = b_len

    for i in range(shorter_len):
        for j in range(shorter_len):
            if b[i]> a[j]:
                return True
    return False


def load_data():
    global startTime
    global parameterChoice
    global endDate
    global endIncrement
    global streamID
    endIncrement = endIncrement + 100000000000
    endTime = startTime + endIncrement
    if loadall == True :
        endTime = endDate
    if endTime >= endDate:
        endTime = endDate
    url = "https://telemetry-query-imperial-factory.platform.quix.ai/parameters/data"
    token = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6Ik1qVTBRVE01TmtJNVJqSTNOVEpFUlVSRFF6WXdRVFF4TjBSRk56SkNNekpFUWpBNFFqazBSUSJ9.eyJodHRwczovL3F1aXguYWkvcm9sZXMiOiJhZG1pbiIsImh0dHBzOi8vcXVpeC5haS9vcmdfaWQiOiJpbXBlcmlhbCIsImlzcyI6Imh0dHBzOi8vbG9naWNhbC1wbGF0Zm9ybS5ldS5hdXRoMC5jb20vIiwic3ViIjoiYXV0aDB8NDI2NzVkODAtYWFjMi00YTBjLWEzMGMtYWZhYzZhODJmOGJiIiwiYXVkIjpbInF1aXgiLCJodHRwczovL2xvZ2ljYWwtcGxhdGZvcm0uZXUuYXV0aDAuY29tL3VzZXJpbmZvIl0sImlhdCI6MTYyMTI3MTI3MSwiZXhwIjoxNjIzODYzMjcxLCJhenAiOiIwem1XZkpka2l1R1BpSld5cFNDQThyS2FWdmZQREtMSSIsInNjb3BlIjoib3BlbmlkIHByb2ZpbGUgZW1haWwiLCJwZXJtaXNzaW9ucyI6W119.WzKojwdPVgILqh9JIFhKJDj3v6hvgA8JwdPbozfDU1FbzR_YI7C0InIK3HEYvNk-BpNc6F90NX3zI5rKkkAWvsnPJUUP65kWhbVsgrivzv8zwFQ5PpowmgN8ckKFdNHpAfwrcup61hUWBtQnhU4zqrb3vs7VRboTYtTbvU_FGOpXGJVdzdInh84lOulB8oug_UN4YzuuxsI0jxcJjBquOw50QeqrfFgr_E1465OFa6s7s9w4au4vuTZU2FeZiwT8ek-wpdtUJZpA9uwu3aucizOg4m9oBtfAmYRgGfHE69MFxQj_7V4Ud99uecEcmKHsDgz3AiHfgR2AV8mhuU4XwQ"
    head = {'Authorization': 'Bearer {}'.format(token), 'Accept': "application/csv"}
    payload = {
        'groupByTime': {
            'timeBucketDuration': 60000000000,
            'interpolationType': 'None'
        },
        'from': startTime,
        'to': endTime,
        'numericParameters': [
            {
                'parameterName': 'progStatus',
                'aggregationType': 'First'
            },
            {
                'parameterName': 'actProgNetTime',
                'aggregationType': 'First'
            },
            {
                'parameterName': 'actParts',
                'aggregationType': 'First'
            }
        ],
        'stringParameters': [],
        'streamIds': [
            streamID
        ],
        'groupBy': []
    }


    response = requests.post(url, headers=head, json=payload)

    df = pd.read_csv(io.StringIO(response.content.decode('utf-8')))

    #with pd.option_context('display.max_rows', None, 'display.max_columns', None):
    if df.size > 0:
            # We convert nanoseconds epoch to datetime for better readability.
        df["Timestamp"] = df["Timestamp"].apply(lambda x: str(datetime.fromtimestamp(x / 1000000000)))
    return df

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
global oldActParts
global oldProgStatus
global oldProgNetTime
global startTime
global endDate
global loadall
global streamID
global oldnclicks
global parameterChoice
global startTimeIncrement
global endTimeIncrement
global endDateMinTime
global startDateMinTime
startTimeIncrement = 0
endTimeIncrement = 8*3600*1000000000
parameterChoice = "actProgNetTime"
oldnclicks = 0
streamID = '78e7dd30-02e2-442a-9b3e-eeb4e5b8eeb0'
loadall = False
endDate = datetime.combine(date.today(), datetime.min.time())
endDate = int(endDate.timestamp()*1000000000)
endDateMinTime = endDate
endDate += endTimeIncrement
startTime = datetime.combine(date.today() - timedelta(days=1), datetime.min.time())
startTime = int(startTime.timestamp()*1000000000)
startDateMinTime = startTime
global endIncrement
global x
x = []
global y
y = []
oldActParts = []

endIncrement = 100000000000
app.layout = html.Div(children=[
    html.H1(children='CloudNC Live Dashboard'),
    html.Div(['Start Date:',
    dcc.DatePickerSingle(
        id='my-date-picker-single-start',
        min_date_allowed=date(2021, 5, 5),
        max_date_allowed=date.today(),
        initial_visible_month= date.today() - timedelta(days=1),
        date=date.today() - timedelta(days=1)
    ),
    'End Date: ',
    dcc.DatePickerSingle(
        id='my-date-picker-single-end',
        min_date_allowed=date(2021, 5, 5),
        max_date_allowed=date.today(),
        initial_visible_month=date.today(),
        date=date.today()
    ),
    html.Button('Load All', id='submit-val', n_clicks=0)]),
    dcc.Dropdown(
        id='demo-dropdown',
        options=[
            {'label': 'dmu60-70', 'value': '78e7dd30-02e2-442a-9b3e-eeb4e5b8eeb0'},
            {'label': 'dmu95-40', 'value': 'd2855d44-3246-4b00-8ce2-9c1489d3cd6a'},
            {'label': 'dmu50-50', 'value': '8e394499-d07f-4e39-b0bf-c06a040b49e9'},
            {'label': 'dmu60-60', 'value': '5650ce03-89c1-4fdd-a85d-c14aa0186895'},
            {'label': 'dmu60-80', 'value': 'cc967389-d614-4410-aab2-44751964f8f5'}
        ],
        value='78e7dd30-02e2-442a-9b3e-eeb4e5b8eeb0'
    ),
    dcc.Dropdown(
        id='paramdropdown',
        options=[
            {'label': 'Net Program Time', 'value': 'actProgNetTime'},
            {'label': 'Number of Parts', 'value': 'actParts'},
            {'label': 'Program Status', 'value': 'progStatus'}
        ],
        value='actProgNetTime'
    ),
    dcc.RangeSlider(
        id='my-range-slider',
        min=0,
        max=24,
        step=1,
        value=[0, 8],
        marks = {
            0: {'label': '0:00'},
            1: {'label': '1:00'},
            2: {'label': '2:00'},
            3: {'label': '3:00'},
            4: {'label': '4:00'},
            5: {'label': '5:00'},
            6: {'label': '6:00'},
            7: {'label': '7:00'},
            8: {'label': '8:00'},
            9: {'label': '9:00'},
            10: {'label': '10:00'},
            11: {'label': '11:00'},
            12: {'label': '12:00'},
            13: {'label': '13:00'},
            14: {'label': '14:00'},
            15: {'label': '15:00'},
            16: {'label': '16:00'},
            17: {'label': '17:00'},
            18: {'label': '18:00'},
            19: {'label': '19:00'},
            20: {'label': '20:00'},
            21: {'label': '21:00'},
            22: {'label': '22:00'},
            23: {'label': '23:00'},
            24: {'label': '24:00'}
        }
    ),
    html.Div(id='output-container-date-picker-single-start'),
    html.Div(id='output-container-date-picker-single-end'),
    html.Div(id='dd-output-container'),
    html.Div(id='parameterChoice'),
    html.Div(id='output-container-range-slider'),
    dcc.Graph(
        id='graph',
    ),
    html.Div(id='hidden-div', style={'display':'none'}),
    dcc.Interval(
        id='interval_component',
        interval=5000,
        n_intervals=0,

    )
])

######################PARAMETER CHOICE CALLBACK###################################
@app.callback(
    dash.dependencies.Output('parameterChoice', 'children'),
    [dash.dependencies.Input('paramdropdown', 'value')])
def update_output(value):
    global parameterChoice
    global endIncrement
    global x
    global y
    global loadall
    if parameterChoice != value:
        loadall = False
        x.clear()
        y.clear()
        endIncrement = 100000000000
        parameterChoice = value
        return 'You have selected "{}"'.format(value)
    else:
        return 'You have selected "{}"'.format(parameterChoice)
############################### TIME CALLBACK######################################
@app.callback(
    dash.dependencies.Output('output-container-range-slider', 'children'),
    [dash.dependencies.Input('my-range-slider', 'value')])
def update_output(value):
    global startTimeIncrement
    global endTimeIncrement
    global x
    global y
    global loadall
    global startTime
    global endDate
    global startDateMinTime
    global endDateMinTime
    global endIncrement
    currStartTimeIncrement = value[0] * 3600 * 1000000000
    currEndTimeIncrement = value[1] * 3600 * 1000000000
    if(startTimeIncrement != currStartTimeIncrement or currEndTimeIncrement != endTimeIncrement):
        loadall = False
        x.clear()
        y.clear()
        endIncrement = 100000000000
        endTimeIncrement = currEndTimeIncrement
        startTimeIncrement = currStartTimeIncrement
        startTime = startDateMinTime + currStartTimeIncrement
        endDate = currEndTimeIncrement + endDateMinTime
    return "You have selected: Time Range: "+ str(value[0]) + ":00 to " + str(value[1])+ ":00"
############################### MACHINE CHOICE CALLBACK #########################
@app.callback(
    dash.dependencies.Output('dd-output-container', 'children'),
    [dash.dependencies.Input('demo-dropdown', 'value')])
def update_output(value):
    global streamID
    global endIncrement
    global x
    global y
    global loadall
    if streamID != value:
        loadall = False
        x.clear()
        y.clear()
        endIncrement = 100000000000
        streamID = value
        return 'You have selected stream "{}"'.format(value)
    else:
        return 'You have selected stream "{}"'.format(streamID)

####################### ALL DATA LOAD IN CALLBACK#############################
@app.callback(
    dash.dependencies.Output('hidden-div','children'),
    [dash.dependencies.Input('submit-val', 'n_clicks')])
def update_output(n_clicks):
    global loadall
    global x
    global y
    global oldnclicks
    global endIncrement
    x.clear()
    y.clear()
    if not(n_clicks is  None) and n_clicks != oldnclicks:
        loadall = True
        oldnclicks = n_clicks
        endIncrement = 100000000000

########################### GRAPH PLOTTING CALLBACK############################################################
@app.callback(Output('graph', 'figure'), [Input('interval_component', 'n_intervals')])
def update_data(n_intervals):
    try:
        global parameterChoice
        global oldActParts
        global oldProgStatus
        global oldProgNetTime
        global x
        global y
        data = load_data()

        loadString = "first("+ parameterChoice+ ")"
        fig1 = go.Figure()
        fig1.add_trace(go.Scatter(x=data["Timestamp"].to_numpy(), y=data[loadString].to_numpy(), name = parameterChoice))
        oldActParts = data["first(actParts)"].to_numpy()
        oldProgStatus = data["first(progStatus)"].to_numpy()
        oldProgNetTime = data["first(actProgNetTime)"].to_numpy()
        currActProgNetTime = data["first(actProgNetTime)"].values
        currActProgNetTime = currActProgNetTime.tolist()
        currActParts = data["first(actParts)"].values
        currActParts = currActParts.tolist()
        currProgStatus = data["first(progStatus)"].values
        currProgStatus = currProgStatus.tolist()

        if bool(not set(currActParts).isdisjoint(oldActParts)):
            if greater_than(currActProgNetTime,oldProgNetTime):
                if 0 in currActProgNetTime:
                    x.append(data["Timestamp"].to_numpy())
                    y.append(data["first(actParts)"].to_numpy())

        for i in range(len(x)):
            fig1.update_layout(
            annotations=[
            go.layout.Annotation(
                text="Bad Part ",
                showarrow=False,
                x=x[i],
                y=y[i])
                ]
            )



        return fig1

    except Exception:
        print(traceback.format_exc())
############################# END DATE PICKER CALLBACK#####################################

@app.callback(
    Output('output-container-date-picker-single-end', 'children'),
    Input('my-date-picker-single-end', 'date'))
def update_output(date_value):
    global startTime
    global endDate
    global loadall
    global endDateMinTime
    global endTimeIncrement
    if date_value is not None:
        end_date_object = date.fromisoformat(date_value)
        dt = datetime.combine(end_date_object, datetime.min.time())
        loadall = False
        endDate = int(dt.timestamp()*1000000000)
        endDateMinTime = endDate
        if endDate == startTime:
            endDate += endTimeIncrement
        end_date_string = end_date_object.strftime('%B %d, %Y')
        string_prefix = 'End Date: ' + end_date_string
        return string_prefix


############################ START DATE PICKER CALLBACK############################
@app.callback(
    Output('output-container-date-picker-single-start', 'children'),
    Input('my-date-picker-single-start', 'date'))
def update_output(date_value):
    global startTime
    global loadall
    global startDateMinTime
    if date_value is not None:
        start_date_object = date.fromisoformat(date_value)
        dt = datetime.combine(start_date_object, datetime.min.time())
        startTime = int(dt.timestamp()*1000000000)
        startDateMinTime = startTime
        loadall = False
        start_date_string = start_date_object.strftime('%B %d, %Y')
        string_prefix ='Start Date: ' + start_date_string
        return string_prefix


if __name__ == '__main__':
    app.run_server(debug=True, host="0.0.0.0", port=80)
