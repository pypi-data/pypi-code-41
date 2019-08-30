"""
This file is part of the MerchantAPI package.

(c) Miva Inc <https://www.miva.com/>

For the full copyright and license information, please view the LICENSE
file that was distributed with this source code.

$Id: model.py 77709 2019-08-30 16:41:54Z gidriss $
"""

from merchantapi.abstract import Model

"""
AvailabilityGroup data model.
"""


class AvailabilityGroup(Model):
	def __init__(self, data: dict = None):
		"""
		AvailabilityGroup Constructor

		:param data: dict
		"""

		super().__init__(data)

	def get_id(self) -> int:
		"""
		Get id.

		:returns: int
		"""

		return self.get_field('id', 0)

	def get_name(self) -> str:
		"""
		Get name.

		:returns: string
		"""

		return self.get_field('name')


"""
Customer data model.
"""


class Customer(Model):
	def __init__(self, data: dict = None):
		"""
		Customer Constructor

		:param data: dict
		"""

		super().__init__(data)
		if self.has_field('CustomField_Values'):
			value = self.get_field('CustomField_Values')
			if isinstance(value, CustomFieldValues):
				pass
			elif isinstance(value, dict):
				self.set_field('CustomField_Values', CustomFieldValues(value))
			else:
				raise Exception('Expected CustomFieldValues or a dict')

	def get_id(self) -> int:
		"""
		Get id.

		:returns: int
		"""

		return self.get_field('id', 0)

	def get_account_id(self) -> int:
		"""
		Get account_id.

		:returns: int
		"""

		return self.get_field('account_id', 0)

	def get_login(self) -> str:
		"""
		Get login.

		:returns: string
		"""

		return self.get_field('login')

	def get_password_email(self) -> str:
		"""
		Get pw_email.

		:returns: string
		"""

		return self.get_field('pw_email')

	def get_ship_id(self) -> int:
		"""
		Get ship_id.

		:returns: int
		"""

		return self.get_field('ship_id', 0)

	def get_shipping_residential(self) -> bool:
		"""
		Get ship_res.

		:returns: bool
		"""

		return self.get_field('ship_res', False)

	def get_ship_first_name(self) -> str:
		"""
		Get ship_fname.

		:returns: string
		"""

		return self.get_field('ship_fname')

	def get_ship_last_name(self) -> str:
		"""
		Get ship_lname.

		:returns: string
		"""

		return self.get_field('ship_lname')

	def get_ship_email(self) -> str:
		"""
		Get ship_email.

		:returns: string
		"""

		return self.get_field('ship_email')

	def get_ship_company(self) -> str:
		"""
		Get ship_comp.

		:returns: string
		"""

		return self.get_field('ship_comp')

	def get_ship_phone(self) -> str:
		"""
		Get ship_phone.

		:returns: string
		"""

		return self.get_field('ship_phone')

	def get_ship_fax(self) -> str:
		"""
		Get ship_fax.

		:returns: string
		"""

		return self.get_field('ship_fax')

	def get_ship_address1(self) -> str:
		"""
		Get ship_addr1.

		:returns: string
		"""

		return self.get_field('ship_addr1')

	def get_ship_address2(self) -> str:
		"""
		Get ship_addr2.

		:returns: string
		"""

		return self.get_field('ship_addr2')

	def get_ship_city(self) -> str:
		"""
		Get ship_city.

		:returns: string
		"""

		return self.get_field('ship_city')

	def get_ship_state(self) -> str:
		"""
		Get ship_state.

		:returns: string
		"""

		return self.get_field('ship_state')

	def get_ship_zip(self) -> str:
		"""
		Get ship_zip.

		:returns: string
		"""

		return self.get_field('ship_zip')

	def get_ship_country(self) -> str:
		"""
		Get ship_cntry.

		:returns: string
		"""

		return self.get_field('ship_cntry')

	def get_bill_id(self) -> int:
		"""
		Get bill_id.

		:returns: int
		"""

		return self.get_field('bill_id', 0)

	def get_bill_first_name(self) -> str:
		"""
		Get bill_fname.

		:returns: string
		"""

		return self.get_field('bill_fname')

	def get_bill_last_name(self) -> str:
		"""
		Get bill_lname.

		:returns: string
		"""

		return self.get_field('bill_lname')

	def get_bill_email(self) -> str:
		"""
		Get bill_email.

		:returns: string
		"""

		return self.get_field('bill_email')

	def get_bill_company(self) -> str:
		"""
		Get bill_comp.

		:returns: string
		"""

		return self.get_field('bill_comp')

	def get_bill_phone(self) -> str:
		"""
		Get bill_phone.

		:returns: string
		"""

		return self.get_field('bill_phone')

	def get_bill_fax(self) -> str:
		"""
		Get bill_fax.

		:returns: string
		"""

		return self.get_field('bill_fax')

	def get_bill_address1(self) -> str:
		"""
		Get bill_addr1.

		:returns: string
		"""

		return self.get_field('bill_addr1')

	def get_bill_address2(self) -> str:
		"""
		Get bill_addr2.

		:returns: string
		"""

		return self.get_field('bill_addr2')

	def get_bill_city(self) -> str:
		"""
		Get bill_city.

		:returns: string
		"""

		return self.get_field('bill_city')

	def get_bill_state(self) -> str:
		"""
		Get bill_state.

		:returns: string
		"""

		return self.get_field('bill_state')

	def get_bill_zip(self) -> str:
		"""
		Get bill_zip.

		:returns: string
		"""

		return self.get_field('bill_zip')

	def get_bill_country(self) -> str:
		"""
		Get bill_cntry.

		:returns: string
		"""

		return self.get_field('bill_cntry')

	def get_note_count(self) -> int:
		"""
		Get note_count.

		:returns: int
		"""

		return self.get_field('note_count', 0)

	def get_created_on(self) -> int:
		"""
		Get dt_created.

		:returns: int
		"""

		return self.get_field('dt_created', 0)

	def get_last_login(self) -> int:
		"""
		Get dt_login.

		:returns: int
		"""

		return self.get_field('dt_login', 0)

	def get_credit(self) -> float:
		"""
		Get credit.

		:returns: float
		"""

		return self.get_field('credit', 0.00)

	def get_formatted_credit(self) -> str:
		"""
		Get formatted_credit.

		:returns: string
		"""

		return self.get_field('formatted_credit')

	def get_business_title(self) -> str:
		"""
		Get business_title.

		:returns: string
		"""

		return self.get_field('business_title')

	def get_custom_field_values(self):
		"""
		Get CustomField_Values.

		:returns: CustomFieldValues|None
		"""

		return self.get_field('CustomField_Values', None)

	def set_login(self, login: str) -> 'Customer':
		"""
		Set login.

		:param login: string
		:returns: Customer
		"""

		return self.set_field('login', login)

	def set_password_email(self, password_email: str) -> 'Customer':
		"""
		Set pw_email.

		:param password_email: string
		:returns: Customer
		"""

		return self.set_field('pw_email', password_email)

	def set_shipping_residential(self, shipping_residential: bool) -> 'Customer':
		"""
		Set ship_res.

		:param shipping_residential: bool
		:returns: Customer
		"""

		return self.set_field('ship_res', shipping_residential)

	def set_ship_first_name(self, ship_first_name: str) -> 'Customer':
		"""
		Set ship_fname.

		:param ship_first_name: string
		:returns: Customer
		"""

		return self.set_field('ship_fname', ship_first_name)

	def set_ship_last_name(self, ship_last_name: str) -> 'Customer':
		"""
		Set ship_lname.

		:param ship_last_name: string
		:returns: Customer
		"""

		return self.set_field('ship_lname', ship_last_name)

	def set_ship_email(self, ship_email: str) -> 'Customer':
		"""
		Set ship_email.

		:param ship_email: string
		:returns: Customer
		"""

		return self.set_field('ship_email', ship_email)

	def set_ship_company(self, ship_company: str) -> 'Customer':
		"""
		Set ship_comp.

		:param ship_company: string
		:returns: Customer
		"""

		return self.set_field('ship_comp', ship_company)

	def set_ship_phone(self, ship_phone: str) -> 'Customer':
		"""
		Set ship_phone.

		:param ship_phone: string
		:returns: Customer
		"""

		return self.set_field('ship_phone', ship_phone)

	def set_ship_fax(self, ship_fax: str) -> 'Customer':
		"""
		Set ship_fax.

		:param ship_fax: string
		:returns: Customer
		"""

		return self.set_field('ship_fax', ship_fax)

	def set_ship_address1(self, ship_address1: str) -> 'Customer':
		"""
		Set ship_addr1.

		:param ship_address1: string
		:returns: Customer
		"""

		return self.set_field('ship_addr1', ship_address1)

	def set_ship_address2(self, ship_address2: str) -> 'Customer':
		"""
		Set ship_addr2.

		:param ship_address2: string
		:returns: Customer
		"""

		return self.set_field('ship_addr2', ship_address2)

	def set_ship_city(self, ship_city: str) -> 'Customer':
		"""
		Set ship_city.

		:param ship_city: string
		:returns: Customer
		"""

		return self.set_field('ship_city', ship_city)

	def set_ship_state(self, ship_state: str) -> 'Customer':
		"""
		Set ship_state.

		:param ship_state: string
		:returns: Customer
		"""

		return self.set_field('ship_state', ship_state)

	def set_ship_zip(self, ship_zip: str) -> 'Customer':
		"""
		Set ship_zip.

		:param ship_zip: string
		:returns: Customer
		"""

		return self.set_field('ship_zip', ship_zip)

	def set_ship_country(self, ship_country: str) -> 'Customer':
		"""
		Set ship_cntry.

		:param ship_country: string
		:returns: Customer
		"""

		return self.set_field('ship_cntry', ship_country)

	def set_bill_first_name(self, bill_first_name: str) -> 'Customer':
		"""
		Set bill_fname.

		:param bill_first_name: string
		:returns: Customer
		"""

		return self.set_field('bill_fname', bill_first_name)

	def set_bill_last_name(self, bill_last_name: str) -> 'Customer':
		"""
		Set bill_lname.

		:param bill_last_name: string
		:returns: Customer
		"""

		return self.set_field('bill_lname', bill_last_name)

	def set_bill_email(self, bill_email: str) -> 'Customer':
		"""
		Set bill_email.

		:param bill_email: string
		:returns: Customer
		"""

		return self.set_field('bill_email', bill_email)

	def set_bill_company(self, bill_company: str) -> 'Customer':
		"""
		Set bill_comp.

		:param bill_company: string
		:returns: Customer
		"""

		return self.set_field('bill_comp', bill_company)

	def set_bill_phone(self, bill_phone: str) -> 'Customer':
		"""
		Set bill_phone.

		:param bill_phone: string
		:returns: Customer
		"""

		return self.set_field('bill_phone', bill_phone)

	def set_bill_fax(self, bill_fax: str) -> 'Customer':
		"""
		Set bill_fax.

		:param bill_fax: string
		:returns: Customer
		"""

		return self.set_field('bill_fax', bill_fax)

	def set_bill_address1(self, bill_address1: str) -> 'Customer':
		"""
		Set bill_addr1.

		:param bill_address1: string
		:returns: Customer
		"""

		return self.set_field('bill_addr1', bill_address1)

	def set_bill_address2(self, bill_address2: str) -> 'Customer':
		"""
		Set bill_addr2.

		:param bill_address2: string
		:returns: Customer
		"""

		return self.set_field('bill_addr2', bill_address2)

	def set_bill_city(self, bill_city: str) -> 'Customer':
		"""
		Set bill_city.

		:param bill_city: string
		:returns: Customer
		"""

		return self.set_field('bill_city', bill_city)

	def set_bill_state(self, bill_state: str) -> 'Customer':
		"""
		Set bill_state.

		:param bill_state: string
		:returns: Customer
		"""

		return self.set_field('bill_state', bill_state)

	def set_bill_zip(self, bill_zip: str) -> 'Customer':
		"""
		Set bill_zip.

		:param bill_zip: string
		:returns: Customer
		"""

		return self.set_field('bill_zip', bill_zip)

	def set_bill_country(self, bill_country: str) -> 'Customer':
		"""
		Set bill_cntry.

		:param bill_country: string
		:returns: Customer
		"""

		return self.set_field('bill_cntry', bill_country)

	def set_custom_field_values(self, custom_field_values) -> 'Customer':
		"""
		Set CustomField_Values.

		:param custom_field_values: CustomFieldValues|dict
		:returns: Customer
		:raises Exception:
		"""

		if custom_field_values is None or isinstance(custom_field_values, CustomFieldValues):
			return self.set_field('CustomField_Values', custom_field_values)
		elif isinstance(custom_field_values, dict):
			return self.set_field('CustomField_Values', CustomFieldValues(custom_field_values))
		raise Exception('Expected instance of CustomFieldValues, Object, or None')

	def to_dict(self) -> dict:
		"""
		Reduce the model to a dict.
		"""

		ret = self.copy()

		if 'CustomField_Values' in ret and isinstance(ret['CustomField_Values'], CustomFieldValues):
			ret['CustomField_Values'] = ret['CustomField_Values'].to_dict()

		return ret


"""
Coupon data model.
"""


class Coupon(Model):
	# CUSTOMER_SCOPE constants.
	CUSTOMER_SCOPE_ALL_SHOPPERS = 'A'
	CUSTOMER_SCOPE_SPECIFIC_CUSTOMERS = 'X'
	CUSTOMER_SCOPE_ALL_LOGGED_IN = 'L'

	def __init__(self, data: dict = None):
		"""
		Coupon Constructor

		:param data: dict
		"""

		super().__init__(data)

	def get_id(self) -> int:
		"""
		Get id.

		:returns: int
		"""

		return self.get_field('id', 0)

	def get_code(self) -> str:
		"""
		Get code.

		:returns: string
		"""

		return self.get_field('code')

	def get_description(self) -> str:
		"""
		Get descrip.

		:returns: string
		"""

		return self.get_field('descrip')

	def get_customer_scope(self) -> str:
		"""
		Get custscope.

		:returns: string
		"""

		return self.get_field('custscope')

	def get_date_time_start(self) -> int:
		"""
		Get dt_start.

		:returns: int
		"""

		return self.get_field('dt_start', 0)

	def get_date_time_end(self) -> int:
		"""
		Get dt_end.

		:returns: int
		"""

		return self.get_field('dt_end', 0)

	def get_max_use(self) -> int:
		"""
		Get max_use.

		:returns: int
		"""

		return self.get_field('max_use', 0)

	def get_max_per(self) -> int:
		"""
		Get max_per.

		:returns: int
		"""

		return self.get_field('max_per', 0)

	def get_active(self) -> bool:
		"""
		Get active.

		:returns: bool
		"""

		return self.get_field('active', False)

	def get_use_count(self) -> int:
		"""
		Get use_count.

		:returns: int
		"""

		return self.get_field('use_count', 0)

	def set_code(self, code: str) -> 'Coupon':
		"""
		Set code.

		:param code: string
		:returns: Coupon
		"""

		return self.set_field('code', code)

	def set_description(self, description: str) -> 'Coupon':
		"""
		Set descrip.

		:param description: string
		:returns: Coupon
		"""

		return self.set_field('descrip', description)

	def set_customer_scope(self, customer_scope: str) -> 'Coupon':
		"""
		Set custscope.

		:param customer_scope: string
		:returns: Coupon
		"""

		return self.set_field('custscope', customer_scope)

	def set_date_time_start(self, date_time_start):
		"""
		Set dt_start.

		:param date_time_start: int
		:returns: Coupon
		"""
		return self.set_field('dt_start', date_time_start)

	def set_date_time_end(self, date_time_end):
		"""
		Set dt_end.

		:param date_time_end: int
		:returns: Coupon
		"""
		return self.set_field('dt_end', date_time_end)

	def set_max_use(self, max_use: int) -> 'Coupon':
		"""
		Set max_use.

		:param max_use: int
		:returns: Coupon
		"""

		return self.set_field('max_use', max_use)

	def set_max_per(self, max_per: int) -> 'Coupon':
		"""
		Set max_per.

		:param max_per: int
		:returns: Coupon
		"""

		return self.set_field('max_per', max_per)

	def set_active(self, active: bool) -> 'Coupon':
		"""
		Set active.

		:param active: bool
		:returns: Coupon
		"""

		return self.set_field('active', active)


"""
CustomFieldValues data model.
"""


class CustomFieldValues(Model):
	def __init__(self, data: dict = None):
		"""
		CustomFieldValues Constructor

		:param data: dict
		"""

		super().__init__(data)

	def get_value(self, code: str, module: str = 'customfields'):
		"""
		Get a value for a module by its code.

		:param code: str
		:param module: str
		:returns: mixed
		"""

		return self[module][code] if self.has_value(code, module) else None

	def has_value(self, code: str, module: str = 'customfields'):
		"""
		Check if a value for code and module exists.

		:param code: {string}
		:param module: {string}
		:returns: bool
		"""

		if self.has_field(module):
			return code in self.get_field(module)

	def has_module(self, module: str):
		"""
		Check if a specific module is defined.

		:param module: str
		:returns: boolean
		"""

		return self.has_field(module)

	def get_module(self, module: str):
		"""
		Get a specific modules custom field values.

		:param module: str
		:returns: dict
		"""

		return self.get_field(module, {})

	def set_value(self, field: str, value, module: str = 'customfields') -> 'CustomFieldValues':
		"""
		Add a custom field value.

		:param field: str
		:param value: mixed
		:param module: std
		:returns: CustomFieldValues
		"""

		if not self.has_module(module):
			self.set_field(module, {})
		self[module][field] = value
		return self

	def add_value(self, field: str, value, module: str = 'customfields') -> 'CustomFieldValues':
		"""
		Same as set_value. 

		:param field: str
		:param value: mixed
		:param module: std
		:returns: CustomFieldValues
		"""

		return self.set_value(field, value, module)



"""
Module data model.
"""


class Module(Model):
	def __init__(self, data: dict = None):
		"""
		Module Constructor

		:param data: dict
		"""

		super().__init__(data)

	def get_id(self) -> int:
		"""
		Get id.

		:returns: int
		"""

		return self.get_field('id', 0)

	def get_code(self) -> str:
		"""
		Get code.

		:returns: string
		"""

		return self.get_field('code')

	def get_name(self) -> str:
		"""
		Get name.

		:returns: string
		"""

		return self.get_field('name')

	def get_provider(self) -> str:
		"""
		Get provider.

		:returns: string
		"""

		return self.get_field('provider')

	def get_api_version(self) -> str:
		"""
		Get api_ver.

		:returns: string
		"""

		return self.get_field('api_ver')

	def get_version(self) -> str:
		"""
		Get version.

		:returns: string
		"""

		return self.get_field('version')

	def get_module(self) -> str:
		"""
		Get module.

		:returns: string
		"""

		return self.get_field('module')

	def get_reference_count(self) -> int:
		"""
		Get refcount.

		:returns: int
		"""

		return self.get_field('refcount', 0)

	def get_active(self) -> bool:
		"""
		Get active.

		:returns: bool
		"""

		return self.get_field('active', False)


"""
Note data model.
"""


