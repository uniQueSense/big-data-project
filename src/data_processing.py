from pyspark.sql import SparkSession
import os


def get_spark_session():
    return SparkSession.builder.appName("Spotify Data Sample").getOrCreate()


def load_data(path):
    if not os.path.exists(path):
        raise FileNotFoundError(f"Plik {path} nie istnieje.")

    spark = get_spark_session()
    return spark.read.csv(path, header=True, inferSchema=True)


def load_samples(path, fraction=None, rows=None):
    df = load_data(path)

    if fraction is not None:
        sample_df = df.sample(fraction=fraction, seed=42)
    elif rows is not None:
        sample_df = df.limit(rows)
    else:
        raise ValueError("podać fraction lub rows.")

    return sample_df


def clean_data(df):
    df_cleaned = df.na.drop()  # usuwanie wierszy z brakującymi wartościami
    df_cleaned = df_cleaned.dropDuplicates()
    return df_cleaned