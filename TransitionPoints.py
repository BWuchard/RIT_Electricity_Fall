import pandas as pd
import numpy as np

def process_transitions(filename, sheet_names, column_name, include_demand_limit=False, include_synced_demand=False):
    """
    Process Excel sheets to identify transitions for a specific column.
    
    Args:
        filename (str): Path to the Excel file
        sheet_names (list): List of sheet names to process
        column_name (str): Name of column to analyze for transitions
        include_demand_limit (bool): Whether to include DemandLimit in transition type
        include_synced_demand (bool): Whether to include SyncedDemandLimit in transition type
    
    Returns:
        tuple: (transitions_df, summary_df) containing the detailed transitions and summary analysis
    """
    all_transitions = []
    overall_transition_count = 1  # Global counter for all transitions
    
    for sheet in sheet_names:
        # Read the sheet
        df = pd.read_excel(filename, sheet_name=sheet)
        
        # Create a mask for where the specified column changes
        transitions = df[column_name] != df[column_name].shift()
        
        # Get indices where transitions occur
        transition_indices = transitions[transitions].index.tolist()
        
        # Keep track of transition number within each sheet
        sheet_transition_count = 1
        
        # Process each transition
        for idx in transition_indices:
            # First, check if we have enough points before and after
            if idx < 2 or idx >= len(df) - 1:
                continue
                
            # Get all potential rows for this transition
            pre_context_idx = idx - 2
            from_idx = idx - 1
            to_idx = idx
            post_context_idx = idx + 1
            
            # Validate demand limit matching for context points
            context_valid = True
            
            # Check if the pre-context point matches the 'from' transition point
            if pre_context_idx >= 0:
                pre_context_demand = df.iloc[pre_context_idx][column_name]
                from_demand = df.iloc[from_idx][column_name]
                if pre_context_demand != from_demand:
                    context_valid = False
            
            # Check if the post-context point matches the 'to' transition point
            if post_context_idx < len(df):
                post_context_demand = df.iloc[post_context_idx][column_name]
                to_demand = df.iloc[to_idx][column_name]
                if post_context_demand != to_demand:
                    context_valid = False
            
            # Only process if context is valid
            if context_valid:
                # Get the rows and add sheet name for reference
                rows_to_include = [pre_context_idx, from_idx, to_idx, post_context_idx]
                transition_rows = df.iloc[rows_to_include].copy()
                transition_rows['Sheet'] = sheet
                
                # Add transition type and numbers
                from_value = df.iloc[from_idx][column_name]
                to_value = df.iloc[to_idx][column_name]
                
                if include_demand_limit:
                    # Include both SyncedDemandLimit and DemandLimit in transition type
                    from_demand = df.iloc[from_idx]['DemandLimit']
                    to_demand = df.iloc[to_idx]['DemandLimit']
                    
                    # Check if SyncedDemandLimit matches DemandLimit at start and end points
                    from_match = "Matches" if from_value == from_demand else "Different"
                    to_match = "Matches" if to_value == to_demand else "Different"
                    
                    transition_type = f"Synced:{from_value}->{to_value} [DL:{from_demand}->{to_demand}] (DL Status: {from_match}->{to_match})"
                
                elif include_synced_demand:
                    # Include both DemandLimit and SyncedDemandLimit in transition type
                    from_synced = df.iloc[from_idx]['SyncedDemandLimit']
                    to_synced = df.iloc[to_idx]['SyncedDemandLimit']
                    
                    # Check if DemandLimit matches SyncedDemandLimit at start and end points
                    from_match = "Matches" if from_value == from_synced else "Different"
                    to_match = "Matches" if to_value == to_synced else "Different"
                    
                    transition_type = f"DL:{from_value}->{to_value} [Synced:{from_synced}->{to_synced}] (Synced Status: {from_match}->{to_match})"
                
                else:
                    transition_type = f"{from_value} to {to_value}"
                
                # Add row markers and transition info
                transition_rows['RowType'] = ['Context Row', 'Transition From', 'Transition To', 'Context Row']
                transition_rows['TransitionType'] = transition_type
                transition_rows['GlobalTransitionNumber'] = overall_transition_count
                transition_rows['SheetTransitionNumber'] = sheet_transition_count
                
                sheet_transition_count += 1
                overall_transition_count += 1
                
                all_transitions.append(transition_rows)
    
    # Combine all transitions into a single dataframe
    if all_transitions:
        result_df = pd.concat(all_transitions, ignore_index=True)
        
        # Sort by Sheet and Date
        sort_columns = ['Sheet']
        if 'Date' in result_df.columns:
            sort_columns.append('Date')
        result_df.sort_values(sort_columns, inplace=True)
        
        # Create summary dataframe with rate of change analysis
        summary_data = []
        
        for transition_num in result_df['GlobalTransitionNumber'].unique():
            transition_data = result_df[result_df['GlobalTransitionNumber'] == transition_num]
            
            # Get transition rows only
            from_row = transition_data[transition_data['RowType'] == 'Transition From']
            to_row = transition_data[transition_data['RowType'] == 'Transition To']
            
            # Only process if we have both transition rows
            if not from_row.empty and not to_row.empty:
                first_value = from_row['Value'].values[0] if 'Value' in from_row.columns else None
                last_value = to_row['Value'].values[0] if 'Value' in to_row.columns else None
                
                # Calculate changes only if we have valid values
                if first_value is not None and last_value is not None:
                    absolute_change = last_value - first_value
                    rate_of_change = absolute_change / 15  # Rate of change per minute
                    percent_change = (absolute_change / first_value) * 100 if first_value != 0 else float('inf')
                else:
                    absolute_change = None
                    rate_of_change = None
                    percent_change = None
                
                # Get demand limit values if needed
                if include_demand_limit:
                    from_dl = from_row['DemandLimit'].iloc[0]
                    to_dl = to_row['DemandLimit'].iloc[0]
                elif include_synced_demand:
                    from_dl = from_row['SyncedDemandLimit'].iloc[0]
                    to_dl = to_row['SyncedDemandLimit'].iloc[0]
                else:
                    from_dl = to_dl = None
                
                summary_data.append({
                    'GlobalTransitionNumber': transition_num,
                    'Month': transition_data['Sheet'].iloc[0],
                    'Circuit': transition_data['Circuit'].iloc[0] if 'Circuit' in transition_data.columns else None,
                    'StartDate': from_row['Date'].iloc[0] if 'Date' in from_row.columns else None,
                    'EndDate': to_row['Date'].iloc[0] if 'Date' in to_row.columns else None,
                    'TransitionType': transition_data['TransitionType'].iloc[0],
                    'StartValue': first_value,
                    'EndValue': last_value,
                    'FromDemandLimit': from_dl if include_demand_limit or include_synced_demand else None,
                    'ToDemandLimit': to_dl if include_demand_limit or include_synced_demand else None,
                    'AbsoluteChange': absolute_change,
                    'RateOfChange': rate_of_change,
                    'PercentChange': percent_change
                })
        
        summary_df = pd.DataFrame(summary_data)
        return result_df, summary_df
    else:
        return pd.DataFrame(), pd.DataFrame()

