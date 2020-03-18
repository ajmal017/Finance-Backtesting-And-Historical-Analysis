from functions import * # importing my custom functions

# GLOBAL PARAMETERS ####################################################################

equities_list = ['SPY', 'AMD', 'SNAP', 'INTC', 'MSFT', 'TSLA', 'AAPL', 'MU', 'NVDA'] # List of equities that are going to be used for backtesting
period = '1y' # valid periods: 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max
interval = '1d' #valid intervals: 1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo
prepost = False # download pre/post regular market hours data

spy_large_move = -0.5 # Setting what is considered to be a SPY large move in one day = -0.5%
target_profit_taking = 5.0 # Setting the target profit for stock when taking a position = + 5%
starting_capital = 10000.0 # Starting capital to invest: $10,000

name_of_output_pdf = 'output.pdf'
pd.plotting.register_matplotlib_converters() # register converters (execution was giving me warning and that seems like the fix)

# MAIN RUNS ##########################################################################

ba_df = create_df_list(['BA'], period ='max', interval='1d' , prepost=False) # Get BA
ba_df = add_change_column_over_month(ba_df) # Add change column (calculated over trailing month)
ba_df = ba_df[0] # extract the Df

ba_df = ba_df[20:].copy()  # remove the first month because chnage column cannot be calculated yet at that point

ba_df['min'] = ba_df.Change[(ba_df.Change.shift(1) > ba_df.Change) & (ba_df.Change.shift(-1) > ba_df.Change)] # find local minimums

ba_df.to_excel('ba_df.xlsx')




