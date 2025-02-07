import pandas as pd
from datetime import datetime, timedelta

# Replace 'path_to_your_file' with the actual file path if it's not in the same directory.
file_path = 'ATest.csv'

# Load the CSV file into a DataFrame
df = pd.read_csv(file_path)

# List to store each subset of transitions (from non-D0 to D0)
transitions = []

# Temporary list to store consecutive non-D0 entries
non_D0_entries = []

# Iterate through each row of the DataFrame
for index, row in df.iterrows():
    # Check if the DemandLimit is not equal to D0
    if row['DemandLimit'] != 'D0':
        # Append the row to the list of non-D0 entries
        non_D0_entries.append(row)
    else:
        # If DemandLimit equals D0 and we have collected non-D0 entries
        if non_D0_entries:
            # Create a DataFrame from the list of non-D0 entries and store it as a transition
            transition_df = pd.DataFrame(non_D0_entries)
            transitions.append(transition_df)
            
            # Clear the list for the next set of non-D0 entries
            non_D0_entries = []

# If there are still non-D0 entries at the end, add them as the final transition
if non_D0_entries:
    transition_df = pd.DataFrame(non_D0_entries)
    transitions.append(transition_df)

# Function to find the "last_limit" by moving up in the rows
def find_last_limit(transition, j, current_limit):
    for k in range(j-1, -1, -1):
        if transition.iloc[k]['DemandLimit'] != current_limit:
            return transition.iloc[k]['DemandLimit']
    return 'D0'  # If no earlier different limit is found, assume 'D0'

# Function to find the "next_limit" by moving down in the rows
def find_next_limit(transition, j, current_limit):
    for k in range(j+1, len(transition)):
        if transition.iloc[k]['DemandLimit'] != current_limit:
            return transition.iloc[k]['DemandLimit']
    return 'D0'  # If no later different limit is found, assume 'D0'

# Function to determine the direction based on last, current, and next limits
def determine_direction(last_limit, current_limit, next_limit):
    if last_limit == 'D0' and current_limit == 'D1':
        if next_limit == 'D0':
            return 'D1 Peak'
        elif next_limit == 'D2':
            return 'D1 Rising'
    elif last_limit == 'D1' and current_limit == 'D2':
        if next_limit == 'D3':
            return 'D2 Rising'
        elif next_limit == 'D1':
            return 'D2 Peak'
    elif last_limit == 'D2' and current_limit == 'D1':
        if next_limit == 'D0':
            return 'D1 Falling'
        elif next_limit == 'D2':
            return 'D2 Catch'
    elif last_limit == 'D2' and current_limit == 'D3':
        if next_limit == 'D2':
            return 'D3 Peak'
    elif last_limit == 'D3' and current_limit == 'D2':
        if next_limit == 'D1':
            return 'D2 Falling'
        elif next_limit == 'D3':
            return 'D2 Catch'
    
    return None  # Return None if no change is detected