class Note(Model):
	def __init__(self, data: dict = None):
		"""
		Note Constructor

		:param data: dict
		"""

		super().__init__(data)

	def get_id(self) -> int:
		"""
		Get id.

		:returns: int
		"""

		return self.get_field('id', 0)

	def get_customer_id(self) -> int:
		"""
		Get cust_id.

		:returns: int
		"""

		return self.get_field('cust_id', 0)

	def get_account_id(self) -> int:
		"""
		Get account_id.

		:returns: int
		"""

		return self.get_field('account_id', 0)

	def get_order_id(self) -> int:
		"""
		Get order_id.

		:returns: int
		"""

		return self.get_field('order_id', 0)

	def get_user_id(self) -> int:
		"""
		Get user_id.

		:returns: int
		"""

		return self.get_field('user_id', 0)

	def get_note_text(self) -> str:
		"""
		Get notetext.

		:returns: string
		"""

		return self.get_field('notetext')

	def get_date_time_stamp(self) -> int:
		"""
		Get dtstamp.

		:returns: int
		"""

		return self.get_field('dtstamp', 0)

	def get_customer_login(self) -> str:
		"""
		Get cust_login.

		:returns: string
		"""

		return self.get_field('cust_login')

	def get_business_title(self) -> str:
		"""
		Get business_title.

		:returns: string
		"""

		return self.get_field('business_title')

	def get_admin_user(self) -> str:
		"""
		Get admin_user.

		:returns: string
		"""

		return self.get_field('admin_user')

	def set_customer_id(self, customer_id: int) -> 'Note':
		"""
		Set cust_id.

		:param customer_id: int
		:returns: Note
		"""

		return self.set_field('cust_id', customer_id)

	def set_account_id(self, account_id: int) -> 'Note':
		"""
		Set account_id.

		:param account_id: int
		:returns: Note
		"""

		return self.set_field('account_id', account_id)

	def set_order_id(self, order_id: int) -> 'Note':
		"""
		Set order_id.

		:param order_id: int
		:returns: Note
		"""

		return self.set_field('order_id', order_id)

	def set_note_text(self, note_text: str) -> 'Note':
		"""
		Set notetext.

		:param note_text: string
		:returns: Note
		"""

		return self.set_field('notetext', note_text)


"""
PriceGroup data model.
"""


class PriceGroup(Model):
	# ELIGIBILITY constants.
	ELIGIBILITY_COUPON = 'C'
	ELIGIBILITY_ALL = 'A'
	ELIGIBILITY_CUSTOMER = 'X'
	ELIGIBILITY_LOGGED_IN = 'L'

	def __init__(self, data: dict = None):
		"""
		PriceGroup Constructor

		:param data: dict
		"""

		super().__init__(data)
		if self.has_field('module'):
			value = self.get_field('module')
			if isinstance(value, Module):
				pass
			elif isinstance(value, dict):
				self.set_field('module', Module(value))
			else:
				raise Exception('Expected Module or a dict')

		if self.has_field('capabilities'):
			value = self.get_field('capabilities')
			if isinstance(value, DiscountModuleCapabilities):
				pass
			elif isinstance(value, dict):
				self.set_field('capabilities', DiscountModuleCapabilities(value))
			else:
				raise Exception('Expected DiscountModuleCapabilities or a dict')

	def get_id(self) -> int:
		"""
		Get id.

		:returns: int
		"""

		return self.get_field('id', 0)

	def get_name(self) -> str:
		"""
		Get name.

		:returns: string
		"""

		return self.get_field('name')

	def get_customer_scope(self) -> str:
		"""
		Get custscope.

		:returns: string
		"""

		return self.get_field('custscope')

	def get_discount(self) -> float:
		"""
		Get discount.

		:returns: float
		"""

		return self.get_field('discount', 0.00)

	def get_markup(self) -> float:
		"""
		Get markup.

		:returns: float
		"""

		return self.get_field('markup', 0.00)

	def get_date_time_start(self) -> int:
		"""
		Get dt_start.

		:returns: int
		"""

		return self.get_field('dt_start', 0)

	def get_date_time_end(self) -> int:
		"""
		Get dt_end.

		:returns: int
		"""

		return self.get_field('dt_end', 0)

	def get_minimum_subtotal(self) -> float:
		"""
		Get qmn_subtot.

		:returns: float
		"""

		return self.get_field('qmn_subtot', 0.00)

	def get_maximum_subtotal(self) -> float:
		"""
		Get qmx_subtot.

		:returns: float
		"""

		return self.get_field('qmx_subtot', 0.00)

	def get_minimum_quantity(self) -> int:
		"""
		Get qmn_quan.

		:returns: int
		"""

		return self.get_field('qmn_quan', 0)

	def get_maximum_quantity(self) -> int:
		"""
		Get qmx_quan.

		:returns: int
		"""

		return self.get_field('qmx_quan', 0)

	def get_minimum_weight(self) -> float:
		"""
		Get qmn_weight.

		:returns: float
		"""

		return self.get_field('qmn_weight', 0.00)

	def get_maximum_weight(self) -> float:
		"""
		Get qmx_weight.

		:returns: float
		"""

		return self.get_field('qmx_weight', 0.00)

	def get_basket_minimum_subtotal(self) -> float:
		"""
		Get bmn_subtot.

		:returns: float
		"""

		return self.get_field('bmn_subtot', 0.00)

	def get_basket_maximum_subtotal(self) -> float:
		"""
		Get bmx_subtot.

		:returns: float
		"""

		return self.get_field('bmx_subtot', 0.00)

	def get_basket_minimum_quantity(self) -> int:
		"""
		Get bmn_quan.

		:returns: int
		"""

		return self.get_field('bmn_quan', 0)

	def get_basket_maximum_quantity(self) -> int:
		"""
		Get bmx_quan.

		:returns: int
		"""

		return self.get_field('bmx_quan', 0)

	def get_basket_minimum_weight(self) -> float:
		"""
		Get bmn_weight.

		:returns: float
		"""

		return self.get_field('bmn_weight', 0.00)

	def get_basket_maximum_weight(self) -> float:
		"""
		Get bmx_weight.

		:returns: float
		"""

		return self.get_field('bmx_weight', 0.00)

	def get_priority(self) -> int:
		"""
		Get priority.

		:returns: int
		"""

		return self.get_field('priority', 0)

	def get_module(self):
		"""
		Get module.

		:returns: Module|None
		"""

		return self.get_field('module', None)

	def get_capabilities(self):
		"""
		Get capabilities.

		:returns: DiscountModuleCapabilities|None
		"""

		return self.get_field('capabilities', None)

	def get_exclusion(self) -> bool:
		"""
		Get exclusion.

		:returns: bool
		"""

		return self.get_field('exclusion', False)

	def get_description(self) -> str:
		"""
		Get descrip.

		:returns: string
		"""

		return self.get_field('descrip')

	def get_display(self) -> bool:
		"""
		Get display.

		:returns: bool
		"""

		return self.get_field('display', False)

	def set_customer_scope(self, customer_scope: str) -> 'PriceGroup':
		"""
		Set custscope.

		:param customer_scope: string
		:returns: PriceGroup
		"""

		return self.set_field('custscope', customer_scope)

	def set_discount(self, discount: float) -> 'PriceGroup':
		"""
		Set discount.

		:param discount: int
		:returns: PriceGroup
		"""

		return self.set_field('discount', discount)

	def set_date_time_start(self, date_time_start):
		"""
		Set dt_start.

		:param date_time_start: int
		:returns: PriceGroup
		"""
		return self.set_field('dt_start', date_time_start)

	def set_date_time_end(self, date_time_end):
		"""
		Set dt_end.

		:param date_time_end: int
		:returns: PriceGroup
		"""
		return self.set_field('dt_end', date_time_end)

	def set_minimum_subtotal(self, minimum_subtotal: float) -> 'PriceGroup':
		"""
		Set qmn_subtot.

		:param minimum_subtotal: int
		:returns: PriceGroup
		"""

		return self.set_field('qmn_subtot', minimum_subtotal)

	def set_maximum_subtotal(self, maximum_subtotal: float) -> 'PriceGroup':
		"""
		Set qmx_subtot.

		:param maximum_subtotal: int
		:returns: PriceGroup
		"""

		return self.set_field('qmx_subtot', maximum_subtotal)

	def set_minimum_quantity(self, minimum_quantity: int) -> 'PriceGroup':
		"""
		Set qmn_quan.

		:param minimum_quantity: int
		:returns: PriceGroup
		"""

		return self.set_field('qmn_quan', minimum_quantity)

	def set_maximum_quantity(self, maximum_quantity: int) -> 'PriceGroup':
		"""
		Set qmx_quan.

		:param maximum_quantity: int
		:returns: PriceGroup
		"""

		return self.set_field('qmx_quan', maximum_quantity)

	def set_minimum_weight(self, minimum_weight: float) -> 'PriceGroup':
		"""
		Set qmn_weight.

		:param minimum_weight: int
		:returns: PriceGroup
		"""

		return self.set_field('qmn_weight', minimum_weight)

	def set_maximum_weight(self, maximum_weight: float) -> 'PriceGroup':
		"""
		Set qmx_weight.

		:param maximum_weight: int
		:returns: PriceGroup
		"""

		return self.set_field('qmx_weight', maximum_weight)

	def set_basket_minimum_subtotal(self, basket_minimum_subtotal: float) -> 'PriceGroup':
		"""
		Set bmn_subtot.

		:param basket_minimum_subtotal: int
		:returns: PriceGroup
		"""

		return self.set_field('bmn_subtot', basket_minimum_subtotal)

	def set_basket_maximum_subtotal(self, basket_maximum_subtotal: float) -> 'PriceGroup':
		"""
		Set bmx_subtot.

		:param basket_maximum_subtotal: int
		:returns: PriceGroup
		"""

		return self.set_field('bmx_subtot', basket_maximum_subtotal)

	def set_basket_minimum_quantity(self, basket_minimum_quantity: int) -> 'PriceGroup':
		"""
		Set bmn_quan.

		:param basket_minimum_quantity: int
		:returns: PriceGroup
		"""

		return self.set_field('bmn_quan', basket_minimum_quantity)

	def set_basket_maximum_quantity(self, basket_maximum_quantity: int) -> 'PriceGroup':
		"""
		Set bmx_quan.

		:param basket_maximum_quantity: int
		:returns: PriceGroup
		"""

		return self.set_field('bmx_quan', basket_maximum_quantity)

	def set_basket_minimum_weight(self, basket_minimum_weight: float) -> 'PriceGroup':
		"""
		Set bmn_weight.

		:param basket_minimum_weight: int
		:returns: PriceGroup
		"""

		return self.set_field('bmn_weight', basket_minimum_weight)

	def set_basket_maximum_weight(self, basket_maximum_weight: float) -> 'PriceGroup':
		"""
		Set bmx_weight.

		:param basket_maximum_weight: int
		:returns: PriceGroup
		"""

		return self.set_field('bmx_weight', basket_maximum_weight)

	def set_priority(self, priority: int) -> 'PriceGroup':
		"""
		Set priority.

		:param priority: int
		:returns: PriceGroup
		"""

		return self.set_field('priority', priority)

	def set_module(self, module) -> 'PriceGroup':
		"""
		Set module.

		:param module: Module|dict
		:returns: PriceGroup
		:raises Exception:
		"""

		if module is None or isinstance(module, Module):
			return self.set_field('module', module)
		elif isinstance(module, dict):
			return self.set_field('module', Module(module))
		raise Exception('Expected instance of Module, Object, or None')

	def set_exclusion(self, exclusion: bool) -> 'PriceGroup':
		"""
		Set exclusion.

		:param exclusion: bool
		:returns: PriceGroup
		"""

		return self.set_field('exclusion', exclusion)

	def set_description(self, description: str) -> 'PriceGroup':
		"""
		Set descrip.

		:param description: string
		:returns: PriceGroup
		"""

		return self.set_field('descrip', description)

	def set_display(self, display: bool) -> 'PriceGroup':
		"""
		Set display.

		:param display: bool
		:returns: PriceGroup
		"""

		return self.set_field('display', display)

	def to_dict(self) -> dict:
		"""
		Reduce the model to a dict.
		"""

		ret = self.copy()

		if 'module' in ret and isinstance(ret['module'], Module):
			ret['module'] = ret['module'].to_dict()

		if 'capabilities' in ret and isinstance(ret['capabilities'], DiscountModuleCapabilities):
			ret['capabilities'] = ret['capabilities'].to_dict()

		return ret


"""
DiscountModuleCapabilities data model.
"""


class DiscountModuleCapabilities(Model):
	def __init__(self, data: dict = None):
		"""
		DiscountModuleCapabilities Constructor

		:param data: dict
		"""

		super().__init__(data)

	def get_preitems(self) -> bool:
		"""
		Get preitems.

		:returns: bool
		"""

		return self.get_field('preitems', False)

	def get_items(self) -> bool:
		"""
		Get items.

		:returns: bool
		"""

		return self.get_field('items', False)

	def get_eligibility(self) -> str:
		"""
		Get eligibility.

		:returns: string
		"""

		return self.get_field('eligibility')

	def get_basket(self) -> bool:
		"""
		Get basket.

		:returns: bool
		"""

		return self.get_field('basket', False)

	def get_shipping(self) -> bool:
		"""
		Get shipping.

		:returns: bool
		"""

		return self.get_field('shipping', False)

	def get_qualifying(self) -> bool:
		"""
		Get qualifying.

		:returns: bool
		"""

		return self.get_field('qualifying', False)


"""
Product data model.
"""


class Product(Model):
	def __init__(self, data: dict = None):
		"""
		Product Constructor

		:param data: dict
		"""

		super().__init__(data)
		if self.has_field('productinventorysettings'):
			value = self.get_field('productinventorysettings')
			if isinstance(value, ProductInventorySettings):
				pass
			elif isinstance(value, dict):
				self.set_field('productinventorysettings', ProductInventorySettings(value))
			else:
				raise Exception('Expected ProductInventorySettings or a dict')

		if self.has_field('CustomField_Values'):
			value = self.get_field('CustomField_Values')
			if isinstance(value, CustomFieldValues):
				pass
			elif isinstance(value, dict):
				self.set_field('CustomField_Values', CustomFieldValues(value))
			else:
				raise Exception('Expected CustomFieldValues or a dict')

		if self.has_field('uris'):
			value = self.get_field('uris')
			if isinstance(value, list):
				for i, e in enumerate(value):
					if isinstance(value, Uri):
						pass
					elif isinstance(e, dict):
						value[i] = Uri(e)
					else:
						raise Exception('Expected list of Uri or dict')
			else:
				raise Exception('Expected list of Uri or dict')

		if self.has_field('relatedproducts'):
			value = self.get_field('relatedproducts')
			if isinstance(value, list):
				for i, e in enumerate(value):
					if isinstance(value, RelatedProduct):
						pass
					elif isinstance(e, dict):
						value[i] = RelatedProduct(e)
					else:
						raise Exception('Expected list of RelatedProduct or dict')
			else:
				raise Exception('Expected list of RelatedProduct or dict')

		if self.has_field('categories'):
			value = self.get_field('categories')
			if isinstance(value, list):
				for i, e in enumerate(value):
					if isinstance(value, Category):
						pass
					elif isinstance(e, dict):
						value[i] = Category(e)
					else:
						raise Exception('Expected list of Category or dict')
			else:
				raise Exception('Expected list of Category or dict')

		if self.has_field('productshippingrules'):
			value = self.get_field('productshippingrules')
			if isinstance(value, ProductShippingRules):
				pass
			elif isinstance(value, dict):
				self.set_field('productshippingrules', ProductShippingRules(value))
			else:
				raise Exception('Expected ProductShippingRules or a dict')

		if self.has_field('productimagedata'):
			value = self.get_field('productimagedata')
			if isinstance(value, list):
				for i, e in enumerate(value):
					if isinstance(value, ProductImageData):
						pass
					elif isinstance(e, dict):
						value[i] = ProductImageData(e)
					else:
						raise Exception('Expected list of ProductImageData or dict')
			else:
				raise Exception('Expected list of ProductImageData or dict')

		if self.has_field('attributes'):
			value = self.get_field('attributes')
			if isinstance(value, list):
				for i, e in enumerate(value):
					if isinstance(value, ProductAttribute):
						pass
					elif isinstance(e, dict):
						value[i] = ProductAttribute(e)
					else:
						raise Exception('Expected list of ProductAttribute or dict')
			else:
				raise Exception('Expected list of ProductAttribute or dict')

	def get_id(self) -> int:
		"""
		Get id.

		:returns: int
		"""

		return self.get_field('id', 0)

	def get_code(self) -> str:
		"""
		Get code.

		:returns: string
		"""

		return self.get_field('code')

	def get_sku(self) -> str:
		"""
		Get sku.

		:returns: string
		"""

		return self.get_field('sku')

	def get_name(self) -> str:
		"""
		Get name.

		:returns: string
		"""

		return self.get_field('name')

	def get_thumbnail(self) -> str:
		"""
		Get thumbnail.

		:returns: string
		"""

		return self.get_field('thumbnail')

	def get_image(self) -> str:
		"""
		Get image.

		:returns: string
		"""

		return self.get_field('image')

	def get_price(self) -> float:
		"""
		Get price.

		:returns: float
		"""

		return self.get_field('price', 0.00)

	def get_formatted_price(self) -> str:
		"""
		Get formatted_price.

		:returns: string
		"""

		return self.get_field('formatted_price')

	def get_cost(self) -> float:
		"""
		Get cost.

		:returns: float
		"""

		return self.get_field('cost', 0.00)

	def get_formatted_cost(self) -> str:
		"""
		Get formatted_cost.

		:returns: string
		"""

		return self.get_field('formatted_cost')

	def get_description(self) -> str:
		"""
		Get descrip.

		:returns: string
		"""

		return self.get_field('descrip')

	def get_category_count(self) -> int:
		"""
		Get catcount.

		:returns: int
		"""

		return self.get_field('catcount', 0)

	def get_weight(self) -> float:
		"""
		Get weight.

		:returns: float
		"""

		return self.get_field('weight', 0.00)

	def get_active(self) -> bool:
		"""
		Get active.

		:returns: bool
		"""

		return self.get_field('active', False)

	def get_page_title(self) -> str:
		"""
		Get page_title.

		:returns: string
		"""

		return self.get_field('page_title')

	def get_taxable(self) -> bool:
		"""
		Get taxable.

		:returns: bool
		"""

		return self.get_field('taxable', False)

	def get_date_time_created(self) -> int:
		"""
		Get dt_created.

		:returns: int
		"""

		return self.get_field('dt_created', 0)

	def get_date_time_update(self) -> int:
		"""
		Get dt_updated.

		:returns: int
		"""

		return self.get_field('dt_updated', 0)

	def get_product_inventory_settings(self):
		"""
		Get productinventorysettings.

		:returns: ProductInventorySettings|None
		"""

		return self.get_field('productinventorysettings', None)

	def get_product_inventory_active(self) -> bool:
		"""
		Get product_inventory_active.

		:returns: bool
		"""

		return self.get_field('product_inventory_active', False)

	def get_product_inventory(self) -> int:
		"""
		Get product_inventory.

		:returns: int
		"""

		return self.get_field('product_inventory', 0)

	def get_canonical_category_code(self) -> str:
		"""
		Get cancat_code.

		:returns: string
		"""

		return self.get_field('cancat_code')

	def get_page_code(self) -> str:
		"""
		Get page_code.

		:returns: string
		"""

		return self.get_field('page_code')

	def get_custom_field_values(self):
		"""
		Get CustomField_Values.

		:returns: CustomFieldValues|None
		"""

		return self.get_field('CustomField_Values', None)

	def get_uris(self):
		"""
		Get uris.

		:returns: List of Uri
		"""

		return self.get_field('uris', [])

	def get_related_products(self):
		"""
		Get relatedproducts.

		:returns: List of RelatedProduct
		"""

		return self.get_field('relatedproducts', [])

	def get_categories(self):
		"""
		Get categories.

		:returns: List of Category
		"""

		return self.get_field('categories', [])

	def get_product_shupping_rules(self):
		"""
		Get productshippingrules.

		:returns: ProductShippingRules|None
		"""

		return self.get_field('productshippingrules', None)

	def get_product_image_data(self):
		"""
		Get productimagedata.

		:returns: List of ProductImageData
		"""

		return self.get_field('productimagedata', [])

	def get_attributes(self):
		"""
		Get attributes.

		:returns: List of ProductAttribute
		"""

		return self.get_field('attributes', [])

	def set_code(self, code: str) -> 'Product':
		"""
		Set code.

		:param code: string
		:returns: Product
		"""

		return self.set_field('code', code)

	def set_sku(self, sku: str) -> 'Product':
		"""
		Set sku.

		:param sku: string
		:returns: Product
		"""

		return self.set_field('sku', sku)

	def set_name(self, name: str) -> 'Product':
		"""
		Set name.

		:param name: string
		:returns: Product
		"""

		return self.set_field('name', name)

	def set_thumbnail(self, thumbnail: str) -> 'Product':
		"""
		Set thumbnail.

		:param thumbnail: string
		:returns: Product
		"""

		return self.set_field('thumbnail', thumbnail)

	def set_image(self, image: str) -> 'Product':
		"""
		Set image.

		:param image: string
		:returns: Product
		"""

		return self.set_field('image', image)

	def set_price(self, price: float) -> 'Product':
		"""
		Set price.

		:param price: int
		:returns: Product
		"""

		return self.set_field('price', price)

	def set_cost(self, cost: float) -> 'Product':
		"""
		Set cost.

		:param cost: int
		:returns: Product
		"""

		return self.set_field('cost', cost)

	def set_description(self, description: str) -> 'Product':
		"""
		Set descrip.

		:param description: string
		:returns: Product
		"""

		return self.set_field('descrip', description)

	def set_weight(self, weight: float) -> 'Product':
		"""
		Set weight.

		:param weight: int
		:returns: Product
		"""

		return self.set_field('weight', weight)

	def set_active(self, active: bool) -> 'Product':
		"""
		Set active.

		:param active: bool
		:returns: Product
		"""

		return self.set_field('active', active)

	def set_page_title(self, page_title: str) -> 'Product':
		"""
		Set page_title.

		:param page_title: string
		:returns: Product
		"""

		return self.set_field('page_title', page_title)

	def set_taxable(self, taxable: bool) -> 'Product':
		"""
		Set taxable.

		:param taxable: bool
		:returns: Product
		"""

		return self.set_field('taxable', taxable)

	def set_product_inventory(self, product_inventory: int) -> 'Product':
		"""
		Set product_inventory.

		:param product_inventory: int
		:returns: Product
		"""

		return self.set_field('product_inventory', product_inventory)

	def set_canonical_category_code(self, canonical_category_code: str) -> 'Product':
		"""
		Set cancat_code.

		:param canonical_category_code: string
		:returns: Product
		"""

		return self.set_field('cancat_code', canonical_category_code)

	def set_page_code(self, page_code: str) -> 'Product':
		"""
		Set page_code.

		:param page_code: string
		:returns: Product
		"""

		return self.set_field('page_code', page_code)

	def set_custom_field_values(self, custom_field_values) -> 'Product':
		"""
		Set CustomField_Values.

		:param custom_field_values: CustomFieldValues|dict
		:returns: Product
		:raises Exception:
		"""

		if custom_field_values is None or isinstance(custom_field_values, CustomFieldValues):
			return self.set_field('CustomField_Values', custom_field_values)
		elif isinstance(custom_field_values, dict):
			return self.set_field('CustomField_Values', CustomFieldValues(custom_field_values))
		raise Exception('Expected instance of CustomFieldValues, Object, or None')

	def to_dict(self) -> dict:
		"""
		Reduce the model to a dict.
		"""

		ret = self.copy()

		if 'productinventorysettings' in ret and isinstance(ret['productinventorysettings'], ProductInventorySettings):
			ret['productinventorysettings'] = ret['productinventorysettings'].to_dict()

		if 'CustomField_Values' in ret and isinstance(ret['CustomField_Values'], CustomFieldValues):
			ret['CustomField_Values'] = ret['CustomField_Values'].to_dict()

		if 'uris' in ret and isinstance(ret['uris'], list):
			for i, e in enumerate(ret['uris']):
				if isinstance(e, Uri):
					ret['uris'][i] = ret['uris'][i].to_dict()

		if 'relatedproducts' in ret and isinstance(ret['relatedproducts'], list):
			for i, e in enumerate(ret['relatedproducts']):
				if isinstance(e, RelatedProduct):
					ret['relatedproducts'][i] = ret['relatedproducts'][i].to_dict()

		if 'categories' in ret and isinstance(ret['categories'], list):
			for i, e in enumerate(ret['categories']):
				if isinstance(e, Category):
					ret['categories'][i] = ret['categories'][i].to_dict()

		if 'productshippingrules' in ret and isinstance(ret['productshippingrules'], ProductShippingRules):
			ret['productshippingrules'] = ret['productshippingrules'].to_dict()

		if 'productimagedata' in ret and isinstance(ret['productimagedata'], list):
			for i, e in enumerate(ret['productimagedata']):
				if isinstance(e, ProductImageData):
					ret['productimagedata'][i] = ret['productimagedata'][i].to_dict()

		if 'attributes' in ret and isinstance(ret['attributes'], list):
			for i, e in enumerate(ret['attributes']):
				if isinstance(e, ProductAttribute):
					ret['attributes'][i] = ret['attributes'][i].to_dict()

		return ret


