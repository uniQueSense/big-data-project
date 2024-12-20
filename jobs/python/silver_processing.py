import sys

from pyspark.sql import SparkSession
from pyspark.sql.functions import lit, when, explode, col, split, trim

csv_header = ["id", "title", "rank", "date", "artist", "url", "region", "chart", "trend", "streams", "track_id",
              "album",
              "popularity", "duration_ms", "explicit", "release_date", "available_markets", "af_danceability",
              "af_energy", "af_key", "af_loudness", "af_mode", "af_speechiness", "af_acousticness",
              "af_instrumentalness", "af_liveness", "af_valence", "af_tempo", "af_time_signature"]

def process_data(input_folder, additional_folders, output_file, partition_num):
    spark = SparkSession.builder.appName("SilverProcessing").getOrCreate()

    df = spark.read.option("header", "false").csv(input_folder)
    df = df.toDF(*csv_header)
    df = df.filter(df["id"] != "id")

    df = df.drop("url", "track_id", "available_markets")

    #df = df.withColumn("markets", explode(col("available_markets").cast(ArrayType(StringType()))))

    artists_df = df.select("artist").distinct()
    artists_df = artists_df.withColumn("artist_array", split(col("artist"), ","))

    # Explode the array to create a new row for each artist
    artists_df = artists_df.withColumn("artist", explode(col("artist_array")))

    # Trim whitespace from artist names
    artists_df = artists_df.withColumn("artist", trim(col("artist")))

    # Remove duplicates
    artists_df = artists_df.drop("artist_array").distinct()

    # Add an ID column
    artists_df = artists_df.withColumn("id", lit(None).cast("int"))

    artist_json_df = spark.read.json(additional_folders["artists"])

    # Flatten aliases to allow matching
    artist_json_df = artist_json_df.withColumn("alias", explode(col("aliases.name")))

    # Match artists_df with artist_json_df
    enriched_artists_df = artists_df.join(
        artist_json_df.select("name", "alias", "country"),
        (artists_df["artist"] == artist_json_df["name"]) | (artists_df["artist"] == artist_json_df["alias"]),
        "left"
    ).withColumn("country", col("country"))

    # Drop temporary columns and duplicates
    enriched_artists_df = enriched_artists_df.drop("name", "alias").dropDuplicates()

    albums_df = df.select("album").distinct()
    albums_df = albums_df.withColumn("id", lit(None).cast("int"))

    songs_df = df.select("id", "title", "release_date", "popularity", "duration_ms", "explicit", "album", "rank", "chart")
    songs_df = songs_df.withColumn("id", songs_df["id"].cast("string"))

    song_rank_history_df = df.select("id", "date", "rank", "trend", "chart", "region").withColumnRenamed("id", "song_id")

    song_data_df = df.select("id", "af_danceability", "af_energy", "af_loudness", "af_speechiness", "af_acousticness", "af_instrumentalness", "af_liveness", "af_valence", "af_tempo", "af_time_signature")
    song_data_df = song_data_df.withColumn("song_id", song_data_df["id"])

    continents_df = spark.read.option("header", "true").csv(additional_folders["continents"])
    continents_df = continents_df.selectExpr("name as country_name", "`alpha-3` as iso_code", "region as continent")

    hdi_df = spark.read.option("header", "true").csv(additional_folders["hdi"])
    hdi_df = hdi_df.selectExpr("ISO3 as iso_code","`Human Development Index (2021)` as hdi", "`Human Development Groups` as hdi_group")

    combined_df = continents_df.join(hdi_df, on="iso_code", how="inner")
    combined_df = combined_df.select("iso_code", "country_name", "continent", "hdi", "hdi_group")

    song_rank_history_df = song_rank_history_df.join(
        combined_df.select("country_name", "iso_code"),
        song_rank_history_df["region"] == combined_df["country_name"],
        "left"
    ).withColumn(
        "iso_code", when(song_rank_history_df["region"] == "global", "global").otherwise(combined_df["iso_code"])
    ).drop("country_name", "region") 

    configs = [
        [enriched_artists_df, "artists"],
        [albums_df, "albums"],
        [songs_df, "songs"],
        [song_rank_history_df, "song_rank_history"],
        [song_data_df, "song_data"],
        [combined_df, "combined_continents_hdi"]
    ]

    for config in configs:
        repartioned_df = config[0].repartition(partition_num)
        repartioned_df.write.option("header", True).mode("overwrite").csv(f"{output_file}/{config[1]}")

    spark.stop()

if __name__ == "__main__":
    input_folder = sys.argv[1]
    additional_folders = {
        "continents": sys.argv[2],
        "hdi": sys.argv[3],
        "artists": sys.argv[4],
    }
    partition_num = int(sys.argv[5])
    output_file = sys.argv[6]

    process_data(input_folder, additional_folders, output_file, partition_num)
