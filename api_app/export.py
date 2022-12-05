import datetime
import pandas as pd
import numpy as np
import seaborn as sns
from pydrive.drive import GoogleDrive
from pydrive.auth import GoogleAuth


sns.set_theme(style="whitegrid")

CSV_FILE_NAME = 'data.csv'

PNG_FILE_NAME_BARS = 'bar_plot.png'

PNG_FILE_NAME_DYNAMICS = 'dynamics_plot.png'


def export_db_data_to_csv(statistics):
    df = pd.DataFrame.from_records(statistics)
    df.to_csv(CSV_FILE_NAME, index=False)


def build_bar_plot(statistics):
    df = pd.DataFrame.from_records(statistics)
    data_grouped_by_club = df.groupby('club').agg(
        Views_count=('club', np.count_nonzero))
    data_grouped_by_club['clubs'] = (
        data_grouped_by_club.index.get_level_values(level='club'))
    plot = sns.catplot(
        data=data_grouped_by_club, kind="bar",
        x="clubs", y="Views_count",
        palette="dark", alpha=.6, height=6
    )
    fig = plot.figure
    fig.savefig(PNG_FILE_NAME_BARS)


def build_dynamics_plot(statistics):
    df = pd.DataFrame.from_records(statistics)
    df['date_time'] = pd.to_datetime(df['date_time'])
    df['view_count'] = 1
    data_grouped_by_club = df.set_index(
        'date_time').groupby('club').resample('1T').agg(
            view_count=('view_count', 'sum')
        )
    plot = sns.lineplot(
        data=data_grouped_by_club,
        x="date_time", y="view_count", hue='club'
    )
    fig = plot.figure
    fig.savefig(PNG_FILE_NAME_DYNAMICS)


def get_google_drive():
    g_login = GoogleAuth()
    g_login.LocalWebserverAuth()
    return GoogleDrive(g_login)


def export_file_to_google(file_name, file_extension):
    drive = get_google_drive()
    file = drive.CreateFile(
        {'title': f'{str(datetime.datetime.utcnow())}.{file_extension}'})
    file.SetContentFile(file_name)
    file.Upload()
