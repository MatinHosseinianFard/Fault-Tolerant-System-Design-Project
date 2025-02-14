import pandas as pd
import numpy as np
import re
import os

# Function for natural sorting (extracts numbers from filenames)
def natural_sort_key(s):
    return [int(text) if text.isdigit() else text.lower() for text in re.split(r'(\d+)', s)]

# Function to compute the integral of current over a sliding window using the trapezoidal rule
def compute_integral_in_windows(df, current_col, time_col, window_size):
    current = df[current_col].to_numpy()
    time = df[time_col].to_numpy()
    integrals = np.full(len(df), np.nan)

    # Calculate the integral for each valid window
    for i in range(len(df)):
        if i >= window_size - 1:
            time_window = time[i - window_size + 1:i + 1]
            current_window = current[i - window_size + 1:i + 1]
            time_diff = np.diff(time_window)
            integrals[i] = np.sum(current_window[:-1] * time_diff)  # Trapezoidal rule
    return pd.Series(integrals, index=df.index, name=f"Integral_{current_col}")

# Function to process a single file
def process_file(file_path, sequence_length, output_folder, dataset_type):
    output_path = os.path.join(output_folder, os.path.basename(file_path))
    
    # Skip processing if the output file already exists
    if os.path.exists(output_path):
        print(f"Output already exists for {file_path}. Skipping processing.")
        return pd.read_excel(output_path)
    
    try:
        df = pd.read_excel(file_path)
        if dataset_type == 'train':
            df = df.iloc[:len(df) // 1]
        elif dataset_type == 'test':
            df = df.iloc[:len(df) // 1]
    except Exception as e:
        raise ValueError(f"Error reading {file_path}: {e}")
    
    print(f"Processing file: {file_path}")
    print("Columns found:", df.columns.tolist())
    
    required_columns = ['Current_measured (Amps)', 'Time (secs)', 'Voltage_measured (Volts)', 'Temperature_measured (C)', 'Ambient_temperature (C)']
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        raise KeyError(f"Missing columns in {file_path}: {missing_columns}")
    
    # Calculate additional features
    df['Integrated_Current_Window'] = compute_integral_in_windows(
        df,
        current_col='Current_measured (Amps)',
        time_col='Time (secs)',
        window_size=sequence_length
    )
    df['Moving_Average_Voltage'] = df['Voltage_measured (Volts)'].rolling(window=sequence_length).mean()
    df['Moving_Average_Current'] = df['Current_measured (Amps)'].rolling(window=sequence_length).mean()
    df['Moving_Average_Integrated_Current'] = df['Integrated_Current_Window'].rolling(window=sequence_length).mean()

    # Calculate delta temperature
    df['Delta_Temperature'] = df['Temperature_measured (C)'] - df['Ambient_temperature (C)']

    # Drop rows with NaNs
    initial_shape = df.shape
    df.dropna(inplace=True)
    final_shape = df.shape
    print(f"Dropped {initial_shape[0] - final_shape[0]} rows due to NaNs.")
    
    # Save the processed file
    output_path = os.path.join(output_folder, os.path.basename(file_path))
    os.makedirs(output_folder, exist_ok=True)
    df.to_excel(output_path, index=False)
    print(f"Processed file saved to: {output_path}")
    return df

# Function to process all files in a list of folders
def process_all_files_in_folders(folder_paths, sequence_length, dataset_type='train'):
    processed_data_list = []
    
    for folder_path in folder_paths:
        print(f"Processing folder: {folder_path}")
        files = [file for file in os.listdir(folder_path)
                 if file.endswith('.xlsx') and 'impedance' not in file.lower()]
        files.sort(key=natural_sort_key)
        
        output_folder = os.path.join(folder_path, "changed")
        
        for file in files:
            file_path = os.path.join(folder_path, file)
            try:
                processed_df = process_file(file_path, sequence_length, output_folder, dataset_type)
                processed_data_list.append(processed_df)
            except KeyError as e:
                print(f"KeyError while processing {file}: {e}")
            except Exception as e:
                print(f"Error while processing {file}: {e}")
                
    if processed_data_list:
        concatenated_df = pd.concat(processed_data_list, ignore_index=True)
        print(f"Concatenated {dataset_type} data shape: {concatenated_df.shape}")
        return concatenated_df
    else:
        raise ValueError(f"No {dataset_type} data was processed successfully.")

# Define the sequence length
sequence_length = 30

# List of training folder paths
train_folder_paths = [
    "D:/Uni/Master's/Term1/Fault-Tolerant System Design/Assignments/Replication/code/Dataset1/5. Battery Data Set/B0030/csv/combined",
    "D:/Uni/Master's/Term1/Fault-Tolerant System Design/Assignments/Replication/code/Dataset1/5. Battery Data Set/B0031/csv/combined",
    "D:/Uni/Master's/Term1/Fault-Tolerant System Design/Assignments/Replication/code/Dataset1/5. Battery Data Set/B0032/csv/combined",
]

# Test folder path
test_folder_path = [
    "D:/Uni/Master's/Term1/Fault-Tolerant System Design/Assignments/Replication/code/Dataset1/5. Battery Data Set/B0029/csv/combined",
]

# Process training data
print("Processing Training Data...")
process_all_files_in_folders(train_folder_paths, sequence_length, dataset_type='train')

# Process testing data
print("\nProcessing Testing Data...")
process_all_files_in_folders(test_folder_path, sequence_length, dataset_type='test')
