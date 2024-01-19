import os
import pandas as pd
import yfinance as yf
import streamlit as st

import plotly.graph_objects as go

FUNDAMENTALS_TO_PLOT = [
    'Cash And Cash Equivalents',
    'Current Debt',
    'Long Term Debt',
    'Invested Capital',
]

def get_data(ticker: str):
    
    try:
        price_data = yf.download(ticker)
        balance_sheet = yf.Ticker(ticker).quarterly_balance_sheet
        
        # Format the balance sheet so the date is the index
        balance_sheet = balance_sheet.T
        balance_sheet.index.name = 'Date'
        
        # Save them in the data directory to access them again later without
        # redownloading the files
        price_data.to_csv(f'data/{ticker}_prices.csv')
        balance_sheet.to_csv(f'data/{ticker}_balance_sheet.csv')
        
    except Exception as e:
        st.write(e)
    
    return (
        price_data.reset_index(),
        balance_sheet.reset_index()
    )

def get_candlestick_chart(price_data, ma_type, ma_length, plot_days):
    
    if ma_type == 'Simple':
        price_data['ma'] = price_data['Close'].rolling(int(ma_length)).mean()
    else:
        price_data['ma'] = price_data['Close'].ewm(int(ma_length)).mean()
    
    price_data = price_data[-int(plot_days):]
    
    fig = go.Figure()
    
    fig.add_trace(
        go.Candlestick(
            x=price_data['Date'],
            open=price_data['Open'],
            high=price_data['High'],
            low=price_data['Low'],
            close=price_data['Close'],
            showlegend=False,
        )
    )
    
    fig.add_trace(
        go.Line(
            x=price_data['Date'],
            y=price_data['ma'],
            name=f'{int(ma_length)} Period {ma_type} Moving Average'
        )    
    )
    
    fig.update_xaxes(
        rangebreaks = [{'bounds': ['sat', 'mon']}],
        rangeslider_visible = False,
    )
    
    fig.update_layout(
        legend = {'x': 0, 'y': -0.05, 'orientation': 'h'},
        margin = {'l': 50, 'r': 50, 'b': 50, 't': 25},
        width = 800,
        height = 800,
    )
    
    return fig


def plot_balance_sheet(balance_sheet):
    
    fig = go.Figure()
    
    for col in FUNDAMENTALS_TO_PLOT:
        
        fig.add_trace(
            go.Line(
                x=balance_sheet['Date'],
                y=balance_sheet[col],
                name=col,
            )    
        )
            
    fig.update_yaxes(type='log')
            
    fig.update_layout(
        legend = {'x': 0, 'y': -0.05, 'orientation': 'h'},
        margin = {'l': 50, 'r': 50, 'b': 50, 't': 25},
        width = 800,
        height = 400,
    )
    
    return fig
    
    
# Sidebar controls -----------------------------------------------------------
ticker = st.sidebar.text_input(
    label='Stock ticker',
    value='TSLA',    
)

ma_type = st.sidebar.selectbox(
    label='Moving average type',
    options=['Simple', 'Exponential'],
)

ma_length = st.sidebar.number_input(
    label='Moving average length',
    value=10,
    min_value=2,
    step=1,    
)

plot_days = st.sidebar.number_input(
    label='Chart viewing length',
    value=120,
    min_value=1,
    step=1,
)

st.sidebar.button(
    label='Update data',
    on_click=get_data,
    kwargs={'ticker': ticker},
)

# The dashboard plots --------------------------------------------------------

st.header(f'{ticker} Dashboard 💵')

# Check if we have the stock data, if not, download it
if os.path.isfile(f'data/{ticker}_prices.csv'):
    price_data = pd.read_csv(f'data/{ticker}_prices.csv')
    balance_sheet = pd.read_csv(f'data/{ticker}_balance_sheet.csv')
else:
    price_data, balance_sheet = get_data(ticker)

with st.expander('Open to see the stock information'):
    st.write(yf.Ticker('TSLA').info['longBusinessSummary'])


st.subheader('Price Chart 📈')    
st.plotly_chart(
    get_candlestick_chart(price_data, ma_type, ma_length, plot_days)
)

st.subheader('Balance Sheet Chart 📊')
st.plotly_chart(
    plot_balance_sheet(balance_sheet)    
)