import os
import pandas as pd

def aggregate_model_results(directory):
    model_results = {}

    # Iterate through each folder in the directory
    for folder_name in os.listdir(directory):
        folder_path = os.path.join(directory, folder_name)
        
        # Check if the path is a directory
        if os.path.isdir(folder_path):
            csv_file_path = os.path.join(folder_path, 'results.csv')
            
            # Check if the results.csv file exists
            if os.path.exists(csv_file_path):
                # Read the CSV file
                df = pd.read_csv(csv_file_path)
                
                # Sort the DataFrame by metrics/mAP50-95(B) in descending order
                df_sorted = df.sort_values(by='metrics/mAP50-95(B)', ascending=False)
                
                # Get the highest metrics/mAP50-95(B) value
                highest_map50_95 = df_sorted.iloc[0]['metrics/mAP50-95(B)']
                
                # Extract model name from folder name
                model_name = '_'.join(folder_name.split('_')[2:-1])
                
                # Store the highest value for this model
                if model_name not in model_results:
                    model_results[model_name] = []
                model_results[model_name].append(highest_map50_95)

    # Calculate the average of the highest metrics/mAP50-95(B) values for each model
    model_averages = {model: sum(values) / len(values) for model, values in model_results.items()}

    # Rank models by average metrics/mAP50-95(B) in descending order
    ranked_models = sorted(model_averages.items(), key=lambda x: x[1], reverse=True)

    # Print the ranked models
    print("Ranked Models by Average metrics/mAP50-95(B):")
    for rank, (model, average) in enumerate(ranked_models, start=1):
        print(f"{rank}. {model}: {average:.4f}")

# Specify the directory containing the model folders
directory_path = r'runs\benchmarks'

# Run the aggregation and ranking
aggregate_model_results(directory_path)
