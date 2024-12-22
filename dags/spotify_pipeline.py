import airflow
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator

dag = DAG(
    dag_id = "spotify_pipeline",
    default_args = {
        "owner": "JK",
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
    application="jobs/python/health_check.py",
    dag=dag
)

repartition = SparkSubmitOperator(
    task_id="repartition",
    conn_id="spark-conn",
    application="jobs/python/bronze_processing.py",
    application_args = [
        "/opt/data/sampled_output.csv", 
        "/opt/data/bronze/kaggle_spotify",
        "10", 
        "/opt/data/artists_sample.txt", 
        "/opt/data/bronze/artists",
        "10", 
        "/opt/data/continents2.csv", 
        "/opt/data/bronze/continents",
        "2", 
        "/opt/data/hdi.csv", 
        "/opt/data/bronze/hdi",
        "2", 
    ],
    dag=dag
)

silver_processing = SparkSubmitOperator(
    task_id="silver_processing",
    conn_id="spark-conn",
    application="jobs/python/silver_processing.py",
    application_args=[
        "/opt/data/bronze/kaggle_spotify", 
        "/opt/data/bronze/continents", 
        "/opt/data/bronze/hdi", 
        "/opt/data/bronze/artists", 
        "10", 
        "/opt/data/silver"],
    dag=dag
)

count_artists_by_country = SparkSubmitOperator(
    task_id="count_artists_by_country",
    conn_id="spark-conn",
    application="jobs/python/gold_processing/count_artists_by_country.py",
    application_args=[
        "/opt/data/silver",
        "/opt/data/gold",
    ],
    dag=dag
)

count_explicit_songs_by_country = SparkSubmitOperator(
    task_id="count_explicit_songs",
    conn_id="spark-conn",
    application="jobs/python/gold_processing/count_explicit_songs.py",
    application_args=[
        "/opt/data/silver",
        "/opt/data/gold",
    ],
    dag=dag
)

avg_days_to_popularity = SparkSubmitOperator(
    task_id="avg_days_to_popularity",
    conn_id="spark-conn",
    application="jobs/python/gold_processing/avg_days_to_popularity.py",
    application_args=[
        "/opt/data/silver",
        "/opt/data/gold",
    ],
    dag=dag
)

local_artist_percentage = SparkSubmitOperator(
    task_id="local_artist_percentage",
    conn_id="spark-conn",
    application="jobs/python/gold_processing/local_artist_percentage.py",
    application_args=[
        "/opt/data/silver",
        "/opt/data/gold",
    ],
    dag=dag
)

top_songs_with_duration = SparkSubmitOperator(
    task_id="top_songs_with_duration",
    conn_id="spark-conn",
    application="jobs/python/gold_processing/top_songs_with_duration.py",
    application_args=[
        "/opt/data/silver",
        "/opt/data/gold",
    ],
    dag=dag
)


end = PythonOperator(
    task_id="end",
    python_callable = lambda: print("Jobs completed successfully"),
    dag=dag
)

start >> health_check >> repartition >> silver_processing >> [
    count_artists_by_country, 
    count_explicit_songs_by_country,
    avg_days_to_popularity,
    local_artist_percentage,
    top_songs_with_duration
] >> end

