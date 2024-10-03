import pandas as pd
import time


start_time = time.time()


sheetName = ['No', '2.6', '2.6GW']    
storage_threshold = 760
pool = 'PoolB'
read_file = pool + '.xlsx'
save_file_max = pool + "_max" + '.xlsx'
save_file_avg = pool + "_avg" + '.xlsx'

bins = [0, 437.5, 437.6, 437.7, 437.8, 438, 438.5, 439, 439.5, 440.5, float('inf')]  # Define your bin edges
labels = []
for i in range(0, 10):
    if i == 0:
        string = "<" + str(bins[i+1])
        labels.append(string)
    elif i == 9:
        string = ">" + str(bins[i])
        labels.append(string)
    else:
        string = str(bins[i]) + "-" + str(bins[i+1])
        labels.append(string)
                      

df_output_max = pd.DataFrame()
df_output_max ['Level Group'] = labels

df_output_avg = pd.DataFrame()
df_output_avg ['Level Group'] = labels

for i in range(3):
    df = pd.read_excel(read_file, sheet_name=sheetName[i])
    

    
    # Create a column to identify wet periods based on storage
    df['Wet Period'] = df['Storage'] > storage_threshold
    
    # Create a unique group identifier for each wet period
    df['Wet Period Group'] = (df['Wet Period'] != df['Wet Period'].shift()).cumsum()
    
    # Filter to only include wet periods
    wet_df = df[df['Wet Period']]
    
    # Get maximum and average values for each wet period
    summary_stats = wet_df.groupby('Wet Period Group').agg(
        Max_Water_Level=('Water Level', 'max'),
        Average_Water_Level=('Water Level', 'mean'),
    ).reset_index()
    
    # Print the summary statistics for each wet period
    print(summary_stats)
    

    
    df_output = pd.DataFrame()
    df_output['Duration'] = labels
    
    summary_stats['Group_Max'] = pd.cut(summary_stats['Max_Water_Level'], bins=bins, labels=labels, right=False)
    summary_stats['Group_Avg'] = pd.cut(summary_stats['Average_Water_Level'], bins=bins, labels=labels, right=False)
    
    # Count the number of water levels in each group and create a DataFrame
    group_counts_max = summary_stats['Group_Max'].value_counts().sort_index().reset_index()
    group_counts_avg = summary_stats['Group_Avg'].value_counts().sort_index().reset_index()
    
    # Rename the columns for clarity
    group_counts_max.columns = ['Group', 'Count']
    group_counts_avg.columns = ['Group', 'Count']
    
    # Print the resulting DataFrame
    df_output_max[sheetName[i]] = group_counts_max['Count']
    df_output_avg[sheetName[i]] = group_counts_avg['Count']

df_output_max.to_excel(save_file_max, index=False)
df_output_avg.to_excel(save_file_avg, index=False)


end_time = time.time()
elapsed_time = end_time - start_time
print(f"Elapsed time: {elapsed_time:.4f} seconds")