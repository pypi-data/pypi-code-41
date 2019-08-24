"""Imgur download handler.

This module handles downloading images, albums, and galleries from Imgur.
"""

import pathlib
import requests
from imgurpython import ImgurClient


class ImgurDownloader:
    """Handler for Imgur downloads.

    Attributes
    ----------
    client : ImgurClient
        Instance of an Imgur API connection.

    """

    def __init__(self, client_id, client_secret):
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

        # Remove the file extension if it exists.
        extension_index = imgur_id.find('.')
        if extension_index != -1:
            imgur_id = imgur_id[:extension_index]

        return imgur_id


    #FIXME: Add error checking
    def download_album(self, url, output_dirpath):
        """Downloads the imgur album from the given url.

        Parameters
        ----------
        url : string
            URL for the imgur album.

        output_dirpath : pathlib.Path
            Path to the directory for saving images.

        Returns
        -------
        success : bool
            Whether the album downloaded successfully.

        """

        if "imgur.com/a/" not in url:
            return False


        imgur_id = self.get_imgur_id(url)
        album = self.client.get_album(imgur_id)

        # Create a directory for just the album.
        output_dir_str = str(output_dirpath)
        if not output_dir_str.endswith('/'):
            output_dir_str = output_dir_str + '/'

        if album.title:
            output_dir_str = output_dir_str + album.title + '/'
        else:
            output_dir_str = output_dir_str + imgur_id + '/'

        output_dirpath = pathlib.Path(output_dir_str)
        output_dirpath.mkdir(parents=True, exist_ok=True)

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


        # FIXME: Implement this
        def download_gallery(self, url, output_path):
            return False
