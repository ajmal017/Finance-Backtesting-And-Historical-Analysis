import pandas as pd
import yfinance as yf
from datetime import datetime

# Global parameters
ticker = '^GSPC'
period = '5d' # valid periods: 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max
interval = '1m' # valid intervals: 1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo
prepost = False # download pre/post regular market hours data


if __name__ == '__main__':

    start = datetime(2020, 3, 30)
    end = datetime(2020, 3, 31)
    df = yf.download(tickers='^GSPC', start=start, end=end, interval='1m')
