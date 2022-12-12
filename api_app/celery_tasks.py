import os
import matplotlib
from asgiref.sync import async_to_sync
from celery import Celery
from celery import shared_task
from celery.schedules import crontab
from dotenv import load_dotenv

from api_app.events import get_filtered_statistics
from api_app.export import export_db_data_to_csv, build_bar_plot, build_displot
from api_app.export import export_file_to_google, build_dynamics_plot
from api_app.export import (
    CSV_FILE_NAME, PNG_FILE_NAME_BARS,
    PNG_FILE_NAME_DYNAMICS, PNG_FILE_NAME_DISPLOT
)


matplotlib.use('agg')

load_dotenv()

PERIOD_FOR_GETTING_STATISTICS = 60

PERIOD_FOR_CELERY_TASK = 1

RABBIT_URL = os.getenv('RABBIT_URL')

celery_app = Celery(
    __name__,
    backend='redis://localhost:6379',
    broker=RABBIT_URL,
    task_track_started=True,
    task_ignore_result=False,
    enable_utc=True
)

celery_app.autodiscover_tasks()


async def publish_data(
        export_data,
        period_for_getting_statistics,
        file_name,
        extension):
    statistics = await get_filtered_statistics(
        period_in_minutes=period_for_getting_statistics)
    export_data(statistics)
    export_file_to_google(
        file_name=file_name,
        file_extension=extension)


@shared_task()
def sync_task_statistics():
    async_to_sync(publish_data)(
        export_db_data_to_csv, PERIOD_FOR_GETTING_STATISTICS,
        CSV_FILE_NAME, 'csv')


@shared_task()
def sync_task_bar_plot():
    async_to_sync(publish_data)(
        build_bar_plot, PERIOD_FOR_GETTING_STATISTICS,
        PNG_FILE_NAME_BARS, 'png')


@shared_task()
def sync_task_dynamics_plot():
    async_to_sync(publish_data)(
        build_dynamics_plot, PERIOD_FOR_GETTING_STATISTICS,
        PNG_FILE_NAME_DYNAMICS, 'png'
    )


@shared_task()
def sync_task_displot():
    async_to_sync(publish_data)(
        build_displot, PERIOD_FOR_GETTING_STATISTICS,
        PNG_FILE_NAME_DISPLOT, 'png'
    )


celery_app.conf.beat_schedule = {
    'publish_statistics': {
        'task': 'api_app.celery_tasks.sync_task_statistics',
        'schedule': crontab(minute=f"*/{PERIOD_FOR_CELERY_TASK}")
    },
    'publish_bar_plot': {
        'task': 'api_app.celery_tasks.sync_task_bar_plot',
        'schedule': crontab(minute=f'*/{PERIOD_FOR_CELERY_TASK}')
    },
    'publish_dynamics_plot': {
        'task': 'api_app.celery_tasks.sync_task_dynamics_plot',
        'schedule': crontab(minute=f'*/{PERIOD_FOR_CELERY_TASK}')
    },
    'publish_displot': {
        'task': 'api_app.celery_tasks.sync_task_displot',
        'schedule': crontab(minute=f'*/{PERIOD_FOR_CELERY_TASK}')
    }
}
