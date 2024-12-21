import sys
from pyspark.sql import SparkSession
from pyspark.sql.functions import avg, col, max, row_number
from pyspark.sql.window import Window


def process_gold_layer(silver_folder, output_folder, partition_num):
    spark = SparkSession.builder.appName("GoldProcessing").getOrCreate()

    # Wczytanie danych z warstwy Silver
    songs_df = spark.read.option("header", "true").csv(f"{silver_folder}/songs")
    song_rank_history_df = spark.read.option("header", "true").csv(f"{silver_folder}/song_rank_history")
    song_data_df = spark.read.option("header", "true").csv(f"{silver_folder}/song_data")

    # Konwersja odpowiednich kolumn do typów numerycznych
    songs_df = songs_df.withColumn("popularity", col("popularity").cast("double"))
    song_rank_history_df = song_rank_history_df.withColumn("rank", col("rank").cast("int"))
    song_data_df = song_data_df.select(
        col("song_id"),
        col("af_danceability").cast("double"),
        col("af_energy").cast("double"),
        col("af_loudness").cast("double"),
        col("af_speechiness").cast("double"),
        col("af_acousticness").cast("double"),
        col("af_instrumentalness").cast("double"),
        col("af_liveness").cast("double"),
        col("af_valence").cast("double"),
        col("af_tempo").cast("double")
    )

    # Ustalenie najpopularniejszych piosenek w każdym regionie
    window_spec = Window.partitionBy("iso_code").orderBy(col("rank").asc())
    top_songs_df = song_rank_history_df.withColumn("row_num", row_number().over(window_spec)).filter(
        col("row_num") == 1)

    # Dołączenie cech `af_*` do najpopularniejszych piosenek
    top_songs_with_features = top_songs_df.join(
        song_data_df,
        top_songs_df["song_id"] == song_data_df["song_id"],
        "inner"
    )

    # Obliczenie średnich wartości `af_*` dla najpopularniejszych piosenek według regionu
    aggregated_df = top_songs_with_features.groupBy("iso_code").agg(
        avg("af_danceability").alias("avg_af_danceability"),
        avg("af_energy").alias("avg_af_energy"),
        avg("af_loudness").alias("avg_af_loudness"),
        avg("af_speechiness").alias("avg_af_speechiness"),
        avg("af_acousticness").alias("avg_af_acousticness"),
        avg("af_instrumentalness").alias("avg_af_instrumentalness"),
        avg("af_liveness").alias("avg_af_liveness"),
        avg("af_valence").alias("avg_af_valence"),
        avg("af_tempo").alias("avg_af_tempo")
    )

    # Zapisanie wyników w warstwie Gold
    aggregated_df.repartition(partition_num).write.option("header", True).mode("overwrite").csv(output_folder)

    spark.stop()


if __name__ == "__main__":
    silver_folder = sys.argv[1]
    output_folder = sys.argv[2]
    partition_num = int(sys.argv[3])

    process_gold_layer(silver_folder, output_folder, partition_num)
