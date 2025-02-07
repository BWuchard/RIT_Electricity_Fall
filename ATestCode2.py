import pandas as pd

# Load the CSV file with low_memory set to False to avoid dtype warnings
df = pd.read_csv('ATest.csv', low_memory=False)

# Sort the dataframe by Year, Month, Day, Hour, Minute
df = df.sort_values(by=['Year', 'Month', 'Day', 'Hour', 'Minute'])

# Initialize dictionaries to store daily reports by circuit
daily_reports = {}

# Loop through the dataframe, row by row
for index, row in df.iterrows():
    current_limit = row['DemandLimit']
    circuit = row['Circuit']
    
    # Extract the date components directly, converting to integers
    date = (int(row['Year']), int(row['Month']), int(row['Day']))
    
    # Extract the time components
    start_time = f"{int(row['Hour']):02d}:{int(row['Minute']):02d}"

    # Initialize daily report for the date and circuit if not present
    if (date, circuit) not in daily_reports:
        daily_reports[(date, circuit)] = {
            'reports': [],
            'total_transitions': [],
            'd1_count': 0,
            'd2_count': 0,
            'd3_count': 0,
            'last_limit': None,
            'current_duration': 0,
            'start_time': None,
            'd1_total_duration': 0,
            'd2_total_duration': 0,
            'd3_total_duration': 0,
        }

    # Only consider rows where the current_limit is not D0
    if current_limit != 'D0':
        # If the limit changes from the last recorded limit
        if daily_reports[(date, circuit)]['last_limit'] != current_limit:
            # Record the transition if we have a last limit
            if daily_reports[(date, circuit)]['last_limit'] is not None:
                # Log the duration of the last limit before transitioning
                end_time = f"{int(row['Hour']):02d}:{int(row['Minute']):02d}"
                transition_report = (
                    f"{date[0]}-{date[1]:02d}-{date[2]:02d} Circuit {circuit} "
                    f"{daily_reports[(date, circuit)]['last_limit']} Duration: "
                    f"{daily_reports[(date, circuit)]['current_duration']} minutes "
                    f"Start Time: {daily_reports[(date, circuit)]['start_time']} "
                    f"End Time: {end_time}"
                )
                daily_reports[(date, circuit)]['reports'].append(transition_report)
                daily_reports[(date, circuit)]['total_transitions'].append(daily_reports[(date, circuit)]['last_limit'])

                # Increment the respective count for the last limit
                if daily_reports[(date, circuit)]['last_limit'] == 'D1':
                    daily_reports[(date, circuit)]['d1_count'] += 1
                    daily_reports[(date, circuit)]['d1_total_duration'] += daily_reports[(date, circuit)]['current_duration']
                elif daily_reports[(date, circuit)]['last_limit'] == 'D2':
                    daily_reports[(date, circuit)]['d2_count'] += 1
                    daily_reports[(date, circuit)]['d2_total_duration'] += daily_reports[(date, circuit)]['current_duration']
                elif daily_reports[(date, circuit)]['last_limit'] == 'D3':
                    daily_reports[(date, circuit)]['d3_count'] += 1
                    daily_reports[(date, circuit)]['d3_total_duration'] += daily_reports[(date, circuit)]['current_duration']

            # Reset the current duration for the new limit
            daily_reports[(date, circuit)]['current_duration'] = 15  # Start with 15 minutes for the first occurrence
            daily_reports[(date, circuit)]['start_time'] = start_time  # Update start time for new limit
        else:
            # If we stay at the same limit, just increment the duration
            daily_reports[(date, circuit)]['current_duration'] += 15  # Add 15 minutes for each occurrence

        # Update the last_limit
        daily_reports[(date, circuit)]['last_limit'] = current_limit

