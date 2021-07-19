import plotly.graph_objects as go
from plotly.offline import plot
from plotly import io
import yfinance as yf
import plotly
import base64
import jinja2
import json


from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from flask import render_template,request, send_file

def get_daily_graph(strategy_data):
    qty_map = {}
    for s in strategy_data['strategy']:
        qty_map[s['data']['0']['symbol']] = s['data']['0']['qty']
        qty_map[s['data']['1']['symbol']] = s['data']['1']['qty']
        qty_map[s['data']['2']['symbol']] = s['data']['2']['qty']
    data = yf.download(" ".join(list(qty_map.keys())), period='5d')['Close']
    data = data.reset_index()
    daily_value_list = list()
    date_list = list()
    for i, row in data.iterrows():  
        daily_value = 0
        for symbol in qty_map:
            daily_value = daily_value + row[symbol] * qty_map[symbol]
        daily_value_list.append(round(daily_value, 2))
        date_list.append(row['Date'].strftime("%m-%d-%Y"))
    fig = go.Figure()
    fig.add_trace(go.Bar(x=date_list, y=daily_value_list, text=daily_value_list, name='Portfolio History', textposition='auto'))
    fig['layout']['yaxis'].update(title='(USD)',
                                  range=[min(daily_value_list) * 0.97, max(daily_value_list) * 1.01],
                                  autorange=False)
   
 
    fig_json = fig.to_json()

    # convert graph to PNG and encode it
    png = plotly.io.to_image(fig)
    png_base64 = base64.b64encode(png).decode('ascii')  

    return "data:image/png;base64,"+png_base64

def get_pie_graph(single_strategy_data):
        
    amts = [single_strategy_data['data']['0']['current_value'], single_strategy_data['data']['1']['amt_invested'],
            single_strategy_data['data']['2']['current_value']]
    companies = [single_strategy_data['data']['0']['company'], single_strategy_data['data']['1']['company'],
                 single_strategy_data['data']['2']['company']]
    fig = go.Figure(data=[go.Pie(labels=companies, values=amts)])
    fig_json = fig.to_json()

    # convert graph to PNG and encode it
    png = plotly.io.to_image(fig)
    png_base64 = base64.b64encode(png).decode('ascii')  

    return "data:image/png;base64,"+png_base64


def get_pie_graph_all(all_strategy_data):
        
    amts = [all_strategy_data['strategy'][0]['data']['0']['current_value'],
            all_strategy_data['strategy'][0]['data']['1']['current_value'],
            all_strategy_data['strategy'][0]['data']['2']['current_value']]
    companies = [all_strategy_data['strategy'][0]['data']['0']['company'],
                 all_strategy_data['strategy'][0]['data']['1']['company'],
                 all_strategy_data['strategy'][0]['data']['2']['company']]
    print(len(all_strategy_data['strategy']))
    if len(all_strategy_data['strategy']) > 1:
        amts.append(all_strategy_data['strategy'][1]['data']['0']['current_value'])
        amts.append(all_strategy_data['strategy'][1]['data']['1']['current_value'])
        amts.append(all_strategy_data['strategy'][1]['data']['2']['current_value'])
        companies.append(all_strategy_data['strategy'][1]['data']['0']['company'])
        companies.append(all_strategy_data['strategy'][1]['data']['1']['company'])
        companies.append(all_strategy_data['strategy'][1]['data']['2']['company'])

    fig = go.Figure(data=[go.Pie(labels=companies, values=amts)])
    fig_json = fig.to_json()

    # convert graph to PNG and encode it
    png = plotly.io.to_image(fig)
    png_base64 = base64.b64encode(png).decode('ascii')  

    return "data:image/png;base64,"+png_base64