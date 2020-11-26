#!/usr/bin/env python3
import click
import dateutil
import logging
from .rss import RssDownloader, SiteData
from .database import (
    PodcastDatabase,
    PodcastExistsException,
    PodcastDoesNotExistException,
)

DBFILE = "rss.db"


@click.group(context_settings=dict(help_option_names=["-h", "--help"]))
@click.option("-v", "--verbose", is_flag=True, help="Verbose debugging info")
@click.option("-b", "--nobackup", is_flag=True, help="Do not create db backup")
@click.option("-d", "--database", default="rss.db", help="database file to use")
def pyres(verbose, nobackup, database):
    global DBFILE
    click.echo(f"verbose:{verbose} backup:{nobackup} database:{database}")
    DBFILE = database


@pyres.command()  # @cli, not @click!
@click.option(
    "-s",
    "--start-date",
    default="1/1/1970",
    help="date before first podcast to download (04/17/15, for example)",
)
@click.option(
    "-m",
    "--max-update",
    default=0,
    type=int,
    help="maximum number of episodes to download at one time",
)
@click.argument("url", type=str)
def add(start_date, max_update, url):
    logging.debug("in add url with %s %s", url, start_date)
    start_date = dateutil.parser.parse(start_date)
    start_date = dateutil.utils.default_tzinfo(start_date, dateutil.tz.UTC)

    click.echo(f"adding {start_date} {url} max:{max_update}")
    pod = SiteData(url, max_update, start_date)
    episodes, errors = RssDownloader([pod]).download_episodes()

    # Add to database
    with PodcastDatabase(DBFILE) as _database:
        for podcast, episodes in episodes.items():
            try:
                _database.add_podcast(podcast, url, max_update)
                for episode in episodes:
                    _database.add_new_episode_data(podcast, episode)
            except PodcastExistsException:
                print(f"Error: Podcast {podcast} already exists.")

    # Report Errors
    # JHA TODO add error reporting
    # print("errors", errors)


@pyres.command()
@click.argument("name", type=str)
def delete(name):
    click.echo(f"Deleting {name}")
    with PodcastDatabase(DBFILE) as _database:
        try:
            _database.delete_podcast(name)
        except PodcastDoesNotExistException:
            print(f"{name} does not exist")


@pyres.command()
def update():
    click.echo(f"updating")


@pyres.command()
@click.option(
    "-p",
    "--path",
    default="/media/usb0/",
    help="path to filesystem on MP3 player",
)
def download(path):
    click.echo(f"download to {path}")


@pyres.command()
@click.option("-a", "--all", is_flag=True, help="show all details")
def database(all):
    click.echo(f"database {all}")
    with PodcastDatabase(DBFILE) as _database:
        _database.show_podcasts(all)


@pyres.command()
def names():
    click.echo("show names")


@pyres.command()
@click.option("-d", "--dir", default=None, help="path from which to copy")
@click.option(
    "-p",
    "--path",
    default="/media/usb0/",
    help="path to filesystem on MP3 player",
)
def audiobook(dir, path):
    click.echo(f"download to {path}")
