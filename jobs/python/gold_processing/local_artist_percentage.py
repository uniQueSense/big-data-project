from pyspark.sql import SparkSession
from pyspark.sql.functions import col, countDistinct, when, expr, isnull

import sys

def calculate_local_artist_percentage(song_rank_history_path, artist_song_relation_path, artists_path, combined_continents_hdi_path, output_path):
    spark = SparkSession.builder.appName("GoldLayerLocalArtistPercentage").getOrCreate()

    song_rank_history_df = spark.read.option("header", "true").csv(song_rank_history_path)
    artist_song_relation_df = spark.read.option("header", "true").csv(artist_song_relation_path)
    artists_df = spark.read.option("header", "true").csv(artists_path)
    combined_continents_hdi_df = spark.read.option("header", "true").csv(combined_continents_hdi_path)

    artists_with_iso_df = artists_df.join(
        combined_continents_hdi_df.select("iso_code", "iso_code_short"),
        artists_df["country"] == combined_continents_hdi_df["iso_code_short"],
        how="left"
    ).drop("iso_code_short")

    songs_with_artists_df = song_rank_history_df.join(
        artist_song_relation_df,
        on="song_id",
        how="inner"
    )

    songs_with_artists_country_df = songs_with_artists_df.join(
        artists_with_iso_df.selectExpr("id as artist_id", "iso_code as artist_country"),
        on="artist_id",
        how="inner"
    )

    songs_with_artists_country_df = songs_with_artists_country_df.withColumn(
        "is_local",
        when(isnull(col("artist_country")), None)  
        .when(col("artist_country") == col("iso_code"), 1)  
        .otherwise(0)  
    )

    songs_with_artists_country_df = songs_with_artists_country_df.filter(col("is_local").isNotNull())

    country_song_stats_df = songs_with_artists_country_df.groupBy("iso_code") \
        .agg(
            countDistinct("song_id").alias("total_songs"),
            expr("sum(is_local)").alias("local_songs")
        )

    country_song_stats_df = country_song_stats_df.withColumn(
        "local_artist_percentage",
        expr("(local_songs / total_songs) * 100")
    )

    sorted_country_song_stats_df = country_song_stats_df.orderBy(col("local_artist_percentage").desc())

    sorted_country_song_stats_df.write.option("header", True).mode("overwrite").csv(output_path)

    spark.stop()


if __name__ == "__main__":
    input_folder = sys.argv[1]
    output_folder = sys.argv[2]

    song_rank_history_folder = f"{input_folder}/song_rank_history"
    artists_folder = f"{input_folder}/artists"
    artist_song_relation_folder = f"{input_folder}/artist_song_relation"
    combined_continents_hdi_path = f"{input_folder}/combined_continents_hdi"
    output_folder = f"{output_folder}/local_artist_percentage"

    calculate_local_artist_percentage(song_rank_history_folder, artist_song_relation_folder, artists_folder, combined_continents_hdi_path, output_folder)