"""
RelatedProduct data model.
"""


class RelatedProduct(Model):
	def __init__(self, data: dict = None):
		"""
		RelatedProduct Constructor

		:param data: dict
		"""

		super().__init__(data)

	def get_id(self) -> int:
		"""
		Get id.

		:returns: int
		"""

		return self.get_field('id', 0)

	def get_code(self) -> str:
		"""
		Get code.

		:returns: string
		"""

		return self.get_field('code')

	def get_sku(self) -> str:
		"""
		Get sku.

		:returns: string
		"""

		return self.get_field('sku')

	def get_name(self) -> str:
		"""
		Get name.

		:returns: string
		"""

		return self.get_field('name')

	def get_thumbnail(self) -> str:
		"""
		Get thumbnail.

		:returns: string
		"""

		return self.get_field('thumbnail')

	def get_image(self) -> str:
		"""
		Get image.

		:returns: string
		"""

		return self.get_field('image')

	def get_price(self) -> float:
		"""
		Get price.

		:returns: float
		"""

		return self.get_field('price', 0.00)

	def get_formatted_price(self) -> str:
		"""
		Get formatted_price.

		:returns: string
		"""

		return self.get_field('formatted_price')

	def get_cost(self) -> float:
		"""
		Get cost.

		:returns: float
		"""

		return self.get_field('cost', 0.00)

	def get_formatted_cost(self) -> str:
		"""
		Get formatted_cost.

		:returns: string
		"""

		return self.get_field('formatted_cost')

	def get_weight(self) -> float:
		"""
		Get weight.

		:returns: float
		"""

		return self.get_field('weight', 0.00)

	def get_active(self) -> bool:
		"""
		Get active.

		:returns: bool
		"""

		return self.get_field('active', False)

	def get_page_title(self) -> str:
		"""
		Get page_title.

		:returns: string
		"""

		return self.get_field('page_title')

	def get_taxable(self) -> bool:
		"""
		Get taxable.

		:returns: bool
		"""

		return self.get_field('taxable', False)

	def get_date_time_created(self) -> int:
		"""
		Get dt_created.

		:returns: int
		"""

		return self.get_field('dt_created', 0)

	def get_date_time_updated(self) -> int:
		"""
		Get dt_updated.

		:returns: int
		"""

		return self.get_field('dt_updated', 0)

	def set_code(self, code: str) -> 'RelatedProduct':
		"""
		Set code.

		:param code: string
		:returns: RelatedProduct
		"""

		return self.set_field('code', code)

	def set_sku(self, sku: str) -> 'RelatedProduct':
		"""
		Set sku.

		:param sku: string
		:returns: RelatedProduct
		"""

		return self.set_field('sku', sku)

	def set_name(self, name: str) -> 'RelatedProduct':
		"""
		Set name.

		:param name: string
		:returns: RelatedProduct
		"""

		return self.set_field('name', name)

	def set_thumbnail(self, thumbnail: str) -> 'RelatedProduct':
		"""
		Set thumbnail.

		:param thumbnail: string
		:returns: RelatedProduct
		"""

		return self.set_field('thumbnail', thumbnail)

	def set_image(self, image: str) -> 'RelatedProduct':
		"""
		Set image.

		:param image: string
		:returns: RelatedProduct
		"""

		return self.set_field('image', image)

	def set_price(self, price: float) -> 'RelatedProduct':
		"""
		Set price.

		:param price: int
		:returns: RelatedProduct
		"""

		return self.set_field('price', price)

	def set_cost(self, cost: float) -> 'RelatedProduct':
		"""
		Set cost.

		:param cost: int
		:returns: RelatedProduct
		"""

		return self.set_field('cost', cost)

	def set_weight(self, weight: float) -> 'RelatedProduct':
		"""
		Set weight.

		:param weight: int
		:returns: RelatedProduct
		"""

		return self.set_field('weight', weight)

	def set_active(self, active: bool) -> 'RelatedProduct':
		"""
		Set active.

		:param active: bool
		:returns: RelatedProduct
		"""

		return self.set_field('active', active)

	def set_page_title(self, page_title: str) -> 'RelatedProduct':
		"""
		Set page_title.

		:param page_title: string
		:returns: RelatedProduct
		"""

		return self.set_field('page_title', page_title)

	def set_taxable(self, taxable: bool) -> 'RelatedProduct':
		"""
		Set taxable.

		:param taxable: bool
		:returns: RelatedProduct
		"""

		return self.set_field('taxable', taxable)


"""
ProductImageData data model.
"""


class ProductImageData(Model):
	def __init__(self, data: dict = None):
		"""
		ProductImageData Constructor

		:param data: dict
		"""

		super().__init__(data)

	def get_id(self) -> int:
		"""
		Get id.

		:returns: int
		"""

		return self.get_field('id', 0)

	def get_product_id(self) -> int:
		"""
		Get product_id.

		:returns: int
		"""

		return self.get_field('product_id', 0)

	def get_image_id(self) -> int:
		"""
		Get image_id.

		:returns: int
		"""

		return self.get_field('image_id', 0)

	def get_type_id(self) -> int:
		"""
		Get type_id.

		:returns: int
		"""

		return self.get_field('type_id', 0)

	def get_code(self) -> str:
		"""
		Get code.

		:returns: string
		"""

		return self.get_field('code')

	def get_type_description(self) -> str:
		"""
		Get type_desc.

		:returns: string
		"""

		return self.get_field('type_desc')

	def get_image(self) -> str:
		"""
		Get image.

		:returns: string
		"""

		return self.get_field('image')

	def get_width(self) -> int:
		"""
		Get width.

		:returns: int
		"""

		return self.get_field('width', 0)

	def get_height(self) -> int:
		"""
		Get height.

		:returns: int
		"""

		return self.get_field('height', 0)

	def get_display_order(self) -> int:
		"""
		Get disp_order.

		:returns: int
		"""

		return self.get_field('disp_order', 0)


"""
ProductAttribute data model.
"""


class ProductAttribute(Model):
	def __init__(self, data: dict = None):
		"""
		ProductAttribute Constructor

		:param data: dict
		"""

		super().__init__(data)
		if self.has_field('options'):
			value = self.get_field('options')
			if isinstance(value, list):
				for i, e in enumerate(value):
					if isinstance(value, ProductOption):
						pass
					elif isinstance(e, dict):
						value[i] = ProductOption(e)
					else:
						raise Exception('Expected list of ProductOption or dict')
			else:
				raise Exception('Expected list of ProductOption or dict')

	def get_id(self) -> int:
		"""
		Get id.

		:returns: int
		"""

		return self.get_field('id', 0)

	def get_product_id(self) -> int:
		"""
		Get product_id.

		:returns: int
		"""

		return self.get_field('product_id', 0)

	def get_default_id(self) -> int:
		"""
		Get default_id.

		:returns: int
		"""

		return self.get_field('default_id', 0)

	def get_display_order(self) -> int:
		"""
		Get disp_order.

		:returns: int
		"""

		if self.has_field('disp_order'):
			return self.get_field('disp_order', 0)
		elif self.has_field('disporder'):
			return self.get_field('disporder', 0)

		return 0

	def get_attribute_template_id(self) -> int:
		"""
		Get attemp_id.

		:returns: int
		"""

		return self.get_field('attemp_id', 0)

	def get_code(self) -> str:
		"""
		Get code.

		:returns: string
		"""

		return self.get_field('code')

	def get_type(self) -> str:
		"""
		Get type.

		:returns: string
		"""

		return self.get_field('type')

	def get_prompt(self) -> str:
		"""
		Get prompt.

		:returns: string
		"""

		return self.get_field('prompt')

	def get_price(self) -> float:
		"""
		Get price.

		:returns: float
		"""

		return self.get_field('price', 0.00)

	def get_cost(self) -> float:
		"""
		Get cost.

		:returns: float
		"""

		return self.get_field('cost', 0.00)

	def get_weight(self) -> float:
		"""
		Get weight.

		:returns: float
		"""

		return self.get_field('weight', 0.00)

	def get_required(self) -> bool:
		"""
		Get required.

		:returns: bool
		"""

		return self.get_field('required', False)

	def get_inventory(self) -> bool:
		"""
		Get inventory.

		:returns: bool
		"""

		return self.get_field('inventory', False)

	def get_image(self) -> str:
		"""
		Get image.

		:returns: string
		"""

		return self.get_field('image')

	def get_options(self):
		"""
		Get options.

		:returns: List of ProductOption
		"""

		return self.get_field('options', [])

	def to_dict(self) -> dict:
		"""
		Reduce the model to a dict.
		"""

		ret = self.copy()

		if 'options' in ret and isinstance(ret['options'], list):
			for i, e in enumerate(ret['options']):
				if isinstance(e, ProductOption):
					ret['options'][i] = ret['options'][i].to_dict()

		return ret


"""
ProductOption data model.
"""


class ProductOption(Model):
	def __init__(self, data: dict = None):
		"""
		ProductOption Constructor

		:param data: dict
		"""

		super().__init__(data)

	def get_id(self) -> int:
		"""
		Get id.

		:returns: int
		"""

		return self.get_field('id', 0)

	def get_product_id(self) -> int:
		"""
		Get product_id.

		:returns: int
		"""

		return self.get_field('product_id', 0)

	def get_attribute_id(self) -> int:
		"""
		Get attr_id.

		:returns: int
		"""

		return self.get_field('attr_id', 0)

	def get_attemp_id(self) -> int:
		"""
		Get attemp_id.

		:returns: int
		"""

		return self.get_field('attemp_id', 0)

	def get_attmpat_id(self) -> int:
		"""
		Get attmpat_id.

		:returns: int
		"""

		return self.get_field('attmpat_id', 0)

	def get_display_order(self) -> int:
		"""
		Get disp_order.

		:returns: int
		"""

		if self.has_field('disp_order'):
			return self.get_field('disp_order', 0)
		elif self.has_field('disporder'):
			return self.get_field('disporder', 0)

		return 0

	def get_code(self) -> str:
		"""
		Get code.

		:returns: string
		"""

		return self.get_field('code')

	def get_prompt(self) -> str:
		"""
		Get prompt.

		:returns: string
		"""

		return self.get_field('prompt')

	def get_price(self) -> float:
		"""
		Get price.

		:returns: float
		"""

		return self.get_field('price', 0.00)

	def get_cost(self) -> float:
		"""
		Get cost.

		:returns: float
		"""

		return self.get_field('cost', 0.00)

	def get_weight(self) -> float:
		"""
		Get weight.

		:returns: float
		"""

		return self.get_field('weight', 0.00)

	def get_image(self) -> str:
		"""
		Get image.

		:returns: string
		"""

		return self.get_field('image')


"""
ProductShippingMethod data model.
"""


class ProductShippingMethod(Model):
	def __init__(self, data: dict = None):
		"""
		ProductShippingMethod Constructor

		:param data: dict
		"""

		super().__init__(data)

	def get_module_code(self) -> str:
		"""
		Get mod_code.

		:returns: string
		"""

		return self.get_field('mod_code')

	def get_method_code(self) -> str:
		"""
		Get meth_code.

		:returns: string
		"""

		return self.get_field('meth_code')


"""
ProductShippingRules data model.
"""


class ProductShippingRules(Model):
	def __init__(self, data: dict = None):
		"""
		ProductShippingRules Constructor

		:param data: dict
		"""

		super().__init__(data)
		if self.has_field('methods'):
			value = self.get_field('methods')
			if isinstance(value, list):
				for i, e in enumerate(value):
					if isinstance(value, ProductShippingMethod):
						pass
					elif isinstance(e, dict):
						value[i] = ProductShippingMethod(e)
					else:
						raise Exception('Expected list of ProductShippingMethod or dict')
			else:
				raise Exception('Expected list of ProductShippingMethod or dict')

	def get_product_id(self) -> int:
		"""
		Get product_id.

		:returns: int
		"""

		return self.get_field('product_id', 0)

	def get_own_package(self) -> bool:
		"""
		Get ownpackage.

		:returns: bool
		"""

		return self.get_field('ownpackage', False)

	def get_width(self) -> float:
		"""
		Get width.

		:returns: float
		"""

		return self.get_field('width', 0.00)

	def get_length(self) -> float:
		"""
		Get length.

		:returns: float
		"""

		return self.get_field('length', 0.00)

	def get_height(self) -> float:
		"""
		Get height.

		:returns: float
		"""

		return self.get_field('height', 0.00)

	def get_limit_methods(self) -> bool:
		"""
		Get limitmeths.

		:returns: bool
		"""

		return self.get_field('limitmeths', False)

	def get_methods(self):
		"""
		Get methods.

		:returns: List of ProductShippingMethod
		"""

		return self.get_field('methods', [])

	def set_methods(self, methods: list) -> 'ProductShippingRules':
		"""
		Set methods.

		:param methods: List of ProductShippingMethod
		:raises Exception:
		:returns: ProductShippingRules
		"""

		for i, e in enumerate(methods, 0):
			if isinstance(e, ProductShippingMethod):
				continue
			elif isinstance(e, dict):
				methods[i] = ProductShippingMethod(e)
			else:
				raise Exception('Expected instance of ProductShippingMethod or dict')
		return self.set_field('methods', methods)

	def add_method(self, method: ProductShippingMethod) -> 'ProductShippingRules':
		"""
		Add a ProductShippingMethod.

		:param method: ProductShippingMethod
		:returns: ProductShippingRules
		"""

		if 'methods' not in self:
			self['methods'] = []
		self['methods'].append(method)
		return self

	def to_dict(self) -> dict:
		"""
		Reduce the model to a dict.
		"""

		ret = self.copy()

		if 'methods' in ret and isinstance(ret['methods'], list):
			for i, e in enumerate(ret['methods']):
				if isinstance(e, ProductShippingMethod):
					ret['methods'][i] = ret['methods'][i].to_dict()

		return ret


"""
Uri data model.
"""


class Uri(Model):
	def __init__(self, data: dict = None):
		"""
		Uri Constructor

		:param data: dict
		"""

		super().__init__(data)

	def get_id(self) -> int:
		"""
		Get id.

		:returns: int
		"""

		return self.get_field('id', 0)

	def get_uri(self) -> str:
		"""
		Get uri.

		:returns: string
		"""

		return self.get_field('uri')

	def get_store_id(self) -> int:
		"""
		Get store_id.

		:returns: int
		"""

		return self.get_field('store_id', 0)

	def get_screen(self) -> str:
		"""
		Get screen.

		:returns: string
		"""

		return self.get_field('screen')

	def get_page_id(self) -> int:
		"""
		Get page_id.

		:returns: int
		"""

		return self.get_field('page_id', 0)

	def get_category_id(self) -> int:
		"""
		Get cat_id.

		:returns: int
		"""

		return self.get_field('cat_id', 0)

	def get_product_id(self) -> int:
		"""
		Get product_id.

		:returns: int
		"""

		return self.get_field('product_id', 0)

	def get_feed_id(self) -> int:
		"""
		Get feed_id.

		:returns: int
		"""

		return self.get_field('feed_id', 0)

	def get_canonical(self) -> bool:
		"""
		Get canonical.

		:returns: bool
		"""

		return self.get_field('canonical', False)

	def get_status(self) -> int:
		"""
		Get status.

		:returns: int
		"""

		return self.get_field('status', 0)


