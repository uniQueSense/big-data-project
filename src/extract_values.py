import csv
import pandas as pd
import sys

def extract_unique_values(csv_file, column_name, output_file=None, use_pandas=True):
    """
    Extracts unique values from a specified column in a CSV file.
    
    :param csv_file: Path to the input CSV file.
    :param column_name: Name of the column to extract unique values from.
    :param output_file: Path to save the unique values. If None, values are printed to the console.
    :param use_pandas: Whether to use pandas for processing. If False, use a memory-efficient approach.
    """
    try:
        if use_pandas:
            # Use pandas for fast and convenient processing
            print("Loading CSV with pandas...")
            df = pd.read_csv(csv_file, usecols=[column_name])
            unique_values = df[column_name].drop_duplicates().sort_values()
        else:
            # Use a memory-efficient approach
            print("Processing CSV without pandas...")
            unique_values = set()
            with open(csv_file, mode="r", encoding="utf-8") as file:
                reader = csv.DictReader(file)
                if column_name not in reader.fieldnames:
                    raise ValueError(f"Column '{column_name}' not found in CSV file.")
                for row in reader:
                    unique_values.add(row[column_name])
            unique_values = sorted(unique_values)

        # Output the unique values
        if output_file:
            with open(output_file, mode="w", encoding="utf-8") as file:
                for value in unique_values:
                    file.write(f"{value}\n")
            print(f"Unique values written to {output_file}")
        else:
            print("Unique values:")
            for value in unique_values:
                print(value)

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    csv_file = "./kaggle_spotify.csv"
    column_name = "region"
    output_file = "./countries.txt"

    extract_unique_values(csv_file, column_name, output_file)
