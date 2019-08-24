import os
import pathlib
import praw
import requests
import shutil
from imgurdownloader import ImgurDownloader
from config import CONFIG


def get_subreddits(reddit):
    """Get a list of subreddit names.

    If any multireddits are being searched, this function grabs the name of
    each sub for the list.

    Parameters
    ----------
    reddit : praw.Reddit
        The reddit instance used to gather data.

    Returns
    -------
    subreddits : set
        Set of subreddit names.

    """

    allow_nsfw = CONFIG["Downloads"].getboolean("AllowNSFW")
    subreddit_config = CONFIG.options("Subreddits")
    subreddits = []

    if not allow_nsfw:
        for subreddit in subreddit_config:
            sub = reddit.subreddit(subreddit)
            if not sub.over18:
                subreddits.append(sub.display_name)
    else:
        subreddits = subreddit_config

    for sub in subreddits:
        sub = sub.lower()


    multi_config = CONFIG.options("Multireddits")
    multi_list = [tuple(m.split()) for m in multi_config]

    for user, multi in multi_list:
        multireddit = reddit.multireddit(user, multi)
        if not allow_nsfw and multireddit.over_18:
            continue
        for sub in multireddit.subreddits:
            subreddits.append(sub.display_name.lower())

    subreddits = set(subreddits)
    return subreddits


def download_post_image(post):
    """Download the image associated with the given reddit post."""

    if post.is_self:
        return False

    # FIXME: Check file permissions when attempting to create directory
    output_dir = pathlib.Path(CONFIG["Downloads"]["OutputDirectory"]).expanduser()
    if str(output_dir) == '.':
        output_dir = pathlib.Path.cwd()  # Get the absolute path
    if not output_dir.exists():
        output_dir.mkdir(parents=True)

    image_types = (".png", ".jpg", ".jpeg", ".gif")
    if not post.url.endswith(image_types):
        return False

    filename_start = post.url.rfind('/')
    filename = post.url[filename_start:]

    output_path = str(output_dir) + filename

    with open(output_path, "wb") as handle:
        response = requests.get(post.url, stream=True)
        if not response.ok:
            print(response)
            return False

        for block in response.iter_content(1024):
            if not block:
                break
            handle.write(block)

    return True


def main():
    """Main entry point of the program."""

    reddit = praw.Reddit("reddit-wall")

    subreddits = get_subreddits(reddit)
    subs = reddit.subreddit('+'.join(subreddits))
    limit = int(CONFIG["Downloads"]["PostLimit"])
    allow_nsfw = CONFIG["Downloads"].getboolean("AllowNSFW")

    # There doesn't seem to be a way to specify a nsfw filter for subs.hot(),
    # so we have to keep track of when we skip posts.
    posts = []
    for submission in subs.hot():
        if not allow_nsfw and submission.over_18:
            continue
        
        posts.append(submission)
        if len(posts) > limit:
            break

    imgur = ImgurDownloader()
    for post in posts:
        if "imgur.com/a/" in post.url:
            imgur.download_album(post.url)
        else:
            download_post_image(post)


if __name__ == "__main__":
    main()
