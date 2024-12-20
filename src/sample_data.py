import pandas as pd
import os

def sample_csv(input_csv: str, output_csv: str, sample_size_mb: int = 100, chunk_size: int = 10000):
    """
    Takes a sample from a large CSV file to create a smaller file of approximately the specified size.

    Args:
        input_csv (str): Path to the input CSV file.
        output_csv (str): Path to the output CSV file.
        sample_size_mb (int): Target size of the sample in megabytes. Defaults to 100MB.
        chunk_size (int): Number of rows to read at a time. Adjust based on memory capacity.
    """
    target_size_bytes = sample_size_mb * 1024 * 1024
    sampled_rows = []
    total_size = 0
    header_written = False

    try:
        # Read the input file in chunks
        for chunk in pd.read_csv(input_csv, chunksize=chunk_size):
            # Append rows from the chunk to the sampled list
            sampled_rows.append(chunk)
            
            # Calculate approximate size of the sampled data
            total_size += chunk.memory_usage(deep=True).sum()
            
            # Check if we've reached the target size
            if total_size >= target_size_bytes:
                break

        # Concatenate all sampled rows
        sample_df = pd.concat(sampled_rows)
        
        # Write the sampled data to the output file
        sample_df.to_csv(output_csv, index=False)
        print(f"Sampled {len(sample_df)} rows into {output_csv} (~{sample_size_mb}MB)")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    # Example usage
    input_file = "./kaggle_spotify.csv"  # Replace with your large CSV file
    output_file = "./sampled_output.csv"  # Replace with your desired output CSV file
    target_size = 100  # Target size in MB
    
    sample_csv(input_file, output_file, sample_size_mb=target_size)
