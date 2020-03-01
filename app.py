import matplotlib.pyplot as plt
plt.close('all')        # Close all figure windows
from backtesting_functions import *     # importing my custom functions

# PARAMETERS ####################################################################

# Names of the files to import (Yahoo Finance csv files)
data_files_names = ['SPY.csv',
                    'TSLA.csv',
                    'BA.csv',
                    'MCD.csv']
time_horizon = 20 # Time horizon used (in open trading days)
spy_large_move = -0.5 # Setting what is considered to be a SPY large move in one day = -0.5%
target_profit_taking = 5.0 # Setting the target profit for stock when taking a position = + 5%
starting_capital = 5000.0 # Starting capital to invest: $10,000

# MAIN ##########################################################################

metadata_df = create_master_data_df(data_files_names) # Create the Metada Data Frame (with Equity name, File name, etc...)
df_list = create_df_list(metadata_df, time_horizon) # Create a list of Data Frames for each Equity
df_list = add_SPY_change(df_list, metadata_df) # Add the SPY Change
df_list = generate_relative_strength_column(df_list, spy_large_move) # Generate the Relative strength signal
df_list = generate_strategy_columns(df_list, starting_capital) # Run the strategy and add corresponding columns
df_list = generate_buy_and_hold_column(df_list, starting_capital) # Add Buy and Hold Equity

# Create Test DF for debugging
test_df1 = df_list[1]
test_df2 = df_list[2]
test_df3 = df_list[3]

# PLOT #########################################################################
fig = plt.figure() # an empty figure with no axes


x = test_df1['Date']
y =
plt.show()
