import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# Replace 'your_file.csv' with the actual path to your CSV file
df = pd.read_csv('C:\\Users\\steak\\Downloads\\DrKatie\\kWTrend.csv')

# Convert the 'Date' column to a pandas datetime object
# Create a new column to identify whether the original time is EST or EDT
df['Timezone'] = df['Date'].str.extract(r'\s(EST|EDT)$')[0]

# Remove timezone abbreviations ('EST', 'EDT') before parsing
df['Date'] = df['Date'].str.replace(r'\s[A-Z]{3}$', '', regex=True)

# Convert the 'Date' column to a pandas datetime object without the timezone
df['Date'] = pd.to_datetime(df['Date'], errors='coerce')

# Localize to 'America/New_York' timezone which handles EST and EDT transitions
df['Date'] = df['Date'].dt.tz_localize('America/New_York')

# Extracting year, month, day, hour, and minute into new columns
df['Year'] = df['Date'].dt.year
df['Month'] = df['Date'].dt.month
df['Day'] = df['Date'].dt.day
df['Hour'] = df['Date'].dt.hour
df['Minute'] = df['Date'].dt.minute
df['Buffer'] = np.where(df['Circuit'] == 'A', 150, np.where(df['Circuit'] == 'B', 75, None))
df['D1Limit'] = 0  # Replace 0 with actual values or expressions
df['D2Limit'] = 0  # Replace 0 with actual values or expressions
df['D3Limit'] = 0  # Replace 0 with actual values or expressions
df['DemandLimit'] = 0  # Replace 0 with actual values or expressions

df = df[df['Month'].isin([4, 5, 6, 7, 8, 9, 10])]
# Set D1Limit based on the conditions
df['D1Limit'] = np.where((df['Circuit'] == 'A') & (df['Month'] == 4), 5519,
                  np.where((df['Circuit'] == 'A') & (df['Month'] == 5), 5500,
                    np.where((df['Circuit'] == 'A') & (df['Month'] == 6), 5979,
                        np.where((df['Circuit'] == 'A') & (df['Month'] == 7), 7682,
                            np.where((df['Circuit'] == 'A') & (df['Month'] == 8), 7227,
                                np.where((df['Circuit'] == 'A') & (df['Month'] == 9), 8488,
                                    np.where((df['Circuit'] == 'A') & (df['Month'] == 10), 8109,
                                        np.where((df['Circuit'] == 'B') & (df['Month'] == 4), 4333,
                                            np.where((df['Circuit'] == 'B') & (df['Month'] == 5), 4720,
                                                np.where((df['Circuit'] == 'B') & (df['Month'] == 6), 5006,
                                                    np.where((df['Circuit'] == 'B') & (df['Month'] == 7), 4609,
                                                        np.where((df['Circuit'] == 'B') & (df['Month'] == 8), 3779,
                                                            np.where((df['Circuit'] == 'B') & (df['Month'] == 9), 4772,
                                                                np.where((df['Circuit'] == 'B') & (df['Month'] == 10), 4506, np.nan))))))))))))))

df['D2Limit'] = np.where((df['Circuit'] == 'A') & (df['Month'] == 4), 5819,
                  np.where((df['Circuit'] == 'A') & (df['Month'] == 5), 5800,
                    np.where((df['Circuit'] == 'A') & (df['Month'] == 6), 6279,
                        np.where((df['Circuit'] == 'A') & (df['Month'] == 7), 7982,
                            np.where((df['Circuit'] == 'A') & (df['Month'] == 8), 7527,
                                np.where((df['Circuit'] == 'A') & (df['Month'] == 9), 8788,
                                    np.where((df['Circuit'] == 'A') & (df['Month'] == 10), 8409,
                                        np.where((df['Circuit'] == 'B') & (df['Month'] == 4), 4483,
                                            np.where((df['Circuit'] == 'B') & (df['Month'] == 5), 4870,
                                                np.where((df['Circuit'] == 'B') & (df['Month'] == 6), 5156,
                                                    np.where((df['Circuit'] == 'B') & (df['Month'] == 7), 4759,
                                                        np.where((df['Circuit'] == 'B') & (df['Month'] == 8), 3929,
                                                            np.where((df['Circuit'] == 'B') & (df['Month'] == 9), 4922,
                                                                np.where((df['Circuit'] == 'B') & (df['Month'] == 10), 4656, np.nan))))))))))))))

