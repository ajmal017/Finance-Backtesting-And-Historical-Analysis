import numpy as np
import pandas as pd
import yfinance as yf # module to retrieve data on financial instruments (in a 'yahoo finance' style)

import matplotlib
matplotlib.use("macosx") # Use that Backend for rendering, to avoid crashing of figure in PyCharm (TkAgg, macosx)
from matplotlib import pyplot as plt # Import pyplot
plt.close('all') # Close all figure windows
plt.style.use('seaborn') # using a specific matplotlib style
import matplotlib.backends.backend_pdf # used to generate multi page pdfs
import matplotlib.ticker as mtick # to format x-axis as %


# FUNCTIONS DEFINITION ################################################################

def create_df_list(equities_list, period, interval, prepost):
    '''Method that creates the list of Data Frames, one per Equity'''
    # Initialize an empty list to store the Data Frames
    df_list = []
    # Iterate over the equity list
    for equity in equities_list:
        # create Data Frame from reading the csv file
        df0 = yf.download(equity, period= period, interval= interval, prepost= prepost)
        # Insert a column with Equity name in the first position
        df0.insert(0, 'Equity', equity)
        # Add the Data Frame to the list
        df_list.append(df0)
    return df_list

def add_change_column(df_list):
    ''' Calculate the Change from one period to the other and returns the list of Data Frames with corresponding column added '''
    for df in df_list: # Iterate over the data frames
        # Be n the length of the data frame
        n = df.__len__()
        # Iterating over the data frame rows
        for r in range(1, n):
            previous_close = df.iloc[r - 1]['Close']
            close = df.iloc[r]['Close']
            try:
                change = ((close - previous_close) / previous_close) * 100
                df.at[df.index[r], 'Change'] = change
            except ZeroDivisionError:
                print('Previous Close = 0, Cannot calculate change. ZeroDivisionError.')
    return df_list

def add_SPY_change(df_list, equities_list):
    '''Add the SPY Change column to each Data Frame and return the list'''
    # Get the index of the SPY Data Frame in the list
    index_of_SPY = equities_list.index('SPY')
    # Get the SPY data frame, only the SPY change column
    spy_df = df_list[index_of_SPY]
    # Extract the Chhange column of SPY and rename the column
    spy_df_extract = spy_df['Change'].rename('SPY Change')
    # Iterate over all the dataframes and Merge the SPY columns into each of the Equity Data Frames
    for i in range(len(df_list)):
        df_list[i] = pd.merge(df_list[i], spy_df_extract, on='Date')
    return df_list

def generate_relative_strength_column(df_list, spy_large_move):
    ''' Method calculating the relative strength signal and returns the list of Data Frames with corresponding column added '''
    for df in df_list:
        # Initiate a list to store the signals
        rs_signal_list = []
        # Iterate over the rows to calculate if signal or not
        for i, j in df.iterrows():
            spy_change = j['SPY Change']
            stock_change = j['Change']
            if is_showing_rstrength(spy_change, stock_change, spy_large_move) == True:
                rs_signal_list.append(True)
            else:
                rs_signal_list.append(False)
        # Add the column to the dataset
        df['RS Signal'] = rs_signal_list
    return df_list

def is_showing_rstrength(spy_change, stock_change, spy_large_move):
    ''' Method returning True if stock showing relative strength versus a SPY large move '''
    # If the SPY is doing a large move down
    if spy_change <= spy_large_move and stock_change >= 0:
        return True
    else:
        return False

