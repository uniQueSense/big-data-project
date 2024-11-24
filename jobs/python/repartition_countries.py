import sys
from pyspark.sql import SparkSession


input_file = sys.argv[1]
output_file = sys.argv[3]
partition_num = int(sys.argv[2])

spark = SparkSession.builder.appName("RepartitionCountries").getOrCreate()

df = spark.read.csv(input_file, header=True, inferSchema=True)
repartioned_df = df.repartition(partition_num)

#repartioned_df.write(output_file, mode="overwrite", header=True)
repartioned_df.write.option("header", True).mode("overwrite").csv(output_file)

spark.stop()