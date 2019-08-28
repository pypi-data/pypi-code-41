from bs4 import BeautifulSoup
import requests
from time import sleep
from pathlib import Path
import tempfile

def fetch_currencies(useTmpDir=False, ephemeral=False, **kwargs):
    """ Download every new foreign exchange rate available 
        
        :param useTmpDir: Use a tempfs, don't persist. If set, ephemeral
                          must also be True
        :param ephemeral: As soon as all currencies have beed fetched, attempt
                          to post directly to an sandbox using postFx. This is 
                          needed because python tempfile/dirs are automatically
                          deleted after completion of the tempfule context.
        :return: Path to currencies directory (either tmp or persistant)
    """

    html_doc = requests.get("http://www.floatrates.com/json-feeds.html")

    soup = BeautifulSoup(html_doc.text, "html.parser")

    download_links = []
    for link in soup.find_all("a"):
        try:
            if link["href"] and ".json" in link["href"]:
                download_links.append(link["href"])
        except:
            pass
    if useTmpDir: # Prepare temp directory to store currencies & exchange rates
      tmpdir = tempfile.TemporaryDirectory()

    # Download each currency conversion into list
    currencies = {}
    for target in download_links:
        try:
            # Get currency code
            currency_code = target.split("daily/")[1].split(".json")[0]
            resp = requests.get(target)
            currencies[currency_code] = resp.text
            print("Fetching {}".format(currency_code))
            # Write to file or tmpdir
            if useTmpDir:
              path = tmpdir.name
              filePath = Path(tmpdir.name, '{}.json'.format(currency_code))
            else: 
              path = "./currencies"
              filePath = Path("./currencies/{}.json".format(currency_code))
            with open(filePath, "w") as f:
                f.write(resp.text)
        except:
            raise
    return Path(path)


if __name__ == "__main__":
    fetch_currencies()
