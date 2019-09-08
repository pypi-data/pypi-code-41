from seiutils import linkutils
import html
import logging


logger = logging.getLogger(__name__)
TWITTER_URL = r'https://twitter.com/'


def get_uploaded_links(status):
    logger.info(f'Getting uploaded links for status {status.id}')
    links = []
    links.extend(get_uploaded_media(status))
    links.extend(get_urls(status))

    return links


def get_text(status):
    logger.info(f'Getting text for status {status.id}')
    status = get_status(status)
    try:
        text = status.extended_tweet['full_text']
    except AttributeError:
        try:
            text = status.full_text
        except AttributeError:
            text = status.text

    return html.unescape(text)


def get_status(status):
    if is_retweet(status):
        return get_status(status.retweeted_status)

    return status


def get_uploaded_media(status):
    logger.info(f'Getting uploaded media for status {status.id}')
    links = []
    video_link = get_uploaded_video(status)

    if video_link is not None:
        links.append(video_link)

    links.extend(get_uploaded_images(status))

    return links


def get_uploaded_video(status):
    logger.info(f'Getting uploaded video for status {status.id}')
    medias = get_media_entities(status)

    for media in medias:
        if media['type'] == 'video':
            videos = media['video_info']['variants']
            bitrate = 0
            index = 0
            for i in range(0, len(videos)):
                if videos[i]['content_type'] == 'video/mp4':
                    br = int(videos[i]['bitrate'])
                    if br > bitrate:
                        bitrate = br
                        index = i

            return videos[index]['url']

    return None


def get_all_images(status):
    logger.info(f'Getting all images for status {status.id}')
    links = []
    links.extend(get_uploaded_images(status))
    links.extend(get_external_images(status))
    return links


def get_uploaded_images(status):
    logger.info(f'Getting uploaded images for status {status.id}')
    links = []
    medias = get_media_entities(status)

    try:
        for media in medias:
            if not media['type'] == 'video':
                links.append(media['media_url'])
    except KeyError:
        pass

    return links


def get_external_images(status):
    logger.info(f'Getting external images for status {status.id}')
    links = []
    urls = get_urls(status)

    try:
        for link in urls:
            ext = link['expanded_url']
            links.extend(linkutils.get_images(ext))
    except KeyError:
        pass

    return links


def get_media_entities(status):
    logger.info(f'Getting media entities for status {status.id}')
    status = get_status(status)

    try:
        try:
            e_status = status.extended_tweet
            return e_status['extended_entities']['media']
        except AttributeError:
            return status.extended_entities['media']
    except (AttributeError, KeyError):
        return []


def get_urls(status):
    logger.info(f'Getting uploaded urls for status {status.id}')
    status = get_status(status)

    try:
        return status.entities['urls']
    except (AttributeError, KeyError, IndexError):
        return []


def get_category(status):
    text = get_text(status)

    cat = text.split('】')[0][1:]
    return cat


def make_url(username):
    return TWITTER_URL + username


def is_reply(status):
    return status.in_reply_to_user_id is not None and status.in_reply_to_user_id != status.user.id


def is_retweet(status):
    return hasattr(status, 'retweeted_status')


def strip_retweets(tweets):
    stripped = list()
    for tweet in tweets:
        if not is_retweet(tweet):
            stripped.append(tweet)

    return stripped


def strip_replies(tweets):
    stripped = list()
    for tweet in tweets:
        if not is_reply(tweet):
            stripped.append(tweet)

    return stripped
