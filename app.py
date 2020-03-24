from functions import * # importing my custom functions

# GLOBAL PARAMETERS ####################################################################

equities_list = ['SPY','AIR','XFAB.PA'] # List of equities that are going to be used for backtesting
period = '10y' # valid periods: 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max
interval = '1d' #valid intervals: 1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo
prepost = False # download pre/post regular market hours data

# MAIN RUNS ##########################################################################

list_tickers_tony_df = pd.read_csv('datatony/libelles.csv') # get raw list
list_tickers_tony_df = list_tickers_tony_df.applymap(lambda x: x.split(';')[-1] + '.PA') # extract the tickers only
list_tickers_tony = list_tickers_tony_df['ISIN;nom;ticker'].to_list()



df_list = create_df_list(list_tickers_tony, period,interval,prepost)

for df in df_list:
    df.to_csv(path_or_buf='data_stocks_tony.csv',mode='a')
