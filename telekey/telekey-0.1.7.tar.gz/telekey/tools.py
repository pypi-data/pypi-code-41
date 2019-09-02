

def is_authenticated(bot, channel_username, user_id):
    return bot.get_chat_member(channel_username, user_id)['status'] == 'member'
