import pandas as pd
import datetime
import time
import streamlit as st
import ccxt

exchanges = pd.DataFrame(ccxt.exchanges)
exchange = st.multiselect("Exchange",exchanges,"binanceus")
exchange = getattr(ccxt, exchange[0])()
markets = exchange.load_markets()
symbols = pd.DataFrame(exchange.symbols)

ticker = st.multiselect("Ticker",symbols,"BTC/USD")

start = st.date_input(
    "Starting Date",
    value= datetime.datetime(2010,1,1), max_value = datetime.datetime.today())

end = st.date_input(
    "End Date",
    datetime.datetime.today(), max_value = datetime.datetime.today())
since = int(datetime.datetime(start.year, start.month, start.day).timestamp())
until = int(datetime.datetime(end.year, start.month, start.day).timestamp())
symbol = markets[ticker[0]]["info"]["symbol"]
history = exchange.fetch_ohlcv(symbol, timeframe="1d", since=since)

df = pd.DataFrame(history,index=None)
df.rename(columns={0: "Date", 1: "Open", 2: "High",3:"Low",4:"Close",5:"Volume"},inplace=True)
for i in range(len(df.Date)):
  df.Date[i]=datetime.date.fromtimestamp(int(df.Date[i]/1000.0))

with st.container():
    st.dataframe(df)
    st.line_chart(df.Close)