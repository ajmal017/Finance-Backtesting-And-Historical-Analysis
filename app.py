from functions import * # importing my custom functions

# MAIN RUNS ##########################################################################

ba_df_lst = create_df_list(['BA'], period ='max', interval='1d', prepost=False) # Get Boeing DataFrame (as a list of only one dataframe)
ba_df_lst = add_change_column_over_month(ba_df_lst) # Add change column (calculated over trailing month)
ba_df = ba_df_lst[0] # extract the only Df for Boeing

ba_df = ba_df[20:].copy()  # remove the first 20 days  because the change column cannot be calculated yet at that point

ba_df['Min'] = ba_df.Change[(ba_df.Change.shift(1) > ba_df.Change) & (ba_df.Change.shift(-1) > ba_df.Change)] # find local minimums

if ba_df.loc[ba_df.index[-1], 'Change'] < ba_df.loc[ba_df.index[-2], 'Change']: # if the last change is smaller than the previous one, consider this is a local minimum as well, add him to the Min column
    ba_df.loc[ba_df.index[-1], 'Min'] = ba_df.loc[ba_df.index[-1], 'Change']

ba_df.loc['20170101':,['Close', 'Change']].plot()

#ba_df.to_excel('ba_df.xlsx')




