
############################# Importing required Libraries ##########################################
import pandas as pd
pd.set_option('max_rows',20)
import plotly.express as px
import plotly.io as pio
import plotly.graph_objects as go
pio.renderers.default = "browser"


import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc

from datetime import date
from pmdarima import auto_arima

import statsmodels.api as sm
from statsmodels.tsa.arima_model import ARIMA 

import pickle
import os

########################################  Load ARIMA  Model   ######################################

with open('NiftyDashModel.pkl', 'rb') as fileReadStream:
        model=pickle.load(fileReadStream)
        fileReadStream.close()
    

########################################  Load Data   ######################################

df2 = pd.read_csv("dashboardData.csv" , index_col="Date")
df2.index = pd.to_datetime(df2.index)



########################################  Function to return plots   ######################################

def getgraph(inputdate = '2029-1-1'):

    tempdf = df2[df2.index <= pd.to_datetime(inputdate)]
    corrprice = tempdf['NIFTY 50'][-1]

    predictiondf = pd.DataFrame(model.predict(n_periods = len(tempdf), 
                                exogenous = tempdf[['RELIANCE' , 'INFY' ,'HDFC' , 'HDFCBANK']]) ,
                                index =tempdf.index)

    predictiondf.columns = ["Predicted"]
    predictionprice = predictiondf['Predicted'][-1]

    fig1 = px.line(tempdf, y='NIFTY 50', x=tempdf.index,title='Nifty-50 Index Price')

    fig2 = go.Figure(data=go.Scatter(
            x=[inputdate],
            y=[corrprice],
            name='Actual Price',
            mode='markers',
            marker=dict(size=[15],
                        color="blue")
    ))

    fig3 = px.line(predictiondf, y='Predicted', x=tempdf.index)
    fig3.update_traces(patch={"line":{"color":"red"}})

    fig4 = go.Figure(data=go.Scatter(
            x=[inputdate],
            y=[predictionprice],
            name='Predicted Price',
            mode='markers',
            marker=dict(size=[15],
                        color="red")
    ))



    fig = go.Figure(data=fig1.data + fig2.data + fig3.data + fig4.data)
 
    fig.update_layout(title_x=0.5,xaxis_title="Date",yaxis_title='Price' )    

    fig.update_xaxes(
            showspikes = True,
            rangeselector=dict(
                buttons=list([
                    dict(count=1, label="1m", step="month", stepmode="backward"),
                    dict(count=6, label="6m", step="month", stepmode="backward"),
                    dict(count=1, label="YTD", step="year", stepmode="todate"),
                    dict(count=1, label="1y", step="year", stepmode="backward"),
                    dict(step="all")
                ])
            )
    )
    fig.update_yaxes(showspikes = True)
    return fig

########################################  Creating Dash App   ######################################

app = dash.Dash()
app.title = "NIFTY 50"
app.layout = html.Div(children=[
    html.H1('NIFTY 50 Index Dashboard',style={'textAlign': 'center' , 'background-color' : 'black' , 'color' : 'lightgreen'}),
    html.H3('Please enter the date',style={'textAlign': 'center'}),
    html.Div(dcc.DatePickerSingle(
        id='input',
        min_date_allowed=date(2018, 5, 1),
        max_date_allowed=date(2021, 6, 15),
        initial_visible_month=date(2020, 1, 1),
        date=date(2020, 1, 1),
        reopen_calendar_on_clear=False,
        is_RTL=False,  # True or False for direction of calendar
        clearable=True,
        display_format='DD/MM/YYYY',

     ),style={'textAlign': 'center' ,'justify-content': 'center', 'align-items': 'center'}),
    dcc.Graph(id="output-graph" , style={'width': '80%' ,'margin' : '1% auto'})
])

# Second the interaction with the user
@app.callback(
    Output(component_id="output-graph", component_property='figure'),
    [Input(component_id="input", component_property="date")]
)
def update_value(input_data):

    fig = getgraph(input_data)
    return fig

########################################  Start App   ######################################

if __name__ == "__main__":
    app.run_server()