#!/usr/bin/env python3
import click
import dateutil
import logging
from .rss import RssDownloader, SiteData
from .copier import copy_episodes_to_player
from .database import (
    PodcastDatabase,
    PodcastExistsException,
    PodcastDoesNotExistException,
)
from .download import Downloader

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
    podcast = RssDownloader([pod]).add_podcast()

    # Add to database
    if podcast:
        with PodcastDatabase(DBFILE) as _database:
            try:
                _database.add_podcast(podcast, url, max_update)
                print(f"Added {podcast}")
            except PodcastExistsException:
                print(f"Error: Podcast {podcast} already exists.")
    else:
        print(f"Failed to add {url}")


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
    with PodcastDatabase(DBFILE) as _database:
        podcasts = _database.get_podcast_urls()
        total_added = 0
        pods = [
            SiteData(url, max_update, start_date)
            for (url, max_update, start_date) in podcasts
        ]
        ep_list, errors = RssDownloader(pods).download_episodes()
        for podcast, episodes in ep_list.items():
            print(f"{podcast} - {len(episodes)} to download")
            total_added += len(episodes)
            for episode in episodes:
                _database.add_new_episode_data(podcast, episode)
        print()
        print(f"There are a total of {total_added} new episodes to be updated.")

    # Close the previous transaction and start a new one.  This has two benefits
    #   1. It ensures that we store the data we collected from the rss query above
    #   2. It retries previous episodes that failed to download
    with PodcastDatabase(DBFILE) as _database:
        episodes = _database.find_episodes_to_download()
        if episodes:
            downloader = Downloader()
            success, fail = downloader.download_episodes(episodes)
            for episode in success:
                _database.mark_episode_downloaded(episode)
            if fail:
                print("failed to download:")
                for f in fail:
                    print(f"   {f}")
            print("\n" * len(episodes))
        else:
            print("Nothing to update")


@pyres.command()
@click.option(
    "-p",
    "--path",
    default="/media/usb0/",
    help="path to filesystem on MP3 player",
)
def copy(path):
    click.echo(f"copy to {path}")
    with PodcastDatabase(DBFILE) as _database:
        episodes = _database.find_episodes_to_copy()
        copy_episodes_to_player(path, episodes)
        for episode in episodes:
            _database.mark_episode_as_copied(episode)


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
