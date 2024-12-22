import sys

from pyspark.sql import SparkSession
from pyspark.sql.functions import col
from pyspark.sql.functions import countDistinct
from pyspark.sql.functions import first

def top_songs_with_duration(songs_folder, song_rank_history_folder, output_folder):
    spark = SparkSession.builder.appName("TopSongWithDuration").getOrCreate()

    # Read the CSV files
    songs_df = spark.read.option("header", True).csv(songs_folder)
    song_rank_history_df = spark.read.option("header", True).csv(song_rank_history_folder)

    # Rename columns to avoid ambiguity
    song_rank_history_df = song_rank_history_df.withColumnRenamed("rank", "song_rank")

    # Join the DataFrames
    joined_df = songs_df.join(
        song_rank_history_df,
        songs_df["id"] == song_rank_history_df["song_id"],
        "inner"
    )

    # Filter rows where song_rank is 1
    filtered_df = joined_df.filter(col("song_rank") == 1)

    # Group by song_id and calculate aggregates
    song_occurrences = filtered_df.groupBy("song_id").agg(
        first("title").alias("title"),
        first("duration_ms").alias("duration_ms"),
        countDistinct("date").alias("occurrences")
    )

    # Write the results to the output folder
    song_occurrences.write.option("header", True).mode("overwrite").csv(output_folder)

    spark.stop()

if __name__ == "__main__":
    silver_folder = sys.argv[1]
    gold_folder = sys.argv[2]

    songs_folder = f"{silver_folder}/songs"
    song_rank_history_folder = f"{silver_folder}/song_rank_history"
    output_folder = f"{gold_folder}/top_songs_with_duration"

    top_songs_with_duration(songs_folder, song_rank_history_folder, output_folder)
