import sys

from pyspark.sql import SparkSession
from pyspark.sql.functions import lit

csv_header = ["id", "title", "rank", "date", "artist", "url", "region", "chart", "trend", "streams", "track_id",
              "album",
              "popularity", "duration_ms", "explicit", "release_date", "available_markets", "af_danceability",
              "af_energy", "af_key", "af_loudness", "af_mode", "af_speechiness", "af_acousticness",
              "af_instrumentalness", "af_liveness", "af_valence", "af_tempo", "af_time_signature"]

def process_data(input_folder, output_file, partition_num):
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
    song_rank_history_df = song_rank_history_df.withColumn("country", lit("").cast("string")) # Zakładając, że kraj jest przypisany później, lit("").cast("string")

    song_data_df = df.select("id", "af_danceability", "af_energy", "af_loudness", "af_speechiness", "af_acousticness",
                             "af_instrumentalness", "af_liveness", "af_valence", "af_tempo", "af_time_signature")
    song_data_df = song_data_df.withColumn("song_id", song_data_df["id"])

    repartioned_df = df.repartition(partition_num)

    artists_df.write.option("header", True).mode("overwrite").csv(f"{output_file}/artists")
    albums_df.write.option("header", True).mode("overwrite").csv(f"{output_file}/albums")
    songs_df.write.option("header", True).mode("overwrite").csv(f"{output_file}/songs")
    song_rank_history_df.write.option("header", True).mode("overwrite").csv(f"{output_file}/song_rank_history")
    song_data_df.write.option("header", True).mode("overwrite").csv(f"{output_file}/song_data")

    spark.stop()

if __name__ == "__main__":
    input_folder = sys.argv[1]
    partition_num = int(sys.argv[2])
    output_file = sys.argv[3]

    process_data(input_folder, output_file, partition_num)
