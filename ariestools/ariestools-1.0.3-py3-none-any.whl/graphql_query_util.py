import requests


def graphql_query(query_url: str, payload: dict):
    res = requests.post(
        url=query_url,
        json=payload,
        headers={'content-type': 'application/json'}
    )

    if res.status_code != 200:
        raise Exception(res.text)
    else:
        return res.json()
