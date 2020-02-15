from builtins import str
import pandas as pd
import numpy as np
import re
import datetime
import matplotlib.pyplot as plt

# Global Parameters #####################################################
# Names of the files to import
data_files_names = ['HistoricalQuotes_SPY_5Y_02112020.csv', 'HistoricalQuotes_TSLA_5Y_02112020.csv']
# List of columns from data source being days
columns_being_prices = ['Close', 'Open', 'High', 'Low']
# Time horizon (in open trading days)
time_horizon = 60
# Setting what is considered to be a SPY large move in one day = -0.5%
spy_large_move = -0.5
# Setting the target profit for TSLA when taking a position = + 5%
target_profit_taking = 5.0
# Starting capital to invest: $5,000
starting_capital = 5000.0

# Read the CSV file  & Prepare data #######################################################
def read_nasdaq_csv(file_name):
    df0 = pd.read_csv(file_name)
    # Re-order from oldest to newest, and re-indexing
    df0 = df0.sort_index(ascending=False)
    df0 = df0.set_index('Date')
    # Rename the Close/Last column to Close
    df0 = df0.rename(columns={'Close/Last': 'Close'})
    # Apply the function on the index to convert the string date into a proper date
    df0.index = df0.index.map(dstring_to_date_NASDAQ)
    # Apply the function on the price columns to make sure prices are float
    df0[columns_being_prices] = df0[columns_being_prices].applymap(price_as_float_NASDAQ)
    # Add a column named 'Change' giving the percentage of change on Close price compared to previous day Close
    df0 = add_change_column(df0)
    # Take a sub-set of the data (for the time horizon) and make it clear it is a copy
    df1 = df0.tail(time_horizon).copy()
    return df1
############################################################################

# TRANSFORM DATE STRING INTO DATE ##########################################
def dstring_to_date_NASDAQ(dstr):
    ''' Method that returns a date based on the date string from the NASDAQ export '''
    # Find the positions of / in the string
    separator_positions = [m.start() for m in re.finditer('/', dstr)]
    # Make sure the month is zero-padded
    if separator_positions[0] == 1:
        # Add a '0' so that the month string be zero-padded
        dstr = '0' + dstr
        # Recalculate new separator positions after dstr altered
        separator_positions = [m.start() for m in re.finditer('/', dstr)]
    # Make sure the day is zero-padded
    if separator_positions[1] - separator_positions[0] == 2:
        # Add a '0' so that the day string be zero-padded
        dstr = dstr[:separator_positions[0] + 1] + '0' + dstr[separator_positions[0] + 1:]
    # Transform the formatted string into date
    format_of_date_string = '%m/%d/%Y'
    date = datetime.datetime.strptime(dstr, format_of_date_string)
    return date
#########################################################################

# TRANSFORM PRICE STRING INTO FLOAT ##########################################
def price_as_float_NASDAQ(price):
    ''' Method that makes sure price value is a float '''
    # Removes the $ sign from the string
    if type(price) == str:
        # Transform the string and return the corresponding float
        price = price.lstrip('$')
        return float(price)
    elif type(price) == float:
        # Price already a float, return it
        return price
    else:
        print('Weird... price columns are neither string nor float... check source')
###########################################################################

# Calculate Change from Day to Day ########################################
def add_change_column(df0):
    # Column initiated to calculate the % Change column
    changes_list = []
    # Initiating previous close
    previous_close = df0.iloc[0]['Close']
    # Iterate through rows to calculate changes from day to day
    for i, j in df0.iterrows():
        day_close = j['Close']
        day_change = ((day_close - previous_close) / previous_close) * 100
        changes_list.append(day_change)
        # Get ready for next iteration
        previous_close = day_close
    df0['Change'] = changes_list
    return df0
##########################################################

# Method adding the relative stregth signal column ##########
def add_relative_stregth_column(rs_df):
    # Initiate a list to store the signals
    rs_signal_list = []
    # Iterate over the rows to calculate if signal or not
    for i,j in rs_df.iterrows():
        spy_change = j['SPY Change']
        stock_change = j['TSLA Change']
        if is_showing_rstrength(spy_change,stock_change, spy_large_move) == True:
            rs_signal_list.append(True)
        else:
            rs_signal_list.append(False)
    # Add the column to the dataset
    rs_df['RS Signal'] = rs_signal_list
    return rs_df
############################################################

