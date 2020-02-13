import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import re
import datetime
import seaborn as sns
# Setting Seaborn style via set()
sns.set()

# Global Parameters #####################################################
# Names of the files to import
data_files_names = ['HistoricalQuotes_SPY_5Y_02112020.csv', 'HistoricalQuotes_TSLA_5Y_02112020.csv']
# List of columns from data source being days
columns_being_prices = ['Close', 'Open', 'High', 'Low']
# Time horizon (in open trading days)
time_horizon = 10

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

# PLOT ############################################
def plot_my_df(df):
    # Plot on ax1
    ax1 = sns.lineplot(x=df.index, y='Close', data=df, markers=True)
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
    plt.show()
##############################################################

# MAIN #######################################################
# Read data
spy_df = read_nasdaq_csv(data_files_names[0])
tsla_df = read_nasdaq_csv(data_files_names[1])
# Add change columns
spy_df = add_change_column(spy_df)
tsla_df = add_change_column(tsla_df)
# Join dataframes into an overall dataframe
#overall_df = spy_df.join(tsla_df, on='Date')

#plot_my_df(spy_df)
