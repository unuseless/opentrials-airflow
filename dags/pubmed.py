import datetime
from airflow.operators.docker_operator import DockerOperator
from airflow.models import DAG, Variable
import utils.helpers as helpers

args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime.datetime.utcnow(),
    'retries': 1,
}

dag = DAG(dag_id='pubmed',
          default_args=args,
          max_active_runs=1,
          schedule_interval='@monthly')

collector_task = DockerOperator(
    task_id='pubmed_collector',
    dag=dag,
    image='okibot/collectors:latest',
    force_pull=True,
    environment={
        'WAREHOUSE_URL': helpers.get_postgres_uri('warehouse_db'),
        'LOGGING_URL': Variable.get('LOGGING_URL'),
        'PYTHON_ENV': Variable.get('ENV'),
        'DOWNLOAD_DELAY': Variable.get('DOWNLOAD_DELAY'),
    },
    command='make start pubmed'
)

processor_task = DockerOperator(
    task_id='pubmed_processor',
    dag=dag,
    image='okibot/processors:latest',
    force_pull=True,
    environment={
        'WAREHOUSE_URL': helpers.get_postgres_uri('warehouse_db'),
        'DATABASE_URL': helpers.get_postgres_uri('api_db'),
        'EXPLORERDB_URL': helpers.get_postgres_uri('explorer_db'),
        'LOGGING_URL': Variable.get('LOGGING_URL'),
    },
    command='make start pubmed'
)

pubmed_linker_task = DockerOperator(
    task_id='pubmed_linker',
    dag=dag,
    image='okibot/processors:latest',
    force_pull=True,
    environment={
        'WAREHOUSE_URL': helpers.get_postgres_uri('warehouse_db'),
        'DATABASE_URL': helpers.get_postgres_uri('api_db'),
        'EXPLORERDB_URL': helpers.get_postgres_uri('explorer_db'),
        'LOGGING_URL': Variable.get('LOGGING_URL'),
    },
    command='make start pubmed_linker'

)

processor_task.set_upstream(collector_task)
pubmed_linker_task.set_upstream(processor_task)