df['D3Limit'] = np.where((df['Circuit'] == 'A') & (df['Month'] == 4), 6119,
                  np.where((df['Circuit'] == 'A') & (df['Month'] == 5), 6100,
                    np.where((df['Circuit'] == 'A') & (df['Month'] == 6), 6579,
                        np.where((df['Circuit'] == 'A') & (df['Month'] == 7), 8282,
                            np.where((df['Circuit'] == 'A') & (df['Month'] == 8), 7827,
                                np.where((df['Circuit'] == 'A') & (df['Month'] == 9), 9088,
                                    np.where((df['Circuit'] == 'A') & (df['Month'] == 10), 8709,
                                        np.where((df['Circuit'] == 'B') & (df['Month'] == 4), 4633,
                                            np.where((df['Circuit'] == 'B') & (df['Month'] == 5), 5020,
                                                np.where((df['Circuit'] == 'B') & (df['Month'] == 6), 5306,
                                                    np.where((df['Circuit'] == 'B') & (df['Month'] == 7), 4909,
                                                        np.where((df['Circuit'] == 'B') & (df['Month'] == 8), 4079,
                                                            np.where((df['Circuit'] == 'B') & (df['Month'] == 9), 5072,
                                                                np.where((df['Circuit'] == 'B') & (df['Month'] == 10), 4806, np.nan))))))))))))))
# Display the updated dataframe
print(df.head())

# Initialize DemandLimit column
df['DemandLimit'] = np.nan

# Variable to track current limit level
current_limit = None  # Track the current demand limit

# Iterate through the DataFrame using iterrows()
for index, row in df.iterrows():
    value = row['Value']
    circuit = row['Circuit']

    # Reset current_limit for Circuit B
    if circuit == 'B':
        current_limit = None

    # Determine DemandLimit based on the current circuit and value
    if circuit == 'A' or circuit == 'B':
        # Check for the highest limit first
        if value > row['D3Limit']:
            df.at[index, 'DemandLimit'] = 'D3'
            current_limit = 'D3'
        elif value > row['D2Limit']:
            df.at[index, 'DemandLimit'] = 'D2'
            current_limit = 'D2'
        elif value > row['D1Limit']:
            df.at[index, 'DemandLimit'] = 'D1'
            current_limit = 'D1'
        else:
            # If it is below D1Limit, check the buffer levels
            if current_limit == 'D3' and value < (row['D3Limit'] - row['Buffer']):
                current_limit = 'D2'  # Drop to D2 if below D3Limit - Buffer
            elif current_limit == 'D2' and value < (row['D2Limit'] - row['Buffer']):
                current_limit = 'D1'  # Drop to D1 if below D2Limit - Buffer
            elif current_limit == 'D1' and value < (row['D1Limit'] - row['Buffer']):
                current_limit = 'D0'  # Drop to D0 if below D1Limit - Buffer
            elif current_limit is None:
                current_limit = 'D0'  # Start at D0 if no limit is active

            # Set the current demand limit if it has been established
            df.at[index, 'DemandLimit'] = current_limit


df.to_csv('ATest.csv', index=False)

print("File saved as 'ATest.csv'")

# Get the rows where demand limit is not D0
df_exceeded_d0 = df[df['DemandLimit'] != 'D0']

# Extract the date part for grouping (creating the 'DateOnly' column)
df['DateOnly'] = df['Date'].dt.date  # Extract only the date part (ensure this is done before grouping)

# Initialize a list to store report data
report_lines = []

# Function to calculate the duration for each period above D0
def calculate_duration_above_d0(group):
    above_d0_periods = []
    current_period_start = None

    for i in range(len(group)):
        if group['DemandLimit'].iloc[i] != 'D0':
            if current_period_start is None:
                current_period_start = group['Date'].iloc[i]  # Start of a new period above D0
        else:
            if current_period_start is not None:
                # End of the current period above D0
                period_end = group['Date'].iloc[i]
                duration = period_end - current_period_start
                above_d0_periods.append((current_period_start, period_end, duration))
                current_period_start = None

    if current_period_start is not None:
        # If still above D0 at the end, use the last time entry as the end
        period_end = group['Date'].iloc[-1]
        duration = period_end - current_period_start
        above_d0_periods.append((current_period_start, period_end, duration))

    return above_d0_periods