def generate_strategy_columns(df_list, starting_capital):
    ''' Method calculating the strategy columns (action, equity, ...) and returns Data Frame with corresponding columns added '''
    for df in df_list:
        # Buying when getting the signal, selling at the profit target

        # Init my tracking variables
        in_out_status = 'OUT'
        position_qty = 0
        entry_point_position_value = 0
        position_value = 0
        # Adjusting the starting capital in order to compare apples to apples between "Buy and Hold" and "Strategy"
        buy_and_hold_initial_qty = int(starting_capital / df['Close'][0])
        adjusted_starting_capital = buy_and_hold_initial_qty * df['Close'][0]
        cash_at_hands = adjusted_starting_capital
        total_equity = position_value + cash_at_hands

        # Initialize strategy columns
        buy_sell_actions_list = []
        buy_sell_qty_list = []
        position_value_list = []
        cash_at_hands_list = []
        total_equity_list = []

        # Iterate over rows
        for i, row in df.iterrows():

            # Evaluate positon value that day (for condition testing in if's below)
            position_value = position_qty * row['Close']

            # WAIT AND DO NOTHING
            if in_out_status == 'OUT' and row['RS Signal'] == False:
                # NO ACTION
                buy_sell_actions_list.append('-')
                # QTY
                buy_sell_qty_list.append(position_qty)
                # POSITION VALUE
                position_value_list.append(position_value)
                # CASH AT HANDS
                cash_at_hands_list.append(cash_at_hands)
                # Strategy Equity
                total_equity = cash_at_hands + position_value
                total_equity_list.append(total_equity)

            # ENTRY POINT (BUY)
            elif in_out_status == 'OUT' and row['RS Signal'] == True:
                # BUY ACTION
                in_out_status = 'IN'
                buy_sell_actions_list.append('BUY')
                # QTY
                position_qty = int(cash_at_hands / row['Close'])
                buy_sell_qty_list.append(position_qty)
                # POSITION VALUE
                position_value = position_qty * row['Close']
                entry_point_position_value = position_value
                position_value_list.append(position_value)
                # CASH AT HANDS
                cash_at_hands = cash_at_hands - position_value
                cash_at_hands_list.append(cash_at_hands)
                # Strategy Equity
                total_equity = cash_at_hands + position_value
                total_equity_list.append(total_equity)

            # HOLD
            elif in_out_status == 'IN' and (position_value - entry_point_position_value) < 1000:
                # HOLD ACTION
                buy_sell_actions_list.append('HOLD')
                # QTY
                buy_sell_qty_list.append(position_qty)
                # POSITION VALUE
                position_value = position_qty * row['Close']
                position_value_list.append(position_value)
                # CASH AT HANDS
                cash_at_hands_list.append(cash_at_hands)
                # Strategy Equity
                total_equity = cash_at_hands + position_value
                total_equity_list.append(total_equity)

            # SELL (EXIT POINT)
            elif in_out_status == 'IN' and (position_value - entry_point_position_value) >= 1000:
                # SELL ACTION
                in_out_status = 'OUT'
                buy_sell_actions_list.append('SELL')
                # CASH AT HANDS
                cash_at_hands = cash_at_hands + (position_qty * row['Close'])
                cash_at_hands_list.append(cash_at_hands)
                # QTY
                position_qty = 0
                buy_sell_qty_list.append(position_qty)
                # POSITION VALUE
                position_value = 0
                position_value_list.append(position_value)
                # Strategy Equity
                total_equity = cash_at_hands + position_value
                total_equity_list.append(total_equity)

        # Add new columns to the DataFrame
        df['Action'] = buy_sell_actions_list
        df['Qty'] = buy_sell_qty_list
        df['Position Value'] = position_value_list
        df['Cash at hands'] = cash_at_hands_list
        df['Strategy Equity'] = total_equity_list

    return df_list

def generate_buy_and_hold_column(df_list, starting_capital):
    '''Methods that adds the Buy and Hold Equity column based on starting capital '''
    for df in df_list:
        position_qty = int(starting_capital / df['Close'][0])
        df['Buy and Hold Equity'] = position_qty * df['Close']
    return df_list

def calculate_pnl_per_equity(df_list):
    '''Method that calculate the P&L of the strategy per equity and returns a list of P&L'''
    pnl_per_equity = [] # initialize the list of P&L per equity
    for df in df_list: # iterates over the dataframes of equities
        pnl = df['Strategy Equity'].iloc[-1] - df['Buy and Hold Equity'].iloc[-1] # calculating the difference at the last point
        pnl_per_equity.append(pnl)
    return pnl_per_equity

def plot_and_export_to_pdf(df_list, nb_columns_fig, nb_rows_fig, ouput_file_name):
    '''Method that generates an output pdf from a list of dataframes, with dimension columns x rows per page '''
    nb_of_axes_per_page = nb_columns_fig * nb_rows_fig  # number of axes hat can be displayed on a single page

    fig_list = []  # list of figures initialization

    for df_index in range(len(df_list)):  # iterate over all the data frames to plot, and create on as many figures as required (with dimensions set above)
        if df_index % nb_of_axes_per_page == 0:  # if the remainder of df_index divided by number of axes per page is 0, then create a new figure (i.e. previous fig is full)
            figure_number = 1 + int(df_index / nb_of_axes_per_page)
            fig, ax_lst = plt.subplots(nb_rows_fig, nb_columns_fig)  # create a figure with a 'rows x columns' grid of axes
            fig.suptitle('page ' + str(figure_number))
            fig_list.append(fig)  # add the figure to the list of figures
            # print('Just created figure ' + str(figure_number))
        i_fig = int((np.floor(df_index / nb_columns_fig)) % nb_rows_fig)  # row position of the axes on that given figure
        j_fig = int((df_index % nb_columns_fig))  # column position of the axes on that given figure

        # print('i_fig, j_fig: ' + str(i_fig) + ', ' + str(j_fig))

        df = df_list[df_index]  # df to plot at that position
        x = df.index.values  # ndarray with dates (index)
        y1 = df['Buy and Hold Equity']  # 1st series to plot
        ax_lst[i_fig, j_fig].set_title(df['Equity'][0])  # set the title of axes in i, j
        ax_lst[i_fig, j_fig].plot(x, y1)  # plot on axes in position i, j
        ax_lst[i_fig, j_fig].set_xticklabels([])
        if df['Equity'][0] != 'SPY':  # plot the strategy axis only if the Equity is different from SPY
            y2 = df['Strategy Equity']  # 2nd series to plot
            ax_lst[i_fig, j_fig].plot(x, y2)  # plot on axes in position i, j

    pdf = matplotlib.backends.backend_pdf.PdfPages(ouput_file_name)  # create my multi pages pdf
    for fig in fig_list:  # iterate over the list of figures
        pdf.savefig(fig)  # save the figure

    pdf.close()
    plt.close('all')  # Close all figure windows

