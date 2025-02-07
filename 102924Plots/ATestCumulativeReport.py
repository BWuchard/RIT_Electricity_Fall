import pandas as pd
from datetime import datetime, timedelta

# Load the CSV file into a DataFrame
file_path = 'ATest.csv'
df = pd.read_csv(file_path, low_memory=False)

# Ensure the 'Date' column is in datetime format
df['Date'] = pd.to_datetime(df['Date'])

# Sort the DataFrame by the 'Date' column
df = df.sort_values(by='Date')

# Define a mapping for DemandLimit to determine the order of priority
demand_priority = {'D0': 0, 'D1': 1, 'D2': 2, 'D3': 3}

# Map the DemandLimit to the priority values
df['DemandPriority'] = df['DemandLimit'].map(demand_priority)

def generate_filtered_sheet(data, filter_condition):
    # Filter data based on the specified condition
    filtered_data = data[filter_condition]

    # Find the highest DemandLimit reached for each day
    daily_max = filtered_data.loc[filtered_data.groupby(filtered_data['Date'].dt.date)['DemandPriority'].idxmax()]

    # Filter out days where the highest DemandLimit is 'D0'
    daily_max = daily_max[daily_max['DemandLimit'] != 'D0']

    # Extract the unique Month, Day, and the highest DemandLimit for that day
    unique_dates = daily_max[['Date', 'DemandLimit']].drop_duplicates()
    unique_dates['Month'] = unique_dates['Date'].dt.month
    unique_dates['Day'] = unique_dates['Date'].dt.day

    # Keep only Month, Day, and highest DemandLimit columns
    result = unique_dates[['Month', 'Day', 'DemandLimit']].drop_duplicates()

    return result

# Generate the overall result
overall_result = generate_filtered_sheet(df, filter_condition=df['DemandLimit'] != 'D0')

# Generate results for Circuit A and Circuit B
circuit_a_result = generate_filtered_sheet(df, filter_condition=(df['Circuit'] == 'A'))
circuit_b_result = generate_filtered_sheet(df, filter_condition=(df['Circuit'] == 'B'))

# Save the results to an Excel file with three sheets
with pd.ExcelWriter('ATestCumulativeReport.xlsx') as writer:
    overall_result.to_excel(writer, sheet_name='Overall', index=False)
    circuit_a_result.to_excel(writer, sheet_name='Circuit A', index=False)
    circuit_b_result.to_excel(writer, sheet_name='Circuit B', index=False)
    
# Filter the DataFrame for Circuit A and Circuit B
circuit_a_df = df[df['Circuit'] == 'A'].copy()
circuit_b_df = df[df['Circuit'] == 'B'].copy()

def calculate_durations_with_counters(data):
    results = []
    current_demand = None
    duration = 0
    start_time = None

    for i, row in data.iterrows():
        demand_limit = row['DemandLimit']

        # Ensure you have a proper 'Date' column, and combine it with 'Hour' and 'Minute' to create full timestamps
        date = pd.to_datetime(row['Date'])
        hour = int(row['Hour'])
        minute = int(row['Minute'])
        timestamp = pd.Timestamp(year=date.year, month=date.month, day=date.day, hour=hour, minute=minute)

        if demand_limit in ['D1', 'D2', 'D3']:
            if current_demand is None:
                # Start new period
                current_demand = demand_limit
                start_time = timestamp
                duration = 15  # Start with 15 minutes for the first entry
            elif demand_limit == current_demand:
                # Same demand limit, increase duration
                duration += 15
            else:
                # Demand limit changed, record the previous demand period
                end_time = timestamp
                results.append({
                    'Month': start_time.month,
                    'Day': start_time.day,
                    'StartTime': start_time,
                    'EndTime': end_time,
                    'DemandLimit': current_demand,
                    'Duration': duration
                })

                # Start new period
                current_demand = demand_limit
                start_time = timestamp
                duration = 15  # Reset duration for new demand limit

        # If the demand limit is D0, reset the current demand
        if demand_limit == 'D0':
            if current_demand is not None:
                end_time = timestamp
                results.append({
                    'Month': start_time.month,
                    'Day': start_time.day,
                    'StartTime': start_time,
                    'EndTime': end_time,
                    'DemandLimit': current_demand,
                    'Duration': duration
                })
                current_demand = None
                start_time = None
                duration = 0

    # Handle the final demand period if it's not D0
    if current_demand is not None and duration > 0:
        end_time = timestamp  # Use the last timestamp for the final period
        results.append({
            'Month': start_time.month,
            'Day': start_time.day,
            'StartTime': start_time,
            'EndTime': end_time,
            'DemandLimit': current_demand,
            'Duration': duration
        })

    # Convert the results list to a DataFrame
    result_df = pd.DataFrame(results)

    # Now count rows in the new DataFrame (total, by month, and by month-day combination)
    total_rows_new = len(result_df)  # Total rows in the new dataframe
    month_row_counter_new = result_df['Month'].value_counts().to_dict()  # Rows per month

    # Create a combined Month-Day key for counting rows by day (accounting for month)
    result_df['MonthDay'] = result_df['Month'].astype(str) + '-' + result_df['Day'].astype(str)
    day_row_counter_new = result_df['MonthDay'].value_counts().to_dict()  # Rows per month-day combination

    # Add the total rows and row counts to the dataframe
    result_df['TotalRowsNew'] = total_rows_new
    result_df['MonthRowCountNew'] = result_df['Month'].map(month_row_counter_new)
    result_df['DayRowCountNew'] = result_df['MonthDay'].map(day_row_counter_new)

    return result_df
