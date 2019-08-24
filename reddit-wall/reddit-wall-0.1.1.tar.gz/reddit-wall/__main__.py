from reddithandler import RedditHandler
from config import CONFIG

def main():
    """Main entry point of the program."""

    reddit = RedditHandler()

    for name in CONFIG.options("Subreddits"):
        reddit.add_subreddit(name)

    multi_list = [tuple(m.split()) for m in CONFIG.options("Multireddits")]
    for user, multi in multi_list:
        reddit.add_multireddit(user, multi)

    all_subs = reddit.combined_subreddits()
    submission_limit = int(CONFIG["Downloads"]["Postlimit"])
    download_count = 0

    for submission in reddit.reddit.subreddit(all_subs).hot():
        if reddit.download_submission_image(submission):
            download_count += 1

        if download_count > submission_limit:
            break


if __name__ == "__main__":
    main()
