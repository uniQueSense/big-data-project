from data_processing import load_samples, clean_data
from pyspark.sql import SparkSession

def main():
    spark = SparkSession.builder.appName("Spotify Data Sample").getOrCreate()

    path = '../data/spotify_data.csv'

    sample_df = load_samples(path, rows=50000)

    sample_df.show(20)

    cleaned_sample_df = clean_data(sample_df)

    cleaned_sample_df.show(20)

    spark.stop()


if __name__ == '__main__':
    main()