# STRATEGY BUY SELL ####################################################
def add_strategy_columns(rs_df):
    # Buying when getting the signal, selling at the profit target

    # Init my tracking variables
    in_out_status = 'OUT'
    position_qty = 0
    entry_point_position_value = 0
    position_value = 0
    cash_at_hands = starting_capital
    total_equity = position_value + cash_at_hands

    # Initialize strategy columns
    buy_sell_actions_list = []
    buy_sell_qty_list = []
    position_value_list = []
    cash_at_hands_list = []
    total_equity_list = []

    # Iterate over rows
    for i,j in rs_df.iterrows():

        # ENTRY POINT (BUY)
        if j['RS Signal'] == True and in_out_status == 'OUT':
            # BUY ACTION
            in_out_status = 'IN'
            buy_sell_actions_list.append('BUY')
            # QTY
            position_qty = int(cash_at_hands / j['TSLA Close'])
            buy_sell_qty_list.append(position_qty)
            # POSITION VALUE
            position_value = position_qty * j['TSLA Close']
            entry_point_position_value = position_value
            position_value_list.append(position_value)
            # CASH AT HANDS
            cash_at_hands = cash_at_hands - position_value
            cash_at_hands_list.append(cash_at_hands)
            # TOTAL EQUITY
            total_equity = cash_at_hands + position_value
            total_equity_list.append(total_equity)


        # SELL (EXIT POINT)
        elif in_out_status == 'IN' and (position_value - entry_point_position_value) >= 1000:
            # SELL ACTION
            in_out_status = 'OUT'
            buy_sell_actions_list.append('SELL')

            buy_sell_qty_list.append('-')
            position_value_list.append('-')
            cash_at_hands_list.append('-')
            total_equity_list.append('-')

        # HOLD
        elif in_out_status =='IN':
            buy_sell_actions_list.append('HOLD')
            buy_sell_qty_list.append('-')
            # Update position value and add to the list
            position_value = position_qty * j['TSLA Close']
            position_value_list.append(position_value)
            cash_at_hands_list.append('-')
            # Update total equity and add to the list
            total_equity = cash_at_hands + position_value
            total_equity_list.append(total_equity)

        # WAIT AND DO NOTHING
        elif in_out_status =='OUT':
            buy_sell_actions_list.append('-')
            buy_sell_qty_list.append('-')
            position_value_list.append('-')
            cash_at_hands_list.append('-')
            total_equity_list.append('-')

    # Add new columns to the DataFrame
    rs_df['Action'] = buy_sell_actions_list
    rs_df['Qty'] = buy_sell_qty_list
    rs_df['Position Value'] = position_value_list
    rs_df['Cash at hands'] = cash_at_hands_list
    rs_df['Total Equity'] = total_equity_list

    return rs_df

######################################################################

# Methods determining if stock showing relative strength ############
def is_showing_rstrength(spy_change, stock_change, spy_large_move):
    ''' Method returning True if stock showing relative strength versus a SPY large move '''
    # If the SPY is doing a large move down
    if spy_change <= spy_large_move and stock_change >= 0:
        return True
    else:
        return False
#####################################################################

# MAIN #######################################################
# Read and prepare data
spy_df = read_nasdaq_csv(data_files_names[0])
tsla_df = read_nasdaq_csv(data_files_names[1])

# Initial position taken - max possible with capital to invest
initial_position_qty = int(starting_capital / tsla_df['Close'][0])

# Create dataframe for my relative strength signal
# Initiate my relative strength Data Frame with the spy change Series of data
rs_df = pd.DataFrame({'SPY Close': spy_df['Close'],
                      'TSLA Close': tsla_df['Close'],
                      'SPY Change': spy_df['Change'],
                      'TSLA Change': tsla_df['Change'],
                      'TSLA Buy and Hold Value': tsla_df['Close'] * initial_position_qty
                      })
# Add column with relative strength signal column
rs_df = add_relative_stregth_column(rs_df)
# Add strategy BUY SELL actions column
rs_df = add_strategy_columns(rs_df)








# PLOT ############################################
'''
def plot_my_df(df):
    # Plot on ax1
    ax1 = sns.lineplot(x=df.index, y='Close', data=df)

    # Creating a new axis sharing the same x
    ax2 = ax1.twinx()
    # Creating a Custom Palette
    custom_palette = []
    for change in df['Change']:
        if change <= 0:
            custom_palette.append('r')
        else:
            custom_palette.append('g')
    # Plot on ax2
    sns.barplot(x=df.index, y='Change', data=df, ax=ax2, palette=custom_palette)
    # Redefine y axis for ax2
    ax2.set(ylim=(-3, 3))
    # Hide the grid on ax2
    ax2.grid(False)
'''
##############################################################