# Write the daily reports to a text file, including the circuit
with open('daily_demand_report.txt', 'w') as file:
    file.write("--- Daily Demand Report by Circuit ---\n")
    
    for (date, circuit), report_data in daily_reports.items():
        # Only report if there are actual transitions logged
        if report_data['reports']:
            # Write individual limit durations
            for limit in report_data['reports']:
                file.write(f"{limit}\n")
            
            # Calculate average durations for D1, D2, D3
            avg_d1 = (report_data['d1_total_duration'] / report_data['d1_count']) if report_data['d1_count'] > 0 else 0
            avg_d2 = (report_data['d2_total_duration'] / report_data['d2_count']) if report_data['d2_count'] > 0 else 0
            avg_d3 = (report_data['d3_total_duration'] / report_data['d3_count']) if report_data['d3_count'] > 0 else 0
            
            # Write the averages to the report
            file.write(f"Date: {date[0]}-{date[1]:02d}-{date[2]:02d}, Circuit: {circuit}\n")
            file.write(f"  Total Transitions: {len(report_data['total_transitions'])}\n")
            file.write(f"  D1 Transitions: {report_data['d1_count']} (Avg: {avg_d1:.2f} minutes)\n")
            file.write(f"  D2 Transitions: {report_data['d2_count']} (Avg: {avg_d2:.2f} minutes)\n")
            file.write(f"  D3 Transitions: {report_data['d3_count']} (Avg: {avg_d3:.2f} minutes)\n")
            file.write(f"  Transitions: {', '.join(report_data['total_transitions'])}\n")
            file.write("\n")


# Assuming daily_reports is already defined from the previous code
# Initialize a dictionary for cumulative statistics
cumulative_stats = {
    'days_with_limits': {},  # Track the number of days limits were hit
    'monthly_days': {},       # Track all days in each month with limits hit
    'monthly_transitions': {}, # Track sum number of transition occurrences
    'd1_total_time': {},      # Total time at D1 for each month and circuit
    'd2_total_time': {},      # Total time at D2 for each month and circuit
    'd1_count': {},           # Count occurrences at D1 for each month and circuit
    'd2_count': {},           # Count occurrences at D2 for each month and circuit
    'd3_total_time': {},      # Total time at D3 for each month and circuit
    'd3_count': {}            # Count occurrences at D3 for each month and circuit
}

# Loop through the daily reports to gather cumulative statistics
for (date, circuit), report_data in daily_reports.items():
    # Extract month and year
    month = f"{date[0]}-{date[1]:02d}"  # Format as "YYYY-MM"

    # Only consider days where the current_limit is not D0
    if report_data['d1_count'] > 0 or report_data['d2_count'] > 0 or report_data['d3_count'] > 0:
        # Count unique days where demand limits were hit
        if circuit not in cumulative_stats['days_with_limits']:
            cumulative_stats['days_with_limits'][circuit] = 0
        cumulative_stats['days_with_limits'][circuit] += 1  # Increment for a day with limits hit

        # Track all days in each month that a demand limit was hit
        if month not in cumulative_stats['monthly_days']:
            cumulative_stats['monthly_days'][month] = {}
        if circuit not in cumulative_stats['monthly_days'][month]:
            cumulative_stats['monthly_days'][month][circuit] = []
        cumulative_stats['monthly_days'][month][circuit].append(f"{date[0]}-{date[1]:02d}-{date[2]:02d}")

    # Track monthly transitions
    if month not in cumulative_stats['monthly_transitions']:
        cumulative_stats['monthly_transitions'][month] = {}
    if circuit not in cumulative_stats['monthly_transitions'][month]:
        cumulative_stats['monthly_transitions'][month][circuit] = 0
    cumulative_stats['monthly_transitions'][month][circuit] += (report_data['d1_count'] + report_data['d2_count'] + report_data['d3_count'])

    # Track total time at D1
    if month not in cumulative_stats['d1_total_time']:
        cumulative_stats['d1_total_time'][month] = {}
    if circuit not in cumulative_stats['d1_total_time'][month]:
        cumulative_stats['d1_total_time'][month][circuit] = 0
    cumulative_stats['d1_total_time'][month][circuit] += report_data['d1_total_duration']
    
    # Track total time at D2
    if month not in cumulative_stats['d2_total_time']:
        cumulative_stats['d2_total_time'][month] = {}
    if circuit not in cumulative_stats['d2_total_time'][month]:
        cumulative_stats['d2_total_time'][month][circuit] = 0
    cumulative_stats['d2_total_time'][month][circuit] += report_data['d2_total_duration']
    
    # Track occurrences at D1
    if month not in cumulative_stats['d1_count']:
        cumulative_stats['d1_count'][month] = {}
    if circuit not in cumulative_stats['d1_count'][month]:
        cumulative_stats['d1_count'][month][circuit] = 0
    cumulative_stats['d1_count'][month][circuit] += report_data['d1_count']
    
    # Track occurrences at D2
    if month not in cumulative_stats['d2_count']:
        cumulative_stats['d2_count'][month] = {}
    if circuit not in cumulative_stats['d2_count'][month]:
        cumulative_stats['d2_count'][month][circuit] = 0
    cumulative_stats['d2_count'][month][circuit] += report_data['d2_count']
    
    # Track total time at D3
    if month not in cumulative_stats['d3_total_time']:
        cumulative_stats['d3_total_time'][month] = {}
    if circuit not in cumulative_stats['d3_total_time'][month]:
        cumulative_stats['d3_total_time'][month][circuit] = 0
    cumulative_stats['d3_total_time'][month][circuit] += report_data['d3_total_duration']
    
    # Track occurrences at D3
    if month not in cumulative_stats['d3_count']:
        cumulative_stats['d3_count'][month] = {}
    if circuit not in cumulative_stats['d3_count'][month]:
        cumulative_stats['d3_count'][month][circuit] = 0
    cumulative_stats['d3_count'][month][circuit] += report_data['d3_count']

