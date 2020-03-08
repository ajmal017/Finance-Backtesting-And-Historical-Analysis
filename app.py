from backtesting_functions import * # importing my custom functions

# PARAMETERS ####################################################################
# List of equities that are going to be used for backtesting
#equities_list = ['SPY', 'AMD', 'BA', 'INTC', 'MSFT', 'MU', 'NFLX', 'NKE', 'NVDA', 'QCOM', 'SNAP', 'AAPL', 'TSLA']
equities_list = ['SPY', 'AMD', 'BA', 'INTC', 'MSFT']
period = '1y' # valid periods: 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max
interval = '1d' #valid intervals: 1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo
prepost = False # download pre/post regular market hours data

spy_large_move = -0.5 # Setting what is considered to be a SPY large move in one day = -0.5%
target_profit_taking = 5.0 # Setting the target profit for stock when taking a position = + 5%
starting_capital = 10000.0 # Starting capital to invest: $10,000

name_of_output_pdf = 'output.pdf'

# MAIN ##########################################################################

df_list = create_df_list(equities_list, period, interval, prepost) # Generates the list of data frames for the equities

df_list = add_change_column(df_list) # Adds a change column to each data frame, tracking change from period to period
df_list = add_SPY_change(df_list, equities_list) # Add the SPY Change

df_list = generate_relative_strength_column(df_list, spy_large_move) # Generate the Relative strength signal
df_list = generate_strategy_columns(df_list, starting_capital) # Run the strategy and add corresponding columns
df_list = generate_buy_and_hold_column(df_list, starting_capital) # Add Buy and Hold Equity



# PLOT #########################################################################

pd.plotting.register_matplotlib_converters() # register converters (execution was giving me warning and that seems like the fix)

#plot_and_export_to_pdf(equities_list, df_list, 3, 3, name_of_output_pdf) # plot the list of dataframes and export to pdf, columns x rows per page, with output pdf file name
distrib = plot_spy_hist(equities_list, df_list) # plot the SPY distribution