"""
ProductVariant data model.
"""


class ProductVariant(Model):
	def __init__(self, data: dict = None):
		"""
		ProductVariant Constructor

		:param data: dict
		"""

		super().__init__(data)
		if self.has_field('parts'):
			value = self.get_field('parts')
			if isinstance(value, list):
				for i, e in enumerate(value):
					if isinstance(value, ProductVariantPart):
						pass
					elif isinstance(e, dict):
						value[i] = ProductVariantPart(e)
					else:
						raise Exception('Expected list of ProductVariantPart or dict')
			else:
				raise Exception('Expected list of ProductVariantPart or dict')

		if self.has_field('dimensions'):
			value = self.get_field('dimensions')
			if isinstance(value, list):
				for i, e in enumerate(value):
					if isinstance(value, ProductVariantDimension):
						pass
					elif isinstance(e, dict):
						value[i] = ProductVariantDimension(e)
					else:
						raise Exception('Expected list of ProductVariantDimension or dict')
			else:
				raise Exception('Expected list of ProductVariantDimension or dict')

	def get_product_id(self) -> int:
		"""
		Get product_id.

		:returns: int
		"""

		return self.get_field('product_id', 0)

	def get_variant_id(self) -> int:
		"""
		Get variant_id.

		:returns: int
		"""

		return self.get_field('variant_id', 0)

	def get_parts(self):
		"""
		Get parts.

		:returns: List of ProductVariantPart
		"""

		return self.get_field('parts', [])

	def get_dimensions(self):
		"""
		Get dimensions.

		:returns: List of ProductVariantDimension
		"""

		return self.get_field('dimensions', [])

	def to_dict(self) -> dict:
		"""
		Reduce the model to a dict.
		"""

		ret = self.copy()

		if 'parts' in ret and isinstance(ret['parts'], list):
			for i, e in enumerate(ret['parts']):
				if isinstance(e, ProductVariantPart):
					ret['parts'][i] = ret['parts'][i].to_dict()

		if 'dimensions' in ret and isinstance(ret['dimensions'], list):
			for i, e in enumerate(ret['dimensions']):
				if isinstance(e, ProductVariantDimension):
					ret['dimensions'][i] = ret['dimensions'][i].to_dict()

		return ret


"""
Category data model.
"""


class Category(Model):
	def __init__(self, data: dict = None):
		"""
		Category Constructor

		:param data: dict
		"""

		super().__init__(data)
		if self.has_field('CustomField_Values'):
			value = self.get_field('CustomField_Values')
			if isinstance(value, CustomFieldValues):
				pass
			elif isinstance(value, dict):
				self.set_field('CustomField_Values', CustomFieldValues(value))
			else:
				raise Exception('Expected CustomFieldValues or a dict')

	def get_id(self) -> int:
		"""
		Get id.

		:returns: int
		"""

		return self.get_field('id', 0)

	def get_parent_id(self) -> int:
		"""
		Get parent_id.

		:returns: int
		"""

		return self.get_field('parent_id', 0)

	def get_availability_group_count(self) -> int:
		"""
		Get agrpcount.

		:returns: int
		"""

		return self.get_field('agrpcount', 0)

	def get_depth(self) -> int:
		"""
		Get depth.

		:returns: int
		"""

		return self.get_field('depth', 0)

	def get_display_order(self) -> int:
		"""
		Get disp_order.

		:returns: int
		"""

		return self.get_field('disp_order', 0)

	def get_page_id(self) -> int:
		"""
		Get page_id.

		:returns: int
		"""

		return self.get_field('page_id', 0)

	def get_code(self) -> str:
		"""
		Get code.

		:returns: string
		"""

		return self.get_field('code')

	def get_name(self) -> str:
		"""
		Get name.

		:returns: string
		"""

		return self.get_field('name')

	def get_page_title(self) -> str:
		"""
		Get page_title.

		:returns: string
		"""

		return self.get_field('page_title')

	def get_active(self) -> bool:
		"""
		Get active.

		:returns: bool
		"""

		return self.get_field('active', False)

	def get_date_time_created(self) -> int:
		"""
		Get dt_created.

		:returns: int
		"""

		return self.get_field('dt_created', 0)

	def get_date_time_updated(self) -> int:
		"""
		Get dt_updated.

		:returns: int
		"""

		return self.get_field('dt_updated', 0)

	def get_page_code(self) -> str:
		"""
		Get page_code.

		:returns: string
		"""

		return self.get_field('page_code')

	def get_parent_category(self) -> str:
		"""
		Get parent_category.

		:returns: string
		"""

		return self.get_field('parent_category')

	def get_custom_field_values(self):
		"""
		Get CustomField_Values.

		:returns: CustomFieldValues|None
		"""

		return self.get_field('CustomField_Values', None)

	def set_code(self, code: str) -> 'Category':
		"""
		Set code.

		:param code: string
		:returns: Category
		"""

		return self.set_field('code', code)

	def set_name(self, name: str) -> 'Category':
		"""
		Set name.

		:param name: string
		:returns: Category
		"""

		return self.set_field('name', name)

	def set_page_title(self, page_title: str) -> 'Category':
		"""
		Set page_title.

		:param page_title: string
		:returns: Category
		"""

		return self.set_field('page_title', page_title)

	def set_active(self, active: bool) -> 'Category':
		"""
		Set active.

		:param active: bool
		:returns: Category
		"""

		return self.set_field('active', active)

	def set_page_code(self, page_code: str) -> 'Category':
		"""
		Set page_code.

		:param page_code: string
		:returns: Category
		"""

		return self.set_field('page_code', page_code)

	def set_parent_category(self, parent_category: str) -> 'Category':
		"""
		Set parent_category.

		:param parent_category: string
		:returns: Category
		"""

		return self.set_field('parent_category', parent_category)

	def set_custom_field_values(self, custom_field_values) -> 'Category':
		"""
		Set CustomField_Values.

		:param custom_field_values: CustomFieldValues|dict
		:returns: Category
		:raises Exception:
		"""

		if custom_field_values is None or isinstance(custom_field_values, CustomFieldValues):
			return self.set_field('CustomField_Values', custom_field_values)
		elif isinstance(custom_field_values, dict):
			return self.set_field('CustomField_Values', CustomFieldValues(custom_field_values))
		raise Exception('Expected instance of CustomFieldValues, Object, or None')

	def to_dict(self) -> dict:
		"""
		Reduce the model to a dict.
		"""

		ret = self.copy()

		if 'CustomField_Values' in ret and isinstance(ret['CustomField_Values'], CustomFieldValues):
			ret['CustomField_Values'] = ret['CustomField_Values'].to_dict()

		return ret


"""
Order data model.
"""


class Order(Model):
	# ORDER_STATUS constants.
	ORDER_STATUS_PENDING = 0
	ORDER_STATUS_PROCESSING = 100
	ORDER_STATUS_SHIPPED = 200
	ORDER_STATUS_PARTIALLY_SHIPPED = 201
	ORDER_STATUS_CANCELLED = 300
	ORDER_STATUS_BACKORDERED = 400
	ORDER_STATUS_RMA_ISSUED = 500
	ORDER_STATUS_RETURNED = 600

	# ORDER_PAYMENT_STATUS constants.
	ORDER_PAYMENT_STATUS_PENDING = 0
	ORDER_PAYMENT_STATUS_AUTHORIZED = 100
	ORDER_PAYMENT_STATUS_CAPTURED = 200
	ORDER_PAYMENT_STATUS_PARTIALLY_CAPTURED = 201

	# ORDER_STOCK_STATUS constants.
	ORDER_STOCK_STATUS_AVAILABLE = 100
	ORDER_STOCK_STATUS_UNAVAILABLE = 200
	ORDER_STOCK_STATUS_PARTIAL = 201

	def __init__(self, data: dict = None):
		"""
		Order Constructor

		:param data: dict
		"""

		super().__init__(data)
		if self.has_field('customer'):
			value = self.get_field('customer')
			if isinstance(value, Customer):
				pass
			elif isinstance(value, dict):
				self.set_field('customer', Customer(value))
			else:
				raise Exception('Expected Customer or a dict')

		if self.has_field('items'):
			value = self.get_field('items')
			if isinstance(value, list):
				for i, e in enumerate(value):
					if isinstance(value, OrderItem):
						pass
					elif isinstance(e, dict):
						value[i] = OrderItem(e)
					else:
						raise Exception('Expected list of OrderItem or dict')
			else:
				raise Exception('Expected list of OrderItem or dict')

		if self.has_field('charges'):
			value = self.get_field('charges')
			if isinstance(value, list):
				for i, e in enumerate(value):
					if isinstance(value, OrderCharge):
						pass
					elif isinstance(e, dict):
						value[i] = OrderCharge(e)
					else:
						raise Exception('Expected list of OrderCharge or dict')
			else:
				raise Exception('Expected list of OrderCharge or dict')

		if self.has_field('coupons'):
			value = self.get_field('coupons')
			if isinstance(value, list):
				for i, e in enumerate(value):
					if isinstance(value, OrderCoupon):
						pass
					elif isinstance(e, dict):
						value[i] = OrderCoupon(e)
					else:
						raise Exception('Expected list of OrderCoupon or dict')
			else:
				raise Exception('Expected list of OrderCoupon or dict')

		if self.has_field('discounts'):
			value = self.get_field('discounts')
			if isinstance(value, list):
				for i, e in enumerate(value):
					if isinstance(value, OrderDiscountTotal):
						pass
					elif isinstance(e, dict):
						value[i] = OrderDiscountTotal(e)
					else:
						raise Exception('Expected list of OrderDiscountTotal or dict')
			else:
				raise Exception('Expected list of OrderDiscountTotal or dict')

		if self.has_field('payments'):
			value = self.get_field('payments')
			if isinstance(value, list):
				for i, e in enumerate(value):
					if isinstance(value, OrderPayment):
						pass
					elif isinstance(e, dict):
						value[i] = OrderPayment(e)
					else:
						raise Exception('Expected list of OrderPayment or dict')
			else:
				raise Exception('Expected list of OrderPayment or dict')

		if self.has_field('notes'):
			value = self.get_field('notes')
			if isinstance(value, list):
				for i, e in enumerate(value):
					if isinstance(value, OrderNote):
						pass
					elif isinstance(e, dict):
						value[i] = OrderNote(e)
					else:
						raise Exception('Expected list of OrderNote or dict')
			else:
				raise Exception('Expected list of OrderNote or dict')

		if self.has_field('CustomField_Values'):
			value = self.get_field('CustomField_Values')
			if isinstance(value, CustomFieldValues):
				pass
			elif isinstance(value, dict):
				self.set_field('CustomField_Values', CustomFieldValues(value))
			else:
				raise Exception('Expected CustomFieldValues or a dict')

	def get_id(self) -> int:
		"""
		Get id.

		:returns: int
		"""

		return self.get_field('id', 0)

	def get_payment_id(self) -> int:
		"""
		Get pay_id.

		:returns: int
		"""

		return self.get_field('pay_id', 0)

	def get_batch_id(self) -> int:
		"""
		Get batch_id.

		:returns: int
		"""

		return self.get_field('batch_id', 0)

	def get_status(self) -> int:
		"""
		Get status.

		:returns: int
		"""

		return self.get_field('status', 0)

	def get_payment_status(self) -> int:
		"""
		Get pay_status.

		:returns: int
		"""

		return self.get_field('pay_status', 0)

	def get_stock_status(self) -> int:
		"""
		Get stk_status.

		:returns: int
		"""

		return self.get_field('stk_status', 0)

	def get_date_in_stock(self) -> int:
		"""
		Get dt_instock.

		:returns: int
		"""

		return self.get_field('dt_instock', 0)

	def get_order_date(self) -> int:
		"""
		Get orderdate.

		:returns: int
		"""

		return self.get_field('orderdate', 0)

	def get_customer_id(self) -> int:
		"""
		Get cust_id.

		:returns: int
		"""

		return self.get_field('cust_id', 0)

	def get_ship_residential(self) -> bool:
		"""
		Get ship_res.

		:returns: bool
		"""

		return self.get_field('ship_res', False)

	def get_ship_first_name(self) -> str:
		"""
		Get ship_fname.

		:returns: string
		"""

		return self.get_field('ship_fname')

	def get_ship_last_name(self) -> str:
		"""
		Get ship_lname.

		:returns: string
		"""

		return self.get_field('ship_lname')

	def get_ship_email(self) -> str:
		"""
		Get ship_email.

		:returns: string
		"""

		return self.get_field('ship_email')

	def get_ship_company(self) -> str:
		"""
		Get ship_comp.

		:returns: string
		"""

		return self.get_field('ship_comp')

	def get_ship_phone(self) -> str:
		"""
		Get ship_phone.

		:returns: string
		"""

		return self.get_field('ship_phone')

	def get_ship_fax(self) -> str:
		"""
		Get ship_fax.

		:returns: string
		"""

		return self.get_field('ship_fax')

	def get_ship_address1(self) -> str:
		"""
		Get ship_addr1.

		:returns: string
		"""

		return self.get_field('ship_addr1')

	def get_ship_address2(self) -> str:
		"""
		Get ship_addr2.

		:returns: string
		"""

		return self.get_field('ship_addr2')

	def get_ship_city(self) -> str:
		"""
		Get ship_city.

		:returns: string
		"""

		return self.get_field('ship_city')

	def get_ship_state(self) -> str:
		"""
		Get ship_state.

		:returns: string
		"""

		return self.get_field('ship_state')

	def get_ship_zip(self) -> str:
		"""
		Get ship_zip.

		:returns: string
		"""

		return self.get_field('ship_zip')

	def get_ship_country(self) -> str:
		"""
		Get ship_cntry.

		:returns: string
		"""

		return self.get_field('ship_cntry')

	def get_bill_first_name(self) -> str:
		"""
		Get bill_fname.

		:returns: string
		"""

		return self.get_field('bill_fname')

	def get_bill_last_name(self) -> str:
		"""
		Get bill_lname.

		:returns: string
		"""

		return self.get_field('bill_lname')

	def get_bill_email(self) -> str:
		"""
		Get bill_email.

		:returns: string
		"""

		return self.get_field('bill_email')

	def get_bill_company(self) -> str:
		"""
		Get bill_comp.

		:returns: string
		"""

		return self.get_field('bill_comp')

	def get_bill_phone(self) -> str:
		"""
		Get bill_phone.

		:returns: string
		"""

		return self.get_field('bill_phone')

	def get_bill_fax(self) -> str:
		"""
		Get bill_fax.

		:returns: string
		"""

		return self.get_field('bill_fax')

	def get_bill_address1(self) -> str:
		"""
		Get bill_addr1.

		:returns: string
		"""

		return self.get_field('bill_addr1')

	def get_bill_address2(self) -> str:
		"""
		Get bill_addr2.

		:returns: string
		"""

		return self.get_field('bill_addr2')

	def get_bill_city(self) -> str:
		"""
		Get bill_city.

		:returns: string
		"""

		return self.get_field('bill_city')

	def get_bill_state(self) -> str:
		"""
		Get bill_state.

		:returns: string
		"""

		return self.get_field('bill_state')

	def get_bill_zip(self) -> str:
		"""
		Get bill_zip.

		:returns: string
		"""

		return self.get_field('bill_zip')

	def get_bill_country(self) -> str:
		"""
		Get bill_cntry.

		:returns: string
		"""

		return self.get_field('bill_cntry')

	def get_shipment_id(self) -> int:
		"""
		Get ship_id.

		:returns: int
		"""

		return self.get_field('ship_id', 0)

	def get_ship_data(self) -> str:
		"""
		Get ship_data.

		:returns: string
		"""

		return self.get_field('ship_data')

	def get_ship_method(self) -> str:
		"""
		Get ship_method.

		:returns: string
		"""

		return self.get_field('ship_method')

	def get_customer_login(self) -> str:
		"""
		Get cust_login.

		:returns: string
		"""

		return self.get_field('cust_login')

	def get_customer_password_email(self) -> str:
		"""
		Get cust_pw_email.

		:returns: string
		"""

		return self.get_field('cust_pw_email')

	def get_business_title(self) -> str:
		"""
		Get business_title.

		:returns: string
		"""

		return self.get_field('business_title')

	def get_payment_module(self) -> str:
		"""
		Get payment_module.

		:returns: string
		"""

		return self.get_field('payment_module')

	def get_source(self) -> str:
		"""
		Get source.

		:returns: string
		"""

		return self.get_field('source')

	def get_source_id(self) -> int:
		"""
		Get source_id.

		:returns: int
		"""

		return self.get_field('source_id', 0)

	def get_total(self) -> float:
		"""
		Get total.

		:returns: float
		"""

		return self.get_field('total', 0.00)

	def get_formatted_total(self) -> str:
		"""
		Get formatted_total.

		:returns: string
		"""

		return self.get_field('formatted_total')

	def get_total_ship(self) -> float:
		"""
		Get total_ship.

		:returns: float
		"""

		return self.get_field('total_ship', 0.00)

	def get_formatted_total_ship(self) -> str:
		"""
		Get formatted_total_ship.

		:returns: string
		"""

		return self.get_field('formatted_total_ship')

	def get_total_tax(self) -> float:
		"""
		Get total_tax.

		:returns: float
		"""

		return self.get_field('total_tax', 0.00)

	def get_formatted_total_tax(self) -> str:
		"""
		Get formatted_total_tax.

		:returns: string
		"""

		return self.get_field('formatted_total_tax')

	def get_total_authorized(self) -> float:
		"""
		Get total_auth.

		:returns: float
		"""

		return self.get_field('total_auth', 0.00)

	def get_formatted_total_authorized(self) -> str:
		"""
		Get formatted_total_auth.

		:returns: string
		"""

		return self.get_field('formatted_total_auth')

	def get_total_captured(self) -> float:
		"""
		Get total_capt.

		:returns: float
		"""

		return self.get_field('total_capt', 0.00)

	def get_formatted_total_captured(self) -> str:
		"""
		Get formatted_total_capt.

		:returns: string
		"""

		return self.get_field('formatted_total_capt')

	def get_total_refunded(self) -> float:
		"""
		Get total_rfnd.

		:returns: float
		"""

		return self.get_field('total_rfnd', 0.00)

	def get_formatted_total_refunded(self) -> str:
		"""
		Get formatted_total_rfnd.

		:returns: string
		"""

		return self.get_field('formatted_total_rfnd')

	def get_net_captured(self) -> float:
		"""
		Get net_capt.

		:returns: float
		"""

		return self.get_field('net_capt', 0.00)

	def get_formatted_net_captured(self) -> str:
		"""
		Get formatted_net_capt.

		:returns: string
		"""

		return self.get_field('formatted_net_capt')

	def get_pending_count(self) -> int:
		"""
		Get pend_count.

		:returns: int
		"""

		return self.get_field('pend_count', 0)

	def get_backorder_count(self) -> int:
		"""
		Get bord_count.

		:returns: int
		"""

		return self.get_field('bord_count', 0)

	def get_note_count(self) -> int:
		"""
		Get note_count.

		:returns: int
		"""

		return self.get_field('note_count', 0)

	def get_customer(self):
		"""
		Get customer.

		:returns: Customer|None
		"""

		return self.get_field('customer', None)

	def get_items(self):
		"""
		Get items.

		:returns: List of OrderItem
		"""

		return self.get_field('items', [])

	def get_charges(self):
		"""
		Get charges.

		:returns: List of OrderCharge
		"""

		return self.get_field('charges', [])

	def get_coupons(self):
		"""
		Get coupons.

		:returns: List of OrderCoupon
		"""

		return self.get_field('coupons', [])

	def get_discounts(self):
		"""
		Get discounts.

		:returns: List of OrderDiscountTotal
		"""

		return self.get_field('discounts', [])

	def get_payments(self):
		"""
		Get payments.

		:returns: List of OrderPayment
		"""

		return self.get_field('payments', [])

	def get_notes(self):
		"""
		Get notes.

		:returns: List of OrderNote
		"""

		return self.get_field('notes', [])

	def get_custom_field_values(self):
		"""
		Get CustomField_Values.

		:returns: CustomFieldValues|None
		"""

		return self.get_field('CustomField_Values', None)

	def set_customer_id(self, customer_id: int) -> 'Order':
		"""
		Set cust_id.

		:param customer_id: int
		:returns: Order
		"""

		return self.set_field('cust_id', customer_id)

	def set_ship_first_name(self, ship_first_name: str) -> 'Order':
		"""
		Set ship_fname.

		:param ship_first_name: string
		:returns: Order
		"""

		return self.set_field('ship_fname', ship_first_name)

	def set_ship_last_name(self, ship_last_name: str) -> 'Order':
		"""
		Set ship_lname.

		:param ship_last_name: string
		:returns: Order
		"""

		return self.set_field('ship_lname', ship_last_name)

	def set_ship_email(self, ship_email: str) -> 'Order':
		"""
		Set ship_email.

		:param ship_email: string
		:returns: Order
		"""

		return self.set_field('ship_email', ship_email)

	def set_ship_company(self, ship_company: str) -> 'Order':
		"""
		Set ship_comp.

		:param ship_company: string
		:returns: Order
		"""

		return self.set_field('ship_comp', ship_company)

	def set_ship_phone(self, ship_phone: str) -> 'Order':
		"""
		Set ship_phone.

		:param ship_phone: string
		:returns: Order
		"""

		return self.set_field('ship_phone', ship_phone)

	def set_ship_fax(self, ship_fax: str) -> 'Order':
		"""
		Set ship_fax.

		:param ship_fax: string
		:returns: Order
		"""

		return self.set_field('ship_fax', ship_fax)

	def set_ship_address1(self, ship_address1: str) -> 'Order':
		"""
		Set ship_addr1.

		:param ship_address1: string
		:returns: Order
		"""

		return self.set_field('ship_addr1', ship_address1)

	def set_ship_address2(self, ship_address2: str) -> 'Order':
		"""
		Set ship_addr2.

		:param ship_address2: string
		:returns: Order
		"""

		return self.set_field('ship_addr2', ship_address2)

	def set_ship_city(self, ship_city: str) -> 'Order':
		"""
		Set ship_city.

		:param ship_city: string
		:returns: Order
		"""

		return self.set_field('ship_city', ship_city)

	def set_ship_state(self, ship_state: str) -> 'Order':
		"""
		Set ship_state.

		:param ship_state: string
		:returns: Order
		"""

		return self.set_field('ship_state', ship_state)

	def set_ship_zip(self, ship_zip: str) -> 'Order':
		"""
		Set ship_zip.

		:param ship_zip: string
		:returns: Order
		"""

		return self.set_field('ship_zip', ship_zip)

	def set_ship_country(self, ship_country: str) -> 'Order':
		"""
		Set ship_cntry.

		:param ship_country: string
		:returns: Order
		"""

		return self.set_field('ship_cntry', ship_country)

	def set_bill_first_name(self, bill_first_name: str) -> 'Order':
		"""
		Set bill_fname.

		:param bill_first_name: string
		:returns: Order
		"""

		return self.set_field('bill_fname', bill_first_name)

	def set_bill_last_name(self, bill_last_name: str) -> 'Order':
		"""
		Set bill_lname.

		:param bill_last_name: string
		:returns: Order
		"""

		return self.set_field('bill_lname', bill_last_name)

	def set_bill_email(self, bill_email: str) -> 'Order':
		"""
		Set bill_email.

		:param bill_email: string
		:returns: Order
		"""

		return self.set_field('bill_email', bill_email)

	def set_bill_company(self, bill_company: str) -> 'Order':
		"""
		Set bill_comp.

		:param bill_company: string
		:returns: Order
		"""

		return self.set_field('bill_comp', bill_company)

	def set_bill_phone(self, bill_phone: str) -> 'Order':
		"""
		Set bill_phone.

		:param bill_phone: string
		:returns: Order
		"""

		return self.set_field('bill_phone', bill_phone)

	def set_bill_fax(self, bill_fax: str) -> 'Order':
		"""
		Set bill_fax.

		:param bill_fax: string
		:returns: Order
		"""

		return self.set_field('bill_fax', bill_fax)

	def set_bill_address1(self, bill_address1: str) -> 'Order':
		"""
		Set bill_addr1.

		:param bill_address1: string
		:returns: Order
		"""

		return self.set_field('bill_addr1', bill_address1)

	def set_bill_address2(self, bill_address2: str) -> 'Order':
		"""
		Set bill_addr2.

		:param bill_address2: string
		:returns: Order
		"""

		return self.set_field('bill_addr2', bill_address2)

	def set_bill_city(self, bill_city: str) -> 'Order':
		"""
		Set bill_city.

		:param bill_city: string
		:returns: Order
		"""

		return self.set_field('bill_city', bill_city)

	def set_bill_state(self, bill_state: str) -> 'Order':
		"""
		Set bill_state.

		:param bill_state: string
		:returns: Order
		"""

		return self.set_field('bill_state', bill_state)

	def set_bill_zip(self, bill_zip: str) -> 'Order':
		"""
		Set bill_zip.

		:param bill_zip: string
		:returns: Order
		"""

		return self.set_field('bill_zip', bill_zip)

	def set_bill_country(self, bill_country: str) -> 'Order':
		"""
		Set bill_cntry.

		:param bill_country: string
		:returns: Order
		"""

		return self.set_field('bill_cntry', bill_country)

	def to_dict(self) -> dict:
		"""
		Reduce the model to a dict.
		"""

		ret = self.copy()

		if 'customer' in ret and isinstance(ret['customer'], Customer):
			ret['customer'] = ret['customer'].to_dict()

		if 'items' in ret and isinstance(ret['items'], list):
			for i, e in enumerate(ret['items']):
				if isinstance(e, OrderItem):
					ret['items'][i] = ret['items'][i].to_dict()

		if 'charges' in ret and isinstance(ret['charges'], list):
			for i, e in enumerate(ret['charges']):
				if isinstance(e, OrderCharge):
					ret['charges'][i] = ret['charges'][i].to_dict()

		if 'coupons' in ret and isinstance(ret['coupons'], list):
			for i, e in enumerate(ret['coupons']):
				if isinstance(e, OrderCoupon):
					ret['coupons'][i] = ret['coupons'][i].to_dict()

		if 'discounts' in ret and isinstance(ret['discounts'], list):
			for i, e in enumerate(ret['discounts']):
				if isinstance(e, OrderDiscountTotal):
					ret['discounts'][i] = ret['discounts'][i].to_dict()

		if 'payments' in ret and isinstance(ret['payments'], list):
			for i, e in enumerate(ret['payments']):
				if isinstance(e, OrderPayment):
					ret['payments'][i] = ret['payments'][i].to_dict()

		if 'notes' in ret and isinstance(ret['notes'], list):
			for i, e in enumerate(ret['notes']):
				if isinstance(e, OrderNote):
					ret['notes'][i] = ret['notes'][i].to_dict()

		if 'CustomField_Values' in ret and isinstance(ret['CustomField_Values'], CustomFieldValues):
			ret['CustomField_Values'] = ret['CustomField_Values'].to_dict()

		return ret


