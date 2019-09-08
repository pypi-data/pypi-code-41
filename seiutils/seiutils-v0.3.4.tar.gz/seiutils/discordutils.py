from seiutils import twitutils
import discord
import html
import logging

logger = logging.getLogger(__name__)


def text_tweet(status):
    logger.info(f'Converting tweet {status.id} into text')
    user = status.user.name
    text = status.text
    send = f"Tweet by {user}: {text}\n"
    try:
        for media in status.extended_entities['media']:
            send += media['media_url'] + ' '
    except AttributeError:
        pass

    return send


def embed_tweet(status):
    logger.info(f'Embedding tweet {status.id}')

    user = status.user
    username = html.unescape(status.user.screen_name)
    name = html.unescape(user.name) + ' (@' + username + ')'
    title = f"Tweet by {html.unescape(user.name)}"
    footer = str(status.created_at) + ' UTC'

    description = ''
    if twitutils.is_retweet(status):
        description += html.unescape(f'RT {html.unescape(twitutils.get_status(status).user.screen_name)}: {twitutils.get_text(status)}')
    else:
        description += twitutils.get_text(status)

    logger.info(f'Title: {title}')
    logger.info(f'Description: {description}')

    video = twitutils.get_uploaded_video(status)

    if video is not None:
        logger.info('Adding video to embed')
        embed = discord.Embed(video=video, description=description, title=title)
        embed.add_field(name='Media', value=video)
    else:
        logger.info('Adding images to embed')
        embed = discord.Embed(description=description, title=title)
        images = twitutils.get_all_images(status)
        if len(images) > 0:
            embed.set_image(url=images[0])

            text = ''

            count = 0
            fields = 1
            for i in range(len(images)):
                if len(text) < 1500 and count < 4:
                    text += make_url(str(count + 1), images[i]) + ' '
                    count += 1
                else:
                    embed.add_field(name=f'Media {fields}', value=text)
                    text = ''
                    count = 0
                    fields += 1

            if len(text) > 0:
                if fields == 1:
                    field_name = 'Media'
                else:
                    field_name = 'Media ' + str(fields)
                embed.add_field(name=field_name, value=text)

    embed.set_author(name=name, url=twitutils.make_url(username), icon_url=user.profile_image_url)
    embed.set_footer(text=footer, icon_url=user.profile_image_url)

    return embed


def make_url(text: str, url: str):
    return f'[{text}]({url})'



