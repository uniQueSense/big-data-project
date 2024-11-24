import airflow
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator



dag = DAG(
    dag_id = "Spotify_pipeline",
    default_args = {
        "owner": "Wojciech Święs",
        "start_date": airflow.utils.dates.days_ago(1)
    },
    schedule_interval = "@daily"
)

start = PythonOperator(
    task_id="start",
    python_callable = lambda: print("Jobs started"),
    dag=dag
)

health_check = SparkSubmitOperator(
    task_id="health_check",
    conn_id="spark-conn",
    application="jobs/python/wordcountjob.py",
    dag=dag
)

# repartition = SparkSubmitOperator(
#     task_id="repartition",
#     conn_id="spark-conn",
#     application="jobs/python/repartition_countries.py",
#     application_args=["/opt/data/source/merged_data.csv", "10", "/opt/data/bronze/kagle_spotify"],
#     dag=dag
# )

silver_processing = SparkSubmitOperator(
    task_id="silver_processing",
    conn_id="spark-conn",
    application="jobs/python/silver_processing.py",
    application_args=["/opt/data/bronze/kagle_spotify", "10", "/opt/data/silver"],
    dag=dag
)
# application_args = ["/opt/data/bronze/kagle_spotify/", "10", "/opt/data/bronze/kagle_spotify"],

scala_job = SparkSubmitOperator(
    task_id="scala_job",
    conn_id="spark-conn",
    application="jobs/scala/target/scala-2.12/word-count_2.12-0.1.jar",
    dag=dag
)

java_job = SparkSubmitOperator(
    task_id="java_job",
    conn_id="spark-conn",
    application="jobs/java/spark-job/target/spark-job-1.0-SNAPSHOT.jar",
    java_class="com.airscholar.spark.WordCountJob",
    dag=dag
)


end = PythonOperator(
    task_id="end",
    python_callable = lambda: print("Jobs completed successfully"),
    dag=dag
)

# start >> [health_check, repartition, silver_processing] >> end
start >> [health_check, silver_processing] >> end
