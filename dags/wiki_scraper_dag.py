from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import sys

# Add the scripts directory to the Python path
sys.path.append('/opt/airflow/scripts')

from main import scrape_wikipedia

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 3, 20),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'wiki_scraper',
    default_args=default_args,
    description='Wikipedia Knowledge Graph Scraper',
    schedule_interval='@daily',
    catchup=False
)

scraper_task = PythonOperator(
    task_id='scrape_wikipedia',
    python_callable=scrape_wikipedia,
    dag=dag,
)

scraper_task