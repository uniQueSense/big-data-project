import sys

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, count_distinct

def count_explicit_songs_by_country(songs_folder, song_rank_history_folder, combined_continents_hdi_folder, output_folder):
    spark = SparkSession.builder.appName("CountExplicitSongs").getOrCreate()

    songs_df = spark.read.option("header", True).csv(songs_folder)

    song_rank_history_df = spark.read.option("header", True).csv(song_rank_history_folder)
    continents_hdi_df = spark.read.option("header", "true").csv(combined_continents_hdi_folder)


    joined_df = songs_df.join(
        song_rank_history_df,
        songs_df["id"] == song_rank_history_df["song_id"],
        "inner"
    )

    explicit_song_counts_df = joined_df.filter(col("explicit") == True).groupBy("iso_code").agg(
        count_distinct("id").alias("unique_explicit_songs")
    )

    explicit_songs_with_continents_df = explicit_song_counts_df.join(
        continents_hdi_df.select("iso_code", "continent"),
        "iso_code",
        "left"
    )
    explicit_songs_by_continent = explicit_songs_with_continents_df.groupBy("continent").agg(count_distinct("unique_explicit_songs").alias("unique_explicit_songs_by_continent"))
    sorted_explicit_songs_by_continent = explicit_songs_by_continent.orderBy(col("unique_explicit_songs_by_continent").desc())
    sorted_explicit_song_counts_df = explicit_song_counts_df.orderBy(col("unique_explicit_songs").desc())

    # Write both outputs to the specified output folder
    sorted_explicit_song_counts_df.write.option("header", "true").mode("overwrite").csv(f"{output_folder}/explicit_songs_by_country")
    sorted_explicit_songs_by_continent.write.option("header", "true").mode("overwrite").csv(f"{output_folder}/explicit_songs_by_continent")


    spark.stop()


if __name__ == "__main__":
    input_folder = sys.argv[1]
    output_folder = sys.argv[2]

    songs_folder = f"{input_folder}/songs"
    song_rank_history_folder = f"{input_folder}/song_rank_history"
    combined_continents_hdi_folder = f"{input_folder}/combined_continents_hdi"
    output_folder = f"{output_folder}/explicit_songs_by_country"

    count_explicit_songs_by_country(songs_folder, song_rank_history_folder, combined_continents_hdi_folder, output_folder)
        
    