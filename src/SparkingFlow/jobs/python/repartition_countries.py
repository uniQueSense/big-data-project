import sys
from pyspark.sql import SparkSession

input_file = sys.argv[1]
partition_num = int(sys.argv[2])
output_file = sys.argv[3]

spark = SparkSession.builder.appName("RepartitionCountries").getOrCreate()

df = spark.read.csv(input_file, header=True, inferSchema=True)
repartitioned_df = df.repartition(partition_num)
repartitioned_df.write.csv(output_file, mode="overwrite", header=True)

spark.stop()