"""
OrderShipment data model.
"""


class OrderShipment(Model):
	# ORDER_SHIPMENT_STATUS constants.
	ORDER_SHIPMENT_STATUS_PENDING = 0
	ORDER_SHIPMENT_STATUS_PICKING = 100
	ORDER_SHIPMENT_STATUS_SHIPPED = 200

	def __init__(self, data: dict = None):
		"""
		OrderShipment Constructor

		:param data: dict
		"""

		super().__init__(data)

	def get_id(self) -> int:
		"""
		Get id.

		:returns: int
		"""

		return self.get_field('id', 0)

	def get_code(self) -> str:
		"""
		Get code.

		:returns: string
		"""

		return self.get_field('code')

	def get_batch_id(self) -> int:
		"""
		Get batch_id.

		:returns: int
		"""

		return self.get_field('batch_id', 0)

	def get_order_id(self) -> int:
		"""
		Get order_id.

		:returns: int
		"""

		return self.get_field('order_id', 0)

	def get_status(self) -> int:
		"""
		Get status.

		:returns: int
		"""

		return self.get_field('status', 0)

	def get_label_count(self) -> int:
		"""
		Get labelcount.

		:returns: int
		"""

		return self.get_field('labelcount', 0)

	def get_ship_date(self) -> int:
		"""
		Get ship_date.

		:returns: int
		"""

		return self.get_field('ship_date', 0)

	def get_tracking_number(self) -> str:
		"""
		Get tracknum.

		:returns: string
		"""

		return self.get_field('tracknum')

	def get_tracking_type(self) -> str:
		"""
		Get tracktype.

		:returns: string
		"""

		return self.get_field('tracktype')

	def get_tracking_link(self) -> str:
		"""
		Get tracklink.

		:returns: string
		"""

		return self.get_field('tracklink')

	def get_weight(self) -> float:
		"""
		Get weight.

		:returns: float
		"""

		return self.get_field('weight', 0.00)

	def get_cost(self) -> float:
		"""
		Get cost.

		:returns: float
		"""

		return self.get_field('cost', 0.00)

	def get_formatted_cost(self) -> str:
		"""
		Get formatted_cost.

		:returns: string
		"""

		return self.get_field('formatted_cost')

	def set_id(self, id: int) -> 'OrderShipment':
		"""
		Set id.

		:param id: int
		:returns: OrderShipment
		"""

		return self.set_field('id', id)

	def set_code(self, code: str) -> 'OrderShipment':
		"""
		Set code.

		:param code: string
		:returns: OrderShipment
		"""

		return self.set_field('code', code)

	def set_batch_id(self, batch_id: int) -> 'OrderShipment':
		"""
		Set batch_id.

		:param batch_id: int
		:returns: OrderShipment
		"""

		return self.set_field('batch_id', batch_id)

	def set_order_id(self, order_id: int) -> 'OrderShipment':
		"""
		Set order_id.

		:param order_id: int
		:returns: OrderShipment
		"""

		return self.set_field('order_id', order_id)

	def set_status(self, status: int) -> 'OrderShipment':
		"""
		Set status.

		:param status: int
		:returns: OrderShipment
		"""

		return self.set_field('status', status)

	def set_label_count(self, label_count: int) -> 'OrderShipment':
		"""
		Set labelcount.

		:param label_count: int
		:returns: OrderShipment
		"""

		return self.set_field('labelcount', label_count)

	def set_ship_date(self, ship_date: int) -> 'OrderShipment':
		"""
		Set ship_date.

		:param ship_date: int
		:returns: OrderShipment
		"""

		return self.set_field('ship_date', ship_date)

	def set_tracking_number(self, tracking_number: str) -> 'OrderShipment':
		"""
		Set tracknum.

		:param tracking_number: string
		:returns: OrderShipment
		"""

		return self.set_field('tracknum', tracking_number)

	def set_tracking_type(self, tracking_type: str) -> 'OrderShipment':
		"""
		Set tracktype.

		:param tracking_type: string
		:returns: OrderShipment
		"""

		return self.set_field('tracktype', tracking_type)

	def set_tracking_link(self, tracking_link: str) -> 'OrderShipment':
		"""
		Set tracklink.

		:param tracking_link: string
		:returns: OrderShipment
		"""

		return self.set_field('tracklink', tracking_link)

	def set_weight(self, weight: float) -> 'OrderShipment':
		"""
		Set weight.

		:param weight: int
		:returns: OrderShipment
		"""

		return self.set_field('weight', weight)

	def set_cost(self, cost: float) -> 'OrderShipment':
		"""
		Set cost.

		:param cost: int
		:returns: OrderShipment
		"""

		return self.set_field('cost', cost)


"""
OrderItemOption data model.
"""


class OrderItemOption(Model):
	def __init__(self, data: dict = None):
		"""
		OrderItemOption Constructor

		:param data: dict
		"""

		super().__init__(data)

	def get_attribute(self) -> str:
		"""
		Get attribute.

		:returns: string
		"""

		return self.get_field('attribute')

	def get_value(self) -> str:
		"""
		Get value.

		:returns: string
		"""

		return self.get_field('value')

	def get_weight(self) -> float:
		"""
		Get weight.

		:returns: float
		"""

		return self.get_field('weight', 0.00)

	def get_retail(self) -> float:
		"""
		Get retail.

		:returns: float
		"""

		return self.get_field('retail', 0.00)

	def get_base_price(self) -> float:
		"""
		Get base_price.

		:returns: float
		"""

		return self.get_field('base_price', 0.00)

	def get_price(self) -> float:
		"""
		Get price.

		:returns: float
		"""

		return self.get_field('price', 0.00)

	def set_attribute(self, attribute: str) -> 'OrderItemOption':
		"""
		Set attribute.

		:param attribute: string
		:returns: OrderItemOption
		"""

		return self.set_field('attribute', attribute)

	def set_value(self, value: str) -> 'OrderItemOption':
		"""
		Set value.

		:param value: string
		:returns: OrderItemOption
		"""

		return self.set_field('value', value)

	def set_weight(self, weight: float) -> 'OrderItemOption':
		"""
		Set weight.

		:param weight: int
		:returns: OrderItemOption
		"""

		return self.set_field('weight', weight)

	def set_price(self, price: float) -> 'OrderItemOption':
		"""
		Set price.

		:param price: int
		:returns: OrderItemOption
		"""

		return self.set_field('price', price)

	def to_dict(self) -> dict:
		"""
		Reduce the model to a dict.
		"""

		ret = {}

		if self.has_field('attribute'):
			ret['attr_code'] = self.get_field('attribute')

		if self.has_field('value'):
			ret['opt_code_or_data'] = self.get_field('value')

		if self.has_field('price'):
			ret['price'] = self.get_field('price')

		if self.has_field('weight'):
			ret['weight'] = self.get_field('weight')

		return ret


"""
OrderItem data model.
"""


class OrderItem(Model):
	# ORDER_ITEM_STATUS constants.
	ORDER_ITEM_STATUS_PENDING = 0
	ORDER_ITEM_STATUS_PROCESSING = 100
	ORDER_ITEM_STATUS_SHIPPED = 200
	ORDER_ITEM_STATUS_PARTIALLY_SHIPPED = 201
	ORDER_ITEM_STATUS_GIFT_CERT_NOT_REDEEMED = 210
	ORDER_ITEM_STATUS_GIFT_CERT_REDEEMED = 211
	ORDER_ITEM_STATUS_DIGITAL_NOT_DOWNLOADED = 220
	ORDER_ITEM_STATUS_DIGITAL_DOWNLOADED = 221
	ORDER_ITEM_STATUS_CANCELLED = 300
	ORDER_ITEM_STATUS_BACKORDERED = 400
	ORDER_ITEM_STATUS_RMA_ISSUED = 500
	ORDER_ITEM_STATUS_RETURNED = 600

	def __init__(self, data: dict = None):
		"""
		OrderItem Constructor

		:param data: dict
		"""

		super().__init__(data)
		if self.has_field('shipment'):
			value = self.get_field('shipment')
			if isinstance(value, OrderShipment):
				pass
			elif isinstance(value, dict):
				self.set_field('shipment', OrderShipment(value))
			else:
				raise Exception('Expected OrderShipment or a dict')

		if self.has_field('discounts'):
			value = self.get_field('discounts')
			if isinstance(value, list):
				for i, e in enumerate(value):
					if isinstance(value, OrderItemDiscount):
						pass
					elif isinstance(e, dict):
						value[i] = OrderItemDiscount(e)
					else:
						raise Exception('Expected list of OrderItemDiscount or dict')
			else:
				raise Exception('Expected list of OrderItemDiscount or dict')

		if self.has_field('options'):
			value = self.get_field('options')
			if isinstance(value, list):
				for i, e in enumerate(value):
					if isinstance(value, OrderItemOption):
						pass
					elif isinstance(e, dict):
						value[i] = OrderItemOption(e)
					else:
						raise Exception('Expected list of OrderItemOption or dict')
			else:
				raise Exception('Expected list of OrderItemOption or dict')

		if self.has_field('subscription'):
			value = self.get_field('subscription')
			if isinstance(value, OrderItemSubscription):
				pass
			elif isinstance(value, dict):
				self.set_field('subscription', OrderItemSubscription(value))
			else:
				raise Exception('Expected OrderItemSubscription or a dict')

	def get_order_id(self) -> int:
		"""
		Get order_id.

		:returns: int
		"""

		return self.get_field('order_id', 0)

	def get_line_id(self) -> int:
		"""
		Get line_id.

		:returns: int
		"""

		return self.get_field('line_id', 0)

	def get_status(self) -> int:
		"""
		Get status.

		:returns: int
		"""

		return self.get_field('status', 0)

	def get_subscription_id(self) -> int:
		"""
		Get subscrp_id.

		:returns: int
		"""

		return self.get_field('subscrp_id', 0)

	def get_subscription_term_id(self) -> int:
		"""
		Get subterm_id.

		:returns: int
		"""

		return self.get_field('subterm_id', 0)

	def get_rma_id(self) -> int:
		"""
		Get rma_id.

		:returns: int
		"""

		return self.get_field('rma_id', 0)

	def get_rma_code(self) -> str:
		"""
		Get rma_code.

		:returns: string
		"""

		return self.get_field('rma_code')

	def get_rma_data_time_issued(self) -> int:
		"""
		Get rma_dt_issued.

		:returns: int
		"""

		return self.get_field('rma_dt_issued', 0)

	def get_rma_date_time_received(self) -> int:
		"""
		Get rma_dt_recvd.

		:returns: int
		"""

		return self.get_field('rma_dt_recvd', 0)

	def get_date_in_stock(self) -> int:
		"""
		Get dt_instock.

		:returns: int
		"""

		return self.get_field('dt_instock', 0)

	def get_code(self) -> str:
		"""
		Get code.

		:returns: string
		"""

		return self.get_field('code')

	def get_name(self) -> str:
		"""
		Get name.

		:returns: string
		"""

		return self.get_field('name')

	def get_sku(self) -> str:
		"""
		Get sku.

		:returns: string
		"""

		return self.get_field('sku')

	def get_retail(self) -> float:
		"""
		Get retail.

		:returns: float
		"""

		return self.get_field('retail', 0.00)

	def get_base_price(self) -> float:
		"""
		Get base_price.

		:returns: float
		"""

		return self.get_field('base_price', 0.00)

	def get_price(self) -> float:
		"""
		Get price.

		:returns: float
		"""

		return self.get_field('price', 0.00)

	def get_weight(self) -> float:
		"""
		Get weight.

		:returns: float
		"""

		return self.get_field('weight', 0.00)

	def get_taxable(self) -> bool:
		"""
		Get taxable.

		:returns: bool
		"""

		return self.get_field('taxable', False)

	def get_upsold(self) -> bool:
		"""
		Get upsold.

		:returns: bool
		"""

		return self.get_field('upsold', False)

	def get_quantity(self) -> int:
		"""
		Get quantity.

		:returns: int
		"""

		return self.get_field('quantity', 0)

	def get_shipment(self):
		"""
		Get shipment.

		:returns: OrderShipment|None
		"""

		return self.get_field('shipment', None)

	def get_discounts(self):
		"""
		Get discounts.

		:returns: List of OrderItemDiscount
		"""

		return self.get_field('discounts', [])

	def get_options(self):
		"""
		Get options.

		:returns: List of OrderItemOption
		"""

		return self.get_field('options', [])

	def get_subscription(self):
		"""
		Get subscription.

		:returns: OrderItemSubscription|None
		"""

		return self.get_field('subscription', None)

	def get_total(self) -> float:
		"""
		Get total.

		:returns: float
		"""

		return self.get_field('total', 0.00)

	def get_tracking_type(self) -> str:
		"""
		Get tracktype.

		:returns: string
		"""

		return self.get_field('tracktype')

	def get_tracking_number(self) -> str:
		"""
		Get tracknum.

		:returns: string
		"""

		return self.get_field('tracknum')

	def set_status(self, status: int) -> 'OrderItem':
		"""
		Set status.

		:param status: int
		:returns: OrderItem
		"""

		return self.set_field('status', status)

	def set_code(self, code: str) -> 'OrderItem':
		"""
		Set code.

		:param code: string
		:returns: OrderItem
		"""

		return self.set_field('code', code)

	def set_name(self, name: str) -> 'OrderItem':
		"""
		Set name.

		:param name: string
		:returns: OrderItem
		"""

		return self.set_field('name', name)

	def set_sku(self, sku: str) -> 'OrderItem':
		"""
		Set sku.

		:param sku: string
		:returns: OrderItem
		"""

		return self.set_field('sku', sku)

	def set_price(self, price: float) -> 'OrderItem':
		"""
		Set price.

		:param price: int
		:returns: OrderItem
		"""

		return self.set_field('price', price)

	def set_weight(self, weight: float) -> 'OrderItem':
		"""
		Set weight.

		:param weight: int
		:returns: OrderItem
		"""

		return self.set_field('weight', weight)

	def set_taxable(self, taxable: bool) -> 'OrderItem':
		"""
		Set taxable.

		:param taxable: bool
		:returns: OrderItem
		"""

		return self.set_field('taxable', taxable)

	def set_upsold(self, upsold: bool) -> 'OrderItem':
		"""
		Set upsold.

		:param upsold: bool
		:returns: OrderItem
		"""

		return self.set_field('upsold', upsold)

	def set_quantity(self, quantity: int) -> 'OrderItem':
		"""
		Set quantity.

		:param quantity: int
		:returns: OrderItem
		"""

		return self.set_field('quantity', quantity)

	def set_options(self, options: list) -> 'OrderItem':
		"""
		Set options.

		:param options: List of OrderItemOption
		:raises Exception:
		:returns: OrderItem
		"""

		for i, e in enumerate(options, 0):
			if isinstance(e, OrderItemOption):
				continue
			elif isinstance(e, dict):
				options[i] = OrderItemOption(e)
			else:
				raise Exception('Expected instance of OrderItemOption or dict')
		return self.set_field('options', options)

	def set_tracking_type(self, tracking_type: str) -> 'OrderItem':
		"""
		Set tracktype.

		:param tracking_type: string
		:returns: OrderItem
		"""

		return self.set_field('tracktype', tracking_type)

	def set_tracking_number(self, tracking_number: str) -> 'OrderItem':
		"""
		Set tracknum.

		:param tracking_number: string
		:returns: OrderItem
		"""

		return self.set_field('tracknum', tracking_number)

	def add_option(self, option: OrderItemOption) -> 'OrderItem':
		"""
		Add a OrderItemOption.

		:param option: OrderItemOption
		:returns: OrderItem
		"""

		if 'options' not in self:
			self['options'] = []
		self['options'].append(option)
		return self

	def to_dict(self) -> dict:
		"""
		Reduce the model to a dict.
		"""

		ret = self.copy()

		if 'shipment' in ret and isinstance(ret['shipment'], OrderShipment):
			ret['shipment'] = ret['shipment'].to_dict()

		if 'discounts' in ret and isinstance(ret['discounts'], list):
			for i, e in enumerate(ret['discounts']):
				if isinstance(e, OrderItemDiscount):
					ret['discounts'][i] = ret['discounts'][i].to_dict()

		if 'options' in ret and isinstance(ret['options'], list):
			for i, e in enumerate(ret['options']):
				if isinstance(e, OrderItemOption):
					ret['options'][i] = ret['options'][i].to_dict()

		if 'subscription' in ret and isinstance(ret['subscription'], OrderItemSubscription):
			ret['subscription'] = ret['subscription'].to_dict()

		return ret


