from autohandshake.src.Pages.Page import Page
from autohandshake.src.HandshakeBrowser import HandshakeBrowser, UserType
from autohandshake.src.constants import BASE_URL
from autohandshake.src.file_download_utils import confirm_file_downloaded
from datetime import datetime


class SurveyPage(Page):
    """
    A survey page in Handshake.
    """

    def __init__(self, survey_id: int, browser: HandshakeBrowser):
        """
        :param survey_id: the id of the survey to load
        :type survey_id: int
        :param browser: a logged-in HandshakeBrowser
        :type browser: HandshakeBrowser
        """
        self._id = survey_id
        super().__init__(f'{BASE_URL}/surveys/{survey_id}', browser)

    @Page.require_user_type(UserType.STAFF)
    def download_responses(self, download_dir: str, wait_time=300) -> str:
        """
        Download a CSV of the survey responses.

        :param download_dir: the directory into which the survey responses will download
        :type download_dir: str
        :param wait_time: the maximum time to wait for the download to appear
        :type wait_time: int
        :return: the file path of the downloaded file
        :rtype: str
        """
        download_btn_xpath = '//a[text()="Download Results (CSV)"]'
        download_link_xpath = '//a[contains(text(), "Your download is ready")]'
        self._browser.wait_then_click_element_by_xpath(download_btn_xpath)
        self._browser.wait_then_click_element_by_xpath(download_link_xpath)
        filename_pattern = self._get_filename_pattern()
        return confirm_file_downloaded(download_dir, filename_pattern, wait_time)

    @staticmethod
    def _get_filename_pattern() -> str:
        """
        Get a regex string describing the form of the downloaded file.
        """
        return f'survey_response_download{datetime.now().strftime("%Y%m%d")}*.csv'

    def _validate_url(self, url):
        """
        Ensure that the given URL is a valid URL.

        Since the URL is not entered by the user, it is always valid.

        :param url: the url to validate
        :type url: str
        """
        return

    def _wait_until_page_is_loaded(self):
        """Wait until the page has finished loading."""
        self._browser.wait_until_element_exists_by_xpath('//div[@class="entity-sidebar tile white"]')
