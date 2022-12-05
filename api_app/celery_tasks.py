import os
import matplotlib
from asgiref.sync import async_to_sync
from celery import Celery
from celery import shared_task
from celery.schedules import crontab
from dotenv import load_dotenv

from api_app.events import get_filtered_statistics
from api_app.export import export_db_data_to_csv, build_bar_plot
from api_app.export import export_file_to_google, build_dynamics_plot
from api_app.export import (
    CSV_FILE_NAME, PNG_FILE_NAME_BARS, PNG_FILE_NAME_DYNAMICS
)


matplotlib.use('agg')

load_dotenv()

PERIOD_FOR_GETTING_STATISTICS = 60

PERIOD_FOR_CELERY_TASK = 60

RABBIT_URL = os.getenv('RABBIT_URL')

celery = Celery(
    __name__,
    backend='rpc://',
    broker=RABBIT_URL
)

celery.conf.enable_utc = True


async def publish_statistics():
    statistics = await get_filtered_statistics(
        period_in_minutes=PERIOD_FOR_GETTING_STATISTICS)
    export_db_data_to_csv(statistics)
    export_file_to_google(
        file_name=CSV_FILE_NAME,
        file_extension='csv')


@shared_task()
def sync_task_statistics():
    async_to_sync(publish_statistics)()


async def publish_bar_plot():
    statistics = await get_filtered_statistics(
        period_in_minutes=PERIOD_FOR_GETTING_STATISTICS)
    build_bar_plot(statistics)
    export_file_to_google(
        file_name=PNG_FILE_NAME_BARS,
        file_extension='png')


@shared_task()
def sync_task_bar_plot():
    async_to_sync(publish_bar_plot)()


async def publish_dynamics_plot():
    statistics = await get_filtered_statistics(
        period_in_minutes=PERIOD_FOR_GETTING_STATISTICS)
    build_dynamics_plot(statistics)
    export_file_to_google(
        file_name=PNG_FILE_NAME_DYNAMICS,
        file_extension='png')


@shared_task()
def sync_task_dynamics_plot():
    async_to_sync(publish_dynamics_plot)()


celery.conf.beat_schedule = {
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
    }
}