"""
OrderCharge data model.
"""


class OrderCharge(Model):
	def __init__(self, data: dict = None):
		"""
		OrderCharge Constructor

		:param data: dict
		"""

		super().__init__(data)

	def get_order_id(self) -> int:
		"""
		Get order_id.

		:returns: int
		"""

		return self.get_field('order_id', 0)

	def get_charge_id(self) -> int:
		"""
		Get charge_id.

		:returns: int
		"""

		return self.get_field('charge_id', 0)

	def get_module_id(self) -> int:
		"""
		Get module_id.

		:returns: int
		"""

		return self.get_field('module_id', 0)

	def get_type(self) -> str:
		"""
		Get type.

		:returns: string
		"""

		return self.get_field('type')

	def get_description(self) -> str:
		"""
		Get descrip.

		:returns: string
		"""

		return self.get_field('descrip')

	def get_amount(self) -> float:
		"""
		Get amount.

		:returns: float
		"""

		return self.get_field('amount', 0.00)

	def get_display_amount(self) -> float:
		"""
		Get disp_amt.

		:returns: float
		"""

		return self.get_field('disp_amt', 0.00)

	def get_tax_exempt(self) -> bool:
		"""
		Get tax_exempt.

		:returns: bool
		"""

		return self.get_field('tax_exempt', False)

	def set_type(self, type: str) -> 'OrderCharge':
		"""
		Set type.

		:param type: string
		:returns: OrderCharge
		"""

		return self.set_field('type', type)

	def set_description(self, description: str) -> 'OrderCharge':
		"""
		Set descrip.

		:param description: string
		:returns: OrderCharge
		"""

		return self.set_field('descrip', description)

	def set_amount(self, amount: float) -> 'OrderCharge':
		"""
		Set amount.

		:param amount: int
		:returns: OrderCharge
		"""

		return self.set_field('amount', amount)

	def set_display_amount(self, display_amount: float) -> 'OrderCharge':
		"""
		Set disp_amt.

		:param display_amount: int
		:returns: OrderCharge
		"""

		return self.set_field('disp_amt', display_amount)

	def set_tax_exempt(self, tax_exempt: bool) -> 'OrderCharge':
		"""
		Set tax_exempt.

		:param tax_exempt: bool
		:returns: OrderCharge
		"""

		return self.set_field('tax_exempt', tax_exempt)


"""
OrderCoupon data model.
"""


class OrderCoupon(Model):
	def __init__(self, data: dict = None):
		"""
		OrderCoupon Constructor

		:param data: dict
		"""

		super().__init__(data)

	def get_order_id(self) -> int:
		"""
		Get order_id.

		:returns: int
		"""

		return self.get_field('order_id', 0)

	def get_coupon_id(self) -> int:
		"""
		Get coupon_id.

		:returns: int
		"""

		return self.get_field('coupon_id', 0)

	def get_code(self) -> str:
		"""
		Get code.

		:returns: string
		"""

		return self.get_field('code')

	def get_description(self) -> str:
		"""
		Get descrip.

		:returns: string
		"""

		return self.get_field('descrip')

	def get_total(self) -> float:
		"""
		Get total.

		:returns: float
		"""

		return self.get_field('total', 0.00)


"""
OrderItemDiscount data model.
"""


class OrderItemDiscount(Model):
	def __init__(self, data: dict = None):
		"""
		OrderItemDiscount Constructor

		:param data: dict
		"""

		super().__init__(data)

	def get_order_id(self) -> int:
		"""
		Get order_id.

		:returns: int
		"""

		return self.get_field('order_id', 0)

	def get_line_id(self) -> int:
		"""
		Get line_id.

		:returns: int
		"""

		return self.get_field('line_id', 0)

	def get_price_group_id(self) -> int:
		"""
		Get pgrp_id.

		:returns: int
		"""

		return self.get_field('pgrp_id', 0)

	def get_display(self) -> bool:
		"""
		Get display.

		:returns: bool
		"""

		return self.get_field('display', False)

	def get_description(self) -> str:
		"""
		Get descrip.

		:returns: string
		"""

		return self.get_field('descrip')

	def get_discount(self) -> float:
		"""
		Get discount.

		:returns: float
		"""

		return self.get_field('discount', 0.00)


"""
OrderDiscountTotal data model.
"""


class OrderDiscountTotal(Model):
	def __init__(self, data: dict = None):
		"""
		OrderDiscountTotal Constructor

		:param data: dict
		"""

		super().__init__(data)

	def get_order_id(self) -> int:
		"""
		Get order_id.

		:returns: int
		"""

		return self.get_field('order_id', 0)

	def get_price_group_id(self) -> int:
		"""
		Get pgrp_id.

		:returns: int
		"""

		return self.get_field('pgrp_id', 0)

	def get_name(self) -> str:
		"""
		Get name.

		:returns: string
		"""

		return self.get_field('name')

	def get_description(self) -> str:
		"""
		Get descrip.

		:returns: string
		"""

		return self.get_field('descrip')

	def get_total(self) -> float:
		"""
		Get total.

		:returns: float
		"""

		return self.get_field('total', 0.00)


"""
OrderPayment data model.
"""


class OrderPayment(Model):
	# ORDER_PAYMENT_TYPE constants.
	ORDER_PAYMENT_TYPE_DECLINED = 0
	ORDER_PAYMENT_TYPE_LEGACY_AUTH = 1
	ORDER_PAYMENT_TYPE_LEGACY_CAPTURE = 2
	ORDER_PAYMENT_TYPE_AUTH = 3
	ORDER_PAYMENT_TYPE_CAPTURE = 4
	ORDER_PAYMENT_TYPE_AUTH_CAPTURE = 5
	ORDER_PAYMENT_TYPE_REFUND = 6
	ORDER_PAYMENT_TYPE_VOID = 7

	def __init__(self, data: dict = None):
		"""
		OrderPayment Constructor

		:param data: dict
		"""

		super().__init__(data)

	def get_id(self) -> int:
		"""
		Get id.

		:returns: int
		"""

		return self.get_field('id', 0)

	def get_order_id(self) -> int:
		"""
		Get order_id.

		:returns: int
		"""

		return self.get_field('order_id', 0)

	def get_type(self) -> int:
		"""
		Get type.

		:returns: int
		"""

		return self.get_field('type', 0)

	def get_reference_number(self) -> str:
		"""
		Get refnum.

		:returns: string
		"""

		return self.get_field('refnum')

	def get_amount(self) -> float:
		"""
		Get amount.

		:returns: float
		"""

		return self.get_field('amount', 0.00)

	def get_formatted_amount(self) -> str:
		"""
		Get formatted_amount.

		:returns: string
		"""

		return self.get_field('formatted_amount')

	def get_available(self) -> float:
		"""
		Get available.

		:returns: float
		"""

		return self.get_field('available', 0.00)

	def get_formatted_available(self) -> str:
		"""
		Get formatted_available.

		:returns: string
		"""

		return self.get_field('formatted_available')

	def get_date_time_stamp(self) -> int:
		"""
		Get dtstamp.

		:returns: int
		"""

		return self.get_field('dtstamp', 0)

	def get_expires(self) -> str:
		"""
		Get expires.

		:returns: string
		"""

		return self.get_field('expires')

	def get_payment_id(self) -> int:
		"""
		Get pay_id.

		:returns: int
		"""

		return self.get_field('pay_id', 0)

	def get_payment_sec_id(self) -> int:
		"""
		Get pay_secid.

		:returns: int
		"""

		return self.get_field('pay_secid', 0)

	def get_decrypt_status(self) -> str:
		"""
		Get decrypt_status.

		:returns: string
		"""

		return self.get_field('decrypt_status')

	def get_decrypt_error(self) -> str:
		"""
		Get decrypt_error.

		:returns: string
		"""

		return self.get_field('decrypt_error')

	def get_description(self) -> str:
		"""
		Get description.

		:returns: string
		"""

		return self.get_field('description')

	def get_payment_data(self) -> dict:
		"""
		Get data.

		:returns: dict
		"""

		return self.get_field('data', {})


"""
Subscription data model.
"""


class Subscription(Model):
	def __init__(self, data: dict = None):
		"""
		Subscription Constructor

		:param data: dict
		"""

		super().__init__(data)

	def get_id(self) -> int:
		"""
		Get id.

		:returns: int
		"""

		return self.get_field('id', 0)

	def get_order_id(self) -> int:
		"""
		Get order_id.

		:returns: int
		"""

		return self.get_field('order_id', 0)

	def get_line_id(self) -> int:
		"""
		Get line_id.

		:returns: int
		"""

		return self.get_field('line_id', 0)

	def get_customer_id(self) -> int:
		"""
		Get cust_id.

		:returns: int
		"""

		return self.get_field('cust_id', 0)

	def get_customer_payment_card_id(self) -> int:
		"""
		Get custpc_id.

		:returns: int
		"""

		return self.get_field('custpc_id', 0)

	def get_product_id(self) -> int:
		"""
		Get product_id.

		:returns: int
		"""

		return self.get_field('product_id', 0)

	def get_subscription_term_id(self) -> int:
		"""
		Get subterm_id.

		:returns: int
		"""

		return self.get_field('subterm_id', 0)

	def get_address_id(self) -> int:
		"""
		Get addr_id.

		:returns: int
		"""

		return self.get_field('addr_id', 0)

	def get_ship_id(self) -> int:
		"""
		Get ship_id.

		:returns: int
		"""

		return self.get_field('ship_id', 0)

	def get_ship_data(self) -> str:
		"""
		Get ship_data.

		:returns: string
		"""

		return self.get_field('ship_data')

	def get_quantity(self) -> int:
		"""
		Get quantity.

		:returns: int
		"""

		return self.get_field('quantity', 0)

	def get_term_remaining(self) -> int:
		"""
		Get termrem.

		:returns: int
		"""

		return self.get_field('termrem', 0)

	def get_term_processed(self) -> int:
		"""
		Get termproc.

		:returns: int
		"""

		return self.get_field('termproc', 0)

	def get_first_date(self) -> int:
		"""
		Get firstdate.

		:returns: int
		"""

		return self.get_field('firstdate', 0)

	def get_last_date(self) -> int:
		"""
		Get lastdate.

		:returns: int
		"""

		return self.get_field('lastdate', 0)

	def get_next_date(self) -> int:
		"""
		Get nextdate.

		:returns: int
		"""

		return self.get_field('nextdate', 0)

	def get_status(self) -> str:
		"""
		Get status.

		:returns: string
		"""

		return self.get_field('status')

	def get_message(self) -> str:
		"""
		Get message.

		:returns: string
		"""

		return self.get_field('message')

	def get_cancel_date(self) -> str:
		"""
		Get cncldate.

		:returns: string
		"""

		return self.get_field('cncldate')

	def get_tax(self) -> float:
		"""
		Get tax.

		:returns: float
		"""

		return self.get_field('tax', 0.00)

	def get_formatted_tax(self) -> str:
		"""
		Get formatted_tax.

		:returns: string
		"""

		return self.get_field('formatted_tax')

	def get_shipping(self) -> float:
		"""
		Get shipping.

		:returns: float
		"""

		return self.get_field('shipping', 0.00)

	def get_formatted_shipping(self) -> str:
		"""
		Get formatted_shipping.

		:returns: string
		"""

		return self.get_field('formatted_shipping')

	def get_subtotal(self) -> float:
		"""
		Get subtotal.

		:returns: float
		"""

		return self.get_field('subtotal', 0.00)

	def get_formatted_subtotal(self) -> str:
		"""
		Get formatted_subtotal.

		:returns: string
		"""

		return self.get_field('formatted_subtotal')

	def get_total(self) -> float:
		"""
		Get total.

		:returns: float
		"""

		return self.get_field('total', 0.00)

	def get_formatted_total(self) -> str:
		"""
		Get formatted_total.

		:returns: string
		"""

		return self.get_field('formatted_total')

	def set_cancel_date(self, cancel_date: str) -> 'Subscription':
		"""
		Set cncldate.

		:param cancel_date: string
		:returns: Subscription
		"""

		return self.set_field('cncldate', cancel_date)


"""
ProductSubscriptionTerm data model.
"""


class ProductSubscriptionTerm(Model):
	# TERM_FREQUENCY constants.
	TERM_FREQUENCY_N_DAYS = 'n'
	TERM_FREQUENCY_N_MONTHS = 'n_months'
	TERM_FREQUENCY_DAILY = 'daily'
	TERM_FREQUENCY_WEEKLY = 'weekly'
	TERM_FREQUENCY_BIWEEKLY = 'biweekly'
	TERM_FREQUENCY_QUARTERLY = 'quarterly'
	TERM_FREQUENCY_SEMIANNUALLY = 'semiannually'
	TERM_FREQUENCY_ANNUALLY = 'annually'
	TERM_FREQUENCY_FIXED_WEEKLY = 'fixedweekly'
	TERM_FREQUENCY_FIXED_MONTHLY = 'fixedmonthly'
	TERM_FREQUENCY_DATES = 'dates'

	def __init__(self, data: dict = None):
		"""
		ProductSubscriptionTerm Constructor

		:param data: dict
		"""

		super().__init__(data)

	def get_id(self) -> int:
		"""
		Get id.

		:returns: int
		"""

		return self.get_field('id', 0)

	def get_product_id(self) -> int:
		"""
		Get product_id.

		:returns: int
		"""

		return self.get_field('product_id', 0)

	def get_frequency(self) -> str:
		"""
		Get frequency.

		:returns: string
		"""

		return self.get_field('frequency')

	def get_term(self) -> int:
		"""
		Get term.

		:returns: int
		"""

		return self.get_field('term', 0)

	def get_description(self) -> str:
		"""
		Get descrip.

		:returns: string
		"""

		return self.get_field('descrip')

	def get_n(self) -> int:
		"""
		Get n.

		:returns: int
		"""

		return self.get_field('n', 0)

	def get_fixed_day_of_week(self) -> int:
		"""
		Get fixed_dow.

		:returns: int
		"""

		return self.get_field('fixed_dow', 0)

	def get_fixed_day_of_month(self) -> int:
		"""
		Get fixed_dom.

		:returns: int
		"""

		return self.get_field('fixed_dom', 0)

	def get_subscription_count(self) -> int:
		"""
		Get sub_count.

		:returns: int
		"""

		return self.get_field('sub_count', 0)


"""
OrderCustomField data model.
"""