def split_summary_by_change(summary_df, sheet_prefix):
    """
    Split a summary DataFrame into positive and negative changes.
    
    Args:
        summary_df (pd.DataFrame): Summary DataFrame to split
        sheet_prefix (str): Prefix for sheet names
    
    Returns:
        tuple: (positive_df, negative_df)
    """
    if not summary_df.empty:
        positive_df = summary_df[summary_df['RateOfChange'] > 0].copy()
        negative_df = summary_df[summary_df['RateOfChange'] < 0].copy()
        
        # Sort both DataFrames by rate of change magnitude
        if not positive_df.empty:
            positive_df = positive_df.sort_values('RateOfChange', ascending=False)
        if not negative_df.empty:
            negative_df = negative_df.sort_values('RateOfChange', ascending=True)
            
        return positive_df, negative_df
    return pd.DataFrame(), pd.DataFrame()

def save_transitions(input_file, output_file):
    """
    Process the input Excel file and save transitions to a new Excel file with multiple sheets.
    """
    # Define sheet names
    sheets = ["April", "May", "June", "July", "August", "September", "October"]
    
    try:
        # Process all types of transitions
        # Original analyses
        demand_transitions_df, demand_summary_df = process_transitions(
            input_file, sheets, 'DemandLimit')
        synced_transitions_df, synced_summary_df = process_transitions(
            input_file, sheets, 'SyncedDemandLimit')
        combined_transitions_df, combined_summary_df = process_transitions(
            input_file, sheets, 'SyncedDemandLimit', include_demand_limit=True)
        
        # New analysis: DemandLimit transitions with SyncedDemandLimit matching
        reverse_combined_transitions_df, reverse_combined_summary_df = process_transitions(
            input_file, sheets, 'DemandLimit', include_synced_demand=True)
        
        # Split summaries into positive and negative changes
        demand_pos, demand_neg = split_summary_by_change(demand_summary_df, "Demand")
        synced_pos, synced_neg = split_summary_by_change(synced_summary_df, "Synced")
        combined_pos, combined_neg = split_summary_by_change(combined_summary_df, "Combined")
        reverse_combined_pos, reverse_combined_neg = split_summary_by_change(reverse_combined_summary_df, "ReverseCombined")
        
        # Save to new Excel file with multiple sheets
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            # Original transition sheets
            if not demand_transitions_df.empty:
                demand_transitions_df.to_excel(writer, sheet_name='Demand Transitions', index=False)
            if not synced_transitions_df.empty:
                synced_transitions_df.to_excel(writer, sheet_name='Synced Transitions', index=False)
            if not combined_transitions_df.empty:
                combined_transitions_df.to_excel(writer, sheet_name='Combined Transitions', index=False)
            # New transition sheets
            if not reverse_combined_transitions_df.empty:
                reverse_combined_transitions_df.to_excel(writer, sheet_name='DemandLimit Based Transitions', index=False)
            
            # Original summaries
            if not demand_pos.empty:
                demand_pos.to_excel(writer, sheet_name='Demand Summary (Positive)', index=False)
            if not demand_neg.empty:
                demand_neg.to_excel(writer, sheet_name='Demand Summary (Negative)', index=False)
            if not synced_pos.empty:
                synced_pos.to_excel(writer, sheet_name='Synced Summary (Positive)', index=False)
            if not synced_neg.empty:
                synced_neg.to_excel(writer, sheet_name='Synced Summary (Negative)', index=False)
            if not combined_pos.empty:
                combined_pos.to_excel(writer, sheet_name='Combined Summary (Positive)', index=False)
            if not combined_neg.empty:
                combined_neg.to_excel(writer, sheet_name='Combined Summary (Negative)', index=False)
                
            # New summaries
            if not reverse_combined_pos.empty:
                reverse_combined_pos.to_excel(writer, sheet_name='DemandLimit Summary (Positive)', index=False)
            if not reverse_combined_neg.empty:
                reverse_combined_neg.to_excel(writer, sheet_name='DemandLimit Summary (Negative)', index=False)

        print(f"Successfully saved transitions and analysis to {output_file}")
        
        # Print summaries for all types
        for transition_type, df, pos_df, neg_df in [
            ("DemandLimit", demand_transitions_df, demand_pos, demand_neg),
            ("SyncedDemandLimit", synced_transitions_df, synced_pos, synced_neg),
            ("Combined", combined_transitions_df, combined_pos, combined_neg),
            ("DemandLimit Based", reverse_combined_transitions_df, reverse_combined_pos, reverse_combined_neg)
        ]:
            if not df.empty:
                total_transitions = df['GlobalTransitionNumber'].nunique()
                print(f"\nTotal {transition_type} transitions: {total_transitions}")
                print(f"  Positive changes: {len(pos_df)}")
                print(f"  Negative changes: {len(neg_df)}")
                
                print(f"\n{transition_type} transitions by sheet:")
                for sheet in sheets:
                    sheet_data = df[df['Sheet'] == sheet]
                    sheet_transitions = sheet_data['SheetTransitionNumber'].nunique()
                    if sheet_transitions > 0:
                        print(f"\n{sheet}: {sheet_transitions} transitions")
                        transition_types = sheet_data[sheet_data['RowType'].isin(['Transition From', 'Transition To'])]['TransitionType'].unique()
                        for t_type in sorted(transition_types):
                            print(f"  - {t_type}")
            else:
                print(f"\nNo {transition_type} transitions found")
            
    except FileNotFoundError:
        print(f"Error: Could not find the input file {input_file}")
    except Exception as e:
        print(f"Error processing file: {str(e)}")
        print("Full error details:")
        import traceback
        traceback.print_exc()

# Example usage
if __name__ == "__main__":
    input_file = "ATestByMonth.xlsx"
    output_file = "DemandTransitions.xlsx"
    save_transitions(input_file, output_file)