# Open a text file for writing
with open('transition_limits_report.txt', 'w') as file:
    # Process each transition and identify the limits
    for i, transition in enumerate(transitions):
        # Get the end time (first D0 entry after the transition)
        end_time = None
        for idx in range(transition.index[-1] + 1, len(df)):
            if df.iloc[idx]['DemandLimit'] == 'D0':
                end_row = df.iloc[idx]
                end_time = datetime(int(end_row['Year']), int(end_row['Month']), 
                                    int(end_row['Day']), int(end_row['Hour']), 
                                    int(end_row['Minute']))
                break

        # Get the start time (last D0 entry before the transition)
        start_time = None
        for idx in range(transition.index[0] - 1, -1, -1):
            if df.iloc[idx]['DemandLimit'] == 'D0':
                start_row = df.iloc[idx]
                start_time = datetime(int(start_row['Year']), int(start_row['Month']), 
                                      int(start_row['Day']), int(start_row['Hour']), 
                                      int(start_row['Minute']))
                break

        # Calculate the duration of the transition
        if start_time and end_time:
            total_duration = end_time - start_time
        else:
            total_duration = None
        
        # ---------------- New Snippet Starts Here ----------------
        # Initialize duration counters
        durations = {
            "D1": timedelta(0),
            "D2": timedelta(0),
            "D3": timedelta(0),
            "D1_or_above": timedelta(0),
            "D2_and_above": timedelta(0),
            "D1_rising": timedelta(0),
            "D1_peak": timedelta(0),
            "D1_falling": timedelta(0),
            "D1_catch": timedelta(0),
            "D2_rising": timedelta(0),
            "D2_peak": timedelta(0),
            "D2_falling": timedelta(0),
            "D2_catch": timedelta(0),
            "D3_peak": timedelta(0),
        }
        # ---------------- New Snippet Ends Here ----------------

        # Iterate over each row in the transition and identify the limits
        last_timestamp = None
        previous_direction = None  # To store the last known direction
        for j in range(len(transition)):
            # Get current_limit from the current row
            current_limit = transition.iloc[j]['DemandLimit']
            
            # Find last_limit (moving upwards if necessary)
            last_limit = find_last_limit(transition, j, current_limit)
            
            # Find next_limit (moving downwards if necessary)
            next_limit = find_next_limit(transition, j, current_limit)
            
            # Combine Month, Day, Hour, and Minute into a single datetime string
            month = int(transition.iloc[j]['Month'])
            day = int(transition.iloc[j]['Day'])
            hour = int(transition.iloc[j]['Hour'])
            minute = int(transition.iloc[j]['Minute'])
            date_time = datetime(2024, month, day, hour, minute)
            
            # Get the value from the 'Value' column
            value = transition.iloc[j]['Value']
            
            # Determine direction
            direction = determine_direction(last_limit, current_limit, next_limit)
            
            # If direction is None, keep the previous direction
            if direction is None:
                direction = previous_direction
            
            # Update previous_direction to the current direction
            previous_direction = direction
            
            # ---------------- New Snippet Starts Here ----------------
            # Add 15 minutes to the duration counters based on the current limit and direction
            duration_increment = timedelta(minutes=15)

            if current_limit == 'D1':
                durations["D1"] += duration_increment
                durations["D1_or_above"] += duration_increment
            elif current_limit == 'D2':
                durations["D2"] += duration_increment
                durations["D1_or_above"] += duration_increment
                durations["D2_and_above"] += duration_increment
            elif current_limit == 'D3':
                durations["D3"] += duration_increment
                durations["D1_or_above"] += duration_increment
                durations["D2_and_above"] += duration_increment

            # Update durations based on direction
            if direction == 'D1 Rising':
                durations["D1_rising"] += duration_increment
            elif direction == 'D1 Peak':
                durations["D1_peak"] += duration_increment
            elif direction == 'D1 Falling':
                durations["D1_falling"] += duration_increment
            elif direction == 'D1 Catch':
                durations["D1_catch"] += duration_increment
            elif direction == 'D2 Rising':
                durations["D2_rising"] += duration_increment
            elif direction == 'D2 Peak':
                durations["D2_peak"] += duration_increment
            elif direction == 'D2 Falling':
                durations["D2_falling"] += duration_increment
            elif direction == 'D2 Catch':
                durations["D2_catch"] += duration_increment
            elif direction == 'D3 Peak':
                durations["D3_peak"] += duration_increment

              # Assign the direction to the row
            transition.at[index, 'Direction'] = direction
            # ---------------- New Snippet Ends Here ----------------

            # Prepare the output text for each row
            output = (
                f"Row {j+1} in Transition {i+1}:\n"
                f"  DateTime: {date_time.strftime('%Y-%m-%d %H:%M')}\n"
                f"  Circuit: {transition.iloc[j]['Circuit']}\n"
                f"  Last Limit: {last_limit}\n"
                f"  Current Limit: {current_limit}\n"
                f"  Next Limit: {next_limit}\n"
                f"  Value: {value}\n"
                f"  Direction: {direction}\n"
            )
            
            # Write the output to the text file
            file.write(output)

            # Update the last timestamp to the current date_time
            last_timestamp = date_time
        
        # Write the durations to the file
        file.write(f"Durations for Transition {i+1}:\n")
        for key, duration in durations.items():
            file.write(f"  Duration at {key}: {duration}\n")


# New Section for Summary Statistics
# Initialize summary statistics
total_transitions = len(transitions)
circuit_transitions = {}
monthly_transitions = {}
daily_transitions = set()

# Loop through each transition to calculate statistics
for transition in transitions:
    # Get the circuit from the first row of the transition
    circuit = transition.iloc[0]['Circuit']
    circuit_transitions[circuit] = circuit_transitions.get(circuit, 0) + 1
    
    # Get the month from the first row of the transition
    month = transition.iloc[0]['Month']
    monthly_transitions[month] = monthly_transitions.get(month, 0) + 1
    
    # Add the days to the set of daily transitions
    for _, row in transition.iterrows():
        day = (row['Month'], row['Day'])  # Tuple of (Month, Day)
        daily_transitions.add(day)

