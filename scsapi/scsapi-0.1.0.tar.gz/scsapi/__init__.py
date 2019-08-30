"""An API to connect to and browse SpeedCubeShop.
Created by MysteryBlokHed in 2019."""
import requests
from requests.models import Response
from bs4 import BeautifulSoup
import configparser
import copy

from .product import Product
from .address import Address
from .order import BasicOrder

class SCS(object):
    _headers = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"}
    _form_data = {"form_type": "customer_login", "utf-8": "✓"}
    _address_form_data = {"form_type": "customer_address", "utf-8": "✓"}

    _user_data = {}

    def __init__(self, section=None, **kwargs):
        """
        Args:
        section (str) - Will look for a section with this name in scsapi.ini. Fields are email, password, and optionally user_agent.

        kwargs:
        email (str) - The email to use when logging in.
        password (str) - The password to use when logging in.
        user_agent (str) - The useragent to use when connecting.
        """
    # Read INI
        if section is not None:
            config = configparser.ConfigParser()
            config.read("scsapi.ini")
            # Check if the section exists:
            try:
                config[section]
            except KeyError as e:
                raise KeyError(f"Could not find section {e} in scsapi.ini")
            # Get data from the ini
            try:
                self._form_data["customer[email]"] = config[section]["email"]
                self._user_data["email"] = config[section]["email"]
                self._form_data["customer[password]"] = config[section]["password"]
            except KeyError as e:
                print(f"Could not find {e} in scsapi.ini")
            # Get optional user_agent field
            try:
                self._headers["user-agent"] = config[section]["user_agent"]
            except KeyError:
                pass
        # Read kwargs
        else:
            try:
                self._form_data["customer[email]"] = kwargs["email"]
                self._user_data["email"] = kwargs["email"]
                self._form_data["customer[password]"] = kwargs["password"]
            except KeyError as e:
                raise KeyError(f"Missing key {e}.")
            try:
                self._headers["user-agent"] = kwargs["user_agent"]
            except KeyError:
                pass
    
    def login(self):
        """Connect to SCS with the provided email and password."""
        request_url = "https://speedcubeshop.com/account/login"
        self._s = requests.Session()

        r = self._s.post(request_url, data=self._form_data, headers=self._headers)
        if r.status_code == 200:
            print("Login successful!")
        else:
            print("Login failed.")
    
    def _get_page_products(self, soup):
        products = []

        NoneType = type(None)

        if type(soup) is not NoneType:
            for product in soup:
                product = product.find("div", {"class": "product-item"})
                if type(product) == NoneType:
                    valid = False
                else:
                    valid = True

                if valid:
                    name = product.find("a", {"class": "product-title"}).find("span").get_text().strip()
                    image = "https:" + product.find("a", {"class": "product-grid-image"}).find("img")["src"]

                    product_url = "https://speedcubeshop.com" + product.find("a", {"class": "product-grid-image"})["href"]
                    price = product.find("span", {"class": "special-price"})

                    if type(price) is not NoneType:
                        price = price.find("span", {"class": "money"}).get_text()
                    else:
                        price = product.find("span", {"class": "money"}).get_text()

                    try:
                        review_score = product.find("span", {"class": "spr-badge"})["data-rating"]
                        review_count = product.find("span", {"class": "spr-badge-caption"}).get_text().split()[0]
                    except TypeError:
                        review_score = None
                        review_count = None

                    # products.append({"name": name, "image": image, "product_url": product_url, "price": price, "review_score": review_score, "review_count": review_count}) # OLD METHOD
                    products.append(Product(name, image, product_url, price, review_score, review_count))
            
        return products

    def get_category(self, cat="", page=1):
        """
        Find at all products from a certain category on a given page.

        Args:
        cat (str) - The main category to search for (eg. wca-puzzles, 2x2, square-1, lubricant, all)
        page (int) - The page of results to view.

        Returns:
        list - A list of Product classes (scsapi.product.Product).
        Each instance will have the keys name, image, product_url, price, review_score, and review_count,
        which can be accessed as if the instance were a dictionary.
        
        review_score and review_count do not work yet.

        Will return an empty list if there are no products for that category/page.
        """
        search_url = "https://speedcubeshop.com/collections/"
        # Sometimes the categories have werid different names
        if cat == "square-1":
            cat = "square-2"
        elif cat == "megaminx":
            cat = "megaminx-1"
        elif cat == "skewb":
            cat = "skewb-1"
        elif cat == "8x8":
            cat = "8x8-plus"
        elif cat == "all":
            cat = "more-puzzles"
        search_url += cat
        search_url += "?page="+str(page)

        r = self._s.get(search_url, headers=self._headers)
        soup = BeautifulSoup(r.content, "html.parser")

        # Find all the products on the page
        try:
            products_soup = soup.find("div", {"class": "product-collection"}).find_all("div")
        except AttributeError:
            return None
        
        if products_soup is not None:
            return self._get_page_products(products_soup)

    def get_sales(self, page=1):
        """
        Get the current sales.

        Args:
        page(int) - The page of results to view.

        Returns:
        list - A list of Product classes (scsapi.product.Product).
        Each instance will have the keys name, image, product_url, price, review_score, and review_count,
        which can be accessed as if the instance were a dictionary.
        
        review_score and review_count do not work yet.

        Will return an empty list if there are no products for that category/page.
        """
        return self.get_category("on-sale", page)
    
    def get_new(self, page=1):
        """
        Get the new arrivals.

        Args:
        page(int) - The page of results to view.

        Returns:
        list - A list of Product classes (scsapi.product.Product).
        Each instance will have the keys name, image, product_url, price, review_score, and review_count,
        which can be accessed as if the instance were a dictionary.
        
        review_score and review_count do not work yet.

        Will return an empty list if there are no products for that category/page.
        """
        return self.get_category("new-arrivals", page)

    def search(self, query, page=1):
        """
        Search SCS.

        Args:
        query (str) - What to search for. Words can be separated by spaces or by pluses.
        page (int) - The page of results to view.

        Returns:
        list - A list of Product classes (scsapi.product.Product).
        Each instance will have the keys name, image, product_url, price, review_score, and review_count,
        which can be accessed as if the instance were a dictionary.

        review_score and review_count do not work yet.

        Will return an empty list if there are no products for that category/page.
        """
        search_url = "https://speedcubeshop.com/search?page="+str(page)
        query = "+".join(query.split())
        search_url += "&q="+query
        search_url += "&type=product"

        r = self._s.get(search_url, headers=self._headers)
        soup = BeautifulSoup(r.content, "html.parser")
        
        # Find all the products on the page
        try:
            products_soup = soup.find("div", {"class": "products-grid"}).find_all("div")
        except AttributeError:
            return None
        
        if products_soup is not None:
            return self._get_page_products(products_soup)

    def get_addresses(self):
        """
        [Currently Non-Functional]
        Get all saved addresses from the Address Book.

        Returns:
        list - A list of Address classes (scsapi.address.Address).
        Each instance will have the functions 
        """
        url = "https://speedcubeshop.com/account/addresses"
        
        r = self._s.get(url, headers=self._headers)
        soup = BeautifulSoup(r.content, "html.parser")

        addresses_soup = soup.find("div", {"class": "box-address-book"}).find_all("div", {"class": "clearfix"})

        addresses = []

        for address in addresses_soup:
            # Get the address ID for editing
            address_id = address.find("div")
            if type(address_id) is not type(None):
                address_id = address_id["id"].strip("edit_address_")

                info = address.find("p")

                name = info.find("strong").get_text()

    def add_address(self, fname, lname, address, city, country, province, zip_code, phone, address2=None, company=None, set_default=False):
        """
        Add an address to the account.

        Args:
        fname (str) - First name for the address.
        lname (str) - Last name for the address.
        address (str) - Address line 1.
        city (str) - City for the address.
        country (str) - Country for the address.
        province (str) - Province/State for the address.
        zip_code (str) - ZIP/Postal Code for the address.
        phone (str) - Phone number for the address.
        address2 (str) - Address line 2.
        company (str) - Company for the address. Should be written exactly as it is on SCS.
        set_default (bool) - Whether or not to make this the default address.

        Returns:
        bool - True if it worked, and False if it didn't.
        """
        self._address_form_data["address[first_name]"] = fname
        self._address_form_data["address[last_name]"] = lname
        self._address_form_data["address[address1]"] = address
        self._address_form_data["address[city]"] = city
        self._address_form_data["address[country]"] = country
        self._address_form_data["address[province]"] = province
        self._address_form_data["address[zip]"] = zip_code
        self._address_form_data["address[phone]"] = phone

        if address2 is not None:
            self._address_form_data["address[address2]"] = address2
        if company is not None:
            self._address_form_data["address[company]"] = company

        if set_default:
            self._address_form_data["address[default]"] = "1"

        request_url = "https://speedcubeshop.com/account/addresses"
        r = self._s.post(request_url, data=self._address_form_data, headers=self._headers)
    
    def get_order_history(self):
        """
        Get a list of past orders.

        Returns:
        list - A list of BasicOrder classes (scsapi.order.BasicOrder).
        Each instance will have the keys number, order_id, date, payment_status, fulfillment_status, and total,
        which can be accessed as if the instance were a dictionary.

        Will return an empty list if there are no orders found.
        """
        url = "https://speedcubeshop.com/account"
        r = self._s.get(url, headers=self._headers)
        soup = BeautifulSoup(r.content, "html.parser")

        orders_soup = soup.find("table", {"class": "full"}).find_all("tr")[1:]

        orders = []

        for order in orders_soup:
            number = int(order.find("a").get_text().strip("#"))
            order_id = order.find("a")["href"].split("/")[-1]
            
            items = order.find_all("td")

            date = items[1].get_text()
            payment_status = items[2].get_text()
            fulfillment_status = items[3].get_text()

            total = order.find("span", {"class": "money"}).get_text()

            orders.append(BasicOrder(number, order_id, date, payment_status, fulfillment_status, total))
        
        return orders

    def add_to_cart(self, item_id, quantity=1, **kwargs):
        """[Currently Non-Functional]
        Add an item to your cart."""
        request_url = "https://speedcubeshop.com/cart/add.js"

    def checkout(self):
        """[Currently Non-Functional]
        Proceed to checkout."""
        pass

    def logout(self):
        """Log out of SCS without closing the session."""
        logout_url = "https://speedcubeshop.com/account/logout"
        self._s.get(logout_url, headers=self._headers)
        print("Logged out.")
    
    def close_no_logout(self):
        """Close the session without logging out."""
        self._s.close()
        print("Closed session.")

    def close(self):
        """Log out of SCS and close the session."""
        self.logout()
        self.close_no_logout()