import pathlib
import requests
from imgurpython import ImgurClient
from config import CONFIG


class ImgurDownloader:

    def __init__(self):
        client_id = CONFIG["Imgur"]["client_id"]
        client_secret = CONFIG["Imgur"]["client_secret"]
        self.client = ImgurClient(client_id, client_secret)

    
    #FIXME: Implement this
    def check_rate_limit(self):
        pass

    
    def get_imgur_id(self, url):
        """Get an Imgur id from a url.
        
        Returns
        -------
        imgur_id : string
            The id of the content at the url.
        
        """

        if "imgur" not in url:
            return None

        imgur_id = url[url.rfind('/') + 1:]

        extension_index = imgur_id.find('.')
        if extension_index != -1:
            imgur_id = imgur_id[:extension_index]

        return imgur_id


    #FIXME: Add error checking
    def download_album(self, url):
        """Downloads the imgur album from the given url.
        
        Parameters
        ----------
        url : string
            URL for the imgur album.

        output_dir : string
            Path to the directory for saving images.
            
        Returns
        -------
        success : bool
            Whether the album downloaded successfully.

        """

        if "imgur.com/a/" not in url:
            return False

        output_dir = pathlib.Path(CONFIG["Downloads"]["OutputDirectory"]).expanduser()
        if str(output_dir) == '.':
            output_dir = pathlib.Path.cwd()  # Get the absolute path
        if not output_dir.exists():
            output_dir.mkdir(parents=True)

        output_dir_str = str(output_dir)
        if not output_dir_str.endswith('/'):
            output_dir_str = output_dir_str + '/'

        imgur_id = self.get_imgur_id(url)
        album = self.client.get_album(imgur_id)

        for image in album.images:
            if type(image) is dict:
                image_id = image["id"]
                image_type = image["type"]
                image_link = image["link"]
            else:
                image_id = image.id
                image_type = image.type
                image_link = image.link
            
            output_filename = output_dir_str + image_id + " - imgur." + image_type[6:]

            with open(output_filename, 'wb') as handle:
                response = requests.get(image_link, stream=True)
                if not response.ok:
                    print(response)
                    return False
                
                for block in response.iter_content(1024):
                    if not block:
                        break
                    handle.write(block)

        return True