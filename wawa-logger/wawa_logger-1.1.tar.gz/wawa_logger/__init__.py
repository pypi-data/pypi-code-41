from requests import post

url = "http://wpg1psint001.linux.wmic.ins:8001/log/pub"

def publish(**kwargs):
    """
    sends data based on input to centralized source

    params
    :tool_name
    :event_type
    :source_host
    :dest_host
    :username
    returns
    :bool True|False
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
        r = post(url, json=payload)
        if r.ok:
            return True
            print(r.ok)
        else:
            return False
            print(r.status_code)
    except Exception as e:
        print(f"Exception: {e}")