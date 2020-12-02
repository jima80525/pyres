import logging
import pathlib
import shutil


def copy_episodes_to_player(base_dir, episodes):
    """ Copies the episodes to the mp3 player """
    base = pathlib.Path(base_dir)

    # make sure the podcast directory exists
    podcast_dir = base / "podcasts"
    podcast_dir.mkdir(exist_ok=True)

    total = len(episodes)
    counter = 0
    for episode in episodes:
        src = pathlib.Path(episode)
        filename = src.name
        dest = podcast_dir / filename
        logging.debug(f"copying {filename} to {podcast_dir}")
        shutil.copyfile(src, dest)

        counter += 1
        logging.debug(f"copied {filename} to {podcast_dir}")
        print(f"{counter:2}/{total}: copied {filename}")