# Generate a report file for cumulative statistics
with open('cumulative_demand_statistics.txt', 'w') as file:
    file.write("--- Cumulative Demand Statistics ---\n")

    # Report the number of days that a demand limit was hit, and for which circuit
    file.write("Number of Days Demand Limit was Hit:\n")
    for circuit, days in cumulative_stats['days_with_limits'].items():
        file.write(f"  Circuit {circuit}: {days} days\n")

    # Report all days in each month that a demand limit was hit and for which circuit
    file.write("\nDays in Each Month that Demand Limit was Hit:\n")
    for month, circuits in cumulative_stats['monthly_days'].items():
        file.write(f"  Month: {month}\n")
        for circuit, days in circuits.items():
            file.write(f"    Circuit {circuit}: {', '.join(days)}\n")

    # Report the sum number of transition occurrences in each month, and for which circuit
    file.write("\nSum Number of Transition Occurrences in Each Month:\n")
    for month, circuits in cumulative_stats['monthly_transitions'].items():
        file.write(f"  Month: {month}\n")
        for circuit, transitions in circuits.items():
            file.write(f"    Circuit {circuit}: {transitions} transitions\n")

    # Report total time at D1 for each month and for each circuit
    file.write("\nTotal Time at D1 for Each Month:\n")
    for month, circuits in cumulative_stats['d1_total_time'].items():
        file.write(f"  Month: {month}\n")
        for circuit, total_time in circuits.items():
            file.write(f"    Circuit {circuit}: {total_time} minutes\n")

    # Report total time at D2 for each month and for each circuit
    file.write("\nTotal Time at D2 for Each Month:\n")
    for month, circuits in cumulative_stats['d2_total_time'].items():
        file.write(f"  Month: {month}\n")
        for circuit, total_time in circuits.items():
            file.write(f"    Circuit {circuit}: {total_time} minutes\n")

    # Calculate and report average time at D1 for each month
    file.write("\nAverage Time at D1 for Each Month:\n")
    for month, circuits in cumulative_stats['d1_total_time'].items():
        file.write(f"  Month: {month}\n")
        for circuit, total_time in circuits.items():
            count = cumulative_stats['d1_count'].get(month, {}).get(circuit, 0)
            avg_time = total_time / count if count > 0 else 0
            file.write(f"    Circuit {circuit}: {avg_time:.2f} minutes\n")

    # Calculate and report average time at D2 for each month
    file.write("\nAverage Time at D2 for Each Month:\n")
    for month, circuits in cumulative_stats['d2_total_time'].items():
        file.write(f"  Month: {month}\n")
        for circuit, total_time in circuits.items():
            count = cumulative_stats['d2_count'].get(month, {}).get(circuit, 0)
            avg_time = total_time / count if count > 0 else 0
            file.write(f"    Circuit {circuit}: {avg_time:.2f} minutes\n")

    # Calculate and report average time at D3 for each month
    file.write("\nAverage Time at D3 for Each Month:\n")
    for month, circuits in cumulative_stats['d3_total_time'].items():
        file.write(f"  Month: {month}\n")
        for circuit, total_time in circuits.items():
            count = cumulative_stats['d3_count'].get(month, {}).get(circuit, 0)
            avg_time = total_time / count if count > 0 else 0
            file.write(f"    Circuit {circuit}: {avg_time:.2f} minutes\n")
