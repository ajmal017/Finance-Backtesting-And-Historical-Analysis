import numpy as np
import matplotlib
matplotlib.use("TkAgg") # Use that Backend for rendering, to avoid crashing of figure in PyCharm
from matplotlib import pyplot as plt # Import pyplot
plt.close('all') # Close all figure windows
plt.style.use('seaborn') # using a specific matplotlib style
from backtesting_functions import * # importing my custom functions

# PARAMETERS ####################################################################

# Names of the files to import (Yahoo Finance csv files)
data_files_names = ['SPY.csv',
                    'AMD.csv',
                    #'BA.csv',
                    #'INTC.csv',
                    'MSFT.csv',
                    'MU.csv',
                    'NFLX.csv',
                    #'NKE.csv',
                    'NVDA.csv',
                    #'QCOM.csv',
                    #'SNAP.csv',
                    'AAPL.csv',
                    'TSLA.csv'
                    ]
time_horizon = 200 # Time horizon used (in open trading days)
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
test_df0 = df_list[0]
test_df1 = df_list[1]
test_df2 = df_list[2]
test_df3 = df_list[3]

# PLOT #########################################################################

pd.plotting.register_matplotlib_converters() # register converters (execution was giving me warning and that seems like the fix)

nb_columns_axes_matrix = 3 # number of columns I want in my matrix of axes (plots)
nb_rows_axes_matrix = int(np.ceil( len(df_list) / nb_columns_axes_matrix ))  # number of rows calculated based on number of df to plot

fig, ax_lst = plt.subplots(nb_rows_axes_matrix, nb_columns_axes_matrix) # a figure with a 'rows x columns' grid of axes
#fig.suptitle('Back testing') # setting the overall figure suptitle

for i in range(nb_rows_axes_matrix): # iterate over rows i of the grid of Axes
    for j in range(nb_columns_axes_matrix): # iterate over columns j of the grid of Axes
        df_list_index_to_plot = (i * nb_columns_axes_matrix) + j # index of the dataframe to plot within the list (df_list): 0, 1, 2, 3
        if df_list_index_to_plot < len(df_list): # check that the index of df to plot is within th length of the data frame list (to avoid going further)
            df = df_list[df_list_index_to_plot] # data frame to plot at that location in the grid
            x = df.index.values # ndarray with dates (index)
            y1 = df['Buy and Hold Equity'] # 1st series to plot
            ax_lst[i, j].set_title(df['Equity'][0])  # set the title of axes in i, j
            ax_lst[i, j].plot(x, y1)  # plot on axes in position i, j
            ax_lst[i, j].set_xticklabels([])
            if df['Equity'][0] != 'SPY': # plot the strategy axis only if the Equity is different from SPY
                y2 = df['Strategy Equity'] # 2nd series to plot
                ax_lst[i, j].plot(x, y2)  # plot on axes in position i, j

plt.savefig('plot.pdf')
plt.show() # show the plot
