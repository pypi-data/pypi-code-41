from utils.mail import handlers


def referral_reward_acquired_handler(sender, user_from, reward_data, *args, **kwargs):
    kwargs = {
        'reward_name': reward_data.get('rewardName'),
        'reward_description': reward_data.get('rewardDescription'),
        'user_email': user_from.email,
        'user_full_name': user_from.full_name
    }

    handlers.mail_handler.send_mail(
        'referral_reward_acquired',
        recipients=['finance@openexo.com', 'kevin@openexo.com'],
        **kwargs)