# Summation of days with at least 1 transition in each month
days_with_transitions_per_month = {month: 0 for month in monthly_transitions.keys()}
for month, count in monthly_transitions.items():
    days_with_transitions_per_month[month] = len(set(day for (m, d) in daily_transitions if m == month))

# Total unique days with at least one transition
total_unique_days_with_transitions = len(daily_transitions)

# Write summary statistics to the same text file
with open('transition_limits_report.txt', 'a') as file:  # Append mode
    file.write("\n--- Summary Statistics ---\n")
    file.write(f"Total Transitions: {total_transitions}\n")
    file.write("Transitions by Circuit:\n")
    for circuit, count in circuit_transitions.items():
        file.write(f"  {circuit}: {count}\n")
    file.write("Monthly Transitions:\n")
    for month, count in monthly_transitions.items():
        file.write(f"  Month {month}: {count}\n")
    file.write("Days with at least 1 Transition in Each Month:\n")
    for month, count in days_with_transitions_per_month.items():
        file.write(f"  Month {month}: {count} days\n")
    file.write(f"Total Unique Days with Transitions: {total_unique_days_with_transitions}\n")


# Initialize dictionaries to store total durations and counts
day_durations = {}
month_durations = {}
overall_durations = {'D1 Peak': 0, 'D1 Rising': 0, 'D1 Falling': 0, 'D1 Catch': 0,
                     'D2 Peak': 0, 'D2 Rising': 0, 'D2 Falling': 0, 'D2 Catch': 0,
                     'D3 Peak': 0, 'Total Count': 0}

# Loop through each transition to calculate statistics
for transition in transitions:
    # Get the date (unique day) and month
    day = (transition.iloc[0]['Month'], transition.iloc[0]['Day'])
    month = transition.iloc[0]['Month']
    
    # Initialize day and month keys if they don't exist
    if day not in day_durations:
        day_durations[day] = {'D1 Peak': 0, 'D1 Rising': 0, 'D1 Falling': 0, 'D1 Catch': 0,
                              'D2 Peak': 0, 'D2 Rising': 0, 'D2 Falling': 0, 'D2 Catch': 0,
                              'D3 Peak': 0, 'Count': 0}
    if month not in month_durations:
        month_durations[month] = {'D1 Peak': 0, 'D1 Rising': 0, 'D1 Falling': 0, 'D1 Catch': 0,
                                  'D2 Peak': 0, 'D2 Rising': 0, 'D2 Falling': 0, 'D2 Catch': 0,
                                  'D3 Peak': 0, 'Count': 0}
    
    # Iterate over each row in the transition and update durations for the day, month, and overall
    for index, row in transition.iterrows():
        direction = row['Direction']
        duration = 15  # Each occurrence counts for 15 minutes
        
        # Update day, month, and overall durations based on the direction
        if direction in day_durations[day]:
            day_durations[day][direction] += duration
            day_durations[day]['Count'] += 1
        if direction in month_durations[month]:
            month_durations[month][direction] += duration
            month_durations[month]['Count'] += 1
        if direction in overall_durations:
            overall_durations[direction] += duration
            overall_durations['Total Count'] += 1

# Calculate averages for each unique day, month, and overall
def calculate_averages(durations_dict):
    averages = {}
    for key, value in durations_dict.items():
        averages[key] = {}
        for transition, total_duration in value.items():
            if transition != 'Count':
                avg_duration = total_duration / value['Count'] if value['Count'] > 0 else 0
                averages[key][transition] = avg_duration
    return averages

# Calculate averages for unique days, months, and overall
day_averages = calculate_averages(day_durations)
month_averages = calculate_averages(month_durations)
overall_averages = {k: (v / overall_durations['Total Count'] if overall_durations['Total Count'] > 0 else 0)
                    for k, v in overall_durations.items() if k != 'Total Count'}

# Write the average statistics to the text file
with open('transition_limits_report.txt', 'a') as file:  # Append mode
    file.write("\n--- Average Durations ---\n")
    
    # Averages per unique day
    file.write("\nAverage Duration per Unique Day:\n")
    for day, averages in day_averages.items():
        file.write(f"  Day {day}: {averages}\n")
    
    # Averages per month
    file.write("\nAverage Duration per Month:\n")
    for month, averages in month_averages.items():
        file.write(f"  Month {month}: {averages}\n")
    
    # Overall averages
    file.write("\nOverall Average Durations:\n")
    for transition, avg_duration in overall_averages.items():
        file.write(f"  {transition}: {avg_duration:.2f} minutes\n")
