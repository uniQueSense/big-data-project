import sys

from pyspark.sql import SparkSession
from pyspark.sql.functions import lit, when

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
    artists_df = artists_df.withColumn("id", lit(None).cast("int"))

    albums_df = df.select("album").distinct()
    albums_df = albums_df.withColumn("id", lit(None).cast("int"))

    songs_df = df.select("id", "title", "release_date", "popularity", "duration_ms", "explicit", "album", "rank", "chart")
    songs_df = songs_df.withColumn("id", songs_df["id"].cast("string"))

    song_rank_history_df = df.select("id", "date", "rank", "trend", "chart", "region").withColumnRenamed("id", "song_id")

    song_data_df = df.select("id", "af_danceability", "af_energy", "af_loudness", "af_speechiness", "af_acousticness",
                             "af_instrumentalness", "af_liveness", "af_valence", "af_tempo", "af_time_signature")
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
        [artists_df, "artists"],
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
        "hdi": sys.argv[3]
    }
    partition_num = int(sys.argv[4])
    output_file = sys.argv[5]

    process_data(input_folder, additional_folders, output_file, partition_num)
