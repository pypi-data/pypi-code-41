from ..models import Campaign
from ..signals_define import referral_reward_acquired
from .referral_reward import referral_reward_acquired_handler


def setup_signals():
    referral_reward_acquired.connect(referral_reward_acquired_handler, sender=Campaign)
