"""Reddit post handler.

This module handles parsing subreddits and multireddits.
It also handles downloading images from submissions.
"""

import pathlib
import requests
import praw
from config import CONFIG
from imgurdownloader import ImgurDownloader


class RedditHandler:
    """The reddit handler.

    Attributes
    ----------
    reddit : praw.reddit
        A connection to the reddit api.
    imgur : ImgurDownloader
        Handler for downloading images from Imgur.
    subreddits : list
        List of reddit.subreddit objects that will be parsed.
    multireddits : list
        List of reddit.multireddit objects that will be parsed.
    allow_nsfw : bool
        Whether to parse subreddits or submissions marked NSFW.
    output_dir : string
        The directory where images will be saved.

    """

    #FIXME: Check if praw.ini exists and allow user to specify creds at runtime.
    def __init__(self):
        self.reddit = praw.Reddit("reddit-wall")
        self.imgur = ImgurDownloader(CONFIG["Imgur"]["client_id"],
                                     CONFIG["Imgur"]["client_secret"])

        self.subreddits = []
        self.multireddits = []

        self.allow_nsfw = CONFIG["Downloads"].getboolean("AllowNSFW")
        self.output_dir = CONFIG["Downloads"]["OutputDirectory"]


    def add_subreddit(self, name):
        """Add a subreddit for the handler to manage.

        Parameters
        ----------
        name : string
            Name of the subreddit to add.

        """

        subreddit = self.reddit.subreddit(name)
        if not self.allow_nsfw and subreddit.over18:
            return

        self.subreddits.append(subreddit)


    def add_multireddit(self, user, name):
        """Add a multireddit for the handler to manage.

        Parameters
        ----------
        user : string
            Username of the owner of the multireddit.

        name : string
            Name of the multireddit.

        """

        multireddit = self.reddit.multireddit(user, name)
        if not self.allow_nsfw and multireddit.over_18:
            return

        self.multireddits.append(multireddit)


    def combined_subreddits(self):
        """Generate a string representing all subreddits being handled.

        On reddit, subs can be combined by adding '+' between the names.
        This effectively acts as one large subreddit.

        Returns
        -------
        combo_str : string
            String listing all subreddits being handled.

        """

        subs = [sub.display_name.lower() for sub in self.subreddits]

        for multireddit in self.multireddits:
            for subreddit in multireddit.subreddits:
                subs.append(subreddit.display_name.lower())

        subs = set(subs)
        combo_str = '+'.join(subs)

        return combo_str


    def valid_submission(self, submission):
        """Check if the given submission has images that can be downloaded.

        Parameters
        ----------
        submission : praw.models.submission
            The submission to check.

        Returns
        -------
        valid : bool
            Whether the submission has downloadable images.

        """

        image_types = (".png", ".jpg", ".jpeg", ".gif")

        is_self = submission.is_self
        is_image = submission.url.endswith(image_types)
        is_album = "imgur.com/a/" in submission.url
        is_gallery = "imgur.com/gallery/" in submission.url

        if not self.allow_nsfw and submission.over_18:
            is_age_appropriate = False
        else:
            is_age_appropriate = True

        return (is_self or is_image or is_album or is_gallery) and is_age_appropriate


    def download_submission_image(self, submission):
        """Download the image associated with the given reddit submission.

        Parameters
        ----------
        submission : praw.models.submission
            The submission to download an image from.

        """

        if not self.valid_submission(submission):
            return False

        # FIXME: Check file permissions when attempting to create directory
        output_dirpath = pathlib.Path(self.output_dir).expanduser()
        if str(output_dirpath) == '.':
            output_dirpath = pathlib.Path.cwd()  # Get the absolute path
        if not output_dirpath.exists():
            output_dirpath.mkdir(parents=True)

        if "imgur.com/a/" in submission.url:
            return self.imgur.download_album(submission.url, output_dirpath)
        if "imgur.com/gallery/" in submission.url:
            return self.imgur.download_gallery(submission.url, output_dirpath)

        filename = submission.url[submission.url.rfind('/'):]
        output_filepath = str(output_dirpath) + filename

        with open(output_filepath, "wb") as handle:
            response = requests.get(submission.url, stream=True)
            if not response.ok:
                print(response)
                return False

            for block in response.iter_content(1024):
                if not block:
                    break
                handle.write(block)

        return True
