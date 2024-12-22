from pyspark.sql import SparkSession
from pyspark.sql.functions import col, min as spark_min, datediff, avg
import sys

def avg_days_to_popularity(song_rank_history_path, songs_path, output_path):
    spark = SparkSession.builder.appName("GoldLayerAverageDays").getOrCreate()

    song_rank_history_df = spark.read.option("header", "true").csv(song_rank_history_path)
    songs_df = spark.read.option("header", "true").csv(songs_path)

    song_rank_history_df = song_rank_history_df.withColumn("date", col("date").cast("date"))
    songs_df = songs_df.withColumn("release_date", col("release_date").cast("date"))

    earliest_rank_date_df = song_rank_history_df.groupBy("song_id", "iso_code").agg(spark_min("date").alias("earliest_rank_date"))

    song_with_dates_df = earliest_rank_date_df.join(
        songs_df.select("id", "release_date").withColumnRenamed("id", "song_id"),
        on="song_id",
        how="inner"
    )

    song_with_dates_df = song_with_dates_df.withColumn(
        "days_to_popularity", datediff(col("earliest_rank_date"), col("release_date"))
    )

    avg_days_to_popularity_df = song_with_dates_df.groupBy("iso_code").agg(avg("days_to_popularity").alias("avg_days_to_popularity"))
    sorted_avg_days_to_popularity_df = avg_days_to_popularity_df.orderBy(col("avg_days_to_popularity").desc())

    sorted_avg_days_to_popularity_df.write.option("header", True).mode("overwrite").csv(output_path)

    spark.stop()


if __name__ == "__main__":
    input_folder = sys.argv[1]
    output_folder = sys.argv[2]

    song_rank_history_path = f"{input_folder}/song_rank_history"
    songs_path = f"{input_folder}/songs"
    output_folder = f"{output_folder}/avg_days_to_popularity"

    avg_days_to_popularity(song_rank_history_path, songs_path, output_folder)
        
    