class WebhookEvents(object):
    ACCESS_GRANTED = 'access_granted'
    ACCESS_MODIFIED = 'access_modified'
    ACCESS_REVOKED = 'access_revoked'
    TERM_CHANGED = 'term_changed'


class WebhookEventTypes(object):
    # Access Granted
    NEW_PURCHASE = 'new_purchase'
    PAYMENT_VERIFIED = 'payment_verified'
    FREE_PROMO_REDEMPTION = 'free_promo_redemption'
    NEW_REGISTRATION_CONVERSION = 'new_registration_conversion'
    FREE_ACCESS_GRANTED = 'free_access_granted'

    # Access Modified
    SUBSCRIPTION_UPDATED = 'subscription_updated'
    SUBSCRIPTION_AUTO_RENEWED = 'subscription_auto_renewed'
    SUBSCRIPTION_MANUALLY_RENEWED = 'subscription_manually_renewed'
    ACCESS_MODIFIED = 'access_modified'
    GRACE_PERIOD_EXTENSION_ON_RENEWAL = 'grace_period_extension_on_renewal'

    # Access Revoked
    ACCESS_REVOKED = 'access_revoked'
    SUBSCRIPTION_AUTO_RENEWED_FAILURE = 'subscription_auto_renewed_failure'
    SUBSCRIPTION_CANCELED = 'subscription_canceled'
    SUBSCRIPTION_EXPIRED = 'subscription_expired'
    ACCESS_ENDED = 'access_ended'

    CROSS_APP_ACCESS_GRANTED = 'cross_app_access_granted'
    CROSS_APP_ACCESS_MODIFIED = 'cross_app_access_modified'
    CROSS_APP_ACCESS_REVOKED = 'cross_app_access_revoked'
    KEYING_CONTENT_STATE_UPDATED = 'keying_content_state_updated'
    NEW_BILL_TERM_CONVERSION = 'new_bill_term_conversion'
    NEW_CUSTOM_TERM_CONVERSION = 'new_custom_term_conversion'
    NEW_EXTERNAL_TERM_CONVERISON = 'new_external_term_conversion'
    NEW_GRANT_ACCESS_TERM_CONVERSION = 'new_grant_access_term_conversion'
    NEW_PAYMENT_TERM_CONVERSION = 'new_payment_term_conversion'
    PROVISIONAL_ACCESS_GRANTED = 'provisional_access_granted'
    TERM_APPLIED_BY_PUBLISHER = 'term_applied_by_publisher'
    TERM_CHANGE = 'term_change'
    TO_GIFTEE_VOUCHER_REDEEMED = 'to_giftee_voucher_redeemed'
    VOUCHER_DELIVERY = 'voucher_delivery'
    VOUCHER_PURCHASE = 'voucher_purchase'
    VOUCHER_REVOKED = 'voucher_revoked'
