from macrobase_driver.hook import HookNames


def sanic_listner_from_hook(hook_name: HookNames) -> str:
    if hook_name.value == HookNames.before_server_start.value:
        return 'before_server_start'
    elif hook_name.value == HookNames.after_server_stop.value:
        return 'after_server_stop'

    return None