class OrderCustomField(Model):
	def __init__(self, data: dict = None):
		"""
		OrderCustomField Constructor

		:param data: dict
		"""

		super().__init__(data)
		if self.has_field('module'):
			value = self.get_field('module')
			if isinstance(value, Module):
				pass
			elif isinstance(value, dict):
				self.set_field('module', Module(value))
			else:
				raise Exception('Expected Module or a dict')

	def get_code(self) -> str:
		"""
		Get code.

		:returns: string
		"""

		return self.get_field('code')

	def get_name(self) -> str:
		"""
		Get name.

		:returns: string
		"""

		return self.get_field('name')

	def get_type(self) -> str:
		"""
		Get type.

		:returns: string
		"""

		return self.get_field('type')

	def get_searchable(self) -> bool:
		"""
		Get searchable.

		:returns: bool
		"""

		return self.get_field('searchable', False)

	def get_sortable(self) -> bool:
		"""
		Get sortable.

		:returns: bool
		"""

		return self.get_field('sortable', False)

	def get_module(self):
		"""
		Get module.

		:returns: Module|None
		"""

		return self.get_field('module', None)

	def get_choices(self) -> dict:
		"""
		Get choices.

		:returns: dict
		"""

		return self.get_field('choices', {})

	def set_code(self, code: str) -> 'OrderCustomField':
		"""
		Set code.

		:param code: string
		:returns: OrderCustomField
		"""

		return self.set_field('code', code)

	def set_name(self, name: str) -> 'OrderCustomField':
		"""
		Set name.

		:param name: string
		:returns: OrderCustomField
		"""

		return self.set_field('name', name)

	def set_type(self, type: str) -> 'OrderCustomField':
		"""
		Set type.

		:param type: string
		:returns: OrderCustomField
		"""

		return self.set_field('type', type)

	def set_searchable(self, searchable: bool) -> 'OrderCustomField':
		"""
		Set searchable.

		:param searchable: bool
		:returns: OrderCustomField
		"""

		return self.set_field('searchable', searchable)

	def set_sortable(self, sortable: bool) -> 'OrderCustomField':
		"""
		Set sortable.

		:param sortable: bool
		:returns: OrderCustomField
		"""

		return self.set_field('sortable', sortable)

	def set_module(self, module) -> 'OrderCustomField':
		"""
		Set module.

		:param module: Module|dict
		:returns: OrderCustomField
		:raises Exception:
		"""

		if module is None or isinstance(module, Module):
			return self.set_field('module', module)
		elif isinstance(module, dict):
			return self.set_field('module', Module(module))
		raise Exception('Expected instance of Module, Object, or None')

	def set_choices(self, choices) -> 'OrderCustomField':
		"""
		Set choices.

		:param choices: list
		:returns: OrderCustomField
		"""

		return self.set_field('choices', choices)

	def to_dict(self) -> dict:
		"""
		Reduce the model to a dict.
		"""

		ret = self.copy()

		if 'module' in ret and isinstance(ret['module'], Module):
			ret['module'] = ret['module'].to_dict()

		return ret


"""
CustomerPaymentCard data model.
"""


class CustomerPaymentCard(Model):
	def __init__(self, data: dict = None):
		"""
		CustomerPaymentCard Constructor

		:param data: dict
		"""

		super().__init__(data)

	def get_id(self) -> int:
		"""
		Get id.

		:returns: int
		"""

		return self.get_field('id', 0)

	def get_customer_id(self) -> int:
		"""
		Get cust_id.

		:returns: int
		"""

		return self.get_field('cust_id', 0)

	def get_first_name(self) -> str:
		"""
		Get fname.

		:returns: string
		"""

		return self.get_field('fname')

	def get_last_name(self) -> str:
		"""
		Get lname.

		:returns: string
		"""

		return self.get_field('lname')

	def get_expiration_month(self) -> int:
		"""
		Get exp_month.

		:returns: int
		"""

		return self.get_field('exp_month', 0)

	def get_expiration_year(self) -> int:
		"""
		Get exp_year.

		:returns: int
		"""

		return self.get_field('exp_year', 0)

	def get_last_four(self) -> str:
		"""
		Get lastfour.

		:returns: string
		"""

		return self.get_field('lastfour')

	def get_address1(self) -> str:
		"""
		Get addr1.

		:returns: string
		"""

		return self.get_field('addr1')

	def get_address2(self) -> str:
		"""
		Get addr2.

		:returns: string
		"""

		return self.get_field('addr2')

	def get_city(self) -> str:
		"""
		Get city.

		:returns: string
		"""

		return self.get_field('city')

	def get_state(self) -> str:
		"""
		Get state.

		:returns: string
		"""

		return self.get_field('state')

	def get_zip(self) -> str:
		"""
		Get zip.

		:returns: string
		"""

		return self.get_field('zip')

	def get_country(self) -> str:
		"""
		Get cntry.

		:returns: string
		"""

		return self.get_field('cntry')

	def get_last_used(self) -> str:
		"""
		Get lastused.

		:returns: string
		"""

		return self.get_field('lastused')

	def get_token(self) -> str:
		"""
		Get token.

		:returns: string
		"""

		return self.get_field('token')

	def get_type_id(self) -> int:
		"""
		Get type_id.

		:returns: int
		"""

		return self.get_field('type_id', 0)

	def get_reference_count(self) -> int:
		"""
		Get refcount.

		:returns: int
		"""

		return self.get_field('refcount', 0)

	def get_type(self) -> str:
		"""
		Get type.

		:returns: string
		"""

		return self.get_field('type')

	def get_module_code(self) -> str:
		"""
		Get mod_code.

		:returns: string
		"""

		return self.get_field('mod_code')

	def get_method_code(self) -> str:
		"""
		Get meth_code.

		:returns: string
		"""

		return self.get_field('meth_code')


"""
OrderProductAttribute data model.
"""


class OrderProductAttribute(Model):
	def __init__(self, data: dict = None):
		"""
		OrderProductAttribute Constructor

		:param data: dict
		"""

		super().__init__(data)

	def get_code(self) -> str:
		"""
		Get code.

		:returns: string
		"""

		return self.get_field('code')

	def get_template_code(self) -> str:
		"""
		Get template_code.

		:returns: string
		"""

		return self.get_field('template_code')

	def get_value(self) -> str:
		"""
		Get value.

		:returns: string
		"""

		return self.get_field('value')

	def set_code(self, code: str) -> 'OrderProductAttribute':
		"""
		Set code.

		:param code: string
		:returns: OrderProductAttribute
		"""

		return self.set_field('code', code)

	def set_template_code(self, template_code: str) -> 'OrderProductAttribute':
		"""
		Set template_code.

		:param template_code: string
		:returns: OrderProductAttribute
		"""

		return self.set_field('template_code', template_code)

	def set_value(self, value: str) -> 'OrderProductAttribute':
		"""
		Set value.

		:param value: string
		:returns: OrderProductAttribute
		"""

		return self.set_field('value', value)


"""
OrderProduct data model.
"""


class OrderProduct(Model):
	def __init__(self, data: dict = None):
		"""
		OrderProduct Constructor

		:param data: dict
		"""

		super().__init__(data)
		if self.has_field('attributes'):
			value = self.get_field('attributes')
			if isinstance(value, list):
				for i, e in enumerate(value):
					if isinstance(value, OrderProductAttribute):
						pass
					elif isinstance(e, dict):
						value[i] = OrderProductAttribute(e)
					else:
						raise Exception('Expected list of OrderProductAttribute or dict')
			else:
				raise Exception('Expected list of OrderProductAttribute or dict')

	def get_status(self) -> int:
		"""
		Get status.

		:returns: int
		"""

		return self.get_field('status', 0)

	def get_code(self) -> str:
		"""
		Get code.

		:returns: string
		"""

		return self.get_field('code')

	def get_sku(self) -> str:
		"""
		Get sku.

		:returns: string
		"""

		return self.get_field('sku')

	def get_tracking_number(self) -> str:
		"""
		Get tracknum.

		:returns: string
		"""

		return self.get_field('tracknum')

	def get_tracking_type(self) -> str:
		"""
		Get tracktype.

		:returns: string
		"""

		return self.get_field('tracktype')

	def get_quantity(self) -> int:
		"""
		Get quantity.

		:returns: int
		"""

		return self.get_field('quantity', 0)

	def get_attributes(self):
		"""
		Get attributes.

		:returns: List of OrderProductAttribute
		"""

		return self.get_field('attributes', [])

	def set_status(self, status: int) -> 'OrderProduct':
		"""
		Set status.

		:param status: int
		:returns: OrderProduct
		"""

		return self.set_field('status', status)

	def set_code(self, code: str) -> 'OrderProduct':
		"""
		Set code.

		:param code: string
		:returns: OrderProduct
		"""

		return self.set_field('code', code)

	def set_sku(self, sku: str) -> 'OrderProduct':
		"""
		Set sku.

		:param sku: string
		:returns: OrderProduct
		"""

		return self.set_field('sku', sku)

	def set_tracking_number(self, tracking_number: str) -> 'OrderProduct':
		"""
		Set tracknum.

		:param tracking_number: string
		:returns: OrderProduct
		"""

		return self.set_field('tracknum', tracking_number)

	def set_tracking_type(self, tracking_type: str) -> 'OrderProduct':
		"""
		Set tracktype.

		:param tracking_type: string
		:returns: OrderProduct
		"""

		return self.set_field('tracktype', tracking_type)

	def set_quantity(self, quantity: int) -> 'OrderProduct':
		"""
		Set quantity.

		:param quantity: int
		:returns: OrderProduct
		"""

		return self.set_field('quantity', quantity)

	def set_attributes(self, attributes: list) -> 'OrderProduct':
		"""
		Set attributes.

		:param attributes: List of OrderProductAttribute
		:raises Exception:
		:returns: OrderProduct
		"""

		for i, e in enumerate(attributes, 0):
			if isinstance(e, OrderProductAttribute):
				continue
			elif isinstance(e, dict):
				attributes[i] = OrderProductAttribute(e)
			else:
				raise Exception('Expected instance of OrderProductAttribute or dict')
		return self.set_field('attributes', attributes)

	def add_attribute(self, attribute: OrderProductAttribute) -> 'OrderProduct':
		"""
		Add a OrderProductAttribute.

		:param attribute: OrderProductAttribute
		:returns: OrderProduct
		"""

		if 'attributes' not in self:
			self['attributes'] = []
		self['attributes'].append(attribute)
		return self

	def to_dict(self) -> dict:
		"""
		Reduce the model to a dict.
		"""

		ret = self.copy()

		if 'attributes' in ret and isinstance(ret['attributes'], list):
			for i, e in enumerate(ret['attributes']):
				if isinstance(e, OrderProductAttribute):
					ret['attributes'][i] = ret['attributes'][i].to_dict()

		return ret


"""
ProductInventorySettings data model.
"""


class ProductInventorySettings(Model):
	def __init__(self, data: dict = None):
		"""
		ProductInventorySettings Constructor

		:param data: dict
		"""

		super().__init__(data)

	def get_active(self) -> bool:
		"""
		Get active.

		:returns: bool
		"""

		return self.get_field('active', False)

	def get_in_stock_message_short(self) -> str:
		"""
		Get in_short.

		:returns: string
		"""

		return self.get_field('in_short')

	def get_in_stock_message_long(self) -> str:
		"""
		Get in_long.

		:returns: string
		"""

		return self.get_field('in_long')

	def get_track_low_stock_level(self) -> str:
		"""
		Get low_track.

		:returns: string
		"""

		return self.get_field('low_track')

	def get_low_stock_level(self) -> int:
		"""
		Get low_level.

		:returns: int
		"""

		return self.get_field('low_level', 0)

	def get_low_stock_level_default(self) -> bool:
		"""
		Get low_lvl_d.

		:returns: bool
		"""

		return self.get_field('low_lvl_d', False)

	def get_low_stock_message_short(self) -> str:
		"""
		Get low_short.

		:returns: string
		"""

		return self.get_field('low_short')

	def get_low_stock_message_long(self) -> str:
		"""
		Get low_long.

		:returns: string
		"""

		return self.get_field('low_long')

	def get_track_out_of_stock_level(self) -> str:
		"""
		Get out_track.

		:returns: string
		"""

		return self.get_field('out_track')

	def get_hide_out_of_stock(self) -> str:
		"""
		Get out_hide.

		:returns: string
		"""

		return self.get_field('out_hide')

	def get_out_of_stock_level(self) -> int:
		"""
		Get out_level.

		:returns: int
		"""

		return self.get_field('out_level', 0)

	def get_out_of_stock_level_default(self) -> bool:
		"""
		Get out_lvl_d.

		:returns: bool
		"""

		return self.get_field('out_lvl_d', False)

	def get_out_of_stock_message_short(self) -> str:
		"""
		Get out_short.

		:returns: string
		"""

		return self.get_field('out_short')

	def get_out_of_stock_message_long(self) -> str:
		"""
		Get out_long.

		:returns: string
		"""

		return self.get_field('out_long')

	def get_limited_stock_message(self) -> str:
		"""
		Get ltd_long.

		:returns: string
		"""

		return self.get_field('ltd_long')


"""
ProductVariantPart data model.
"""


class ProductVariantPart(Model):
	def __init__(self, data: dict = None):
		"""
		ProductVariantPart Constructor

		:param data: dict
		"""

		super().__init__(data)

	def get_product_id(self) -> int:
		"""
		Get product_id.

		:returns: int
		"""

		return self.get_field('product_id', 0)

	def get_product_code(self) -> str:
		"""
		Get product_code.

		:returns: string
		"""

		return self.get_field('product_code')

	def get_product_name(self) -> str:
		"""
		Get product_name.

		:returns: string
		"""

		return self.get_field('product_name')

	def get_quantity(self) -> int:
		"""
		Get quantity.

		:returns: int
		"""

		return self.get_field('quantity', 0)


"""
ProductVariantDimension data model.
"""


class ProductVariantDimension(Model):
	def __init__(self, data: dict = None):
		"""
		ProductVariantDimension Constructor

		:param data: dict
		"""

		super().__init__(data)

	def get_attribute_id(self) -> int:
		"""
		Get attr_id.

		:returns: int
		"""

		return self.get_field('attr_id', 0)

	def get_attribute_template_attribute_id(self) -> int:
		"""
		Get attmpat_id.

		:returns: int
		"""

		return self.get_field('attmpat_id', 0)

	def get_option_id(self) -> int:
		"""
		Get option_id.

		:returns: int
		"""

		return self.get_field('option_id', 0)

	def get_option_code(self) -> str:
		"""
		Get option_code.

		:returns: string
		"""

		return self.get_field('option_code')


"""
OrderItemSubscription data model.
"""


class OrderItemSubscription(Model):
	def __init__(self, data: dict = None):
		"""
		OrderItemSubscription Constructor

		:param data: dict
		"""

		super().__init__(data)
		if self.has_field('productsubscriptionterm'):
			value = self.get_field('productsubscriptionterm')
			if isinstance(value, ProductSubscriptionTerm):
				pass
			elif isinstance(value, dict):
				self.set_field('productsubscriptionterm', ProductSubscriptionTerm(value))
			else:
				raise Exception('Expected ProductSubscriptionTerm or a dict')

		if self.has_field('options'):
			value = self.get_field('options')
			if isinstance(value, list):
				for i, e in enumerate(value):
					if isinstance(value, SubscriptionOption):
						pass
					elif isinstance(e, dict):
						value[i] = SubscriptionOption(e)
					else:
						raise Exception('Expected list of SubscriptionOption or dict')
			else:
				raise Exception('Expected list of SubscriptionOption or dict')

	def get_method(self) -> str:
		"""
		Get method.

		:returns: string
		"""

		return self.get_field('method')

	def get_product_subscription_term(self):
		"""
		Get productsubscriptionterm.

		:returns: ProductSubscriptionTerm|None
		"""

		return self.get_field('productsubscriptionterm', None)

	def get_options(self):
		"""
		Get options.

		:returns: List of SubscriptionOption
		"""

		return self.get_field('options', [])

	def to_dict(self) -> dict:
		"""
		Reduce the model to a dict.
		"""

		ret = self.copy()

		if 'productsubscriptionterm' in ret and isinstance(ret['productsubscriptionterm'], ProductSubscriptionTerm):
			ret['productsubscriptionterm'] = ret['productsubscriptionterm'].to_dict()

		if 'options' in ret and isinstance(ret['options'], list):
			for i, e in enumerate(ret['options']):
				if isinstance(e, SubscriptionOption):
					ret['options'][i] = ret['options'][i].to_dict()

		return ret


"""
SubscriptionOption data model.
"""


class SubscriptionOption(Model):
	def __init__(self, data: dict = None):
		"""
		SubscriptionOption Constructor

		:param data: dict
		"""

		super().__init__(data)

	def get_subscription_id(self) -> int:
		"""
		Get subscrp_id.

		:returns: int
		"""

		return self.get_field('subscrp_id', 0)

	def get_template_code(self) -> str:
		"""
		Get templ_code.

		:returns: string
		"""

		return self.get_field('templ_code')

	def get_attribute_code(self) -> str:
		"""
		Get attr_code.

		:returns: string
		"""

		return self.get_field('attr_code')

	def get_value(self) -> str:
		"""
		Get value.

		:returns: string
		"""

		return self.get_field('value')


"""
ProductInventoryAdjustment data model.
"""


class ProductInventoryAdjustment(Model):
	def __init__(self, data: dict = None):
		"""
		ProductInventoryAdjustment Constructor

		:param data: dict
		"""

		super().__init__(data)

	def get_product_id(self) -> int:
		"""
		Get product_id.

		:returns: int
		"""

		return self.get_field('product_id', 0)

	def get_product_code(self) -> str:
		"""
		Get product_code.

		:returns: string
		"""

		return self.get_field('product_code')

	def get_product_sku(self) -> str:
		"""
		Get product_sku.

		:returns: string
		"""

		return self.get_field('product_sku')

	def get_adjustment(self) -> float:
		"""
		Get adjustment.

		:returns: float
		"""

		return self.get_field('adjustment', 0.00)

	def set_product_id(self, product_id: int) -> 'ProductInventoryAdjustment':
		"""
		Set product_id.

		:param product_id: int
		:returns: ProductInventoryAdjustment
		"""

		return self.set_field('product_id', product_id)

	def set_product_code(self, product_code: str) -> 'ProductInventoryAdjustment':
		"""
		Set product_code.

		:param product_code: string
		:returns: ProductInventoryAdjustment
		"""

		return self.set_field('product_code', product_code)

	def set_product_sku(self, product_sku: str) -> 'ProductInventoryAdjustment':
		"""
		Set product_sku.

		:param product_sku: string
		:returns: ProductInventoryAdjustment
		"""

		return self.set_field('product_sku', product_sku)

	def set_adjustment(self, adjustment: float) -> 'ProductInventoryAdjustment':
		"""
		Set adjustment.

		:param adjustment: int
		:returns: ProductInventoryAdjustment
		"""

		return self.set_field('adjustment', adjustment)


"""
OrderItemAttribute data model.
"""


class OrderItemAttribute(Model):
	def __init__(self, data: dict = None):
		"""
		OrderItemAttribute Constructor

		:param data: dict
		"""

		super().__init__(data)

	def get_attribute_code(self) -> str:
		"""
		Get attr_code.

		:returns: string
		"""

		return self.get_field('attr_code')

	def get_option_code_or_data(self) -> str:
		"""
		Get opt_code_or_data.

		:returns: string
		"""

		return self.get_field('opt_code_or_data')

	def get_price(self) -> float:
		"""
		Get price.

		:returns: float
		"""

		return self.get_field('price', 0.00)

	def get_weight(self) -> float:
		"""
		Get weight.

		:returns: float
		"""

		return self.get_field('weight', 0.00)

	def set_attribute_code(self, attribute_code: str) -> 'OrderItemAttribute':
		"""
		Set attr_code.

		:param attribute_code: string
		:returns: OrderItemAttribute
		"""

		return self.set_field('attr_code', attribute_code)

	def set_option_code_or_data(self, option_code_or_data: str) -> 'OrderItemAttribute':
		"""
		Set opt_code_or_data.

		:param option_code_or_data: string
		:returns: OrderItemAttribute
		"""

		return self.set_field('opt_code_or_data', option_code_or_data)

	def set_price(self, price: float) -> 'OrderItemAttribute':
		"""
		Set price.

		:param price: int
		:returns: OrderItemAttribute
		"""

		return self.set_field('price', price)

	def set_weight(self, weight: float) -> 'OrderItemAttribute':
		"""
		Set weight.

		:param weight: int
		:returns: OrderItemAttribute
		"""

		return self.set_field('weight', weight)