# Calculate durations for Circuit A and Circuit B
circuit_a_result = calculate_durations_with_counters(circuit_a_df)
circuit_b_result = calculate_durations_with_counters(circuit_b_df)

# Output file path
output_file = 'ATestCumulativeReport.xlsx'

# Save the results to new sheets in the existing Excel file
with pd.ExcelWriter(output_file, engine='openpyxl', mode='a') as writer:
    circuit_a_result.to_excel(writer, sheet_name='Circuit_A_Durations', index=False)
    circuit_b_result.to_excel(writer, sheet_name='Circuit_B_Durations', index=False)

print("Duration calculations completed and saved to new sheets.")

# Define a mapping for DemandLimit to determine the order of priority
demand_priority = {'D0': 0, 'D1': 1, 'D2': 2, 'D3': 3}

# Map the DemandLimit to the priority values
df['DemandPriority'] = df['DemandLimit'].map(demand_priority)

def generate_filtered_sheet(data, filter_condition):
    # Filter data based on the specified condition
    filtered_data = data[filter_condition]

    # Find the highest DemandLimit reached for each day
    daily_max = filtered_data.loc[filtered_data.groupby(filtered_data['Date'].dt.date)['DemandPriority'].idxmax()]

    # Filter out days where the highest DemandLimit is 'D0'
    daily_max = daily_max[daily_max['DemandLimit'] != 'D0']

    # Extract the unique Month, Day, and the highest DemandLimit for that day
    unique_dates = daily_max[['Date', 'DemandLimit']].drop_duplicates()
    unique_dates['Month'] = unique_dates['Date'].dt.month
    unique_dates['Day'] = unique_dates['Date'].dt.day

    # Keep only Month, Day, and highest DemandLimit columns
    result = unique_dates[['Month', 'Day', 'DemandLimit']].drop_duplicates()

    return result

# Generate results for D1, D2, and D3 for the entire dataset (Overall)
overall_d1 = generate_filtered_sheet(df, filter_condition=(df['DemandLimit'] == 'D1'))
overall_d2 = generate_filtered_sheet(df, filter_condition=(df['DemandLimit'] == 'D2'))
overall_d3 = generate_filtered_sheet(df, filter_condition=(df['DemandLimit'] == 'D3'))

# Generate results for Circuit A
circuit_a_d1 = generate_filtered_sheet(df, filter_condition=(df['Circuit'] == 'A') & (df['DemandLimit'] == 'D1'))
circuit_a_d2 = generate_filtered_sheet(df, filter_condition=(df['Circuit'] == 'A') & (df['DemandLimit'] == 'D2'))
circuit_a_d3 = generate_filtered_sheet(df, filter_condition=(df['Circuit'] == 'A') & (df['DemandLimit'] == 'D3'))

# Generate results for Circuit B
circuit_b_d1 = generate_filtered_sheet(df, filter_condition=(df['Circuit'] == 'B') & (df['DemandLimit'] == 'D1'))
circuit_b_d2 = generate_filtered_sheet(df, filter_condition=(df['Circuit'] == 'B') & (df['DemandLimit'] == 'D2'))
circuit_b_d3 = generate_filtered_sheet(df, filter_condition=(df['Circuit'] == 'B') & (df['DemandLimit'] == 'D3'))

# Save the results to an Excel file with 9 new sheets
output_file = 'ATestCumulativeReport.xlsx'
with pd.ExcelWriter(output_file, mode='a', engine='openpyxl') as writer:  # Append to existing file
    # Overall sheets
    overall_d1.to_excel(writer, sheet_name='Overall_D1', index=False)
    overall_d2.to_excel(writer, sheet_name='Overall_D2', index=False)
    overall_d3.to_excel(writer, sheet_name='Overall_D3', index=False)
    
    # Circuit A sheets
    circuit_a_d1.to_excel(writer, sheet_name='Circuit_A_D1', index=False)
    circuit_a_d2.to_excel(writer, sheet_name='Circuit_A_D2', index=False)
    circuit_a_d3.to_excel(writer, sheet_name='Circuit_A_D3', index=False)
    
    # Circuit B sheets
    circuit_b_d1.to_excel(writer, sheet_name='Circuit_B_D1', index=False)
    circuit_b_d2.to_excel(writer, sheet_name='Circuit_B_D2', index=False)
    circuit_b_d3.to_excel(writer, sheet_name='Circuit_B_D3', index=False)

print("9 new sheets for D1, D2, and D3 have been saved to the Excel file.")
