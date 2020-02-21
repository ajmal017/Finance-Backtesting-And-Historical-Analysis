from builtins import str
import numpy as np
import pandas as pd
import re
import datetime
import matplotlib.pyplot as plt
# Close all figure windows
plt.close('all')

# GLOBAL PARAMETERS ####################################################################
# Names of the files to import (Yahoo Finance csv files)
data_files_names = ['SPY.csv',
                    'TSLA.csv',
                    'BA.csv',
                    'MCD.csv'
                    ]
# Time horizon used (in open trading days)
time_horizon = 10
# Setting what is considered to be a SPY large move in one day = -0.5%
spy_large_move = -0.5
# Setting the target profit for TSLA when taking a position = + 5%
target_profit_taking = 5.0
# Starting capital to invest: $10,000
starting_capital = 10000.0
#####################################################################################

# FUNCTIONS DEFINITION ################################################################
def create_master_data_df(data_files_names):
    '''Function returning a Data Frame with metadata about the source files'''
    # Create a list of Equity names based on files names
    # Create a lambda function extracting the string name of equity
    extract_name = lambda x: x[0:x.find('.')]
    # Create the list of equities
    equities_list = list(map(extract_name,data_files_names))
    # Create the Data Frame with all that metadata
    meta_data_df = pd.DataFrame({'Equity': equities_list, 'File Name': data_files_names})
    return meta_data_df

def read_data_source_csv(file_name):
    ''' Read the CSV file  & returns corresponding Data Frame '''
    df0 = pd.read_csv(file_name)
    # Set the date as the index
    df0 = df0.set_index('Date')
    # Apply the function on the index to convert the string date into a proper date
    df0.index = df0.index.map(dstring_to_date)
    # Add a column named 'Change' giving the percentage of change between today's Close and previous Close
    df0 = add_change_column(df0)
    # Take a sub-set of the data (for the time horizon) and make it clear it is a copy
    df1 = df0.tail(time_horizon).copy()
    return df1

def dstring_to_date(dstr):
    ''' Method that returns a date object based on the date string  '''
    # Set the format as it is originally (as a string in the Data Frame read from the CSV)
    format_of_date_string = '%Y-%m-%d'
    # Convert into a datetime object and return it
    return datetime.datetime.strptime(dstr, format_of_date_string)

def add_change_column(df):
    ''' Calculate the Change from Day Close to Day Close and returns Data Frame with corresponding column added '''
    # Be n the length of the data frame
    n = df.__len__()
    # Iterating over the data frame rows
    for r in range(1, n):
        previous_close = df.iloc[r-1]['Close']
        close = df.iloc[r]['Close']
        try:
            change = ((close - previous_close) / previous_close)*100
            df.at[df.index[r], 'Change'] = change
        except ZeroDivisionError:
            print('Previous Close = 0, Cannot calculate change. ZeroDivisionError.')
    return df

def add_relative_stregth_column(df):
    ''' Method calculating the relative strength signal and returns Data Frame with corresponding column added '''
    # Initiate a list to store the signals
    rs_signal_list = []
    # Iterate over the rows to calculate if signal or not
    for i,j in df.iterrows():
        spy_change = j['SPY Change']
        stock_change = j['TSLA Change']
        if is_showing_rstrength(spy_change,stock_change, spy_large_move) == True:
            rs_signal_list.append(True)
        else:
            rs_signal_list.append(False)
    # Add the column to the dataset
    df['RS Signal'] = rs_signal_list
    return df

def add_strategy_columns(df):
    ''' Method calculating the strategy columns (action, equity, ...) and returns Data Frame with corresponding columns added '''
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
    for i,j in df.iterrows():

        # WAIT AND DO NOTHING
        if in_out_status == 'OUT' and j['RS Signal'] == False :
            # NO ACTION
            buy_sell_actions_list.append('-')
            # QTY
            buy_sell_qty_list.append(position_qty)
            # POSITION VALUE
            position_value_list.append(position_value)
            # CASH AT HANDS
            cash_at_hands_list.append(cash_at_hands)
            # TOTAL EQUITY
            total_equity = cash_at_hands + position_value
            total_equity_list.append(total_equity)

        # ENTRY POINT (BUY)
        elif in_out_status == 'OUT' and j['RS Signal'] == True :
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

        # HOLD
        elif in_out_status =='IN' and (position_value - entry_point_position_value) < 1000:
            # HOLD ACTION
            buy_sell_actions_list.append('HOLD')
            # QTY
            buy_sell_qty_list.append(position_qty)
            # POSITION VALUE
            position_value = position_qty * j['TSLA Close']
            position_value_list.append(position_value)
            # CASH AT HANDS
            cash_at_hands_list.append(cash_at_hands)
            # TOTAL EQUITY
            total_equity = cash_at_hands + position_value
            total_equity_list.append(total_equity)

        # SELL (EXIT POINT)
        elif in_out_status == 'IN' and (position_value - entry_point_position_value) >= 1000:
            # SELL ACTION
            in_out_status = 'OUT'
            buy_sell_actions_list.append('SELL')
            # CASH AT HANDS
            cash_at_hands = cash_at_hands + (position_qty * j['TSLA Close'])
            cash_at_hands_list.append(cash_at_hands)
            # QTY
            position_qty = 0
            buy_sell_qty_list.append(position_qty)
            # POSITION VALUE
            position_value = 0
            position_value_list.append(position_value)
            # TOTAL EQUITY
            total_equity = cash_at_hands + position_value
            total_equity_list.append(total_equity)

    # Add new columns to the DataFrame
    df['Action'] = buy_sell_actions_list
    df['Qty'] = buy_sell_qty_list
    df['Position Value'] = position_value_list
    df['Cash at hands'] = cash_at_hands_list
    df['Total Equity'] = total_equity_list

    return df

def create_df_list(meta_data_df):
    '''Method that creates the list of Data Frames, one per Equity'''
    # Initialize an empty list to store the Data Frames
    df_list = []
    # Iterate over the equity list
    for index, equity_row in metadata_df.iterrows():
        # create Data Frame from reading the csv file
        df0 = read_data_source_csv(equity_row['File Name'])
        # Insert a column with Equity name in the first position
        df0.insert(0,'Equity',equity_row['Equity'])
        # Add the Data Frame to the list
        df_list.append(df0)
    return df_list

def add_SPY_change(df_list):
    '''Add the SPY Change column to each Data Frame and return the list'''
    # Get the index of the SPY Data Frame in the list



def is_showing_rstrength(spy_change, stock_change, spy_large_move):
    ''' Method returning True if stock showing relative strength versus a SPY large move '''
    # If the SPY is doing a large move down
    if spy_change <= spy_large_move and stock_change >= 0:
        return True
    else:
        return False

# MAIN ################################################################################################3
# Create the Metada Data Frame (with Equity name, File name, etc...)
metadata_df = create_master_data_df(data_files_names)
# Create a list of Data Frames for each Equity
df_list = create_df_list(metadata_df)
# Add the SPY Change to all the Equity Data Frames
df_list = add_SPY_change(df_list)
# Generate the Relative strength signal and add corresponding column



# Run the strategy and add corresponding columns (BUY/SELL action, position value, ...)


# Create Test DF for debugging
test_df0 = df_list[0]
test_df1 = df_list[1]
test_df2 = df_list[3]



'''
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

# PLOT
# Plot the selected columns
rs_df.loc[ : , ['TSLA Buy and Hold Value', 'Total Equity'] ].plot()
'''
#######################################################################################################3