"""
OrderShipmentUpdate data model.
"""


class OrderShipmentUpdate(Model):
	def __init__(self, data: dict = None):
		"""
		OrderShipmentUpdate Constructor

		:param data: dict
		"""

		super().__init__(data)

	def get_shipment_id(self) -> int:
		"""
		Get shpmnt_id.

		:returns: int
		"""

		return self.get_field('shpmnt_id', 0)

	def get_mark_shipped(self) -> bool:
		"""
		Get mark_shipped.

		:returns: bool
		"""

		return self.get_field('mark_shipped', False)

	def get_tracking_number(self) -> str:
		"""
		Get tracknum.

		:returns: string
		"""

		return self.get_field('tracknum')

	def get_tracking_type(self) -> str:
		"""
		Get tracktype.

		:returns: string
		"""

		return self.get_field('tracktype')

	def get_cost(self) -> float:
		"""
		Get cost.

		:returns: float
		"""

		return self.get_field('cost', 0.00)

	def set_shipment_id(self, shipment_id: int) -> 'OrderShipmentUpdate':
		"""
		Set shpmnt_id.

		:param shipment_id: int
		:returns: OrderShipmentUpdate
		"""

		return self.set_field('shpmnt_id', shipment_id)

	def set_mark_shipped(self, mark_shipped: bool) -> 'OrderShipmentUpdate':
		"""
		Set mark_shipped.

		:param mark_shipped: bool
		:returns: OrderShipmentUpdate
		"""

		return self.set_field('mark_shipped', mark_shipped)

	def set_tracking_number(self, tracking_number: str) -> 'OrderShipmentUpdate':
		"""
		Set tracknum.

		:param tracking_number: string
		:returns: OrderShipmentUpdate
		"""

		return self.set_field('tracknum', tracking_number)

	def set_tracking_type(self, tracking_type: str) -> 'OrderShipmentUpdate':
		"""
		Set tracktype.

		:param tracking_type: string
		:returns: OrderShipmentUpdate
		"""

		return self.set_field('tracktype', tracking_type)

	def set_cost(self, cost: float) -> 'OrderShipmentUpdate':
		"""
		Set cost.

		:param cost: int
		:returns: OrderShipmentUpdate
		"""

		return self.set_field('cost', cost)


"""
ProductVariantLimit data model.
"""


class ProductVariantLimit(Model):
	def __init__(self, data: dict = None):
		"""
		ProductVariantLimit Constructor

		:param data: dict
		"""

		super().__init__(data)

	def get_attribute_id(self) -> int:
		"""
		Get attr_id.

		:returns: int
		"""

		return self.get_field('attr_id', 0)

	def get_attribute_template_id(self) -> int:
		"""
		Get attmpat_id.

		:returns: int
		"""

		return self.get_field('attmpat_id', 0)

	def get_option_id(self) -> int:
		"""
		Get option_id.

		:returns: int
		"""

		return self.get_field('option_id', 0)

	def set_attribute_id(self, attribute_id: int) -> 'ProductVariantLimit':
		"""
		Set attr_id.

		:param attribute_id: int
		:returns: ProductVariantLimit
		"""

		return self.set_field('attr_id', attribute_id)

	def set_attribute_template_id(self, attribute_template_id: int) -> 'ProductVariantLimit':
		"""
		Set attmpat_id.

		:param attribute_template_id: int
		:returns: ProductVariantLimit
		"""

		return self.set_field('attmpat_id', attribute_template_id)

	def set_option_id(self, option_id: int) -> 'ProductVariantLimit':
		"""
		Set option_id.

		:param option_id: int
		:returns: ProductVariantLimit
		"""

		return self.set_field('option_id', option_id)


"""
ProductVariantExclusion data model.
"""


class ProductVariantExclusion(Model):
	def __init__(self, data: dict = None):
		"""
		ProductVariantExclusion Constructor

		:param data: dict
		"""

		super().__init__(data)

	def get_attribute_id(self) -> int:
		"""
		Get attr_id.

		:returns: int
		"""

		return self.get_field('attr_id', 0)

	def get_attribute_template_id(self) -> int:
		"""
		Get attmpat_id.

		:returns: int
		"""

		return self.get_field('attmpat_id', 0)

	def get_option_id(self) -> int:
		"""
		Get option_id.

		:returns: int
		"""

		return self.get_field('option_id', 0)

	def set_attribute_id(self, attribute_id: int) -> 'ProductVariantExclusion':
		"""
		Set attr_id.

		:param attribute_id: int
		:returns: ProductVariantExclusion
		"""

		return self.set_field('attr_id', attribute_id)

	def set_attribute_template_id(self, attribute_template_id: int) -> 'ProductVariantExclusion':
		"""
		Set attmpat_id.

		:param attribute_template_id: int
		:returns: ProductVariantExclusion
		"""

		return self.set_field('attmpat_id', attribute_template_id)

	def set_option_id(self, option_id: int) -> 'ProductVariantExclusion':
		"""
		Set option_id.

		:param option_id: int
		:returns: ProductVariantExclusion
		"""

		return self.set_field('option_id', option_id)


"""
ProvisionMessage data model.
"""


class ProvisionMessage(Model):
	def __init__(self, data: dict = None):
		"""
		ProvisionMessage Constructor

		:param data: dict
		"""

		super().__init__(data)

	def get_date_time_stamp(self) -> str:
		"""
		Get dtstamp.

		:returns: string
		"""

		return self.get_field('dtstamp')

	def get_line_number(self) -> int:
		"""
		Get lineno.

		:returns: int
		"""

		return self.get_field('lineno', 0)

	def get_tag(self) -> str:
		"""
		Get tag.

		:returns: string
		"""

		return self.get_field('tag')

	def get_message(self) -> str:
		"""
		Get message.

		:returns: string
		"""

		return self.get_field('message')


"""
CustomerAddress data model.
"""


class CustomerAddress(Model):
	def __init__(self, data: dict = None):
		"""
		CustomerAddress Constructor

		:param data: dict
		"""

		super().__init__(data)

	def get_id(self) -> int:
		"""
		Get id.

		:returns: int
		"""

		return self.get_field('id', 0)

	def get_customer_id(self) -> int:
		"""
		Get cust_id.

		:returns: int
		"""

		return self.get_field('cust_id', 0)

	def get_description(self) -> str:
		"""
		Get descrip.

		:returns: string
		"""

		return self.get_field('descrip')

	def get_first_name(self) -> str:
		"""
		Get fname.

		:returns: string
		"""

		return self.get_field('fname')

	def get_last_name(self) -> str:
		"""
		Get lname.

		:returns: string
		"""

		return self.get_field('lname')

	def get_email(self) -> str:
		"""
		Get email.

		:returns: string
		"""

		return self.get_field('email')

	def get_company(self) -> str:
		"""
		Get comp.

		:returns: string
		"""

		return self.get_field('comp')

	def get_phone(self) -> str:
		"""
		Get phone.

		:returns: string
		"""

		return self.get_field('phone')

	def get_fax(self) -> str:
		"""
		Get fax.

		:returns: string
		"""

		return self.get_field('fax')

	def get_address1(self) -> str:
		"""
		Get addr1.

		:returns: string
		"""

		return self.get_field('addr1')

	def get_address2(self) -> str:
		"""
		Get addr2.

		:returns: string
		"""

		return self.get_field('addr2')

	def get_city(self) -> str:
		"""
		Get city.

		:returns: string
		"""

		return self.get_field('city')

	def get_state(self) -> str:
		"""
		Get state.

		:returns: string
		"""

		return self.get_field('state')

	def get_zip(self) -> str:
		"""
		Get zip.

		:returns: string
		"""

		return self.get_field('zip')

	def get_country(self) -> str:
		"""
		Get cntry.

		:returns: string
		"""

		return self.get_field('cntry')

	def get_residential(self) -> bool:
		"""
		Get resdntl.

		:returns: bool
		"""

		return self.get_field('resdntl', False)


"""
OrderTotal data model.
"""


class OrderTotal(Model):
	def __init__(self, data: dict = None):
		"""
		OrderTotal Constructor

		:param data: dict
		"""

		super().__init__(data)

	def get_total(self) -> float:
		"""
		Get total.

		:returns: float
		"""

		return self.get_field('total', 0.00)

	def get_formatted_total(self) -> str:
		"""
		Get formatted_total.

		:returns: string
		"""

		return self.get_field('formatted_total')


"""
OrderPaymentTotal data model.
"""


class OrderPaymentTotal(Model):
	def __init__(self, data: dict = None):
		"""
		OrderPaymentTotal Constructor

		:param data: dict
		"""

		super().__init__(data)

	def get_order_id(self) -> int:
		"""
		Get order_id.

		:returns: int
		"""

		return self.get_field('order_id', 0)

	def get_total_authorized(self) -> float:
		"""
		Get total_auth.

		:returns: float
		"""

		return self.get_field('total_auth', 0.00)

	def get_formatted_total_authorized(self) -> str:
		"""
		Get formatted_total_auth.

		:returns: string
		"""

		return self.get_field('formatted_total_auth')

	def get_total_captured(self) -> float:
		"""
		Get total_capt.

		:returns: float
		"""

		return self.get_field('total_capt', 0.00)

	def get_formatted_total_captured(self) -> str:
		"""
		Get formatted_total_capt.

		:returns: string
		"""

		return self.get_field('formatted_total_capt')

	def get_total_refunded(self) -> float:
		"""
		Get total_rfnd.

		:returns: float
		"""

		return self.get_field('total_rfnd', 0.00)

	def get_formatted_total_refunded(self) -> str:
		"""
		Get formatted_total_rfnd.

		:returns: string
		"""

		return self.get_field('formatted_total_rfnd')

	def get_net_captured(self) -> float:
		"""
		Get net_capt.

		:returns: float
		"""

		return self.get_field('net_capt', 0.00)

	def get_formatted_net_captured(self) -> str:
		"""
		Get formatted_net_capt.

		:returns: string
		"""

		return self.get_field('formatted_net_capt')


"""
PrintQueue data model.
"""


class PrintQueue(Model):
	def __init__(self, data: dict = None):
		"""
		PrintQueue Constructor

		:param data: dict
		"""

		super().__init__(data)

	def get_id(self) -> int:
		"""
		Get id.

		:returns: int
		"""

		return self.get_field('id', 0)

	def get_description(self) -> str:
		"""
		Get descrip.

		:returns: string
		"""

		return self.get_field('descrip')


"""
PrintQueueJob data model.
"""


class PrintQueueJob(Model):
	def __init__(self, data: dict = None):
		"""
		PrintQueueJob Constructor

		:param data: dict
		"""

		super().__init__(data)

	def get_id(self) -> int:
		"""
		Get id.

		:returns: int
		"""

		return self.get_field('id', 0)

	def get_queue_id(self) -> int:
		"""
		Get queue_id.

		:returns: int
		"""

		return self.get_field('queue_id', 0)

	def get_store_id(self) -> int:
		"""
		Get store_id.

		:returns: int
		"""

		return self.get_field('store_id', 0)

	def get_user_id(self) -> int:
		"""
		Get user_id.

		:returns: int
		"""

		return self.get_field('user_id', 0)

	def get_description(self) -> str:
		"""
		Get descrip.

		:returns: string
		"""

		return self.get_field('descrip')

	def get_job_format(self) -> str:
		"""
		Get job_fmt.

		:returns: string
		"""

		return self.get_field('job_fmt')

	def get_job_data(self) -> str:
		"""
		Get job_data.

		:returns: string
		"""

		return self.get_field('job_data')

	def get_date_time_created(self) -> int:
		"""
		Get dt_created.

		:returns: int
		"""

		return self.get_field('dt_created', 0)

	def get_print_queue_description(self) -> str:
		"""
		Get printqueue_descrip.

		:returns: string
		"""

		return self.get_field('printqueue_descrip')

	def get_user_name(self) -> str:
		"""
		Get user_name.

		:returns: string
		"""

		return self.get_field('user_name')

	def get_store_code(self) -> str:
		"""
		Get store_code.

		:returns: string
		"""

		return self.get_field('store_code')

	def get_store_name(self) -> str:
		"""
		Get store_name.

		:returns: string
		"""

		return self.get_field('store_name')


"""
PaymentMethod data model.
"""


class PaymentMethod(Model):
	def __init__(self, data: dict = None):
		"""
		PaymentMethod Constructor

		:param data: dict
		"""

		super().__init__(data)
		if self.has_field('paymentcard'):
			value = self.get_field('paymentcard')
			if isinstance(value, CustomerPaymentCard):
				pass
			elif isinstance(value, dict):
				self.set_field('paymentcard', CustomerPaymentCard(value))
			else:
				raise Exception('Expected CustomerPaymentCard or a dict')

		if self.has_field('orderpaymentcard'):
			value = self.get_field('orderpaymentcard')
			if isinstance(value, OrderPaymentCard):
				pass
			elif isinstance(value, dict):
				self.set_field('orderpaymentcard', OrderPaymentCard(value))
			else:
				raise Exception('Expected OrderPaymentCard or a dict')

		if self.has_field('paymentcardtype'):
			value = self.get_field('paymentcardtype')
			if isinstance(value, PaymentCardType):
				pass
			elif isinstance(value, dict):
				self.set_field('paymentcardtype', PaymentCardType(value))
			else:
				raise Exception('Expected PaymentCardType or a dict')

	def get_module_id(self) -> int:
		"""
		Get module_id.

		:returns: int
		"""

		return self.get_field('module_id', 0)

	def get_module_api(self) -> float:
		"""
		Get module_api.

		:returns: float
		"""

		return self.get_field('module_api', 0.00)

	def get_method_code(self) -> str:
		"""
		Get method_code.

		:returns: string
		"""

		return self.get_field('method_code')

	def get_method_name(self) -> str:
		"""
		Get method_name.

		:returns: string
		"""

		return self.get_field('method_name')

	def get_mivapay(self) -> bool:
		"""
		Get mivapay.

		:returns: bool
		"""

		return self.get_field('mivapay', False)

	def get_payment_card(self):
		"""
		Get paymentcard.

		:returns: CustomerPaymentCard|None
		"""

		return self.get_field('paymentcard', None)

	def get_order_payment_card(self):
		"""
		Get orderpaymentcard.

		:returns: OrderPaymentCard|None
		"""

		return self.get_field('orderpaymentcard', None)

	def get_payment_card_type(self):
		"""
		Get paymentcardtype.

		:returns: PaymentCardType|None
		"""

		return self.get_field('paymentcardtype', None)

	def to_dict(self) -> dict:
		"""
		Reduce the model to a dict.
		"""

		ret = self.copy()

		if 'paymentcard' in ret and isinstance(ret['paymentcard'], CustomerPaymentCard):
			ret['paymentcard'] = ret['paymentcard'].to_dict()

		if 'orderpaymentcard' in ret and isinstance(ret['orderpaymentcard'], OrderPaymentCard):
			ret['orderpaymentcard'] = ret['orderpaymentcard'].to_dict()

		if 'paymentcardtype' in ret and isinstance(ret['paymentcardtype'], PaymentCardType):
			ret['paymentcardtype'] = ret['paymentcardtype'].to_dict()

		return ret


"""
PaymentCardType data model.
"""


class PaymentCardType(Model):
	def __init__(self, data: dict = None):
		"""
		PaymentCardType Constructor

		:param data: dict
		"""

		super().__init__(data)

	def get_id(self) -> int:
		"""
		Get id.

		:returns: int
		"""

		return self.get_field('id', 0)

	def get_type(self) -> str:
		"""
		Get type.

		:returns: string
		"""

		return self.get_field('type')

	def get_prefixes(self) -> str:
		"""
		Get prefixes.

		:returns: string
		"""

		return self.get_field('prefixes')

	def get_lengths(self) -> str:
		"""
		Get lengths.

		:returns: string
		"""

		return self.get_field('lengths')

	def get_cvv(self) -> bool:
		"""
		Get cvv.

		:returns: bool
		"""

		return self.get_field('cvv', False)


"""
OrderPaymentAuthorize data model.
"""


class OrderPaymentAuthorize(Model):
	def __init__(self, data: dict = None):
		"""
		OrderPaymentAuthorize Constructor

		:param data: dict
		"""

		super().__init__(data)

	def get_valid(self) -> bool:
		"""
		Get valid.

		:returns: bool
		"""

		return self.get_field('valid', False)

	def get_total_authorized(self) -> float:
		"""
		Get total_auth.

		:returns: float
		"""

		return self.get_field('total_auth', 0.00)

	def get_formatted_total_authorized(self) -> str:
		"""
		Get formatted_total_auth.

		:returns: string
		"""

		return self.get_field('formatted_total_auth')

	def get_total_captured(self) -> float:
		"""
		Get total_capt.

		:returns: float
		"""

		return self.get_field('total_capt', 0.00)

	def get_formatted_total_captured(self) -> str:
		"""
		Get formatted_total_capt.

		:returns: string
		"""

		return self.get_field('formatted_total_capt')

	def get_total_refunded(self) -> float:
		"""
		Get total_rfnd.

		:returns: float
		"""

		return self.get_field('total_rfnd', 0.00)

	def get_formatted_total_refunded(self) -> str:
		"""
		Get formatted_total_rfnd.

		:returns: string
		"""

		return self.get_field('formatted_total_rfnd')

	def get_net_captured(self) -> float:
		"""
		Get net_capt.

		:returns: float
		"""

		return self.get_field('net_capt', 0.00)

	def get_formatted_net_captured(self) -> str:
		"""
		Get formatted_net_capt.

		:returns: string
		"""

		return self.get_field('formatted_net_capt')


"""
OrderNote data model.
"""


class OrderNote(Note):
	def __init__(self, data: dict = None):
		"""
		OrderNote Constructor

		:param data: dict
		"""

		super().__init__(data)


"""
CategoryProduct data model.
"""


class CategoryProduct(Product):
	def __init__(self, data: dict = None):
		"""
		CategoryProduct Constructor

		:param data: dict
		"""

		super().__init__(data)

	def get_assigned(self) -> bool:
		"""
		Get assigned.

		:returns: bool
		"""

		return self.get_field('assigned', False)


"""
CouponPriceGroup data model.
"""


class CouponPriceGroup(PriceGroup):
	def __init__(self, data: dict = None):
		"""
		CouponPriceGroup Constructor

		:param data: dict
		"""

		super().__init__(data)

	def get_assigned(self) -> bool:
		"""
		Get assigned.

		:returns: bool
		"""

		return self.get_field('assigned', False)


"""
OrderPaymentCard data model.
"""


class OrderPaymentCard(CustomerPaymentCard):
	def __init__(self, data: dict = None):
		"""
		OrderPaymentCard Constructor

		:param data: dict
		"""

		super().__init__(data)


"""
PriceGroupCustomer data model.
"""


class PriceGroupCustomer(Customer):
	def __init__(self, data: dict = None):
		"""
		PriceGroupCustomer Constructor

		:param data: dict
		"""

		super().__init__(data)

	def get_assigned(self) -> bool:
		"""
		Get assigned.

		:returns: bool
		"""

		return self.get_field('assigned', False)


"""
PriceGroupProduct data model.
"""


class PriceGroupProduct(Product):
	def __init__(self, data: dict = None):
		"""
		PriceGroupProduct Constructor

		:param data: dict
		"""

		super().__init__(data)

	def get_assigned(self) -> bool:
		"""
		Get assigned.

		:returns: bool
		"""

		return self.get_field('assigned', False)


"""
CustomerPriceGroup data model.
"""


class CustomerPriceGroup(PriceGroup):
	def __init__(self, data: dict = None):
		"""
		CustomerPriceGroup Constructor

		:param data: dict
		"""

		super().__init__(data)

	def get_assigned(self) -> bool:
		"""
		Get assigned.

		:returns: bool
		"""

		return self.get_field('assigned', False)
