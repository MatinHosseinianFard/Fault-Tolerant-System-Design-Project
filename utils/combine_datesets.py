import pandas as pd
import os
import re

# Function for natural sorting (extracts numbers from filenames)
def natural_sort_key(s):
    return [int(text) if text.isdigit() else text.lower() for text in re.split(r'(\d+)', s)]


def combine(folder_path):
    
    # Create the "combined" folder if it doesn't exist
    combined_folder_path = os.path.join(folder_path, 'combined')
    os.makedirs(combined_folder_path, exist_ok=True)
    
    # List all CSV files in the folder
    csv_files = [file for file in os.listdir(folder_path) if file.endswith('.csv')]

    # Sort files using the natural sorting function
    csv_files.sort(key=natural_sort_key)

    # Specify the required columns
    required_columns = ['Voltage_measured (Volts)', 'Current_measured (Amps)', 
                        'Temperature_measured (C)', 'Time (secs)', 'Ambient_temperature (C)']

    # Create an empty list to hold data for each segment
    combined_data = []
    file_counter = 1  # Counter for naming the output files

    for file in csv_files:
        file_path = os.path.join(folder_path, file)
        
        if 'impedance' in file.lower():
            # Save the current combined data into a new Excel file
            if combined_data:
                output_path = os.path.join(folder_path, f'combined/Combined_Output_{file_counter}.xlsx')
                final_df = pd.concat(combined_data, ignore_index=True)
                final_df.to_excel(output_path, index=False, engine='openpyxl')
                print(f"Segment saved to: {output_path}")
                file_counter += 1
                combined_data = []  # Reset the data list for the next segment
            
            print(f"Skipped impedance file: {file}")
            continue

        try:
            # Load the data and append it to the current segment
            df = pd.read_csv(file_path, usecols=required_columns)  # Only load specific columns
            df['Source_File'] = file  # Add a column to track the source file name
            combined_data.append(df)
            print(f"Successfully processed: {file}")
        except ValueError as ve:
            print(f"Skipped {file} due to missing required columns: {ve}")
        except Exception as e:
            print(f"Error reading {file}: {e}")

    # Save the last segment if any data remains
    if combined_data:
        output_path = os.path.join(folder_path, f'Combined_Output_{file_counter}.xlsx')
        final_df = pd.concat(combined_data, ignore_index=True)
        final_df.to_excel(output_path, index=False, engine='openpyxl')
        print(f"Final segment saved to: {output_path}")


# Specify the folder path where CSV files are located
folder_paths = [
    "D:/Uni/Master's/Term1/Fault-Tolerant System Design/Assignments/Replication/code/Dataset1/5. Battery Data Set/B0029/csv/",
    "D:/Uni/Master's/Term1/Fault-Tolerant System Design/Assignments/Replication/code/Dataset1/5. Battery Data Set/B0030/csv/",
    "D:/Uni/Master's/Term1/Fault-Tolerant System Design/Assignments/Replication/code/Dataset1/5. Battery Data Set/B0031/csv/",
    "D:/Uni/Master's/Term1/Fault-Tolerant System Design/Assignments/Replication/code/Dataset1/5. Battery Data Set/B0032/csv/",
]

# Process each folder
for folder_path in folder_paths:
    combine(folder_path)