def plot_equity_change_distribution(equity, period):
    '''plots the Equity changes distribution for a given period, and returns the corresponding data frame and distribution'''
    df_equity_lst = create_df_list([equity], period =period, interval='1d', prepost=False) # create a list with only the equity df in it (methods are working on a list)
    df_equity_lst = add_change_column(df_equity_lst) # add the Change column
    df_equity = df_equity_lst[0] # extract the unique equity df of the list

    # df_equity.loc['20200218': '20200312']

    '''   
    min = df_equity['Change'].describe().loc['min'] # retrieve the minimum value of changes
    max = df_equity['Change'].describe().loc['max'] # retrieve the maximum value of changes
    bins_start = int(np.floor(min)) # starting integer of the bins range (E.g. -9.5 rounded down = floor = -10)
    bins_end = int(np.ceil(max))  # ending integer of the bins range (E.g. 8.5 rounded up = ceil = 9)
    bins = np.arange(bins_start,bins_end + 1) # bins (array) covering the entire spectrum of changes from min to max (added +1 to get arange function to include max value)
    '''

    bins = np.arange(-10, 11) # fixed bins (from -10% to +10%)

    fig, ax = plt.subplots()  # create a fig and axes

    hist_values, bins, patches = ax.hist(x=df_equity['Change'], bins= bins, density=True, cumulative=False, rwidth=0.8, label='over the past 10 years') # plots histogram on the full period
    hist_values_sub, bins_sub, patches_sub = ax.hist(x=df_equity['Change'].loc['20200218': '20200312'], bins= bins, density=True, cumulative=False, rwidth=0.8, label='over last month (February 18th to March 13th, 2020)') # plots histogram for sub-period

    for bin, patch in zip(bins[:-1], patches): # format the main histogram by iterating over its patches (rectangles)
        patch.set_alpha(1) # set alpha (transparency)
        patch.set_color('#545454') # blackkish color

    for bin, patch in zip(bins[:-1], patches_sub): # format the subperiod histogram by iterating over its patches (rectangles)
        patch.set_alpha(0.6) # set alpha (transparency)
        patch.set_color('#CD4343') # reddish color

    ax.set_xticks(bins) # set the x ticks locations, aligned with bins breakdown
    ax.set_title('Probability density of the S&P 500 daily changes')
    ax.set_xlabel('S&P 500 daily change') # x label
    ax.set_ylabel('Probability density')  # y label

    ax.legend(loc='upper left') # makes the legend appear at the upper left
    ax.set(ylim=(0,0.5)) # set the y limit of y-axis
    ax.axes.xaxis.set_major_formatter(mtick.PercentFormatter(decimals=0)) # format x-axis with %


    return df_equity, hist_values, bins, patches


def run_backtesting(equities_list, period, interval, prepost, spy_large_move, starting_capital):
    '''Wrap Function that gets the data, run the overall backtesting and returns the output df_list with strategy columns '''
    df_list = create_df_list(equities_list, period, interval, prepost)  # Generates the list of data frames for the equities

    df_list = add_change_column(df_list)  # Adds a change column to each data frame, tracking change from period to period
    df_list = add_SPY_change(df_list, equities_list)  # Add the SPY Change

    df_list = generate_relative_strength_column(df_list, spy_large_move)  # Generate the Relative strength signal
    df_list = generate_strategy_columns(df_list, starting_capital)  # Run the strategy and add corresponding columns
    df_list = generate_buy_and_hold_column(df_list, starting_capital)  # Add Buy and Hold Equity

    return df_list