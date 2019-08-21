from lxml import html
import requests

BASE_URL = "https://www.sec.gov"


class Company:
    """
    Used for downloading filings for a particular company.
    """

    def __init__(self, name, cik):
        self.name = name
        self.cik = cik

    def get_filings_url(self, filing_type="", prior_to="", ownership="include", no_of_entries=100):
        url = "https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=" + self.cik + "&type=" + filing_type + \
              "&dateb=" + prior_to + "&owner=" + ownership + "&count=" + str(no_of_entries)
        return url

    def get_all_filings(self, filing_type="", prior_to="", ownership="include", no_of_entries=100):
        page = requests.get(self.get_filings_url(filing_type, prior_to, ownership, no_of_entries))
        return html.fromstring(page.content)


class Edgar:
    """
    Used for getting companies.
    """

    def __init__(self):
        all_companies_page = requests.get("https://www.sec.gov/Archives/edgar/cik-lookup-data.txt")
        all_companies_content = all_companies_page.content.decode("latin1")
        all_companies_array = all_companies_content.split("\n")
        del all_companies_array[-1]
        all_companies_array_rev = []
        for i, item in enumerate(all_companies_array):
            if item == "":
                continue
            item_arr = item.split(":")
            all_companies_array[i] = (item_arr[0], item_arr[1])
            all_companies_array_rev.append((item_arr[1], item_arr[0]))
        self.all_companies_dict = dict(all_companies_array)
        self.all_companies_dict_rev = dict(all_companies_array_rev)

    def get_cik_by_company_name(self, name):
        return self.all_companies_dict[name]

    def get_company_name_by_cik(self, cik):
        return self.all_companies_dict_rev[cik]

    def find_company_name(self, words):
        possibleCompanies = []
        words = words.lower()
        for company in self.all_companies_dict:
            if all(word in company.lower() for word in words.split(" ")):
                possibleCompanies.append(company)
        return possibleCompanies
        

class Filing:
    """
    Class which allows downloading of filing and contains filing metadata.
    """
    main_xpath = '//*[@id="formDiv"]/div/table/tr[2]/td[3]/a'

    def __init__(self, elem):
        self.url = BASE_URL + elem.attrib["href"]
        self.elem = _get_request_as_html_obj(self.url)

    @property
    def text_content(self):
        return self._get_text_content_by_link_xpath(self.main_xpath)

    @property
    def content(self):
        return self._get_html_by_link_xpath(self.main_xpath)

    @property
    def filing_date(self):
        return self._get_filing_info('Filing Date')

    @property
    def accepted(self):
        return self._get_filing_info('Accepted')

    @property
    def period_of_report(self):
        return self._get_filing_info('Period of Report')

    def sub_filing(self, sub_document, as_html = False):
        xpath = '//*[@id="formDiv"]/div/table/tr[td[4]/text()="{sub_document}"]/td[3]/a'.format(
            sub_document=sub_document
        )
        if as_html:
            return self._get_html_by_link_xpath(xpath)
        return self._get_text_content_by_link_xpath(xpath)

    def _get_content_by_link_xpath(self, xpath):
        url = BASE_URL + self.elem.xpath(xpath)[0].attrib["href"]
        content = _get_request_as_html_obj(url)
        return content

    def _get_text_content_by_link_xpath(self, xpath):
        content = self._get_content_by_link_xpath(xpath)
        return content.body.text_content()

    def _get_html_by_link_xpath(self, xpath):
        content = self._get_content_by_link_xpath(xpath)
        return html.tostring(content).decode('utf8')

    def _get_filing_info(self, info_str):
        info_xpath = '//*[@id="formDiv"]//div[@class="formGrouping"]/div[preceding-sibling::div[1]/' \
                     'text()="{info_str}"]/text()'.format(info_str=info_str)
        return self.elem.xpath(info_xpath)[0]


def _get_request_as_html_obj(href):
    page = requests.get(href)
    return html.fromstring(page.content)


def get_documents(tree, sub_document=None, no_of_documents=1, as_html=False):
    filings = get_filings(tree, no_of_documents=no_of_documents)
    if sub_document is None:
        if as_html:
            attr = 'content'
        else:
            attr = 'text_content'
        result = [getattr(filing, attr) for filing in filings]
    else:
        result = [filing.sub_filing(sub_document, as_html=as_html) for filing in filings]

    if len(result) == 1:
        return result[0]
    return result


def get_filings(tree, no_of_documents=1):
    elems = tree.xpath('//*[@id="documentsbutton"]')[:no_of_documents]
    return [Filing(elem) for elem in elems]


def _get_sub_document_xpath(sub_document=None):
    if sub_document is None:
        return '//*[@id="formDiv"]/div/table/tr[2]/td[3]/a'

    return '//*[@id="formDiv"]/div/table/tr[td[4]/text()="{sub_document}"]/td[3]/a'.format(sub_document=sub_document)


def get_cik_from_company(companyName):
    tree = _get_request_as_html_obj("https://www.sec.gov/cgi-bin/browse-edgar?company=" + companyName)
    CIKList = tree.xpath('//*[@id="seriesDiv"]/table/tr[*]/td[1]/a/text()')
    namesList = []
    for elem in tree.xpath('//*[@id="seriesDiv"]/table/tr[*]/td[2]'):
        namesList.append(elem.text_content())
    return list(zip(CIKList, namesList))

