import sys

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, count

def count_artists_by_country(hdi_folder, artists_folder, output_folder):
    spark = SparkSession.builder.appName("CountArtistsByCountry").getOrCreate()
    hdi_df = spark.read.option("header", True).csv(hdi_folder)

    artists_df = spark.read.option("header", True).csv(artists_folder)

    enriched_df = artists_df.join(
        hdi_df,
        artists_df["country"] == hdi_df["iso_code_short"],
        "inner"
    )

    artist_counts_df = enriched_df.groupBy("iso_code_short").agg(
        count("artist").alias("artist_count")
    )

    sorted_artist_counts_df = artist_counts_df.orderBy(col("artist_count").desc())
    sorted_artist_counts_df.write.mode("overwrite").option("header", True).csv(output_folder)

    spark.stop()

if __name__ == "__main__":
    input_folder = sys.argv[1]
    output_folder = sys.argv[2]
    mode = sys.argv[3]

    if mode == "popular_artists_by_country":
        hdi_folder = f"{input_folder}/combined_continents_hdi"
        artists_folder = f"{input_folder}/artists"
        output_folder = f"{output_folder}/artist_counts_by_country"

        count_artists_by_country(hdi_folder, artists_folder, output_folder)
    
    