from requests import post

url = "https://wpg1psint001.linux.wmic.ins:8001/log/pub"

def publish(**kwargs):
    """
    sends data based on input to centralized source
    """
    noval = "no_data"
    payload = {
        "tool_name": kwargs.get("tool_name"),
        "event_type": kwargs.get("event_type"),
        "source_host": kwargs.get("source_host", noval),
        "dest_host": kwargs.get("dest_host", noval),
        "username": kwargs.get("username", noval)
    }
    try:
        r = post(url, verify=False, json=payload)
        if r.ok:
            return True
        else:
            return False
    except Exception as e:
        print(f"Exception: {e}")