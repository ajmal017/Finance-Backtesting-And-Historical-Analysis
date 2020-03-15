from functions import * # importing my custom functions

# GLOBAL PARAMETERS ####################################################################

equities_list = ['SPY', 'AMD', 'BA', 'INTC', 'MSFT'] # List of equities that are going to be used for backtesting
period = '1y' # valid periods: 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max
interval = '1d' #valid intervals: 1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo
prepost = False # download pre/post regular market hours data

spy_large_move = -0.5 # Setting what is considered to be a SPY large move in one day = -0.5%
target_profit_taking = 5.0 # Setting the target profit for stock when taking a position = + 5%
starting_capital = 10000.0 # Starting capital to invest: $10,000

name_of_output_pdf = 'output.pdf'
pd.plotting.register_matplotlib_converters() # register converters (execution was giving me warning and that seems like the fix)

# MAIN RUNS ##########################################################################

# df_list = run_backtesting(equities_list, period, interval, prepost, spy_large_move, starting_capital) # run the backtesting
# plot_and_export_to_pdf(df_list, 3, 3, name_of_output_pdf) # plot the list of dataframes and export to pdf, columns, rows per page

df_sp, sp_hist, sp_bins, sp_patches = plot_equity_change_distribution(equity='^GSPC', period='10y') # plot the S&P distribution