# Generate the report for exceeding D0 and durations
grouped_dates = df.groupby(['DateOnly'])
for date, group in grouped_dates:
    # Check if either circuit exceeded D0
    if not group[group['DemandLimit'] != 'D0'].empty:  # If there's any DemandLimit != 'D0' for this date
        circuits = group.groupby('Circuit')
        
        for circuit, circuit_group in circuits:
            max_limit_reached = circuit_group['DemandLimit'].max()  # Find the highest demand limit reached on that day
            report_lines.append(f"Date: {date}, Circuit: {circuit}, Maximum Demand Limit Reached: {max_limit_reached}")

            # Now calculate the duration of periods where DemandLimit was above D0
            periods_above_d0 = calculate_duration_above_d0(circuit_group)

            for start, end, duration in periods_above_d0:
                report_lines.append(f"    Demand exceeded D0 from {start} to {end}, duration: {duration}")

# Write the report to a text file (only if there's data to report)
if report_lines:
    with open('DemandLimitReportWithDuration.txt', 'w') as report_file:
        for line in report_lines:
            report_file.write(line + '\n')

    print("Report generated and saved as 'DemandLimitReportWithDuration.txt'")
else:
    print("No days exceeded D0. No report generated.")

# Step 1: Convert 'Date' to just the date part for day-based analysis
df['DateOnly'] = df['Date'].dt.date

# Step 2: Filter rows where DemandLimit is not 'D0'
df_exceeded_d0 = df[df['DemandLimit'] != 'D0']

# Step 3: Identify cases where only Circuit A, only Circuit B, or both exceeded D0
# Group by date and circuit to check for exceedances per circuit
grouped_dates = df_exceeded_d0.groupby(['DateOnly', 'Circuit'])['DemandLimit'].max()

# Convert to a DataFrame for easier manipulation
grouped_df = grouped_dates.reset_index()

# Count unique days for Circuit A and Circuit B exceedances
only_a_exceeded = grouped_df[grouped_df['Circuit'] == 'A']['DateOnly'].unique()
only_b_exceeded = grouped_df[grouped_df['Circuit'] == 'B']['DateOnly'].unique()

# Count cases where both circuits exceeded D0 on the same date
both_exceeded = grouped_df.groupby('DateOnly').filter(lambda x: len(x) > 1)

# Unique counts for the final report
unique_days_a = len(set(only_a_exceeded))
unique_days_b = len(set(only_b_exceeded))
unique_days_both = len(set(both_exceeded['DateOnly']))

# Step 4: Count by month for individual circuits with specific dates
grouped_by_month = df_exceeded_d0.groupby([df['Date'].dt.month, 'Circuit'])['DateOnly'].apply(list)

# Step 5: Count months where both circuits exceeded D0
both_exceeded_by_month = both_exceeded.groupby(both_exceeded['DateOnly'].map(lambda d: d.month))['DateOnly'].apply(list)

# Write results to a text file
with open('exceeded_d0_report.txt', 'w') as f:
    # Total unique days that exceeded D0
    total_unique_days = df_exceeded_d0['DateOnly'].nunique()
    f.write(f"Total unique days exceeding D0: {total_unique_days}\n\n")

    # Count for each circuit
    f.write(f"Unique days where only Circuit A exceeded D0: {unique_days_a}\n")
    f.write(f"Unique days where only Circuit B exceeded D0: {unique_days_b}\n")
    f.write(f"Unique days where both circuits exceeded D0: {unique_days_both}\n\n")

    # Count by month with specific dates
    f.write("Monthly exceedance report (by Circuit A and B):\n")
    for (month, circuit), dates in grouped_by_month.items():
        unique_dates = set(dates)
        f.write(f"Month {month}, Circuit {circuit}: {len(unique_dates)} unique days (Dates: {', '.join(map(str, unique_dates))})\n")

    # Count for both circuits exceeding D0 by month with specific dates
    f.write("\nMonthly count where both circuits exceeded D0:\n")
    for month, dates in both_exceeded_by_month.items():
        unique_dates = set(dates)
        f.write(f"Month {month}: {len(unique_dates)} unique days (Dates: {', '.join(map(str, unique_dates))})\n")

print("Report saved to 'exceeded_d0_report.txt'")





