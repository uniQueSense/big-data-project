import sys
import math
from pyspark.sql import SparkSession

input_groups = math.floor((len(sys.argv) - 1) / 3)
spark = SparkSession.builder.appName("BronzeProcessing").getOrCreate()

for input_index in range(0, input_groups):
    input_file = sys.argv[input_index * 3 + 1]
    output_file = sys.argv[input_index * 3 + 2]
    partition_num = int(sys.argv[input_index * 3 + 3])

    if input_file.endswith("csv"):
        df = spark.read.csv(input_file, header=True, inferSchema=True)
        repartitioned_df = df.repartition(partition_num)
        repartitioned_df.write.csv(output_file, mode="overwrite", header=True)
    elif input_file.endswith("txt"):
        df = spark.read.json(input_file)
        repartitioned_df = df.repartition(partition_num)
        repartitioned_df.write.json(output_file, mode="overwrite")

spark.stop()