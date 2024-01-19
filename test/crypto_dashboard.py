import pandas as pd
from binance.client import Client
import streamlit as st

client = Client()
tickers = client.get_all_tickers()
dropdown = st.selectbox("Pick your coin", tickers)

start = st.date_input("Start", value = pd.to_datetime("2021-10-31"))
investment = st.number_input("Choose investment per month")

def getdata(symbol, start):
  frame = pd.DataFrame(client.get_historical_klines(symbol,
                                                    "1d",
                                                    start))
  frame = frame.iloc[:,:6]
  frame.columns = ["Time", "Open", "High", "Low", "Close", "Volume"]
  frame.set_index = pd.to_datetime(frame.index,unit="ms")
  frame = frame.astype(float)
  return frame

df = getdata(dropdown, start)
st.table(df)
st.line_chart(df)