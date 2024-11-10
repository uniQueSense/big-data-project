from src.data_processing import load_data, clean_data, load_samples
from src.visualization import plot_top_tracks

def run_pipeline():
    # df = load_data('data/spotify_data.csv')
    df = load_samples('../data/spotify_data.csv', 1000)
    # print(df.to_string(index=False))
    df_cleaned = clean_data(df)

    plot_top_tracks(df_cleaned)

if __name__ == '__main__':
    run_pipeline()