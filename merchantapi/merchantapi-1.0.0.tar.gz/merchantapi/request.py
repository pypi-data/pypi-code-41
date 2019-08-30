"""
This file is part of the MerchantAPI package.

(c) Miva Inc <https://www.miva.com/>

For the full copyright and license information, please view the LICENSE
file that was distributed with this source code.

$Id: request.py 77709 2019-08-30 16:41:54Z gidriss $
"""

import merchantapi.abstract
import merchantapi.model
import merchantapi.response
from merchantapi.client import Client
from merchantapi.listquery import ListQueryRequest

"""
Handles API Request AvailabilityGroupBusinessAccount_Update_Assigned.
Scope: Store.
:see: https://docs.miva.com/json-api/functions/availabilitygroupbusinessaccount_update_assigned
"""


class AvailabilityGroupBusinessAccountUpdateAssigned(merchantapi.abstract.Request):
	def __init__(self, client: Client = None, availability_group: merchantapi.model.AvailabilityGroup = None):
		"""
		AvailabilityGroupBusinessAccountUpdateAssigned Constructor.

		:param client: Client
		:param availability_group: AvailabilityGroup
		"""

		super().__init__(client)
		self.availability_group_id = None
		self.edit_availability_group = None
		self.availability_group_name = None
		self.business_account_id = None
		self.business_account_title = None
		self.assigned = False
		if isinstance(availability_group, merchantapi.model.AvailabilityGroup):
			if availability_group.get_id():
				self.set_availability_group_id(availability_group.get_id())
			elif availability_group.get_name():
				self.set_edit_availability_group(availability_group.get_name())

	def get_function(self):
		"""
		Get the function of the request.

		:returns: str
		"""

		return 'AvailabilityGroupBusinessAccount_Update_Assigned'

	def get_availability_group_id(self) -> int:
		"""
		Get AvailabilityGroup_ID.

		:returns: int
		"""

		return self.availability_group_id

	def get_edit_availability_group(self) -> str:
		"""
		Get Edit_AvailabilityGroup.

		:returns: str
		"""

		return self.edit_availability_group

	def get_availability_group_name(self) -> str:
		"""
		Get AvailabilityGroup_Name.

		:returns: str
		"""

		return self.availability_group_name

	def get_business_account_id(self) -> int:
		"""
		Get BusinessAccount_ID.

		:returns: int
		"""

		return self.business_account_id

	def get_business_account_title(self) -> str:
		"""
		Get BusinessAccount_Title.

		:returns: str
		"""

		return self.business_account_title

	def get_assigned(self) -> bool:
		"""
		Get Assigned.

		:returns: bool
		"""

		return self.assigned

	def set_availability_group_id(self, availability_group_id: int) -> 'AvailabilityGroupBusinessAccountUpdateAssigned':
		"""
		Set AvailabilityGroup_ID.

		:param availability_group_id: int
		:returns: AvailabilityGroupBusinessAccountUpdateAssigned
		"""

		self.availability_group_id = availability_group_id
		return self

	def set_edit_availability_group(self, edit_availability_group: str) -> 'AvailabilityGroupBusinessAccountUpdateAssigned':
		"""
		Set Edit_AvailabilityGroup.

		:param edit_availability_group: str
		:returns: AvailabilityGroupBusinessAccountUpdateAssigned
		"""

		self.edit_availability_group = edit_availability_group
		return self

	def set_availability_group_name(self, availability_group_name: str) -> 'AvailabilityGroupBusinessAccountUpdateAssigned':
		"""
		Set AvailabilityGroup_Name.

		:param availability_group_name: str
		:returns: AvailabilityGroupBusinessAccountUpdateAssigned
		"""

		self.availability_group_name = availability_group_name
		return self

	def set_business_account_id(self, business_account_id: int) -> 'AvailabilityGroupBusinessAccountUpdateAssigned':
		"""
		Set BusinessAccount_ID.

		:param business_account_id: int
		:returns: AvailabilityGroupBusinessAccountUpdateAssigned
		"""

		self.business_account_id = business_account_id
		return self

	def set_business_account_title(self, business_account_title: str) -> 'AvailabilityGroupBusinessAccountUpdateAssigned':
		"""
		Set BusinessAccount_Title.

		:param business_account_title: str
		:returns: AvailabilityGroupBusinessAccountUpdateAssigned
		"""

		self.business_account_title = business_account_title
		return self

	def set_assigned(self, assigned: bool) -> 'AvailabilityGroupBusinessAccountUpdateAssigned':
		"""
		Set Assigned.

		:param assigned: bool
		:returns: AvailabilityGroupBusinessAccountUpdateAssigned
		"""

		self.assigned = assigned
		return self

	# noinspection PyTypeChecker
	def send(self) -> 'merchantapi.response.AvailabilityGroupBusinessAccountUpdateAssigned':
		return super().send()

	def create_response(self, data) -> 'AvailabilityGroupBusinessAccountUpdateAssigned':
		"""
		Create a response object from the response data

		:param data:
		:returns: Response
		"""

		return merchantapi.response.AvailabilityGroupBusinessAccountUpdateAssigned(self, data)

	def to_dict(self) -> dict:
		"""
		Reduce the request to a dict

		:override:
		:returns: dict
		"""

		data = super().to_dict()

		if self.availability_group_id is not None:
			data['AvailabilityGroup_ID'] = self.availability_group_id
		elif self.edit_availability_group is not None:
			data['Edit_AvailabilityGroup'] = self.edit_availability_group
		elif self.availability_group_name is not None:
			data['AvailabilityGroup_Name'] = self.availability_group_name

		if self.business_account_id is not None:
			data['BusinessAccount_ID'] = self.business_account_id
		elif self.business_account_title is not None:
			data['BusinessAccount_Title'] = self.business_account_title

		if self.assigned is not None:
			data['Assigned'] = self.assigned
		return data


"""
Handles API Request AvailabilityGroupCustomer_Update_Assigned.
Scope: Store.
:see: https://docs.miva.com/json-api/functions/availabilitygroupcustomer_update_assigned
"""


class AvailabilityGroupCustomerUpdateAssigned(merchantapi.abstract.Request):
	def __init__(self, client: Client = None, availability_group: merchantapi.model.AvailabilityGroup = None):
		"""
		AvailabilityGroupCustomerUpdateAssigned Constructor.

		:param client: Client
		:param availability_group: AvailabilityGroup
		"""

		super().__init__(client)
		self.availability_group_id = None
		self.edit_availability_group = None
		self.availability_group_name = None
		self.customer_id = None
		self.edit_customer = None
		self.customer_login = None
		self.assigned = False
		if isinstance(availability_group, merchantapi.model.AvailabilityGroup):
			if availability_group.get_id():
				self.set_availability_group_id(availability_group.get_id())
			elif availability_group.get_name():
				self.set_edit_availability_group(availability_group.get_name())

	def get_function(self):
		"""
		Get the function of the request.

		:returns: str
		"""

		return 'AvailabilityGroupCustomer_Update_Assigned'

	def get_availability_group_id(self) -> int:
		"""
		Get AvailabilityGroup_ID.

		:returns: int
		"""

		return self.availability_group_id

	def get_edit_availability_group(self) -> str:
		"""
		Get Edit_AvailabilityGroup.

		:returns: str
		"""

		return self.edit_availability_group

	def get_availability_group_name(self) -> str:
		"""
		Get AvailabilityGroup_Name.

		:returns: str
		"""

		return self.availability_group_name

	def get_customer_id(self) -> int:
		"""
		Get Customer_ID.

		:returns: int
		"""

		return self.customer_id

	def get_edit_customer(self) -> str:
		"""
		Get Edit_Customer.

		:returns: str
		"""

		return self.edit_customer

	def get_customer_login(self) -> str:
		"""
		Get Customer_Login.

		:returns: str
		"""

		return self.customer_login

	def get_assigned(self) -> bool:
		"""
		Get Assigned.

		:returns: bool
		"""

		return self.assigned

	def set_availability_group_id(self, availability_group_id: int) -> 'AvailabilityGroupCustomerUpdateAssigned':
		"""
		Set AvailabilityGroup_ID.

		:param availability_group_id: int
		:returns: AvailabilityGroupCustomerUpdateAssigned
		"""

		self.availability_group_id = availability_group_id
		return self

	def set_edit_availability_group(self, edit_availability_group: str) -> 'AvailabilityGroupCustomerUpdateAssigned':
		"""
		Set Edit_AvailabilityGroup.

		:param edit_availability_group: str
		:returns: AvailabilityGroupCustomerUpdateAssigned
		"""

		self.edit_availability_group = edit_availability_group
		return self

	def set_availability_group_name(self, availability_group_name: str) -> 'AvailabilityGroupCustomerUpdateAssigned':
		"""
		Set AvailabilityGroup_Name.

		:param availability_group_name: str
		:returns: AvailabilityGroupCustomerUpdateAssigned
		"""

		self.availability_group_name = availability_group_name
		return self

	def set_customer_id(self, customer_id: int) -> 'AvailabilityGroupCustomerUpdateAssigned':
		"""
		Set Customer_ID.

		:param customer_id: int
		:returns: AvailabilityGroupCustomerUpdateAssigned
		"""

		self.customer_id = customer_id
		return self

	def set_edit_customer(self, edit_customer: str) -> 'AvailabilityGroupCustomerUpdateAssigned':
		"""
		Set Edit_Customer.

		:param edit_customer: str
		:returns: AvailabilityGroupCustomerUpdateAssigned
		"""

		self.edit_customer = edit_customer
		return self

	def set_customer_login(self, customer_login: str) -> 'AvailabilityGroupCustomerUpdateAssigned':
		"""
		Set Customer_Login.

		:param customer_login: str
		:returns: AvailabilityGroupCustomerUpdateAssigned
		"""

		self.customer_login = customer_login
		return self

	def set_assigned(self, assigned: bool) -> 'AvailabilityGroupCustomerUpdateAssigned':
		"""
		Set Assigned.

		:param assigned: bool
		:returns: AvailabilityGroupCustomerUpdateAssigned
		"""

		self.assigned = assigned
		return self

	# noinspection PyTypeChecker
	def send(self) -> 'merchantapi.response.AvailabilityGroupCustomerUpdateAssigned':
		return super().send()

	def create_response(self, data) -> 'AvailabilityGroupCustomerUpdateAssigned':
		"""
		Create a response object from the response data

		:param data:
		:returns: Response
		"""

		return merchantapi.response.AvailabilityGroupCustomerUpdateAssigned(self, data)

	def to_dict(self) -> dict:
		"""
		Reduce the request to a dict

		:override:
		:returns: dict
		"""

		data = super().to_dict()

		if self.availability_group_id is not None:
			data['AvailabilityGroup_ID'] = self.availability_group_id
		elif self.edit_availability_group is not None:
			data['Edit_AvailabilityGroup'] = self.edit_availability_group
		elif self.availability_group_name is not None:
			data['AvailabilityGroup_Name'] = self.availability_group_name

		if self.customer_id is not None:
			data['Customer_ID'] = self.customer_id
		elif self.edit_customer is not None:
			data['Edit_Customer'] = self.edit_customer
		elif self.customer_login is not None:
			data['Customer_Login'] = self.customer_login

		if self.assigned is not None:
			data['Assigned'] = self.assigned
		return data


"""
Handles API Request AvailabilityGroupList_Load_Query.
Scope: Store.
:see: https://docs.miva.com/json-api/functions/availabilitygrouplist_load_query
"""


class AvailabilityGroupListLoadQuery(ListQueryRequest):

	available_search_fields = [
		'id',
		'name'
	]

	available_sort_fields = [
		'id',
		'name'
	]

	def __init__(self, client: Client = None):
		"""
		AvailabilityGroupListLoadQuery Constructor.

		:param client: Client
		"""

		super().__init__(client)

	def get_function(self):
		"""
		Get the function of the request.

		:returns: str
		"""

		return 'AvailabilityGroupList_Load_Query'

	# noinspection PyTypeChecker
	def send(self) -> 'merchantapi.response.AvailabilityGroupListLoadQuery':
		return super().send()

	def create_response(self, data) -> 'AvailabilityGroupListLoadQuery':
		"""
		Create a response object from the response data

		:param data:
		:returns: Response
		"""

		return merchantapi.response.AvailabilityGroupListLoadQuery(self, data)


"""
Handles API Request AvailabilityGroupPaymentMethod_Update_Assigned.
Scope: Store.
:see: https://docs.miva.com/json-api/functions/availabilitygrouppaymentmethod_update_assigned
"""


class AvailabilityGroupPaymentMethodUpdateAssigned(merchantapi.abstract.Request):
	def __init__(self, client: Client = None, availability_group: merchantapi.model.AvailabilityGroup = None):
		"""
		AvailabilityGroupPaymentMethodUpdateAssigned Constructor.

		:param client: Client
		:param availability_group: AvailabilityGroup
		"""

		super().__init__(client)
		self.availability_group_id = None
		self.edit_availability_group = None
		self.availability_group_name = None
		self.module_code = None
		self.method_code = None
		self.payment_card_type_id = None
		self.assigned = False
		if isinstance(availability_group, merchantapi.model.AvailabilityGroup):
			if availability_group.get_id():
				self.set_availability_group_id(availability_group.get_id())
			elif availability_group.get_name():
				self.set_edit_availability_group(availability_group.get_name())

	def get_function(self):
		"""
		Get the function of the request.

		:returns: str
		"""

		return 'AvailabilityGroupPaymentMethod_Update_Assigned'

	def get_availability_group_id(self) -> int:
		"""
		Get AvailabilityGroup_ID.

		:returns: int
		"""

		return self.availability_group_id

	def get_edit_availability_group(self) -> str:
		"""
		Get Edit_AvailabilityGroup.

		:returns: str
		"""

		return self.edit_availability_group

	def get_availability_group_name(self) -> str:
		"""
		Get AvailabilityGroup_Name.

		:returns: str
		"""

		return self.availability_group_name

	def get_module_code(self) -> str:
		"""
		Get Module_Code.

		:returns: str
		"""

		return self.module_code

	def get_method_code(self) -> str:
		"""
		Get Method_Code.

		:returns: str
		"""

		return self.method_code

	def get_payment_card_type_id(self) -> int:
		"""
		Get PaymentCardType_ID.

		:returns: int
		"""

		return self.payment_card_type_id

	def get_assigned(self) -> bool:
		"""
		Get Assigned.

		:returns: bool
		"""

		return self.assigned

	def set_availability_group_id(self, availability_group_id: int) -> 'AvailabilityGroupPaymentMethodUpdateAssigned':
		"""
		Set AvailabilityGroup_ID.

		:param availability_group_id: int
		:returns: AvailabilityGroupPaymentMethodUpdateAssigned
		"""

		self.availability_group_id = availability_group_id
		return self

	def set_edit_availability_group(self, edit_availability_group: str) -> 'AvailabilityGroupPaymentMethodUpdateAssigned':
		"""
		Set Edit_AvailabilityGroup.

		:param edit_availability_group: str
		:returns: AvailabilityGroupPaymentMethodUpdateAssigned
		"""

		self.edit_availability_group = edit_availability_group
		return self

	def set_availability_group_name(self, availability_group_name: str) -> 'AvailabilityGroupPaymentMethodUpdateAssigned':
		"""
		Set AvailabilityGroup_Name.

		:param availability_group_name: str
		:returns: AvailabilityGroupPaymentMethodUpdateAssigned
		"""

		self.availability_group_name = availability_group_name
		return self

	def set_module_code(self, module_code: str) -> 'AvailabilityGroupPaymentMethodUpdateAssigned':
		"""
		Set Module_Code.

		:param module_code: str
		:returns: AvailabilityGroupPaymentMethodUpdateAssigned
		"""

		self.module_code = module_code
		return self

	def set_method_code(self, method_code: str) -> 'AvailabilityGroupPaymentMethodUpdateAssigned':
		"""
		Set Method_Code.

		:param method_code: str
		:returns: AvailabilityGroupPaymentMethodUpdateAssigned
		"""

		self.method_code = method_code
		return self

	def set_payment_card_type_id(self, payment_card_type_id: int) -> 'AvailabilityGroupPaymentMethodUpdateAssigned':
		"""
		Set PaymentCardType_ID.

		:param payment_card_type_id: int
		:returns: AvailabilityGroupPaymentMethodUpdateAssigned
		"""

		self.payment_card_type_id = payment_card_type_id
		return self

	def set_assigned(self, assigned: bool) -> 'AvailabilityGroupPaymentMethodUpdateAssigned':
		"""
		Set Assigned.

		:param assigned: bool
		:returns: AvailabilityGroupPaymentMethodUpdateAssigned
		"""

		self.assigned = assigned
		return self

	# noinspection PyTypeChecker
	def send(self) -> 'merchantapi.response.AvailabilityGroupPaymentMethodUpdateAssigned':
		return super().send()

	def create_response(self, data) -> 'AvailabilityGroupPaymentMethodUpdateAssigned':
		"""
		Create a response object from the response data

		:param data:
		:returns: Response
		"""

		return merchantapi.response.AvailabilityGroupPaymentMethodUpdateAssigned(self, data)

	def to_dict(self) -> dict:
		"""
		Reduce the request to a dict

		:override:
		:returns: dict
		"""

		data = super().to_dict()

		if self.availability_group_id is not None:
			data['AvailabilityGroup_ID'] = self.availability_group_id
		elif self.edit_availability_group is not None:
			data['Edit_AvailabilityGroup'] = self.edit_availability_group
		elif self.availability_group_name is not None:
			data['AvailabilityGroup_Name'] = self.availability_group_name

		data['Module_Code'] = self.module_code
		data['Method_Code'] = self.method_code
		if self.payment_card_type_id is not None:
			data['PaymentCardType_ID'] = self.payment_card_type_id
		data['Assigned'] = self.assigned
		return data


"""
Handles API Request AvailabilityGroupProduct_Update_Assigned.
Scope: Store.
:see: https://docs.miva.com/json-api/functions/availabilitygroupproduct_update_assigned
"""


class AvailabilityGroupProductUpdateAssigned(merchantapi.abstract.Request):
	def __init__(self, client: Client = None, availability_group: merchantapi.model.AvailabilityGroup = None):
		"""
		AvailabilityGroupProductUpdateAssigned Constructor.

		:param client: Client
		:param availability_group: AvailabilityGroup
		"""

		super().__init__(client)
		self.availability_group_id = None
		self.edit_availability_group = None
		self.availability_group_name = None
		self.product_id = None
		self.product_code = None
		self.product_sku = None
		self.edit_product = None
		self.assigned = False
		if isinstance(availability_group, merchantapi.model.AvailabilityGroup):
			if availability_group.get_id():
				self.set_availability_group_id(availability_group.get_id())
			elif availability_group.get_name():
				self.set_edit_availability_group(availability_group.get_name())

	def get_function(self):
		"""
		Get the function of the request.

		:returns: str
		"""

		return 'AvailabilityGroupProduct_Update_Assigned'

	def get_availability_group_id(self) -> int:
		"""
		Get AvailabilityGroup_ID.

		:returns: int
		"""

		return self.availability_group_id

	def get_edit_availability_group(self) -> str:
		"""
		Get Edit_AvailabilityGroup.

		:returns: str
		"""

		return self.edit_availability_group

	def get_availability_group_name(self) -> str:
		"""
		Get AvailabilityGroup_Name.

		:returns: str
		"""

		return self.availability_group_name

	def get_product_id(self) -> int:
		"""
		Get Product_ID.

		:returns: int
		"""

		return self.product_id

	def get_product_code(self) -> str:
		"""
		Get Product_Code.

		:returns: str
		"""

		return self.product_code

	def get_product_sku(self) -> str:
		"""
		Get Product_SKU.

		:returns: str
		"""

		return self.product_sku

	def get_edit_product(self) -> str:
		"""
		Get Edit_Product.

		:returns: str
		"""

		return self.edit_product

	def get_assigned(self) -> bool:
		"""
		Get Assigned.

		:returns: bool
		"""

		return self.assigned

	def set_availability_group_id(self, availability_group_id: int) -> 'AvailabilityGroupProductUpdateAssigned':
		"""
		Set AvailabilityGroup_ID.

		:param availability_group_id: int
		:returns: AvailabilityGroupProductUpdateAssigned
		"""

		self.availability_group_id = availability_group_id
		return self

	def set_edit_availability_group(self, edit_availability_group: str) -> 'AvailabilityGroupProductUpdateAssigned':
		"""
		Set Edit_AvailabilityGroup.

		:param edit_availability_group: str
		:returns: AvailabilityGroupProductUpdateAssigned
		"""

		self.edit_availability_group = edit_availability_group
		return self

	def set_availability_group_name(self, availability_group_name: str) -> 'AvailabilityGroupProductUpdateAssigned':
		"""
		Set AvailabilityGroup_Name.

		:param availability_group_name: str
		:returns: AvailabilityGroupProductUpdateAssigned
		"""

		self.availability_group_name = availability_group_name
		return self

	def set_product_id(self, product_id: int) -> 'AvailabilityGroupProductUpdateAssigned':
		"""
		Set Product_ID.

		:param product_id: int
		:returns: AvailabilityGroupProductUpdateAssigned
		"""

		self.product_id = product_id
		return self

	def set_product_code(self, product_code: str) -> 'AvailabilityGroupProductUpdateAssigned':
		"""
		Set Product_Code.

		:param product_code: str
		:returns: AvailabilityGroupProductUpdateAssigned
		"""

		self.product_code = product_code
		return self

	def set_product_sku(self, product_sku: str) -> 'AvailabilityGroupProductUpdateAssigned':
		"""
		Set Product_SKU.

		:param product_sku: str
		:returns: AvailabilityGroupProductUpdateAssigned
		"""

		self.product_sku = product_sku
		return self

	def set_edit_product(self, edit_product: str) -> 'AvailabilityGroupProductUpdateAssigned':
		"""
		Set Edit_Product.

		:param edit_product: str
		:returns: AvailabilityGroupProductUpdateAssigned
		"""

		self.edit_product = edit_product
		return self

	def set_assigned(self, assigned: bool) -> 'AvailabilityGroupProductUpdateAssigned':
		"""
		Set Assigned.

		:param assigned: bool
		:returns: AvailabilityGroupProductUpdateAssigned
		"""

		self.assigned = assigned
		return self

	# noinspection PyTypeChecker
	def send(self) -> 'merchantapi.response.AvailabilityGroupProductUpdateAssigned':
		return super().send()

	def create_response(self, data) -> 'AvailabilityGroupProductUpdateAssigned':
		"""
		Create a response object from the response data

		:param data:
		:returns: Response
		"""

		return merchantapi.response.AvailabilityGroupProductUpdateAssigned(self, data)

	def to_dict(self) -> dict:
		"""
		Reduce the request to a dict

		:override:
		:returns: dict
		"""

		data = super().to_dict()

		if self.availability_group_id is not None:
			data['AvailabilityGroup_ID'] = self.availability_group_id
		elif self.edit_availability_group is not None:
			data['Edit_AvailabilityGroup'] = self.edit_availability_group
		elif self.availability_group_name is not None:
			data['AvailabilityGroup_Name'] = self.availability_group_name

		if self.product_id is not None:
			data['Product_ID'] = self.product_id
		elif self.edit_product is not None:
			data['Edit_Product'] = self.edit_product
		elif self.product_code is not None:
			data['Product_Code'] = self.product_code
		elif self.product_sku is not None:
			data['Product_SKU'] = self.product_sku

		data['Assigned'] = self.assigned
		return data


"""
Handles API Request AvailabilityGroupShippingMethod_Update_Assigned.
Scope: Store.
:see: https://docs.miva.com/json-api/functions/availabilitygroupshippingmethod_update_assigned
"""


class AvailabilityGroupShippingMethodUpdateAssigned(merchantapi.abstract.Request):
	def __init__(self, client: Client = None, availability_group: merchantapi.model.AvailabilityGroup = None):
		"""
		AvailabilityGroupShippingMethodUpdateAssigned Constructor.

		:param client: Client
		:param availability_group: AvailabilityGroup
		"""

		super().__init__(client)
		self.availability_group_id = None
		self.edit_availability_group = None
		self.availability_group_name = None
		self.module_code = None
		self.method_code = None
		self.assigned = False
		if isinstance(availability_group, merchantapi.model.AvailabilityGroup):
			if availability_group.get_id():
				self.set_availability_group_id(availability_group.get_id())
			elif availability_group.get_name():
				self.set_edit_availability_group(availability_group.get_name())

	def get_function(self):
		"""
		Get the function of the request.

		:returns: str
		"""

		return 'AvailabilityGroupShippingMethod_Update_Assigned'

	def get_availability_group_id(self) -> int:
		"""
		Get AvailabilityGroup_ID.

		:returns: int
		"""

		return self.availability_group_id

	def get_edit_availability_group(self) -> str:
		"""
		Get Edit_AvailabilityGroup.

		:returns: str
		"""

		return self.edit_availability_group

	def get_availability_group_name(self) -> str:
		"""
		Get AvailabilityGroup_Name.

		:returns: str
		"""

		return self.availability_group_name

	def get_module_code(self) -> str:
		"""
		Get Module_Code.

		:returns: str
		"""

		return self.module_code

	def get_method_code(self) -> str:
		"""
		Get Method_Code.

		:returns: str
		"""

		return self.method_code

	def get_assigned(self) -> bool:
		"""
		Get Assigned.

		:returns: bool
		"""

		return self.assigned

	def set_availability_group_id(self, availability_group_id: int) -> 'AvailabilityGroupShippingMethodUpdateAssigned':
		"""
		Set AvailabilityGroup_ID.

		:param availability_group_id: int
		:returns: AvailabilityGroupShippingMethodUpdateAssigned
		"""

		self.availability_group_id = availability_group_id
		return self

	def set_edit_availability_group(self, edit_availability_group: str) -> 'AvailabilityGroupShippingMethodUpdateAssigned':
		"""
		Set Edit_AvailabilityGroup.

		:param edit_availability_group: str
		:returns: AvailabilityGroupShippingMethodUpdateAssigned
		"""

		self.edit_availability_group = edit_availability_group
		return self

	def set_availability_group_name(self, availability_group_name: str) -> 'AvailabilityGroupShippingMethodUpdateAssigned':
		"""
		Set AvailabilityGroup_Name.

		:param availability_group_name: str
		:returns: AvailabilityGroupShippingMethodUpdateAssigned
		"""

		self.availability_group_name = availability_group_name
		return self

	def set_module_code(self, module_code: str) -> 'AvailabilityGroupShippingMethodUpdateAssigned':
		"""
		Set Module_Code.

		:param module_code: str
		:returns: AvailabilityGroupShippingMethodUpdateAssigned
		"""

		self.module_code = module_code
		return self

	def set_method_code(self, method_code: str) -> 'AvailabilityGroupShippingMethodUpdateAssigned':
		"""
		Set Method_Code.

		:param method_code: str
		:returns: AvailabilityGroupShippingMethodUpdateAssigned
		"""

		self.method_code = method_code
		return self

	def set_assigned(self, assigned: bool) -> 'AvailabilityGroupShippingMethodUpdateAssigned':
		"""
		Set Assigned.

		:param assigned: bool
		:returns: AvailabilityGroupShippingMethodUpdateAssigned
		"""

		self.assigned = assigned
		return self

	# noinspection PyTypeChecker
	def send(self) -> 'merchantapi.response.AvailabilityGroupShippingMethodUpdateAssigned':
		return super().send()

	def create_response(self, data) -> 'AvailabilityGroupShippingMethodUpdateAssigned':
		"""
		Create a response object from the response data

		:param data:
		:returns: Response
		"""

		return merchantapi.response.AvailabilityGroupShippingMethodUpdateAssigned(self, data)

	def to_dict(self) -> dict:
		"""
		Reduce the request to a dict

		:override:
		:returns: dict
		"""

		data = super().to_dict()

		if self.availability_group_id is not None:
			data['AvailabilityGroup_ID'] = self.availability_group_id
		elif self.edit_availability_group is not None:
			data['Edit_AvailabilityGroup'] = self.edit_availability_group
		elif self.availability_group_name is not None:
			data['AvailabilityGroup_Name'] = self.availability_group_name

		data['Module_Code'] = self.module_code
		data['Method_Code'] = self.method_code
		data['Assigned'] = self.assigned
		return data


"""
Handles API Request CategoryList_Load_Parent.
Scope: Store.
:see: https://docs.miva.com/json-api/functions/categorylist_load_parent
"""


class CategoryListLoadParent(merchantapi.abstract.Request):
	def __init__(self, client: Client = None, category: merchantapi.model.Category = None):
		"""
		CategoryListLoadParent Constructor.

		:param client: Client
		:param category: Category
		"""

		super().__init__(client)
		self.parent_id = None
		if isinstance(category, merchantapi.model.Category):
			self.set_parent_id(category.get_id())

	def get_function(self):
		"""
		Get the function of the request.

		:returns: str
		"""

		return 'CategoryList_Load_Parent'

	def get_parent_id(self) -> int:
		"""
		Get Parent_ID.

		:returns: int
		"""

		return self.parent_id

	def set_parent_id(self, parent_id: int) -> 'CategoryListLoadParent':
		"""
		Set Parent_ID.

		:param parent_id: int
		:returns: CategoryListLoadParent
		"""

		self.parent_id = parent_id
		return self

	# noinspection PyTypeChecker
	def send(self) -> 'merchantapi.response.CategoryListLoadParent':
		return super().send()

	def create_response(self, data) -> 'CategoryListLoadParent':
		"""
		Create a response object from the response data

		:param data:
		:returns: Response
		"""

		return merchantapi.response.CategoryListLoadParent(self, data)

	def to_dict(self) -> dict:
		"""
		Reduce the request to a dict

		:override:
		:returns: dict
		"""

		data = super().to_dict()

		data['Parent_ID'] = self.get_parent_id()

		return data


"""
Handles API Request CategoryList_Load_Query.
Scope: Store.
:see: https://docs.miva.com/json-api/functions/categorylist_load_query
"""


class CategoryListLoadQuery(ListQueryRequest):
	# CATEGORY_SHOW constants.
	CATEGORY_SHOW_ALL = 'All'
	CATEGORY_SHOW_ACTIVE = 'Active'

	available_search_fields = [
		'id',
		'code',
		'name',
		'page_title',
		'parent_category',
		'page_code',
		'dt_created',
		'dt_updated',
		'depth'
	]

	available_sort_fields = [
		'id',
		'code',
		'name',
		'page_title',
		'active',
		'page_code',
		'parent_category',
		'disp_order',
		'dt_created',
		'dt_updated',
		'depth'
	]

	available_custom_filters = {
		'Category_Show': [
			CATEGORY_SHOW_ALL,
			CATEGORY_SHOW_ACTIVE
		]
	}

	def __init__(self, client: Client = None):
		"""
		CategoryListLoadQuery Constructor.

		:param client: Client
		"""

		super().__init__(client)

	def get_function(self):
		"""
		Get the function of the request.

		:returns: str
		"""

		return 'CategoryList_Load_Query'

	# noinspection PyTypeChecker
	def send(self) -> 'merchantapi.response.CategoryListLoadQuery':
		return super().send()

	def create_response(self, data) -> 'CategoryListLoadQuery':
		"""
		Create a response object from the response data

		:param data:
		:returns: Response
		"""

		return merchantapi.response.CategoryListLoadQuery(self, data)


"""
Handles API Request CategoryProduct_Update_Assigned.
Scope: Store.
:see: https://docs.miva.com/json-api/functions/categoryproduct_update_assigned
"""


class CategoryProductUpdateAssigned(merchantapi.abstract.Request):
	def __init__(self, client: Client = None, category: merchantapi.model.Category = None):
		"""
		CategoryProductUpdateAssigned Constructor.

		:param client: Client
		:param category: Category
		"""

		super().__init__(client)
		self.category_id = None
		self.edit_category = None
		self.category_code = None
		self.product_id = None
		self.edit_product = None
		self.product_code = None
		self.product_sku = None
		self.assigned = False
		if isinstance(category, merchantapi.model.Category):
			if category.get_id():
				self.set_category_id(category.get_id())
			elif category.get_code():
				self.set_edit_category(category.get_code())

	def get_function(self):
		"""
		Get the function of the request.

		:returns: str
		"""

		return 'CategoryProduct_Update_Assigned'

	def get_category_id(self) -> int:
		"""
		Get Category_ID.

		:returns: int
		"""

		return self.category_id

	def get_edit_category(self) -> str:
		"""
		Get Edit_Category.

		:returns: str
		"""

		return self.edit_category

	def get_category_code(self) -> str:
		"""
		Get Category_Code.

		:returns: str
		"""

		return self.category_code

	def get_product_id(self) -> int:
		"""
		Get Product_ID.

		:returns: int
		"""

		return self.product_id

	def get_edit_product(self) -> str:
		"""
		Get Edit_Product.

		:returns: str
		"""

		return self.edit_product

	def get_product_code(self) -> str:
		"""
		Get Product_Code.

		:returns: str
		"""

		return self.product_code

	def get_product_sku(self) -> str:
		"""
		Get Product_SKU.

		:returns: str
		"""

		return self.product_sku

	def get_assigned(self) -> bool:
		"""
		Get Assigned.

		:returns: bool
		"""

		return self.assigned

	def set_category_id(self, category_id: int) -> 'CategoryProductUpdateAssigned':
		"""
		Set Category_ID.

		:param category_id: int
		:returns: CategoryProductUpdateAssigned
		"""

		self.category_id = category_id
		return self

	def set_edit_category(self, edit_category: str) -> 'CategoryProductUpdateAssigned':
		"""
		Set Edit_Category.

		:param edit_category: str
		:returns: CategoryProductUpdateAssigned
		"""

		self.edit_category = edit_category
		return self

	def set_category_code(self, category_code: str) -> 'CategoryProductUpdateAssigned':
		"""
		Set Category_Code.

		:param category_code: str
		:returns: CategoryProductUpdateAssigned
		"""

		self.category_code = category_code
		return self

	def set_product_id(self, product_id: int) -> 'CategoryProductUpdateAssigned':
		"""
		Set Product_ID.

		:param product_id: int
		:returns: CategoryProductUpdateAssigned
		"""

		self.product_id = product_id
		return self

	def set_edit_product(self, edit_product: str) -> 'CategoryProductUpdateAssigned':
		"""
		Set Edit_Product.

		:param edit_product: str
		:returns: CategoryProductUpdateAssigned
		"""

		self.edit_product = edit_product
		return self

	def set_product_code(self, product_code: str) -> 'CategoryProductUpdateAssigned':
		"""
		Set Product_Code.

		:param product_code: str
		:returns: CategoryProductUpdateAssigned
		"""

		self.product_code = product_code
		return self

	def set_product_sku(self, product_sku: str) -> 'CategoryProductUpdateAssigned':
		"""
		Set Product_SKU.

		:param product_sku: str
		:returns: CategoryProductUpdateAssigned
		"""

		self.product_sku = product_sku
		return self

	def set_assigned(self, assigned: bool) -> 'CategoryProductUpdateAssigned':
		"""
		Set Assigned.

		:param assigned: bool
		:returns: CategoryProductUpdateAssigned
		"""

		self.assigned = assigned
		return self

	# noinspection PyTypeChecker
	def send(self) -> 'merchantapi.response.CategoryProductUpdateAssigned':
		return super().send()

	def create_response(self, data) -> 'CategoryProductUpdateAssigned':
		"""
		Create a response object from the response data

		:param data:
		:returns: Response
		"""

		return merchantapi.response.CategoryProductUpdateAssigned(self, data)

	def to_dict(self) -> dict:
		"""
		Reduce the request to a dict

		:override:
		:returns: dict
		"""

		data = super().to_dict()

		if self.category_id is not None:
			data['Category_ID'] = self.category_id
		elif self.edit_category is not None:
			data['Edit_Category'] = self.edit_category
		elif self.category_code is not None:
			data['Category_Code'] = self.category_code

		if self.product_id is not None:
			data['Product_ID'] = self.product_id
		elif self.edit_product is not None:
			data['Edit_Product'] = self.edit_product
		elif self.product_code is not None:
			data['Product_Code'] = self.product_code
		elif self.product_sku is not None:
			data['Product_SKU'] = self.product_sku

		data['Assigned'] = self.assigned
		return data


"""
Handles API Request Category_Insert.
Scope: Store.
:see: https://docs.miva.com/json-api/functions/category_insert
"""


class CategoryInsert(merchantapi.abstract.Request):
	def __init__(self, client: Client = None, category: merchantapi.model.Category = None):
		"""
		CategoryInsert Constructor.

		:param client: Client
		:param category: Category
		"""

		super().__init__(client)
		self.category_code = None
		self.category_name = None
		self.category_active = False
		self.category_page_title = None
		self.category_parent_category = None
		self.category_alternate_display_page = None
		self.custom_field_values = merchantapi.model.CustomFieldValues()
		if isinstance(category, merchantapi.model.Category):
			self.set_category_code(category.get_code())
			self.set_category_name(category.get_name())
			self.set_category_active(category.get_active())
			self.set_category_page_title(category.get_page_title())
			self.set_category_alternate_display_page(category.get_page_code())

			if category.get_custom_field_values():
				self.set_custom_field_values(category.get_custom_field_values())

	def get_function(self):
		"""
		Get the function of the request.

		:returns: str
		"""

		return 'Category_Insert'

	def get_category_code(self) -> str:
		"""
		Get Category_Code.

		:returns: str
		"""

		return self.category_code

	def get_category_name(self) -> str:
		"""
		Get Category_Name.

		:returns: str
		"""

		return self.category_name

	def get_category_active(self) -> bool:
		"""
		Get Category_Active.

		:returns: bool
		"""

		return self.category_active

	def get_category_page_title(self) -> str:
		"""
		Get Category_Page_Title.

		:returns: str
		"""

		return self.category_page_title

	def get_category_parent_category(self) -> str:
		"""
		Get Category_Parent_Category.

		:returns: str
		"""

		return self.category_parent_category

	def get_category_alternate_display_page(self) -> str:
		"""
		Get Category_Alternate_Display_Page.

		:returns: str
		"""

		return self.category_alternate_display_page

	def get_custom_field_values(self) -> merchantapi.model.CustomFieldValues:
		"""
		Get CustomField_Values.

		:returns: CustomFieldValues}|None
		"""

		return self.custom_field_values

	def set_category_code(self, category_code: str) -> 'CategoryInsert':
		"""
		Set Category_Code.

		:param category_code: str
		:returns: CategoryInsert
		"""

		self.category_code = category_code
		return self

	def set_category_name(self, category_name: str) -> 'CategoryInsert':
		"""
		Set Category_Name.

		:param category_name: str
		:returns: CategoryInsert
		"""

		self.category_name = category_name
		return self

	def set_category_active(self, category_active: bool) -> 'CategoryInsert':
		"""
		Set Category_Active.

		:param category_active: bool
		:returns: CategoryInsert
		"""

		self.category_active = category_active
		return self

	def set_category_page_title(self, category_page_title: str) -> 'CategoryInsert':
		"""
		Set Category_Page_Title.

		:param category_page_title: str
		:returns: CategoryInsert
		"""

		self.category_page_title = category_page_title
		return self

	def set_category_parent_category(self, category_parent_category: str) -> 'CategoryInsert':
		"""
		Set Category_Parent_Category.

		:param category_parent_category: str
		:returns: CategoryInsert
		"""

		self.category_parent_category = category_parent_category
		return self

	def set_category_alternate_display_page(self, category_alternate_display_page: str) -> 'CategoryInsert':
		"""
		Set Category_Alternate_Display_Page.

		:param category_alternate_display_page: str
		:returns: CategoryInsert
		"""

		self.category_alternate_display_page = category_alternate_display_page
		return self

	def set_custom_field_values(self, custom_field_values: merchantapi.model.CustomFieldValues) -> 'CategoryInsert':
		"""
		Set CustomField_Values.

		:param custom_field_values: CustomFieldValues}|None
		:raises Exception:
		:returns: CategoryInsert
		"""

		if not isinstance(custom_field_values, merchantapi.model.CustomFieldValues):
			raise Exception("")
		self.custom_field_values = custom_field_values
		return self

	# noinspection PyTypeChecker
	def send(self) -> 'merchantapi.response.CategoryInsert':
		return super().send()

	def create_response(self, data) -> 'CategoryInsert':
		"""
		Create a response object from the response data

		:param data:
		:returns: Response
		"""

		return merchantapi.response.CategoryInsert(self, data)

	def to_dict(self) -> dict:
		"""
		Reduce the request to a dict

		:override:
		:returns: dict
		"""

		data = super().to_dict()

		data['Category_Code'] = self.category_code
		data['Category_Name'] = self.category_name
		if self.category_active is not None:
			data['Category_Active'] = self.category_active
		if self.category_page_title is not None:
			data['Category_Page_Title'] = self.category_page_title
		if self.category_parent_category is not None:
			data['Category_Parent_Category'] = self.category_parent_category
		if self.category_alternate_display_page is not None:
			data['Category_Alternate_Display_Page'] = self.category_alternate_display_page
		if self.custom_field_values is not None:
			data['CustomField_Values'] = self.custom_field_values.to_dict()
		return data


"""
Handles API Request Category_Delete.
Scope: Store.
:see: https://docs.miva.com/json-api/functions/category_delete
"""


class CategoryDelete(merchantapi.abstract.Request):
	def __init__(self, client: Client = None, category: merchantapi.model.Category = None):
		"""
		CategoryDelete Constructor.

		:param client: Client
		:param category: Category
		"""

		super().__init__(client)
		self.category_id = None
		self.edit_category = None
		self.category_code = None
		if isinstance(category, merchantapi.model.Category):
			if category.get_id():
				self.set_category_id(category.get_id())
			elif category.get_code():
				self.set_edit_category(category.get_code())

	def get_function(self):
		"""
		Get the function of the request.

		:returns: str
		"""

		return 'Category_Delete'

	def get_category_id(self) -> int:
		"""
		Get Category_ID.

		:returns: int
		"""

		return self.category_id

	def get_edit_category(self) -> str:
		"""
		Get Edit_Category.

		:returns: str
		"""

		return self.edit_category

	def get_category_code(self) -> str:
		"""
		Get Category_Code.

		:returns: str
		"""

		return self.category_code

	def set_category_id(self, category_id: int) -> 'CategoryDelete':
		"""
		Set Category_ID.

		:param category_id: int
		:returns: CategoryDelete
		"""

		self.category_id = category_id
		return self

	def set_edit_category(self, edit_category: str) -> 'CategoryDelete':
		"""
		Set Edit_Category.

		:param edit_category: str
		:returns: CategoryDelete
		"""

		self.edit_category = edit_category
		return self

	def set_category_code(self, category_code: str) -> 'CategoryDelete':
		"""
		Set Category_Code.

		:param category_code: str
		:returns: CategoryDelete
		"""

		self.category_code = category_code
		return self

	# noinspection PyTypeChecker
	def send(self) -> 'merchantapi.response.CategoryDelete':
		return super().send()

	def create_response(self, data) -> 'CategoryDelete':
		"""
		Create a response object from the response data

		:param data:
		:returns: Response
		"""

		return merchantapi.response.CategoryDelete(self, data)

	def to_dict(self) -> dict:
		"""
		Reduce the request to a dict

		:override:
		:returns: dict
		"""

		data = super().to_dict()

		if self.category_id is not None:
			data['Category_ID'] = self.category_id
		elif self.edit_category is not None:
			data['Edit_Category'] = self.edit_category
		elif self.category_code is not None:
			data['Category_Code'] = self.category_code

		return data


"""
Handles API Request Category_Update.
Scope: Store.
:see: https://docs.miva.com/json-api/functions/category_update
"""


class CategoryUpdate(merchantapi.abstract.Request):
	def __init__(self, client: Client = None, category: merchantapi.model.Category = None):
		"""
		CategoryUpdate Constructor.

		:param client: Client
		:param category: Category
		"""

		super().__init__(client)
		self.category_id = None
		self.category_code = None
		self.edit_category = None
		self.category_name = None
		self.category_page_title = None
		self.category_active = False
		self.category_parent_category = None
		self.category_alternate_display_page = None
		self.custom_field_values = merchantapi.model.CustomFieldValues()
		if isinstance(category, merchantapi.model.Category):
			if category.get_id():
				self.set_category_id(category.get_id())
			elif category.get_code():
				self.set_edit_category(category.get_code())

			self.set_category_code(category.get_code())
			self.set_category_name(category.get_name())
			self.set_category_page_title(category.get_page_title())
			self.set_category_active(category.get_active())
			self.set_category_parent_category(category.get_parent_category())
			self.set_category_alternate_display_page(category.get_page_code())

			if category.get_custom_field_values():
				self.set_custom_field_values(category.get_custom_field_values())

	def get_function(self):
		"""
		Get the function of the request.

		:returns: str
		"""

		return 'Category_Update'

	def get_category_id(self) -> int:
		"""
		Get Category_ID.

		:returns: int
		"""

		return self.category_id

	def get_category_code(self) -> str:
		"""
		Get Category_Code.

		:returns: str
		"""

		return self.category_code

	def get_edit_category(self) -> str:
		"""
		Get Edit_Category.

		:returns: str
		"""

		return self.edit_category

	def get_category_name(self) -> str:
		"""
		Get Category_Name.

		:returns: str
		"""

		return self.category_name

	def get_category_page_title(self) -> str:
		"""
		Get Category_Page_Title.

		:returns: str
		"""

		return self.category_page_title

	def get_category_active(self) -> bool:
		"""
		Get Category_Active.

		:returns: bool
		"""

		return self.category_active

	def get_category_parent_category(self) -> str:
		"""
		Get Category_Parent_Category.

		:returns: str
		"""

		return self.category_parent_category

	def get_category_alternate_display_page(self) -> str:
		"""
		Get Category_Alternate_Display_Page.

		:returns: str
		"""

		return self.category_alternate_display_page

	def get_custom_field_values(self) -> merchantapi.model.CustomFieldValues:
		"""
		Get CustomField_Values.

		:returns: CustomFieldValues}|None
		"""

		return self.custom_field_values

	def set_category_id(self, category_id: int) -> 'CategoryUpdate':
		"""
		Set Category_ID.

		:param category_id: int
		:returns: CategoryUpdate
		"""

		self.category_id = category_id
		return self

	def set_category_code(self, category_code: str) -> 'CategoryUpdate':
		"""
		Set Category_Code.

		:param category_code: str
		:returns: CategoryUpdate
		"""

		self.category_code = category_code
		return self

	def set_edit_category(self, edit_category: str) -> 'CategoryUpdate':
		"""
		Set Edit_Category.

		:param edit_category: str
		:returns: CategoryUpdate
		"""

		self.edit_category = edit_category
		return self

	def set_category_name(self, category_name: str) -> 'CategoryUpdate':
		"""
		Set Category_Name.

		:param category_name: str
		:returns: CategoryUpdate
		"""

		self.category_name = category_name
		return self

	def set_category_page_title(self, category_page_title: str) -> 'CategoryUpdate':
		"""
		Set Category_Page_Title.

		:param category_page_title: str
		:returns: CategoryUpdate
		"""

		self.category_page_title = category_page_title
		return self

	def set_category_active(self, category_active: bool) -> 'CategoryUpdate':
		"""
		Set Category_Active.

		:param category_active: bool
		:returns: CategoryUpdate
		"""

		self.category_active = category_active
		return self

	def set_category_parent_category(self, category_parent_category: str) -> 'CategoryUpdate':
		"""
		Set Category_Parent_Category.

		:param category_parent_category: str
		:returns: CategoryUpdate
		"""

		self.category_parent_category = category_parent_category
		return self

	def set_category_alternate_display_page(self, category_alternate_display_page: str) -> 'CategoryUpdate':
		"""
		Set Category_Alternate_Display_Page.

		:param category_alternate_display_page: str
		:returns: CategoryUpdate
		"""

		self.category_alternate_display_page = category_alternate_display_page
		return self

	def set_custom_field_values(self, custom_field_values: merchantapi.model.CustomFieldValues) -> 'CategoryUpdate':
		"""
		Set CustomField_Values.

		:param custom_field_values: CustomFieldValues}|None
		:raises Exception:
		:returns: CategoryUpdate
		"""

		if not isinstance(custom_field_values, merchantapi.model.CustomFieldValues):
			raise Exception("")
		self.custom_field_values = custom_field_values
		return self

	# noinspection PyTypeChecker
	def send(self) -> 'merchantapi.response.CategoryUpdate':
		return super().send()

	def create_response(self, data) -> 'CategoryUpdate':
		"""
		Create a response object from the response data

		:param data:
		:returns: Response
		"""

		return merchantapi.response.CategoryUpdate(self, data)

	def to_dict(self) -> dict:
		"""
		Reduce the request to a dict

		:override:
		:returns: dict
		"""

		data = super().to_dict()

		if self.category_id is not None:
			data['Category_ID'] = self.category_id
		elif self.edit_category is not None:
			data['Edit_Category'] = self.edit_category

		if self.category_code is not None:
			data['Category_Code'] = self.category_code
		if self.category_name is not None:
			data['Category_Name'] = self.category_name
		if self.category_page_title is not None:
			data['Category_Page_Title'] = self.category_page_title
		if self.category_active is not None:
			data['Category_Active'] = self.category_active
		if self.category_parent_category is not None:
			data['Category_Parent_Category'] = self.category_parent_category
		if self.category_alternate_display_page is not None:
			data['Category_Alternate_Display_Page'] = self.category_alternate_display_page
		if self.custom_field_values is not None:
			data['CustomField_Values'] = self.custom_field_values.to_dict()
		return data


"""
Handles API Request CouponList_Delete.
Scope: Store.
:see: https://docs.miva.com/json-api/functions/couponlist_delete
"""


class CouponListDelete(merchantapi.abstract.Request):
	def __init__(self, client: Client = None):
		"""
		CouponListDelete Constructor.

		:param client: Client
		"""

		super().__init__(client)
		self.coupon_ids = []

	def get_function(self):
		"""
		Get the function of the request.

		:returns: str
		"""

		return 'CouponList_Delete'

	def get_coupon_ids(self):
		"""
		Get Coupon_IDs.

		:returns: list
		"""

		return self.coupon_ids

	def add_coupon_id(self, coupon_id) -> 'CouponListDelete':
		"""
		Add Coupon_IDs.

		:param coupon_id: int
		:returns: {CouponListDelete}
		"""

		self.coupon_ids.append(coupon_id)
		return self

	def add_coupon(self, coupon: merchantapi.model.Coupon) -> 'CouponListDelete':
		"""
		Add Coupon model.

		:param coupon: Coupon
		:raises Exception:
		:returns: CouponListDelete
		"""
		if not isinstance(coupon, merchantapi.model.Coupon):
			raise Exception('Expected an instance of Coupon')

		if coupon.get_id():
			self.coupon_ids.append(coupon.get_id())

		return self

	# noinspection PyTypeChecker
	def send(self) -> 'merchantapi.response.CouponListDelete':
		return super().send()

	def create_response(self, data) -> 'CouponListDelete':
		"""
		Create a response object from the response data

		:param data:
		:returns: Response
		"""

		return merchantapi.response.CouponListDelete(self, data)

	def to_dict(self) -> dict:
		"""
		Reduce the request to a dict

		:override:
		:returns: dict
		"""

		data = super().to_dict()

		data['Coupon_IDs'] = self.coupon_ids
		return data


"""
Handles API Request CouponList_Load_Query.
Scope: Store.
:see: https://docs.miva.com/json-api/functions/couponlist_load_query
"""


class CouponListLoadQuery(ListQueryRequest):

	available_search_fields = [
		'id',
		'code',
		'descrip',
		'custscope',
		'dt_start',
		'dt_end',
		'max_use',
		'max_per',
		'active',
		'use_count'
	]

	available_sort_fields = [
		'id',
		'code',
		'descrip',
		'custscope',
		'dt_start',
		'dt_end',
		'max_use',
		'max_per',
		'active',
		'use_count'
	]

	def __init__(self, client: Client = None):
		"""
		CouponListLoadQuery Constructor.

		:param client: Client
		"""

		super().__init__(client)

	def get_function(self):
		"""
		Get the function of the request.

		:returns: str
		"""

		return 'CouponList_Load_Query'

	# noinspection PyTypeChecker
	def send(self) -> 'merchantapi.response.CouponListLoadQuery':
		return super().send()

	def create_response(self, data) -> 'CouponListLoadQuery':
		"""
		Create a response object from the response data

		:param data:
		:returns: Response
		"""

		return merchantapi.response.CouponListLoadQuery(self, data)


"""
Handles API Request CouponPriceGroup_Update_Assigned.
Scope: Store.
:see: https://docs.miva.com/json-api/functions/couponpricegroup_update_assigned
"""


class CouponPriceGroupUpdateAssigned(merchantapi.abstract.Request):
	def __init__(self, client: Client = None, coupon: merchantapi.model.Coupon = None):
		"""
		CouponPriceGroupUpdateAssigned Constructor.

		:param client: Client
		:param coupon: Coupon
		"""

		super().__init__(client)
		self.coupon_id = None
		self.edit_coupon = None
		self.coupon_code = None
		self.price_group_id = None
		self.price_group_name = None
		self.assigned = False
		if isinstance(coupon, merchantapi.model.Coupon):
			if coupon.get_id():
				self.set_coupon_id(coupon.get_id())
			elif coupon.get_code():
				self.set_edit_coupon(coupon.get_code())

	def get_function(self):
		"""
		Get the function of the request.

		:returns: str
		"""

		return 'CouponPriceGroup_Update_Assigned'

	def get_coupon_id(self) -> int:
		"""
		Get Coupon_ID.

		:returns: int
		"""

		return self.coupon_id

	def get_edit_coupon(self) -> str:
		"""
		Get Edit_Coupon.

		:returns: str
		"""

		return self.edit_coupon

	def get_coupon_code(self) -> str:
		"""
		Get Coupon_Code.

		:returns: str
		"""

		return self.coupon_code

	def get_price_group_id(self) -> int:
		"""
		Get PriceGroup_ID.

		:returns: int
		"""

		return self.price_group_id

	def get_price_group_name(self) -> str:
		"""
		Get PriceGroup_Name.

		:returns: str
		"""

		return self.price_group_name

	def get_assigned(self) -> bool:
		"""
		Get Assigned.

		:returns: bool
		"""

		return self.assigned

	def set_coupon_id(self, coupon_id: int) -> 'CouponPriceGroupUpdateAssigned':
		"""
		Set Coupon_ID.

		:param coupon_id: int
		:returns: CouponPriceGroupUpdateAssigned
		"""

		self.coupon_id = coupon_id
		return self

	def set_edit_coupon(self, edit_coupon: str) -> 'CouponPriceGroupUpdateAssigned':
		"""
		Set Edit_Coupon.

		:param edit_coupon: str
		:returns: CouponPriceGroupUpdateAssigned
		"""

		self.edit_coupon = edit_coupon
		return self

	def set_coupon_code(self, coupon_code: str) -> 'CouponPriceGroupUpdateAssigned':
		"""
		Set Coupon_Code.

		:param coupon_code: str
		:returns: CouponPriceGroupUpdateAssigned
		"""

		self.coupon_code = coupon_code
		return self

	def set_price_group_id(self, price_group_id: int) -> 'CouponPriceGroupUpdateAssigned':
		"""
		Set PriceGroup_ID.

		:param price_group_id: int
		:returns: CouponPriceGroupUpdateAssigned
		"""

		self.price_group_id = price_group_id
		return self

	def set_price_group_name(self, price_group_name: str) -> 'CouponPriceGroupUpdateAssigned':
		"""
		Set PriceGroup_Name.

		:param price_group_name: str
		:returns: CouponPriceGroupUpdateAssigned
		"""

		self.price_group_name = price_group_name
		return self

	def set_assigned(self, assigned: bool) -> 'CouponPriceGroupUpdateAssigned':
		"""
		Set Assigned.

		:param assigned: bool
		:returns: CouponPriceGroupUpdateAssigned
		"""

		self.assigned = assigned
		return self

	# noinspection PyTypeChecker
	def send(self) -> 'merchantapi.response.CouponPriceGroupUpdateAssigned':
		return super().send()

	def create_response(self, data) -> 'CouponPriceGroupUpdateAssigned':
		"""
		Create a response object from the response data

		:param data:
		:returns: Response
		"""

		return merchantapi.response.CouponPriceGroupUpdateAssigned(self, data)

	def to_dict(self) -> dict:
		"""
		Reduce the request to a dict

		:override:
		:returns: dict
		"""

		data = super().to_dict()

		if self.coupon_id is not None:
			data['Coupon_ID'] = self.coupon_id
		elif self.edit_coupon is not None:
			data['Edit_Coupon'] = self.edit_coupon
		elif self.coupon_code is not None:
			data['Coupon_Code'] = self.coupon_code

		if self.price_group_id is not None:
			data['PriceGroup_ID'] = self.price_group_id
		elif self.price_group_name is not None:
			data['PriceGroup_Name'] = self.price_group_name

		data['Assigned'] = self.assigned
		return data


"""
Handles API Request Coupon_Insert.
Scope: Store.
:see: https://docs.miva.com/json-api/functions/coupon_insert
"""


class CouponInsert(merchantapi.abstract.Request):
	def __init__(self, client: Client = None, coupon: merchantapi.model.Coupon = None):
		"""
		CouponInsert Constructor.

		:param client: Client
		:param coupon: Coupon
		"""

		super().__init__(client)
		self.code = None
		self.description = None
		self.customer_scope = None
		self.date_time_start = None
		self.date_time_end = None
		self.max_use = None
		self.max_per = None
		self.active = False
		self.price_group_id = None
		if isinstance(coupon, merchantapi.model.Coupon):
			self.set_code(coupon.get_code())
			self.set_description(coupon.get_description())
			self.set_customer_scope(coupon.get_customer_scope())
			self.set_date_time_start(coupon.get_date_time_start())
			self.set_date_time_end(coupon.get_date_time_end())
			self.set_max_use(coupon.get_max_use())
			self.set_max_per(coupon.get_max_per())
			self.set_active(coupon.get_active())

	def get_function(self):
		"""
		Get the function of the request.

		:returns: str
		"""

		return 'Coupon_Insert'

	def get_code(self) -> str:
		"""
		Get Code.

		:returns: str
		"""

		return self.code

	def get_description(self) -> str:
		"""
		Get Description.

		:returns: str
		"""

		return self.description

	def get_customer_scope(self) -> str:
		"""
		Get CustomerScope.

		:returns: str
		"""

		return self.customer_scope

	def get_date_time_start(self) -> int:
		"""
		Get DateTime_Start.

		:returns: int
		"""

		return self.date_time_start

	def get_date_time_end(self) -> int:
		"""
		Get DateTime_End.

		:returns: int
		"""

		return self.date_time_end

	def get_max_use(self) -> int:
		"""
		Get Max_Use.

		:returns: int
		"""

		return self.max_use

	def get_max_per(self) -> int:
		"""
		Get Max_Per.

		:returns: int
		"""

		return self.max_per

	def get_active(self) -> bool:
		"""
		Get Active.

		:returns: bool
		"""

		return self.active

	def get_price_group_id(self) -> int:
		"""
		Get PriceGroup_ID.

		:returns: int
		"""

		return self.price_group_id

	def set_code(self, code: str) -> 'CouponInsert':
		"""
		Set Code.

		:param code: str
		:returns: CouponInsert
		"""

		self.code = code
		return self

	def set_description(self, description: str) -> 'CouponInsert':
		"""
		Set Description.

		:param description: str
		:returns: CouponInsert
		"""

		self.description = description
		return self

	def set_customer_scope(self, customer_scope: str) -> 'CouponInsert':
		"""
		Set CustomerScope.

		:param customer_scope: str
		:returns: CouponInsert
		"""

		self.customer_scope = customer_scope
		return self

	def set_date_time_start(self, date_time_start: int) -> 'CouponInsert':
		"""
		Set DateTime_Start.

		:param date_time_start: int
		:returns: CouponInsert
		"""

		self.date_time_start = date_time_start
		return self

	def set_date_time_end(self, date_time_end: int) -> 'CouponInsert':
		"""
		Set DateTime_End.

		:param date_time_end: int
		:returns: CouponInsert
		"""

		self.date_time_end = date_time_end
		return self

	def set_max_use(self, max_use: int) -> 'CouponInsert':
		"""
		Set Max_Use.

		:param max_use: int
		:returns: CouponInsert
		"""

		self.max_use = max_use
		return self

	def set_max_per(self, max_per: int) -> 'CouponInsert':
		"""
		Set Max_Per.

		:param max_per: int
		:returns: CouponInsert
		"""

		self.max_per = max_per
		return self

	def set_active(self, active: bool) -> 'CouponInsert':
		"""
		Set Active.

		:param active: bool
		:returns: CouponInsert
		"""

		self.active = active
		return self

	def set_price_group_id(self, price_group_id: int) -> 'CouponInsert':
		"""
		Set PriceGroup_ID.

		:param price_group_id: int
		:returns: CouponInsert
		"""

		self.price_group_id = price_group_id
		return self

	# noinspection PyTypeChecker
	def send(self) -> 'merchantapi.response.CouponInsert':
		return super().send()

	def create_response(self, data) -> 'CouponInsert':
		"""
		Create a response object from the response data

		:param data:
		:returns: Response
		"""

		return merchantapi.response.CouponInsert(self, data)

	def to_dict(self) -> dict:
		"""
		Reduce the request to a dict

		:override:
		:returns: dict
		"""

		data = super().to_dict()

		data['Code'] = self.code
		if self.description is not None:
			data['Description'] = self.description
		if self.customer_scope is not None:
			data['CustomerScope'] = self.customer_scope
		if self.date_time_start is not None:
			data['DateTime_Start'] = self.date_time_start
		if self.date_time_end is not None:
			data['DateTime_End'] = self.date_time_end
		if self.max_use is not None:
			data['Max_Use'] = self.max_use
		if self.max_per is not None:
			data['Max_Per'] = self.max_per
		if self.active is not None:
			data['Active'] = self.active
		if self.price_group_id is not None:
			data['PriceGroup_ID'] = self.price_group_id
		return data


"""
Handles API Request Coupon_Update.
Scope: Store.
:see: https://docs.miva.com/json-api/functions/coupon_update
"""


class CouponUpdate(merchantapi.abstract.Request):
	def __init__(self, client: Client = None, coupon: merchantapi.model.Coupon = None):
		"""
		CouponUpdate Constructor.

		:param client: Client
		:param coupon: Coupon
		"""

		super().__init__(client)
		self.coupon_id = None
		self.coupon_code = None
		self.edit_coupon = None
		self.code = None
		self.description = None
		self.customer_scope = None
		self.date_time_start = None
		self.date_time_end = None
		self.max_use = None
		self.max_per = None
		self.active = False
		if isinstance(coupon, merchantapi.model.Coupon):
			if coupon.get_id():
				self.set_coupon_id(coupon.get_id())
			elif coupon.get_code():
				self.set_edit_coupon(coupon.get_code())

			self.set_coupon_code(coupon.get_code())
			self.set_code(coupon.get_code())
			self.set_description(coupon.get_description())
			self.set_customer_scope(coupon.get_customer_scope())
			self.set_date_time_start(coupon.get_date_time_start())
			self.set_date_time_end(coupon.get_date_time_end())
			self.set_max_use(coupon.get_max_use())
			self.set_max_per(coupon.get_max_per())
			self.set_active(coupon.get_active())

	def get_function(self):
		"""
		Get the function of the request.

		:returns: str
		"""

		return 'Coupon_Update'

	def get_coupon_id(self) -> int:
		"""
		Get Coupon_ID.

		:returns: int
		"""

		return self.coupon_id

	def get_coupon_code(self) -> str:
		"""
		Get Coupon_Code.

		:returns: str
		"""

		return self.coupon_code

	def get_edit_coupon(self) -> str:
		"""
		Get Edit_Coupon.

		:returns: str
		"""

		return self.edit_coupon

	def get_code(self) -> str:
		"""
		Get Code.

		:returns: str
		"""

		return self.code

	def get_description(self) -> str:
		"""
		Get Description.

		:returns: str
		"""

		return self.description

	def get_customer_scope(self) -> str:
		"""
		Get CustomerScope.

		:returns: str
		"""

		return self.customer_scope

	def get_date_time_start(self) -> int:
		"""
		Get DateTime_Start.

		:returns: int
		"""

		return self.date_time_start

	def get_date_time_end(self) -> int:
		"""
		Get DateTime_End.

		:returns: int
		"""

		return self.date_time_end

	def get_max_use(self) -> int:
		"""
		Get Max_Use.

		:returns: int
		"""

		return self.max_use

	def get_max_per(self) -> int:
		"""
		Get Max_Per.

		:returns: int
		"""

		return self.max_per

	def get_active(self) -> bool:
		"""
		Get Active.

		:returns: bool
		"""

		return self.active

	def set_coupon_id(self, coupon_id: int) -> 'CouponUpdate':
		"""
		Set Coupon_ID.

		:param coupon_id: int
		:returns: CouponUpdate
		"""

		self.coupon_id = coupon_id
		return self

	def set_coupon_code(self, coupon_code: str) -> 'CouponUpdate':
		"""
		Set Coupon_Code.

		:param coupon_code: str
		:returns: CouponUpdate
		"""

		self.coupon_code = coupon_code
		return self

	def set_edit_coupon(self, edit_coupon: str) -> 'CouponUpdate':
		"""
		Set Edit_Coupon.

		:param edit_coupon: str
		:returns: CouponUpdate
		"""

		self.edit_coupon = edit_coupon
		return self

	def set_code(self, code: str) -> 'CouponUpdate':
		"""
		Set Code.

		:param code: str
		:returns: CouponUpdate
		"""

		self.code = code
		return self

	def set_description(self, description: str) -> 'CouponUpdate':
		"""
		Set Description.

		:param description: str
		:returns: CouponUpdate
		"""

		self.description = description
		return self

	def set_customer_scope(self, customer_scope: str) -> 'CouponUpdate':
		"""
		Set CustomerScope.

		:param customer_scope: str
		:returns: CouponUpdate
		"""

		self.customer_scope = customer_scope
		return self

	def set_date_time_start(self, date_time_start: int) -> 'CouponUpdate':
		"""
		Set DateTime_Start.

		:param date_time_start: int
		:returns: CouponUpdate
		"""

		self.date_time_start = date_time_start
		return self

	def set_date_time_end(self, date_time_end: int) -> 'CouponUpdate':
		"""
		Set DateTime_End.

		:param date_time_end: int
		:returns: CouponUpdate
		"""

		self.date_time_end = date_time_end
		return self

	def set_max_use(self, max_use: int) -> 'CouponUpdate':
		"""
		Set Max_Use.

		:param max_use: int
		:returns: CouponUpdate
		"""

		self.max_use = max_use
		return self

	def set_max_per(self, max_per: int) -> 'CouponUpdate':
		"""
		Set Max_Per.

		:param max_per: int
		:returns: CouponUpdate
		"""

		self.max_per = max_per
		return self

	def set_active(self, active: bool) -> 'CouponUpdate':
		"""
		Set Active.

		:param active: bool
		:returns: CouponUpdate
		"""

		self.active = active
		return self

	# noinspection PyTypeChecker
	def send(self) -> 'merchantapi.response.CouponUpdate':
		return super().send()

	def create_response(self, data) -> 'CouponUpdate':
		"""
		Create a response object from the response data

		:param data:
		:returns: Response
		"""

		return merchantapi.response.CouponUpdate(self, data)

	def to_dict(self) -> dict:
		"""
		Reduce the request to a dict

		:override:
		:returns: dict
		"""

		data = super().to_dict()

		if self.coupon_id is not None:
			data['Coupon_ID'] = self.coupon_id
		elif self.edit_coupon is not None:
			data['Edit_Coupon'] = self.edit_coupon

		if self.coupon_code is not None:
			data['Coupon_Code'] = self.coupon_code
		if self.code is not None:
			data['Code'] = self.code
		if self.description is not None:
			data['Description'] = self.description
		if self.customer_scope is not None:
			data['CustomerScope'] = self.customer_scope
		if self.date_time_start is not None:
			data['DateTime_Start'] = self.date_time_start
		if self.date_time_end is not None:
			data['DateTime_End'] = self.date_time_end
		if self.max_use is not None:
			data['Max_Use'] = self.max_use
		if self.max_per is not None:
			data['Max_Per'] = self.max_per
		if self.active is not None:
			data['Active'] = self.active
		return data


"""
Handles API Request CustomerList_Load_Query.
Scope: Store.
:see: https://docs.miva.com/json-api/functions/customerlist_load_query
"""


class CustomerListLoadQuery(ListQueryRequest):

	available_search_fields = [
		'id',
		'login',
		'pw_email',
		'ship_fname',
		'ship_lname',
		'ship_email',
		'ship_comp',
		'ship_phone',
		'ship_fax',
		'ship_addr1',
		'ship_addr2',
		'ship_city',
		'ship_state',
		'ship_zip',
		'ship_cntry',
		'ship_res',
		'bill_fname',
		'bill_lname',
		'bill_email',
		'bill_comp',
		'bill_phone',
		'bill_fax',
		'bill_addr1',
		'bill_addr2',
		'bill_city',
		'bill_state',
		'bill_zip',
		'bill_cntry',
		'business_title',
		'note_count',
		'dt_created',
		'dt_login',
		'credit'
	]

	available_sort_fields = [
		'id',
		'login',
		'pw_email',
		'ship_fname',
		'ship_lname',
		'ship_email',
		'ship_comp',
		'ship_phone',
		'ship_fax',
		'ship_addr1',
		'ship_addr2',
		'ship_city',
		'ship_state',
		'ship_zip',
		'ship_cntry',
		'ship_res',
		'bill_fname',
		'bill_lname',
		'bill_email',
		'bill_comp',
		'bill_phone',
		'bill_fax',
		'bill_addr1',
		'bill_addr2',
		'bill_city',
		'bill_state',
		'bill_zip',
		'bill_cntry',
		'business_title',
		'note_count',
		'dt_created',
		'dt_login',
		'credit'
	]

	def __init__(self, client: Client = None):
		"""
		CustomerListLoadQuery Constructor.

		:param client: Client
		"""

		super().__init__(client)

	def get_function(self):
		"""
		Get the function of the request.

		:returns: str
		"""

		return 'CustomerList_Load_Query'

	# noinspection PyTypeChecker
	def send(self) -> 'merchantapi.response.CustomerListLoadQuery':
		return super().send()

	def create_response(self, data) -> 'CustomerListLoadQuery':
		"""
		Create a response object from the response data

		:param data:
		:returns: Response
		"""

		return merchantapi.response.CustomerListLoadQuery(self, data)


"""
Handles API Request Customer_Delete.
Scope: Store.
:see: https://docs.miva.com/json-api/functions/customer_delete
"""


class CustomerDelete(merchantapi.abstract.Request):
	def __init__(self, client: Client = None, customer: merchantapi.model.Customer = None):
		"""
		CustomerDelete Constructor.

		:param client: Client
		:param customer: Customer
		"""

		super().__init__(client)
		self.customer_id = None
		self.customer_login = None
		self.edit_customer = None
		if isinstance(customer, merchantapi.model.Customer):
			if customer.get_id():
				self.set_customer_id(customer.get_id())
			elif customer.get_login():
				self.set_edit_customer(customer.get_login())

	def get_function(self):
		"""
		Get the function of the request.

		:returns: str
		"""

		return 'Customer_Delete'

	def get_customer_id(self) -> int:
		"""
		Get Customer_ID.

		:returns: int
		"""

		return self.customer_id

	def get_customer_login(self) -> str:
		"""
		Get Customer_Login.

		:returns: str
		"""

		return self.customer_login

	def get_edit_customer(self) -> str:
		"""
		Get Edit_Customer.

		:returns: str
		"""

		return self.edit_customer

	def set_customer_id(self, customer_id: int) -> 'CustomerDelete':
		"""
		Set Customer_ID.

		:param customer_id: int
		:returns: CustomerDelete
		"""

		self.customer_id = customer_id
		return self

	def set_customer_login(self, customer_login: str) -> 'CustomerDelete':
		"""
		Set Customer_Login.

		:param customer_login: str
		:returns: CustomerDelete
		"""

		self.customer_login = customer_login
		return self

	def set_edit_customer(self, edit_customer: str) -> 'CustomerDelete':
		"""
		Set Edit_Customer.

		:param edit_customer: str
		:returns: CustomerDelete
		"""

		self.edit_customer = edit_customer
		return self

	# noinspection PyTypeChecker
	def send(self) -> 'merchantapi.response.CustomerDelete':
		return super().send()

	def create_response(self, data) -> 'CustomerDelete':
		"""
		Create a response object from the response data

		:param data:
		:returns: Response
		"""

		return merchantapi.response.CustomerDelete(self, data)

	def to_dict(self) -> dict:
		"""
		Reduce the request to a dict

		:override:
		:returns: dict
		"""

		data = super().to_dict()

		if self.customer_id is not None:
			data['Customer_ID'] = self.customer_id
		elif self.customer_login is not None:
			data['Customer_Login'] = self.customer_login
		elif self.edit_customer is not None:
			data['Edit_Customer'] = self.edit_customer

		return data


"""
Handles API Request Customer_Insert.
Scope: Store.
:see: https://docs.miva.com/json-api/functions/customer_insert
"""


class CustomerInsert(merchantapi.abstract.Request):
	def __init__(self, client: Client = None, customer: merchantapi.model.Customer = None):
		"""
		CustomerInsert Constructor.

		:param client: Client
		:param customer: Customer
		"""

		super().__init__(client)
		self.customer_login = None
		self.customer_password_email = None
		self.customer_password = None
		self.customer_ship_residential = False
		self.customer_ship_first_name = None
		self.customer_ship_last_name = None
		self.customer_ship_email = None
		self.customer_ship_company = None
		self.customer_ship_phone = None
		self.customer_ship_fax = None
		self.customer_ship_address1 = None
		self.customer_ship_address2 = None
		self.customer_ship_city = None
		self.customer_ship_state = None
		self.customer_ship_zip = None
		self.customer_ship_country = None
		self.customer_bill_first_name = None
		self.customer_bill_last_name = None
		self.customer_bill_email = None
		self.customer_bill_company = None
		self.customer_bill_phone = None
		self.customer_bill_fax = None
		self.customer_bill_address1 = None
		self.customer_bill_address2 = None
		self.customer_bill_city = None
		self.customer_bill_state = None
		self.customer_bill_zip = None
		self.customer_bill_country = None
		self.customer_tax_exempt = False
		self.customer_business_account = None
		self.custom_field_values = merchantapi.model.CustomFieldValues()
		if isinstance(customer, merchantapi.model.Customer):
			self.set_customer_login(customer.get_login())
			self.set_customer_password_email(customer.get_password_email())
			self.set_customer_ship_residential(customer.get_shipping_residential())
			self.set_customer_ship_first_name(customer.get_ship_first_name())
			self.set_customer_ship_last_name(customer.get_ship_last_name())
			self.set_customer_ship_email(customer.get_ship_email())
			self.set_customer_ship_company(customer.get_ship_company())
			self.set_customer_ship_phone(customer.get_ship_phone())
			self.set_customer_ship_fax(customer.get_ship_fax())
			self.set_customer_ship_address1(customer.get_ship_address1())
			self.set_customer_ship_address2(customer.get_ship_address2())
			self.set_customer_ship_city(customer.get_ship_city())
			self.set_customer_ship_state(customer.get_ship_state())
			self.set_customer_ship_zip(customer.get_ship_zip())
			self.set_customer_ship_country(customer.get_ship_country())
			self.set_customer_bill_first_name(customer.get_bill_first_name())
			self.set_customer_bill_last_name(customer.get_bill_last_name())
			self.set_customer_bill_email(customer.get_bill_email())
			self.set_customer_bill_company(customer.get_bill_company())
			self.set_customer_bill_phone(customer.get_bill_phone())
			self.set_customer_bill_fax(customer.get_bill_fax())
			self.set_customer_bill_address1(customer.get_bill_address1())
			self.set_customer_bill_address2(customer.get_bill_address2())
			self.set_customer_bill_city(customer.get_bill_city())
			self.set_customer_bill_state(customer.get_bill_state())
			self.set_customer_bill_zip(customer.get_bill_zip())
			self.set_customer_bill_country(customer.get_bill_country())
			self.set_customer_business_account(customer.get_business_title())

			if customer.get_custom_field_values():
				self.set_custom_field_values(customer.get_custom_field_values())

	def get_function(self):
		"""
		Get the function of the request.

		:returns: str
		"""

		return 'Customer_Insert'

	def get_customer_login(self) -> str:
		"""
		Get Customer_Login.

		:returns: str
		"""

		return self.customer_login

	def get_customer_password_email(self) -> str:
		"""
		Get Customer_PasswordEmail.

		:returns: str
		"""

		return self.customer_password_email

	def get_customer_password(self) -> str:
		"""
		Get Customer_Password.

		:returns: str
		"""

		return self.customer_password

	def get_customer_ship_residential(self) -> bool:
		"""
		Get Customer_ShipResidential.

		:returns: bool
		"""

		return self.customer_ship_residential

	def get_customer_ship_first_name(self) -> str:
		"""
		Get Customer_ShipFirstName.

		:returns: str
		"""

		return self.customer_ship_first_name

	def get_customer_ship_last_name(self) -> str:
		"""
		Get Customer_ShipLastName.

		:returns: str
		"""

		return self.customer_ship_last_name

	def get_customer_ship_email(self) -> str:
		"""
		Get Customer_ShipEmail.

		:returns: str
		"""

		return self.customer_ship_email

	def get_customer_ship_company(self) -> str:
		"""
		Get Customer_ShipCompany.

		:returns: str
		"""

		return self.customer_ship_company

	def get_customer_ship_phone(self) -> str:
		"""
		Get Customer_ShipPhone.

		:returns: str
		"""

		return self.customer_ship_phone

	def get_customer_ship_fax(self) -> str:
		"""
		Get Customer_ShipFax.

		:returns: str
		"""

		return self.customer_ship_fax

	def get_customer_ship_address1(self) -> str:
		"""
		Get Customer_ShipAddress1.

		:returns: str
		"""

		return self.customer_ship_address1

	def get_customer_ship_address2(self) -> str:
		"""
		Get Customer_ShipAddress2.

		:returns: str
		"""

		return self.customer_ship_address2

	def get_customer_ship_city(self) -> str:
		"""
		Get Customer_ShipCity.

		:returns: str
		"""

		return self.customer_ship_city

	def get_customer_ship_state(self) -> str:
		"""
		Get Customer_ShipState.

		:returns: str
		"""

		return self.customer_ship_state

	def get_customer_ship_zip(self) -> str:
		"""
		Get Customer_ShipZip.

		:returns: str
		"""

		return self.customer_ship_zip

	def get_customer_ship_country(self) -> str:
		"""
		Get Customer_ShipCountry.

		:returns: str
		"""

		return self.customer_ship_country

	def get_customer_bill_first_name(self) -> str:
		"""
		Get Customer_BillFirstName.

		:returns: str
		"""

		return self.customer_bill_first_name

	def get_customer_bill_last_name(self) -> str:
		"""
		Get Customer_BillLastName.

		:returns: str
		"""

		return self.customer_bill_last_name

	def get_customer_bill_email(self) -> str:
		"""
		Get Customer_BillEmail.

		:returns: str
		"""

		return self.customer_bill_email

	def get_customer_bill_company(self) -> str:
		"""
		Get Customer_BillCompany.

		:returns: str
		"""

		return self.customer_bill_company

	def get_customer_bill_phone(self) -> str:
		"""
		Get Customer_BillPhone.

		:returns: str
		"""

		return self.customer_bill_phone

	def get_customer_bill_fax(self) -> str:
		"""
		Get Customer_BillFax.

		:returns: str
		"""

		return self.customer_bill_fax

	def get_customer_bill_address1(self) -> str:
		"""
		Get Customer_BillAddress1.

		:returns: str
		"""

		return self.customer_bill_address1

	def get_customer_bill_address2(self) -> str:
		"""
		Get Customer_BillAddress2.

		:returns: str
		"""

		return self.customer_bill_address2

	def get_customer_bill_city(self) -> str:
		"""
		Get Customer_BillCity.

		:returns: str
		"""

		return self.customer_bill_city

	def get_customer_bill_state(self) -> str:
		"""
		Get Customer_BillState.

		:returns: str
		"""

		return self.customer_bill_state

	def get_customer_bill_zip(self) -> str:
		"""
		Get Customer_BillZip.

		:returns: str
		"""

		return self.customer_bill_zip

	def get_customer_bill_country(self) -> str:
		"""
		Get Customer_BillCountry.

		:returns: str
		"""

		return self.customer_bill_country

	def get_customer_tax_exempt(self) -> bool:
		"""
		Get Customer_Tax_Exempt.

		:returns: bool
		"""

		return self.customer_tax_exempt

	def get_customer_business_account(self) -> str:
		"""
		Get Customer_BusinessAccount.

		:returns: str
		"""

		return self.customer_business_account

	def get_custom_field_values(self) -> merchantapi.model.CustomFieldValues:
		"""
		Get CustomField_Values.

		:returns: CustomFieldValues}|None
		"""

		return self.custom_field_values

	def set_customer_login(self, customer_login: str) -> 'CustomerInsert':
		"""
		Set Customer_Login.

		:param customer_login: str
		:returns: CustomerInsert
		"""

		self.customer_login = customer_login
		return self

	def set_customer_password_email(self, customer_password_email: str) -> 'CustomerInsert':
		"""
		Set Customer_PasswordEmail.

		:param customer_password_email: str
		:returns: CustomerInsert
		"""

		self.customer_password_email = customer_password_email
		return self

	def set_customer_password(self, customer_password: str) -> 'CustomerInsert':
		"""
		Set Customer_Password.

		:param customer_password: str
		:returns: CustomerInsert
		"""

		self.customer_password = customer_password
		return self

	def set_customer_ship_residential(self, customer_ship_residential: bool) -> 'CustomerInsert':
		"""
		Set Customer_ShipResidential.

		:param customer_ship_residential: bool
		:returns: CustomerInsert
		"""

		self.customer_ship_residential = customer_ship_residential
		return self

	def set_customer_ship_first_name(self, customer_ship_first_name: str) -> 'CustomerInsert':
		"""
		Set Customer_ShipFirstName.

		:param customer_ship_first_name: str
		:returns: CustomerInsert
		"""

		self.customer_ship_first_name = customer_ship_first_name
		return self

	def set_customer_ship_last_name(self, customer_ship_last_name: str) -> 'CustomerInsert':
		"""
		Set Customer_ShipLastName.

		:param customer_ship_last_name: str
		:returns: CustomerInsert
		"""

		self.customer_ship_last_name = customer_ship_last_name
		return self

	def set_customer_ship_email(self, customer_ship_email: str) -> 'CustomerInsert':
		"""
		Set Customer_ShipEmail.

		:param customer_ship_email: str
		:returns: CustomerInsert
		"""

		self.customer_ship_email = customer_ship_email
		return self

	def set_customer_ship_company(self, customer_ship_company: str) -> 'CustomerInsert':
		"""
		Set Customer_ShipCompany.

		:param customer_ship_company: str
		:returns: CustomerInsert
		"""

		self.customer_ship_company = customer_ship_company
		return self

	def set_customer_ship_phone(self, customer_ship_phone: str) -> 'CustomerInsert':
		"""
		Set Customer_ShipPhone.

		:param customer_ship_phone: str
		:returns: CustomerInsert
		"""

		self.customer_ship_phone = customer_ship_phone
		return self

	def set_customer_ship_fax(self, customer_ship_fax: str) -> 'CustomerInsert':
		"""
		Set Customer_ShipFax.

		:param customer_ship_fax: str
		:returns: CustomerInsert
		"""

		self.customer_ship_fax = customer_ship_fax
		return self

	def set_customer_ship_address1(self, customer_ship_address1: str) -> 'CustomerInsert':
		"""
		Set Customer_ShipAddress1.

		:param customer_ship_address1: str
		:returns: CustomerInsert
		"""

		self.customer_ship_address1 = customer_ship_address1
		return self

	def set_customer_ship_address2(self, customer_ship_address2: str) -> 'CustomerInsert':
		"""
		Set Customer_ShipAddress2.

		:param customer_ship_address2: str
		:returns: CustomerInsert
		"""

		self.customer_ship_address2 = customer_ship_address2
		return self

	def set_customer_ship_city(self, customer_ship_city: str) -> 'CustomerInsert':
		"""
		Set Customer_ShipCity.

		:param customer_ship_city: str
		:returns: CustomerInsert
		"""

		self.customer_ship_city = customer_ship_city
		return self

	def set_customer_ship_state(self, customer_ship_state: str) -> 'CustomerInsert':
		"""
		Set Customer_ShipState.

		:param customer_ship_state: str
		:returns: CustomerInsert
		"""

		self.customer_ship_state = customer_ship_state
		return self

	def set_customer_ship_zip(self, customer_ship_zip: str) -> 'CustomerInsert':
		"""
		Set Customer_ShipZip.

		:param customer_ship_zip: str
		:returns: CustomerInsert
		"""

		self.customer_ship_zip = customer_ship_zip
		return self

	def set_customer_ship_country(self, customer_ship_country: str) -> 'CustomerInsert':
		"""
		Set Customer_ShipCountry.

		:param customer_ship_country: str
		:returns: CustomerInsert
		"""

		self.customer_ship_country = customer_ship_country
		return self

	def set_customer_bill_first_name(self, customer_bill_first_name: str) -> 'CustomerInsert':
		"""
		Set Customer_BillFirstName.

		:param customer_bill_first_name: str
		:returns: CustomerInsert
		"""

		self.customer_bill_first_name = customer_bill_first_name
		return self

	def set_customer_bill_last_name(self, customer_bill_last_name: str) -> 'CustomerInsert':
		"""
		Set Customer_BillLastName.

		:param customer_bill_last_name: str
		:returns: CustomerInsert
		"""

		self.customer_bill_last_name = customer_bill_last_name
		return self

	def set_customer_bill_email(self, customer_bill_email: str) -> 'CustomerInsert':
		"""
		Set Customer_BillEmail.

		:param customer_bill_email: str
		:returns: CustomerInsert
		"""

		self.customer_bill_email = customer_bill_email
		return self

	def set_customer_bill_company(self, customer_bill_company: str) -> 'CustomerInsert':
		"""
		Set Customer_BillCompany.

		:param customer_bill_company: str
		:returns: CustomerInsert
		"""

		self.customer_bill_company = customer_bill_company
		return self

	def set_customer_bill_phone(self, customer_bill_phone: str) -> 'CustomerInsert':
		"""
		Set Customer_BillPhone.

		:param customer_bill_phone: str
		:returns: CustomerInsert
		"""

		self.customer_bill_phone = customer_bill_phone
		return self

	def set_customer_bill_fax(self, customer_bill_fax: str) -> 'CustomerInsert':
		"""
		Set Customer_BillFax.

		:param customer_bill_fax: str
		:returns: CustomerInsert
		"""

		self.customer_bill_fax = customer_bill_fax
		return self

	def set_customer_bill_address1(self, customer_bill_address1: str) -> 'CustomerInsert':
		"""
		Set Customer_BillAddress1.

		:param customer_bill_address1: str
		:returns: CustomerInsert
		"""

		self.customer_bill_address1 = customer_bill_address1
		return self

	def set_customer_bill_address2(self, customer_bill_address2: str) -> 'CustomerInsert':
		"""
		Set Customer_BillAddress2.

		:param customer_bill_address2: str
		:returns: CustomerInsert
		"""

		self.customer_bill_address2 = customer_bill_address2
		return self

	def set_customer_bill_city(self, customer_bill_city: str) -> 'CustomerInsert':
		"""
		Set Customer_BillCity.

		:param customer_bill_city: str
		:returns: CustomerInsert
		"""

		self.customer_bill_city = customer_bill_city
		return self

	def set_customer_bill_state(self, customer_bill_state: str) -> 'CustomerInsert':
		"""
		Set Customer_BillState.

		:param customer_bill_state: str
		:returns: CustomerInsert
		"""

		self.customer_bill_state = customer_bill_state
		return self

	def set_customer_bill_zip(self, customer_bill_zip: str) -> 'CustomerInsert':
		"""
		Set Customer_BillZip.

		:param customer_bill_zip: str
		:returns: CustomerInsert
		"""

		self.customer_bill_zip = customer_bill_zip
		return self

	def set_customer_bill_country(self, customer_bill_country: str) -> 'CustomerInsert':
		"""
		Set Customer_BillCountry.

		:param customer_bill_country: str
		:returns: CustomerInsert
		"""

		self.customer_bill_country = customer_bill_country
		return self

	def set_customer_tax_exempt(self, customer_tax_exempt: bool) -> 'CustomerInsert':
		"""
		Set Customer_Tax_Exempt.

		:param customer_tax_exempt: bool
		:returns: CustomerInsert
		"""

		self.customer_tax_exempt = customer_tax_exempt
		return self

	def set_customer_business_account(self, customer_business_account: str) -> 'CustomerInsert':
		"""
		Set Customer_BusinessAccount.

		:param customer_business_account: str
		:returns: CustomerInsert
		"""

		self.customer_business_account = customer_business_account
		return self

	def set_custom_field_values(self, custom_field_values: merchantapi.model.CustomFieldValues) -> 'CustomerInsert':
		"""
		Set CustomField_Values.

		:param custom_field_values: CustomFieldValues}|None
		:raises Exception:
		:returns: CustomerInsert
		"""

		if not isinstance(custom_field_values, merchantapi.model.CustomFieldValues):
			raise Exception("")
		self.custom_field_values = custom_field_values
		return self

	# noinspection PyTypeChecker
	def send(self) -> 'merchantapi.response.CustomerInsert':
		return super().send()

	def create_response(self, data) -> 'CustomerInsert':
		"""
		Create a response object from the response data

		:param data:
		:returns: Response
		"""

		return merchantapi.response.CustomerInsert(self, data)

	def to_dict(self) -> dict:
		"""
		Reduce the request to a dict

		:override:
		:returns: dict
		"""

		data = super().to_dict()

		data['Customer_Login'] = self.customer_login
		data['Customer_PasswordEmail'] = self.customer_password_email
		data['Customer_Password'] = self.customer_password
		if self.customer_ship_residential is not None:
			data['Customer_ShipResidential'] = self.customer_ship_residential
		if self.customer_ship_first_name is not None:
			data['Customer_ShipFirstName'] = self.customer_ship_first_name
		if self.customer_ship_last_name is not None:
			data['Customer_ShipLastName'] = self.customer_ship_last_name
		if self.customer_ship_email is not None:
			data['Customer_ShipEmail'] = self.customer_ship_email
		if self.customer_ship_company is not None:
			data['Customer_ShipCompany'] = self.customer_ship_company
		if self.customer_ship_phone is not None:
			data['Customer_ShipPhone'] = self.customer_ship_phone
		if self.customer_ship_fax is not None:
			data['Customer_ShipFax'] = self.customer_ship_fax
		if self.customer_ship_address1 is not None:
			data['Customer_ShipAddress1'] = self.customer_ship_address1
		if self.customer_ship_address2 is not None:
			data['Customer_ShipAddress2'] = self.customer_ship_address2
		if self.customer_ship_city is not None:
			data['Customer_ShipCity'] = self.customer_ship_city
		if self.customer_ship_state is not None:
			data['Customer_ShipState'] = self.customer_ship_state
		if self.customer_ship_zip is not None:
			data['Customer_ShipZip'] = self.customer_ship_zip
		if self.customer_ship_country is not None:
			data['Customer_ShipCountry'] = self.customer_ship_country
		if self.customer_bill_first_name is not None:
			data['Customer_BillFirstName'] = self.customer_bill_first_name
		if self.customer_bill_last_name is not None:
			data['Customer_BillLastName'] = self.customer_bill_last_name
		if self.customer_bill_email is not None:
			data['Customer_BillEmail'] = self.customer_bill_email
		if self.customer_bill_company is not None:
			data['Customer_BillCompany'] = self.customer_bill_company
		if self.customer_bill_phone is not None:
			data['Customer_BillPhone'] = self.customer_bill_phone
		if self.customer_bill_fax is not None:
			data['Customer_BillFax'] = self.customer_bill_fax
		if self.customer_bill_address1 is not None:
			data['Customer_BillAddress1'] = self.customer_bill_address1
		if self.customer_bill_address2 is not None:
			data['Customer_BillAddress2'] = self.customer_bill_address2
		if self.customer_bill_city is not None:
			data['Customer_BillCity'] = self.customer_bill_city
		if self.customer_bill_state is not None:
			data['Customer_BillState'] = self.customer_bill_state
		if self.customer_bill_zip is not None:
			data['Customer_BillZip'] = self.customer_bill_zip
		if self.customer_bill_country is not None:
			data['Customer_BillCountry'] = self.customer_bill_country
		if self.customer_tax_exempt is not None:
			data['Customer_Tax_Exempt'] = self.customer_tax_exempt
		if self.customer_business_account is not None:
			data['Customer_BusinessAccount'] = self.customer_business_account
		if self.custom_field_values is not None:
			data['CustomField_Values'] = self.custom_field_values.to_dict()
		return data


"""
Handles API Request Customer_Update.
Scope: Store.
:see: https://docs.miva.com/json-api/functions/customer_update
"""


class CustomerUpdate(merchantapi.abstract.Request):
	def __init__(self, client: Client = None, customer: merchantapi.model.Customer = None):
		"""
		CustomerUpdate Constructor.

		:param client: Client
		:param customer: Customer
		"""

		super().__init__(client)
		self.customer_id = None
		self.edit_customer = None
		self.customer_login = None
		self.customer_password_email = None
		self.customer_password = None
		self.customer_ship_residential = False
		self.customer_ship_first_name = None
		self.customer_ship_last_name = None
		self.customer_ship_email = None
		self.customer_ship_company = None
		self.customer_ship_phone = None
		self.customer_ship_fax = None
		self.customer_ship_address1 = None
		self.customer_ship_address2 = None
		self.customer_ship_city = None
		self.customer_ship_state = None
		self.customer_ship_zip = None
		self.customer_ship_country = None
		self.customer_bill_first_name = None
		self.customer_bill_last_name = None
		self.customer_bill_email = None
		self.customer_bill_company = None
		self.customer_bill_phone = None
		self.customer_bill_fax = None
		self.customer_bill_address1 = None
		self.customer_bill_address2 = None
		self.customer_bill_city = None
		self.customer_bill_state = None
		self.customer_bill_zip = None
		self.customer_bill_country = None
		self.customer_tax_exempt = None
		self.customer_business_account = None
		self.custom_field_values = merchantapi.model.CustomFieldValues()
		if isinstance(customer, merchantapi.model.Customer):
			if customer.get_id():
				self.set_customer_id(customer.get_id())
			elif customer.get_login():
				self.set_edit_customer(customer.get_login())

			self.set_customer_login(customer.get_login())
			self.set_customer_password_email(customer.get_password_email())
			self.set_customer_ship_residential(customer.get_shipping_residential())
			self.set_customer_ship_first_name(customer.get_ship_first_name())
			self.set_customer_ship_last_name(customer.get_ship_last_name())
			self.set_customer_ship_email(customer.get_ship_email())
			self.set_customer_ship_company(customer.get_ship_company())
			self.set_customer_ship_phone(customer.get_ship_phone())
			self.set_customer_ship_fax(customer.get_ship_fax())
			self.set_customer_ship_address1(customer.get_ship_address1())
			self.set_customer_ship_address2(customer.get_ship_address2())
			self.set_customer_ship_city(customer.get_ship_city())
			self.set_customer_ship_state(customer.get_ship_state())
			self.set_customer_ship_zip(customer.get_ship_zip())
			self.set_customer_ship_country(customer.get_ship_country())
			self.set_customer_bill_first_name(customer.get_bill_first_name())
			self.set_customer_bill_last_name(customer.get_bill_last_name())
			self.set_customer_bill_email(customer.get_bill_email())
			self.set_customer_bill_company(customer.get_bill_company())
			self.set_customer_bill_phone(customer.get_bill_phone())
			self.set_customer_bill_fax(customer.get_bill_fax())
			self.set_customer_bill_address1(customer.get_bill_address1())
			self.set_customer_bill_address2(customer.get_bill_address2())
			self.set_customer_bill_city(customer.get_bill_city())
			self.set_customer_bill_state(customer.get_bill_state())
			self.set_customer_bill_zip(customer.get_bill_zip())
			self.set_customer_bill_country(customer.get_bill_country())
			self.set_customer_business_account(customer.get_business_title())

			if customer.get_custom_field_values():
				self.set_custom_field_values(customer.get_custom_field_values())

	def get_function(self):
		"""
		Get the function of the request.

		:returns: str
		"""

		return 'Customer_Update'

	def get_customer_id(self) -> int:
		"""
		Get Customer_ID.

		:returns: int
		"""

		return self.customer_id

	def get_edit_customer(self) -> str:
		"""
		Get Edit_Customer.

		:returns: str
		"""

		return self.edit_customer

	def get_customer_login(self) -> str:
		"""
		Get Customer_Login.

		:returns: str
		"""

		return self.customer_login

	def get_customer_password_email(self) -> str:
		"""
		Get Customer_PasswordEmail.

		:returns: str
		"""

		return self.customer_password_email

	def get_customer_password(self) -> str:
		"""
		Get Customer_Password.

		:returns: str
		"""

		return self.customer_password

	def get_customer_ship_residential(self) -> bool:
		"""
		Get Customer_ShipResidential.

		:returns: bool
		"""

		return self.customer_ship_residential

	def get_customer_ship_first_name(self) -> str:
		"""
		Get Customer_ShipFirstName.

		:returns: str
		"""

		return self.customer_ship_first_name

	def get_customer_ship_last_name(self) -> str:
		"""
		Get Customer_ShipLastName.

		:returns: str
		"""

		return self.customer_ship_last_name

	def get_customer_ship_email(self) -> str:
		"""
		Get Customer_ShipEmail.

		:returns: str
		"""

		return self.customer_ship_email

	def get_customer_ship_company(self) -> str:
		"""
		Get Customer_ShipCompany.

		:returns: str
		"""

		return self.customer_ship_company

	def get_customer_ship_phone(self) -> str:
		"""
		Get Customer_ShipPhone.

		:returns: str
		"""

		return self.customer_ship_phone

	def get_customer_ship_fax(self) -> str:
		"""
		Get Customer_ShipFax.

		:returns: str
		"""

		return self.customer_ship_fax

	def get_customer_ship_address1(self) -> str:
		"""
		Get Customer_ShipAddress1.

		:returns: str
		"""

		return self.customer_ship_address1

	def get_customer_ship_address2(self) -> str:
		"""
		Get Customer_ShipAddress2.

		:returns: str
		"""

		return self.customer_ship_address2

	def get_customer_ship_city(self) -> str:
		"""
		Get Customer_ShipCity.

		:returns: str
		"""

		return self.customer_ship_city

	def get_customer_ship_state(self) -> str:
		"""
		Get Customer_ShipState.

		:returns: str
		"""

		return self.customer_ship_state

	def get_customer_ship_zip(self) -> str:
		"""
		Get Customer_ShipZip.

		:returns: str
		"""

		return self.customer_ship_zip

	def get_customer_ship_country(self) -> str:
		"""
		Get Customer_ShipCountry.

		:returns: str
		"""

		return self.customer_ship_country

	def get_customer_bill_first_name(self) -> str:
		"""
		Get Customer_BillFirstName.

		:returns: str
		"""

		return self.customer_bill_first_name

	def get_customer_bill_last_name(self) -> str:
		"""
		Get Customer_BillLastName.

		:returns: str
		"""

		return self.customer_bill_last_name

	def get_customer_bill_email(self) -> str:
		"""
		Get Customer_BillEmail.

		:returns: str
		"""

		return self.customer_bill_email

	def get_customer_bill_company(self) -> str:
		"""
		Get Customer_BillCompany.

		:returns: str
		"""

		return self.customer_bill_company

	def get_customer_bill_phone(self) -> str:
		"""
		Get Customer_BillPhone.

		:returns: str
		"""

		return self.customer_bill_phone

	def get_customer_bill_fax(self) -> str:
		"""
		Get Customer_BillFax.

		:returns: str
		"""

		return self.customer_bill_fax

	def get_customer_bill_address1(self) -> str:
		"""
		Get Customer_BillAddress1.

		:returns: str
		"""

		return self.customer_bill_address1

	def get_customer_bill_address2(self) -> str:
		"""
		Get Customer_BillAddress2.

		:returns: str
		"""

		return self.customer_bill_address2

	def get_customer_bill_city(self) -> str:
		"""
		Get Customer_BillCity.

		:returns: str
		"""

		return self.customer_bill_city

	def get_customer_bill_state(self) -> str:
		"""
		Get Customer_BillState.

		:returns: str
		"""

		return self.customer_bill_state

	def get_customer_bill_zip(self) -> str:
		"""
		Get Customer_BillZip.

		:returns: str
		"""

		return self.customer_bill_zip

	def get_customer_bill_country(self) -> str:
		"""
		Get Customer_BillCountry.

		:returns: str
		"""

		return self.customer_bill_country

	def get_customer_tax_exempt(self) -> str:
		"""
		Get Customer_Tax_Exempt.

		:returns: str
		"""

		return self.customer_tax_exempt

	def get_customer_business_account(self) -> str:
		"""
		Get Customer_BusinessAccount.

		:returns: str
		"""

		return self.customer_business_account

	def get_custom_field_values(self) -> merchantapi.model.CustomFieldValues:
		"""
		Get CustomField_Values.

		:returns: CustomFieldValues}|None
		"""

		return self.custom_field_values

	def set_customer_id(self, customer_id: int) -> 'CustomerUpdate':
		"""
		Set Customer_ID.

		:param customer_id: int
		:returns: CustomerUpdate
		"""

		self.customer_id = customer_id
		return self

	def set_edit_customer(self, edit_customer: str) -> 'CustomerUpdate':
		"""
		Set Edit_Customer.

		:param edit_customer: str
		:returns: CustomerUpdate
		"""

		self.edit_customer = edit_customer
		return self

	def set_customer_login(self, customer_login: str) -> 'CustomerUpdate':
		"""
		Set Customer_Login.

		:param customer_login: str
		:returns: CustomerUpdate
		"""

		self.customer_login = customer_login
		return self

	def set_customer_password_email(self, customer_password_email: str) -> 'CustomerUpdate':
		"""
		Set Customer_PasswordEmail.

		:param customer_password_email: str
		:returns: CustomerUpdate
		"""

		self.customer_password_email = customer_password_email
		return self

	def set_customer_password(self, customer_password: str) -> 'CustomerUpdate':
		"""
		Set Customer_Password.

		:param customer_password: str
		:returns: CustomerUpdate
		"""

		self.customer_password = customer_password
		return self

	def set_customer_ship_residential(self, customer_ship_residential: bool) -> 'CustomerUpdate':
		"""
		Set Customer_ShipResidential.

		:param customer_ship_residential: bool
		:returns: CustomerUpdate
		"""

		self.customer_ship_residential = customer_ship_residential
		return self

	def set_customer_ship_first_name(self, customer_ship_first_name: str) -> 'CustomerUpdate':
		"""
		Set Customer_ShipFirstName.

		:param customer_ship_first_name: str
		:returns: CustomerUpdate
		"""

		self.customer_ship_first_name = customer_ship_first_name
		return self

	def set_customer_ship_last_name(self, customer_ship_last_name: str) -> 'CustomerUpdate':
		"""
		Set Customer_ShipLastName.

		:param customer_ship_last_name: str
		:returns: CustomerUpdate
		"""

		self.customer_ship_last_name = customer_ship_last_name
		return self

	def set_customer_ship_email(self, customer_ship_email: str) -> 'CustomerUpdate':
		"""
		Set Customer_ShipEmail.

		:param customer_ship_email: str
		:returns: CustomerUpdate
		"""

		self.customer_ship_email = customer_ship_email
		return self

	def set_customer_ship_company(self, customer_ship_company: str) -> 'CustomerUpdate':
		"""
		Set Customer_ShipCompany.

		:param customer_ship_company: str
		:returns: CustomerUpdate
		"""

		self.customer_ship_company = customer_ship_company
		return self

	def set_customer_ship_phone(self, customer_ship_phone: str) -> 'CustomerUpdate':
		"""
		Set Customer_ShipPhone.

		:param customer_ship_phone: str
		:returns: CustomerUpdate
		"""

		self.customer_ship_phone = customer_ship_phone
		return self

	def set_customer_ship_fax(self, customer_ship_fax: str) -> 'CustomerUpdate':
		"""
		Set Customer_ShipFax.

		:param customer_ship_fax: str
		:returns: CustomerUpdate
		"""

		self.customer_ship_fax = customer_ship_fax
		return self

	def set_customer_ship_address1(self, customer_ship_address1: str) -> 'CustomerUpdate':
		"""
		Set Customer_ShipAddress1.

		:param customer_ship_address1: str
		:returns: CustomerUpdate
		"""

		self.customer_ship_address1 = customer_ship_address1
		return self

	def set_customer_ship_address2(self, customer_ship_address2: str) -> 'CustomerUpdate':
		"""
		Set Customer_ShipAddress2.

		:param customer_ship_address2: str
		:returns: CustomerUpdate
		"""

		self.customer_ship_address2 = customer_ship_address2
		return self

	def set_customer_ship_city(self, customer_ship_city: str) -> 'CustomerUpdate':
		"""
		Set Customer_ShipCity.

		:param customer_ship_city: str
		:returns: CustomerUpdate
		"""

		self.customer_ship_city = customer_ship_city
		return self

	def set_customer_ship_state(self, customer_ship_state: str) -> 'CustomerUpdate':
		"""
		Set Customer_ShipState.

		:param customer_ship_state: str
		:returns: CustomerUpdate
		"""

		self.customer_ship_state = customer_ship_state
		return self

	def set_customer_ship_zip(self, customer_ship_zip: str) -> 'CustomerUpdate':
		"""
		Set Customer_ShipZip.

		:param customer_ship_zip: str
		:returns: CustomerUpdate
		"""

		self.customer_ship_zip = customer_ship_zip
		return self

	def set_customer_ship_country(self, customer_ship_country: str) -> 'CustomerUpdate':
		"""
		Set Customer_ShipCountry.

		:param customer_ship_country: str
		:returns: CustomerUpdate
		"""

		self.customer_ship_country = customer_ship_country
		return self

	def set_customer_bill_first_name(self, customer_bill_first_name: str) -> 'CustomerUpdate':
		"""
		Set Customer_BillFirstName.

		:param customer_bill_first_name: str
		:returns: CustomerUpdate
		"""

		self.customer_bill_first_name = customer_bill_first_name
		return self

	def set_customer_bill_last_name(self, customer_bill_last_name: str) -> 'CustomerUpdate':
		"""
		Set Customer_BillLastName.

		:param customer_bill_last_name: str
		:returns: CustomerUpdate
		"""

		self.customer_bill_last_name = customer_bill_last_name
		return self

	def set_customer_bill_email(self, customer_bill_email: str) -> 'CustomerUpdate':
		"""
		Set Customer_BillEmail.

		:param customer_bill_email: str
		:returns: CustomerUpdate
		"""

		self.customer_bill_email = customer_bill_email
		return self

	def set_customer_bill_company(self, customer_bill_company: str) -> 'CustomerUpdate':
		"""
		Set Customer_BillCompany.

		:param customer_bill_company: str
		:returns: CustomerUpdate
		"""

		self.customer_bill_company = customer_bill_company
		return self

	def set_customer_bill_phone(self, customer_bill_phone: str) -> 'CustomerUpdate':
		"""
		Set Customer_BillPhone.

		:param customer_bill_phone: str
		:returns: CustomerUpdate
		"""

		self.customer_bill_phone = customer_bill_phone
		return self

	def set_customer_bill_fax(self, customer_bill_fax: str) -> 'CustomerUpdate':
		"""
		Set Customer_BillFax.

		:param customer_bill_fax: str
		:returns: CustomerUpdate
		"""

		self.customer_bill_fax = customer_bill_fax
		return self

	def set_customer_bill_address1(self, customer_bill_address1: str) -> 'CustomerUpdate':
		"""
		Set Customer_BillAddress1.

		:param customer_bill_address1: str
		:returns: CustomerUpdate
		"""

		self.customer_bill_address1 = customer_bill_address1
		return self

	def set_customer_bill_address2(self, customer_bill_address2: str) -> 'CustomerUpdate':
		"""
		Set Customer_BillAddress2.

		:param customer_bill_address2: str
		:returns: CustomerUpdate
		"""

		self.customer_bill_address2 = customer_bill_address2
		return self

	def set_customer_bill_city(self, customer_bill_city: str) -> 'CustomerUpdate':
		"""
		Set Customer_BillCity.

		:param customer_bill_city: str
		:returns: CustomerUpdate
		"""

		self.customer_bill_city = customer_bill_city
		return self

	def set_customer_bill_state(self, customer_bill_state: str) -> 'CustomerUpdate':
		"""
		Set Customer_BillState.

		:param customer_bill_state: str
		:returns: CustomerUpdate
		"""

		self.customer_bill_state = customer_bill_state
		return self

	def set_customer_bill_zip(self, customer_bill_zip: str) -> 'CustomerUpdate':
		"""
		Set Customer_BillZip.

		:param customer_bill_zip: str
		:returns: CustomerUpdate
		"""

		self.customer_bill_zip = customer_bill_zip
		return self

	def set_customer_bill_country(self, customer_bill_country: str) -> 'CustomerUpdate':
		"""
		Set Customer_BillCountry.

		:param customer_bill_country: str
		:returns: CustomerUpdate
		"""

		self.customer_bill_country = customer_bill_country
		return self

	def set_customer_tax_exempt(self, customer_tax_exempt: str) -> 'CustomerUpdate':
		"""
		Set Customer_Tax_Exempt.

		:param customer_tax_exempt: str
		:returns: CustomerUpdate
		"""

		self.customer_tax_exempt = customer_tax_exempt
		return self

	def set_customer_business_account(self, customer_business_account: str) -> 'CustomerUpdate':
		"""
		Set Customer_BusinessAccount.

		:param customer_business_account: str
		:returns: CustomerUpdate
		"""

		self.customer_business_account = customer_business_account
		return self

	def set_custom_field_values(self, custom_field_values: merchantapi.model.CustomFieldValues) -> 'CustomerUpdate':
		"""
		Set CustomField_Values.

		:param custom_field_values: CustomFieldValues}|None
		:raises Exception:
		:returns: CustomerUpdate
		"""

		if not isinstance(custom_field_values, merchantapi.model.CustomFieldValues):
			raise Exception("")
		self.custom_field_values = custom_field_values
		return self

	# noinspection PyTypeChecker
	def send(self) -> 'merchantapi.response.CustomerUpdate':
		return super().send()

	def create_response(self, data) -> 'CustomerUpdate':
		"""
		Create a response object from the response data

		:param data:
		:returns: Response
		"""

		return merchantapi.response.CustomerUpdate(self, data)

	def to_dict(self) -> dict:
		"""
		Reduce the request to a dict

		:override:
		:returns: dict
		"""

		data = super().to_dict()

		if self.customer_id is not None:
			data['Customer_ID'] = self.customer_id
		elif self.edit_customer is not None:
			data['Edit_Customer'] = self.edit_customer

		if self.customer_login is not None:
			data['Customer_Login'] = self.customer_login
		if self.customer_password_email is not None:
			data['Customer_PasswordEmail'] = self.customer_password_email
		if self.customer_password is not None:
			data['Customer_Password'] = self.customer_password
		if self.customer_ship_residential is not None:
			data['Customer_ShipResidential'] = self.customer_ship_residential
		if self.customer_ship_first_name is not None:
			data['Customer_ShipFirstName'] = self.customer_ship_first_name
		if self.customer_ship_last_name is not None:
			data['Customer_ShipLastName'] = self.customer_ship_last_name
		if self.customer_ship_email is not None:
			data['Customer_ShipEmail'] = self.customer_ship_email
		if self.customer_ship_company is not None:
			data['Customer_ShipCompany'] = self.customer_ship_company
		if self.customer_ship_phone is not None:
			data['Customer_ShipPhone'] = self.customer_ship_phone
		if self.customer_ship_fax is not None:
			data['Customer_ShipFax'] = self.customer_ship_fax
		if self.customer_ship_address1 is not None:
			data['Customer_ShipAddress1'] = self.customer_ship_address1
		if self.customer_ship_address2 is not None:
			data['Customer_ShipAddress2'] = self.customer_ship_address2
		if self.customer_ship_city is not None:
			data['Customer_ShipCity'] = self.customer_ship_city
		if self.customer_ship_state is not None:
			data['Customer_ShipState'] = self.customer_ship_state
		if self.customer_ship_zip is not None:
			data['Customer_ShipZip'] = self.customer_ship_zip
		if self.customer_ship_country is not None:
			data['Customer_ShipCountry'] = self.customer_ship_country
		if self.customer_bill_first_name is not None:
			data['Customer_BillFirstName'] = self.customer_bill_first_name
		if self.customer_bill_last_name is not None:
			data['Customer_BillLastName'] = self.customer_bill_last_name
		if self.customer_bill_email is not None:
			data['Customer_BillEmail'] = self.customer_bill_email
		if self.customer_bill_company is not None:
			data['Customer_BillCompany'] = self.customer_bill_company
		if self.customer_bill_phone is not None:
			data['Customer_BillPhone'] = self.customer_bill_phone
		if self.customer_bill_fax is not None:
			data['Customer_BillFax'] = self.customer_bill_fax
		if self.customer_bill_address1 is not None:
			data['Customer_BillAddress1'] = self.customer_bill_address1
		if self.customer_bill_address2 is not None:
			data['Customer_BillAddress2'] = self.customer_bill_address2
		if self.customer_bill_city is not None:
			data['Customer_BillCity'] = self.customer_bill_city
		if self.customer_bill_state is not None:
			data['Customer_BillState'] = self.customer_bill_state
		if self.customer_bill_zip is not None:
			data['Customer_BillZip'] = self.customer_bill_zip
		if self.customer_bill_country is not None:
			data['Customer_BillCountry'] = self.customer_bill_country
		if self.customer_tax_exempt is not None:
			data['Customer_Tax_Exempt'] = self.customer_tax_exempt
		if self.customer_business_account is not None:
			data['Customer_BusinessAccount'] = self.customer_business_account
		if self.custom_field_values is not None:
			data['CustomField_Values'] = self.custom_field_values.to_dict()
		return data


"""
Handles API Request CustomerPaymentCard_Register.
Scope: Store.
:see: https://docs.miva.com/json-api/functions/customerpaymentcard_register
"""


class CustomerPaymentCardRegister(merchantapi.abstract.Request):
	def __init__(self, client: Client = None, customer: merchantapi.model.Customer = None):
		"""
		CustomerPaymentCardRegister Constructor.

		:param client: Client
		:param customer: Customer
		"""

		super().__init__(client)
		self.customer_id = None
		self.edit_customer = None
		self.customer_login = None
		self.first_name = None
		self.last_name = None
		self.card_type = None
		self.card_number = None
		self.expiration_month = None
		self.expiration_year = None
		self.address1 = None
		self.address2 = None
		self.city = None
		self.state = None
		self.zip = None
		self.country = None
		if isinstance(customer, merchantapi.model.Customer):
			if customer.get_id():
				self.set_customer_id(customer.get_id())
			elif customer.get_login():
				self.set_edit_customer(customer.get_login())

	def get_function(self):
		"""
		Get the function of the request.

		:returns: str
		"""

		return 'CustomerPaymentCard_Register'

	def get_customer_id(self) -> int:
		"""
		Get Customer_ID.

		:returns: int
		"""

		return self.customer_id

	def get_edit_customer(self) -> str:
		"""
		Get Edit_Customer.

		:returns: str
		"""

		return self.edit_customer

	def get_customer_login(self) -> str:
		"""
		Get Customer_Login.

		:returns: str
		"""

		return self.customer_login

	def get_first_name(self) -> str:
		"""
		Get FirstName.

		:returns: str
		"""

		return self.first_name

	def get_last_name(self) -> str:
		"""
		Get LastName.

		:returns: str
		"""

		return self.last_name

	def get_card_type(self) -> str:
		"""
		Get CardType.

		:returns: str
		"""

		return self.card_type

	def get_card_number(self) -> str:
		"""
		Get CardNumber.

		:returns: str
		"""

		return self.card_number

	def get_expiration_month(self) -> int:
		"""
		Get ExpirationMonth.

		:returns: int
		"""

		return self.expiration_month

	def get_expiration_year(self) -> int:
		"""
		Get ExpirationYear.

		:returns: int
		"""

		return self.expiration_year

	def get_address1(self) -> str:
		"""
		Get Address1.

		:returns: str
		"""

		return self.address1

	def get_address2(self) -> str:
		"""
		Get Address2.

		:returns: str
		"""

		return self.address2

	def get_city(self) -> str:
		"""
		Get City.

		:returns: str
		"""

		return self.city

	def get_state(self) -> str:
		"""
		Get State.

		:returns: str
		"""

		return self.state

	def get_zip(self) -> str:
		"""
		Get Zip.

		:returns: str
		"""

		return self.zip

	def get_country(self) -> str:
		"""
		Get Country.

		:returns: str
		"""

		return self.country

	def set_customer_id(self, customer_id: int) -> 'CustomerPaymentCardRegister':
		"""
		Set Customer_ID.

		:param customer_id: int
		:returns: CustomerPaymentCardRegister
		"""

		self.customer_id = customer_id
		return self

	def set_edit_customer(self, edit_customer: str) -> 'CustomerPaymentCardRegister':
		"""
		Set Edit_Customer.

		:param edit_customer: str
		:returns: CustomerPaymentCardRegister
		"""

		self.edit_customer = edit_customer
		return self

	def set_customer_login(self, customer_login: str) -> 'CustomerPaymentCardRegister':
		"""
		Set Customer_Login.

		:param customer_login: str
		:returns: CustomerPaymentCardRegister
		"""

		self.customer_login = customer_login
		return self

	def set_first_name(self, first_name: str) -> 'CustomerPaymentCardRegister':
		"""
		Set FirstName.

		:param first_name: str
		:returns: CustomerPaymentCardRegister
		"""

		self.first_name = first_name
		return self

	def set_last_name(self, last_name: str) -> 'CustomerPaymentCardRegister':
		"""
		Set LastName.

		:param last_name: str
		:returns: CustomerPaymentCardRegister
		"""

		self.last_name = last_name
		return self

	def set_card_type(self, card_type: str) -> 'CustomerPaymentCardRegister':
		"""
		Set CardType.

		:param card_type: str
		:returns: CustomerPaymentCardRegister
		"""

		self.card_type = card_type
		return self

	def set_card_number(self, card_number: str) -> 'CustomerPaymentCardRegister':
		"""
		Set CardNumber.

		:param card_number: str
		:returns: CustomerPaymentCardRegister
		"""

		self.card_number = card_number
		return self

	def set_expiration_month(self, expiration_month: int) -> 'CustomerPaymentCardRegister':
		"""
		Set ExpirationMonth.

		:param expiration_month: int
		:returns: CustomerPaymentCardRegister
		"""

		self.expiration_month = expiration_month
		return self

	def set_expiration_year(self, expiration_year: int) -> 'CustomerPaymentCardRegister':
		"""
		Set ExpirationYear.

		:param expiration_year: int
		:returns: CustomerPaymentCardRegister
		"""

		self.expiration_year = expiration_year
		return self

	def set_address1(self, address1: str) -> 'CustomerPaymentCardRegister':
		"""
		Set Address1.

		:param address1: str
		:returns: CustomerPaymentCardRegister
		"""

		self.address1 = address1
		return self

	def set_address2(self, address2: str) -> 'CustomerPaymentCardRegister':
		"""
		Set Address2.

		:param address2: str
		:returns: CustomerPaymentCardRegister
		"""

		self.address2 = address2
		return self

	def set_city(self, city: str) -> 'CustomerPaymentCardRegister':
		"""
		Set City.

		:param city: str
		:returns: CustomerPaymentCardRegister
		"""

		self.city = city
		return self

	def set_state(self, state: str) -> 'CustomerPaymentCardRegister':
		"""
		Set State.

		:param state: str
		:returns: CustomerPaymentCardRegister
		"""

		self.state = state
		return self

	def set_zip(self, zip: str) -> 'CustomerPaymentCardRegister':
		"""
		Set Zip.

		:param zip: str
		:returns: CustomerPaymentCardRegister
		"""

		self.zip = zip
		return self

	def set_country(self, country: str) -> 'CustomerPaymentCardRegister':
		"""
		Set Country.

		:param country: str
		:returns: CustomerPaymentCardRegister
		"""

		self.country = country
		return self

	# noinspection PyTypeChecker
	def send(self) -> 'merchantapi.response.CustomerPaymentCardRegister':
		return super().send()

	def create_response(self, data) -> 'CustomerPaymentCardRegister':
		"""
		Create a response object from the response data

		:param data:
		:returns: Response
		"""

		return merchantapi.response.CustomerPaymentCardRegister(self, data)

	def to_dict(self) -> dict:
		"""
		Reduce the request to a dict

		:override:
		:returns: dict
		"""

		data = super().to_dict()

		if self.customer_id is not None:
			data['Customer_ID'] = self.customer_id
		elif self.edit_customer is not None:
			data['Edit_Customer'] = self.edit_customer
		elif self.customer_login is not None:
			data['Customer_Login'] = self.customer_login

		if self.first_name is not None:
			data['FirstName'] = self.first_name
		if self.last_name is not None:
			data['LastName'] = self.last_name
		if self.card_type is not None:
			data['CardType'] = self.card_type
		if self.card_number is not None:
			data['CardNumber'] = self.card_number
		if self.expiration_month is not None:
			data['ExpirationMonth'] = self.expiration_month
		if self.expiration_year is not None:
			data['ExpirationYear'] = self.expiration_year
		if self.address1 is not None:
			data['Address1'] = self.address1
		if self.address2 is not None:
			data['Address2'] = self.address2
		if self.city is not None:
			data['City'] = self.city
		if self.state is not None:
			data['State'] = self.state
		if self.zip is not None:
			data['Zip'] = self.zip
		if self.country is not None:
			data['Country'] = self.country
		return data


"""
Handles API Request Module.
Scope: Store.
:see: https://docs.miva.com/json-api/functions/module
"""


class Module(merchantapi.abstract.Request):
	def __init__(self, client: Client = None):
		"""
		Module Constructor.

		:param client: Client
		"""

		super().__init__(client)
		self.module_code = None
		self.module_function = None
		self.module_fields = {}

	def get_function(self):
		"""
		Get the function of the request.

		:returns: str
		"""

		return 'Module'

	def get_module_code(self) -> str:
		"""
		Get Module_Code.

		:returns: str
		"""

		return self.module_code

	def get_module_function(self) -> str:
		"""
		Get Module_Function.

		:returns: str
		"""

		return self.module_function

	def get_module_fields(self):
		"""
		Get Module_Fields.

		:returns: dict
		"""

		return self.module_fields

	def set_module_code(self, module_code: str) -> 'Module':
		"""
		Set Module_Code.

		:param module_code: str
		:returns: Module
		"""

		self.module_code = module_code
		return self

	def set_module_function(self, module_function: str) -> 'Module':
		"""
		Set Module_Function.

		:param module_function: str
		:returns: Module
		"""

		self.module_function = module_function
		return self

	def set_module_fields(self, module_fields) -> 'Module':
		"""
		Set Module_Fields.

		:param module_fields: dict
		:returns: Module
		"""

		self.module_fields = module_fields
		return self

	def set_module_field(self, field: str, value) -> 'Module':
		"""
		Add custom data to the request.

		:param field: str
		:param value: mixed
		:returns: {Module}
		"""

		self.module_fields[field] = value
		return self

	# noinspection PyTypeChecker
	def send(self) -> 'merchantapi.response.Module':
		return super().send()

	def create_response(self, data) -> 'Module':
		"""
		Create a response object from the response data

		:param data:
		:returns: Response
		"""

		return merchantapi.response.Module(self, data)

	def to_dict(self) -> dict:
		"""
		Reduce the request to a dict

		:override:
		:returns: dict
		"""

		data = super().to_dict()
		data.update(self.get_module_fields())

		data['Module_Code'] = self.module_code
		data['Module_Function'] = self.module_function
		return data


"""
Handles API Request NoteList_Load_Query.
Scope: Store.
:see: https://docs.miva.com/json-api/functions/notelist_load_query
"""


class NoteListLoadQuery(ListQueryRequest):

	available_search_fields = [
		'id',
		'notetext',
		'dtstamp',
		'cust_id',
		'account_id',
		'order_id',
		'admin_user',
		'cust_login',
		'business_title'
	]

	available_sort_fields = [
		'id',
		'notetext',
		'dtstamp',
		'cust_id',
		'account_id',
		'order_id',
		'admin_user',
		'cust_login',
		'business_title'
	]

	def __init__(self, client: Client = None):
		"""
		NoteListLoadQuery Constructor.

		:param client: Client
		"""

		super().__init__(client)

	def get_function(self):
		"""
		Get the function of the request.

		:returns: str
		"""

		return 'NoteList_Load_Query'

	# noinspection PyTypeChecker
	def send(self) -> 'merchantapi.response.NoteListLoadQuery':
		return super().send()

	def create_response(self, data) -> 'NoteListLoadQuery':
		"""
		Create a response object from the response data

		:param data:
		:returns: Response
		"""

		return merchantapi.response.NoteListLoadQuery(self, data)


"""
Handles API Request Note_Delete.
Scope: Store.
:see: https://docs.miva.com/json-api/functions/note_delete
"""


class NoteDelete(merchantapi.abstract.Request):
	def __init__(self, client: Client = None, note: merchantapi.model.Note = None):
		"""
		NoteDelete Constructor.

		:param client: Client
		:param note: Note
		"""

		super().__init__(client)
		self.note_id = None
		if isinstance(note, merchantapi.model.Note):
			self.set_note_id(note.get_id())

	def get_function(self):
		"""
		Get the function of the request.

		:returns: str
		"""

		return 'Note_Delete'

	def get_note_id(self) -> int:
		"""
		Get Note_ID.

		:returns: int
		"""

		return self.note_id

	def set_note_id(self, note_id: int) -> 'NoteDelete':
		"""
		Set Note_ID.

		:param note_id: int
		:returns: NoteDelete
		"""

		self.note_id = note_id
		return self

	# noinspection PyTypeChecker
	def send(self) -> 'merchantapi.response.NoteDelete':
		return super().send()

	def create_response(self, data) -> 'NoteDelete':
		"""
		Create a response object from the response data

		:param data:
		:returns: Response
		"""

		return merchantapi.response.NoteDelete(self, data)

	def to_dict(self) -> dict:
		"""
		Reduce the request to a dict

		:override:
		:returns: dict
		"""

		data = super().to_dict()

		data['Note_ID'] = self.note_id
		return data


"""
Handles API Request Note_Insert.
Scope: Store.
:see: https://docs.miva.com/json-api/functions/note_insert
"""


class NoteInsert(merchantapi.abstract.Request):
	def __init__(self, client: Client = None):
		"""
		NoteInsert Constructor.

		:param client: Client
		"""

		super().__init__(client)
		self.note_text = None
		self.customer_id = None
		self.account_id = None
		self.order_id = None

	def get_function(self):
		"""
		Get the function of the request.

		:returns: str
		"""

		return 'Note_Insert'

	def get_note_text(self) -> str:
		"""
		Get NoteText.

		:returns: str
		"""

		return self.note_text

	def get_customer_id(self) -> int:
		"""
		Get Customer_ID.

		:returns: int
		"""

		return self.customer_id

	def get_account_id(self) -> int:
		"""
		Get Account_ID.

		:returns: int
		"""

		return self.account_id

	def get_order_id(self) -> int:
		"""
		Get Order_ID.

		:returns: int
		"""

		return self.order_id

	def set_note_text(self, note_text: str) -> 'NoteInsert':
		"""
		Set NoteText.

		:param note_text: str
		:returns: NoteInsert
		"""

		self.note_text = note_text
		return self

	def set_customer_id(self, customer_id: int) -> 'NoteInsert':
		"""
		Set Customer_ID.

		:param customer_id: int
		:returns: NoteInsert
		"""

		self.customer_id = customer_id
		return self

	def set_account_id(self, account_id: int) -> 'NoteInsert':
		"""
		Set Account_ID.

		:param account_id: int
		:returns: NoteInsert
		"""

		self.account_id = account_id
		return self

	def set_order_id(self, order_id: int) -> 'NoteInsert':
		"""
		Set Order_ID.

		:param order_id: int
		:returns: NoteInsert
		"""

		self.order_id = order_id
		return self

	# noinspection PyTypeChecker
	def send(self) -> 'merchantapi.response.NoteInsert':
		return super().send()

	def create_response(self, data) -> 'NoteInsert':
		"""
		Create a response object from the response data

		:param data:
		:returns: Response
		"""

		return merchantapi.response.NoteInsert(self, data)

	def to_dict(self) -> dict:
		"""
		Reduce the request to a dict

		:override:
		:returns: dict
		"""

		data = super().to_dict()

		data['NoteText'] = self.note_text
		if self.customer_id is not None:
			data['Customer_ID'] = self.customer_id
		if self.account_id is not None:
			data['Account_ID'] = self.account_id
		if self.order_id is not None:
			data['Order_ID'] = self.order_id
		return data


"""
Handles API Request Note_Update.
Scope: Store.
:see: https://docs.miva.com/json-api/functions/note_update
"""


class NoteUpdate(merchantapi.abstract.Request):
	def __init__(self, client: Client = None, note: merchantapi.model.Note = None):
		"""
		NoteUpdate Constructor.

		:param client: Client
		:param note: Note
		"""

		super().__init__(client)
		self.note_id = None
		self.note_text = None
		if isinstance(note, merchantapi.model.Note):
			self.set_note_id(note.get_id())
			self.set_note_text(note.get_note_text())

	def get_function(self):
		"""
		Get the function of the request.

		:returns: str
		"""

		return 'Note_Update'

	def get_note_id(self) -> int:
		"""
		Get Note_ID.

		:returns: int
		"""

		return self.note_id

	def get_note_text(self) -> str:
		"""
		Get NoteText.

		:returns: str
		"""

		return self.note_text

	def set_note_id(self, note_id: int) -> 'NoteUpdate':
		"""
		Set Note_ID.

		:param note_id: int
		:returns: NoteUpdate
		"""

		self.note_id = note_id
		return self

	def set_note_text(self, note_text: str) -> 'NoteUpdate':
		"""
		Set NoteText.

		:param note_text: str
		:returns: NoteUpdate
		"""

		self.note_text = note_text
		return self

	# noinspection PyTypeChecker
	def send(self) -> 'merchantapi.response.NoteUpdate':
		return super().send()

	def create_response(self, data) -> 'NoteUpdate':
		"""
		Create a response object from the response data

		:param data:
		:returns: Response
		"""

		return merchantapi.response.NoteUpdate(self, data)

	def to_dict(self) -> dict:
		"""
		Reduce the request to a dict

		:override:
		:returns: dict
		"""

		data = super().to_dict()

		data['Note_ID'] = self.get_note_id()

		data['NoteText'] = self.note_text
		return data


"""
Handles API Request OrderCustomFieldList_Load.
Scope: Store.
:see: https://docs.miva.com/json-api/functions/ordercustomfieldlist_load
"""


class OrderCustomFieldListLoad(merchantapi.abstract.Request):
	def __init__(self, client: Client = None):
		"""
		OrderCustomFieldListLoad Constructor.

		:param client: Client
		"""

		super().__init__(client)

	def get_function(self):
		"""
		Get the function of the request.

		:returns: str
		"""

		return 'OrderCustomFieldList_Load'

	# noinspection PyTypeChecker
	def send(self) -> 'merchantapi.response.OrderCustomFieldListLoad':
		return super().send()

	def create_response(self, data) -> 'OrderCustomFieldListLoad':
		"""
		Create a response object from the response data

		:param data:
		:returns: Response
		"""

		return merchantapi.response.OrderCustomFieldListLoad(self, data)


"""
Handles API Request OrderCustomFields_Update.
Scope: Store.
:see: https://docs.miva.com/json-api/functions/ordercustomfields_update
"""


class OrderCustomFieldsUpdate(merchantapi.abstract.Request):
	def __init__(self, client: Client = None, order: merchantapi.model.Order = None):
		"""
		OrderCustomFieldsUpdate Constructor.

		:param client: Client
		:param order: Order
		"""

		super().__init__(client)
		self.order_id = None
		self.custom_field_values = merchantapi.model.CustomFieldValues()
		if isinstance(order, merchantapi.model.Order):
			if order.get_id():
				self.set_order_id(order.get_id())

	def get_function(self):
		"""
		Get the function of the request.

		:returns: str
		"""

		return 'OrderCustomFields_Update'

	def get_order_id(self) -> int:
		"""
		Get Order_ID.

		:returns: int
		"""

		return self.order_id

	def get_custom_field_values(self) -> merchantapi.model.CustomFieldValues:
		"""
		Get CustomField_Values.

		:returns: CustomFieldValues}|None
		"""

		return self.custom_field_values

	def set_order_id(self, order_id: int) -> 'OrderCustomFieldsUpdate':
		"""
		Set Order_ID.

		:param order_id: int
		:returns: OrderCustomFieldsUpdate
		"""

		self.order_id = order_id
		return self

	def set_custom_field_values(self, custom_field_values: merchantapi.model.CustomFieldValues) -> 'OrderCustomFieldsUpdate':
		"""
		Set CustomField_Values.

		:param custom_field_values: CustomFieldValues}|None
		:raises Exception:
		:returns: OrderCustomFieldsUpdate
		"""

		if not isinstance(custom_field_values, merchantapi.model.CustomFieldValues):
			raise Exception("")
		self.custom_field_values = custom_field_values
		return self

	# noinspection PyTypeChecker
	def send(self) -> 'merchantapi.response.OrderCustomFieldsUpdate':
		return super().send()

	def create_response(self, data) -> 'OrderCustomFieldsUpdate':
		"""
		Create a response object from the response data

		:param data:
		:returns: Response
		"""

		return merchantapi.response.OrderCustomFieldsUpdate(self, data)

	def to_dict(self) -> dict:
		"""
		Reduce the request to a dict

		:override:
		:returns: dict
		"""

		data = super().to_dict()

		if self.order_id is not None:
			data['Order_ID'] = self.order_id

		if self.custom_field_values is not None:
			data['CustomField_Values'] = self.custom_field_values.to_dict()
		return data


"""
Handles API Request OrderItemList_BackOrder.
Scope: Store.
:see: https://docs.miva.com/json-api/functions/orderitemlist_backorder
"""


class OrderItemListBackOrder(merchantapi.abstract.Request):
	def __init__(self, client: Client = None, order: merchantapi.model.Order = None):
		"""
		OrderItemListBackOrder Constructor.

		:param client: Client
		:param order: Order
		"""

		super().__init__(client)
		self.order_id = None
		self.line_ids = []
		self.date_in_stock = None
		if isinstance(order, merchantapi.model.Order):
			if order.get_id():
				self.set_order_id(order.get_id())

	def get_function(self):
		"""
		Get the function of the request.

		:returns: str
		"""

		return 'OrderItemList_BackOrder'

	def get_order_id(self) -> int:
		"""
		Get Order_ID.

		:returns: int
		"""

		return self.order_id

	def get_line_ids(self):
		"""
		Get Line_IDs.

		:returns: list
		"""

		return self.line_ids

	def get_date_in_stock(self) -> int:
		"""
		Get Date_InStock.

		:returns: int
		"""

		return self.date_in_stock

	def set_order_id(self, order_id: int) -> 'OrderItemListBackOrder':
		"""
		Set Order_ID.

		:param order_id: int
		:returns: OrderItemListBackOrder
		"""

		self.order_id = order_id
		return self

	def set_date_in_stock(self, date_in_stock: int) -> 'OrderItemListBackOrder':
		"""
		Set Date_InStock.

		:param date_in_stock: int
		:returns: OrderItemListBackOrder
		"""

		self.date_in_stock = date_in_stock
		return self

	def add_line_id(self, line_id) -> 'OrderItemListBackOrder':
		"""
		Add Line_IDs.

		:param line_id: int
		:returns: {OrderItemListBackOrder}
		"""

		self.line_ids.append(line_id)
		return self

	def add_order_item(self, order_item: merchantapi.model.OrderItem) -> 'OrderItemListBackOrder':
		"""
		Add OrderItem model.

		:param order_item: OrderItem
		:raises Exception:
		:returns: OrderItemListBackOrder
		"""
		if not isinstance(order_item, merchantapi.model.OrderItem):
			raise Exception('Expected an instance of OrderItem')

		if order_item.get_line_id():
			self.line_ids.append(order_item.get_line_id())

		return self

	# noinspection PyTypeChecker
	def send(self) -> 'merchantapi.response.OrderItemListBackOrder':
		return super().send()

	def create_response(self, data) -> 'OrderItemListBackOrder':
		"""
		Create a response object from the response data

		:param data:
		:returns: Response
		"""

		return merchantapi.response.OrderItemListBackOrder(self, data)

	def to_dict(self) -> dict:
		"""
		Reduce the request to a dict

		:override:
		:returns: dict
		"""

		data = super().to_dict()

		if self.order_id is not None:
			data['Order_ID'] = self.order_id

		data['Line_IDs'] = self.line_ids
		if self.date_in_stock is not None:
			data['Date_InStock'] = self.date_in_stock
		return data


"""
Handles API Request OrderItemList_Cancel.
Scope: Store.
:see: https://docs.miva.com/json-api/functions/orderitemlist_cancel
"""


class OrderItemListCancel(merchantapi.abstract.Request):
	def __init__(self, client: Client = None, order: merchantapi.model.Order = None):
		"""
		OrderItemListCancel Constructor.

		:param client: Client
		:param order: Order
		"""

		super().__init__(client)
		self.order_id = None
		self.line_ids = []
		self.reason = None
		if isinstance(order, merchantapi.model.Order):
			self.set_order_id(order.get_id())

	def get_function(self):
		"""
		Get the function of the request.

		:returns: str
		"""

		return 'OrderItemList_Cancel'

	def get_order_id(self) -> int:
		"""
		Get Order_ID.

		:returns: int
		"""

		return self.order_id

	def get_line_ids(self):
		"""
		Get Line_IDs.

		:returns: list
		"""

		return self.line_ids

	def get_reason(self) -> str:
		"""
		Get Reason.

		:returns: str
		"""

		return self.reason

	def set_order_id(self, order_id: int) -> 'OrderItemListCancel':
		"""
		Set Order_ID.

		:param order_id: int
		:returns: OrderItemListCancel
		"""

		self.order_id = order_id
		return self

	def set_reason(self, reason: str) -> 'OrderItemListCancel':
		"""
		Set Reason.

		:param reason: str
		:returns: OrderItemListCancel
		"""

		self.reason = reason
		return self

	def add_line_id(self, line_id) -> 'OrderItemListCancel':
		"""
		Add Line_IDs.

		:param line_id: int
		:returns: {OrderItemListCancel}
		"""

		self.line_ids.append(line_id)
		return self

	def add_order_item(self, order_item: merchantapi.model.OrderItem) -> 'OrderItemListCancel':
		"""
		Add OrderItem model.

		:param order_item: OrderItem
		:raises Exception:
		:returns: OrderItemListCancel
		"""
		if not isinstance(order_item, merchantapi.model.OrderItem):
			raise Exception('Expected an instance of OrderItem')

		if order_item.get_line_id():
			self.line_ids.append(order_item.get_line_id())

		return self

	# noinspection PyTypeChecker
	def send(self) -> 'merchantapi.response.OrderItemListCancel':
		return super().send()

	def create_response(self, data) -> 'OrderItemListCancel':
		"""
		Create a response object from the response data

		:param data:
		:returns: Response
		"""

		return merchantapi.response.OrderItemListCancel(self, data)

	def to_dict(self) -> dict:
		"""
		Reduce the request to a dict

		:override:
		:returns: dict
		"""

		data = super().to_dict()

		data['Order_ID'] = self.get_order_id()

		data['Line_IDs'] = self.line_ids
		if self.reason is not None:
			data['Reason'] = self.reason
		return data


"""
Handles API Request OrderItemList_CreateShipment.
Scope: Store.
:see: https://docs.miva.com/json-api/functions/orderitemlist_createshipment
"""


class OrderItemListCreateShipment(merchantapi.abstract.Request):
	def __init__(self, client: Client = None, order: merchantapi.model.Order = None):
		"""
		OrderItemListCreateShipment Constructor.

		:param client: Client
		:param order: Order
		"""

		super().__init__(client)
		self.order_id = None
		self.line_ids = []
		if isinstance(order, merchantapi.model.Order):
			self.set_order_id(order.get_id())

	def get_function(self):
		"""
		Get the function of the request.

		:returns: str
		"""

		return 'OrderItemList_CreateShipment'

	def get_order_id(self) -> int:
		"""
		Get Order_ID.

		:returns: int
		"""

		return self.order_id

	def get_line_ids(self):
		"""
		Get Line_IDs.

		:returns: list
		"""

		return self.line_ids

	def set_order_id(self, order_id: int) -> 'OrderItemListCreateShipment':
		"""
		Set Order_ID.

		:param order_id: int
		:returns: OrderItemListCreateShipment
		"""

		self.order_id = order_id
		return self

	def add_line_id(self, line_id) -> 'OrderItemListCreateShipment':
		"""
		Add Line_IDs.

		:param line_id: int
		:returns: {OrderItemListCreateShipment}
		"""

		self.line_ids.append(line_id)
		return self

	def add_order_item(self, order_item: merchantapi.model.OrderItem) -> 'OrderItemListCreateShipment':
		"""
		Add OrderItem model.

		:param order_item: OrderItem
		:raises Exception:
		:returns: OrderItemListCreateShipment
		"""
		if not isinstance(order_item, merchantapi.model.OrderItem):
			raise Exception('Expected an instance of OrderItem')

		if order_item.get_line_id():
			self.line_ids.append(order_item.get_line_id())

		return self

	# noinspection PyTypeChecker
	def send(self) -> 'merchantapi.response.OrderItemListCreateShipment':
		return super().send()

	def create_response(self, data) -> 'OrderItemListCreateShipment':
		"""
		Create a response object from the response data

		:param data:
		:returns: Response
		"""

		return merchantapi.response.OrderItemListCreateShipment(self, data)

	def to_dict(self) -> dict:
		"""
		Reduce the request to a dict

		:override:
		:returns: dict
		"""

		data = super().to_dict()

		data['Order_ID'] = self.get_order_id()

		data['Line_IDs'] = self.line_ids
		return data


"""
Handles API Request OrderItemList_Delete.
Scope: Store.
:see: https://docs.miva.com/json-api/functions/orderitemlist_delete
"""


class OrderItemListDelete(merchantapi.abstract.Request):
	def __init__(self, client: Client = None, order: merchantapi.model.Order = None):
		"""
		OrderItemListDelete Constructor.

		:param client: Client
		:param order: Order
		"""

		super().__init__(client)
		self.order_id = None
		self.line_ids = []
		if isinstance(order, merchantapi.model.Order):
			self.set_order_id(order.get_id())

	def get_function(self):
		"""
		Get the function of the request.

		:returns: str
		"""

		return 'OrderItemList_Delete'

	def get_order_id(self) -> int:
		"""
		Get Order_ID.

		:returns: int
		"""

		return self.order_id

	def get_line_ids(self):
		"""
		Get Line_IDs.

		:returns: list
		"""

		return self.line_ids

	def set_order_id(self, order_id: int) -> 'OrderItemListDelete':
		"""
		Set Order_ID.

		:param order_id: int
		:returns: OrderItemListDelete
		"""

		self.order_id = order_id
		return self

	def add_line_id(self, line_id) -> 'OrderItemListDelete':
		"""
		Add Line_IDs.

		:param line_id: int
		:returns: {OrderItemListDelete}
		"""

		self.line_ids.append(line_id)
		return self

	def add_order_item(self, order_item: merchantapi.model.OrderItem) -> 'OrderItemListDelete':
		"""
		Add OrderItem model.

		:param order_item: OrderItem
		:raises Exception:
		:returns: OrderItemListDelete
		"""
		if not isinstance(order_item, merchantapi.model.OrderItem):
			raise Exception('Expected an instance of OrderItem')

		if order_item.get_line_id():
			self.line_ids.append(order_item.get_line_id())

		return self

	# noinspection PyTypeChecker
	def send(self) -> 'merchantapi.response.OrderItemListDelete':
		return super().send()

	def create_response(self, data) -> 'OrderItemListDelete':
		"""
		Create a response object from the response data

		:param data:
		:returns: Response
		"""

		return merchantapi.response.OrderItemListDelete(self, data)

	def to_dict(self) -> dict:
		"""
		Reduce the request to a dict

		:override:
		:returns: dict
		"""

		data = super().to_dict()

		data['Order_ID'] = self.order_id
		data['Line_IDs'] = self.line_ids
		return data


"""
Handles API Request OrderItem_Add.
Scope: Store.
:see: https://docs.miva.com/json-api/functions/orderitem_add
"""


class OrderItemAdd(merchantapi.abstract.Request):
	def __init__(self, client: Client = None, order: merchantapi.model.Order = None):
		"""
		OrderItemAdd Constructor.

		:param client: Client
		:param order: Order
		"""

		super().__init__(client)
		self.order_id = None
		self.code = None
		self.name = None
		self.sku = None
		self.quantity = None
		self.price = None
		self.weight = None
		self.taxable = False
		self.options = []
		if isinstance(order, merchantapi.model.Order):
			self.set_order_id(order.get_id())

	def get_function(self):
		"""
		Get the function of the request.

		:returns: str
		"""

		return 'OrderItem_Add'

	def get_order_id(self) -> int:
		"""
		Get Order_ID.

		:returns: int
		"""

		return self.order_id

	def get_code(self) -> str:
		"""
		Get Code.

		:returns: str
		"""

		return self.code

	def get_name(self) -> str:
		"""
		Get Name.

		:returns: str
		"""

		return self.name

	def get_sku(self) -> str:
		"""
		Get Sku.

		:returns: str
		"""

		return self.sku

	def get_quantity(self) -> int:
		"""
		Get Quantity.

		:returns: int
		"""

		return self.quantity

	def get_price(self) -> float:
		"""
		Get Price.

		:returns: float
		"""

		return self.price

	def get_weight(self) -> float:
		"""
		Get Weight.

		:returns: float
		"""

		return self.weight

	def get_taxable(self) -> bool:
		"""
		Get Taxable.

		:returns: bool
		"""

		return self.taxable

	def get_options(self) -> list:
		"""
		Get Options.

		:returns: List of OrderItemOption
		"""

		return self.options

	def set_order_id(self, order_id: int) -> 'OrderItemAdd':
		"""
		Set Order_ID.

		:param order_id: int
		:returns: OrderItemAdd
		"""

		self.order_id = order_id
		return self

	def set_code(self, code: str) -> 'OrderItemAdd':
		"""
		Set Code.

		:param code: str
		:returns: OrderItemAdd
		"""

		self.code = code
		return self

	def set_name(self, name: str) -> 'OrderItemAdd':
		"""
		Set Name.

		:param name: str
		:returns: OrderItemAdd
		"""

		self.name = name
		return self

	def set_sku(self, sku: str) -> 'OrderItemAdd':
		"""
		Set Sku.

		:param sku: str
		:returns: OrderItemAdd
		"""

		self.sku = sku
		return self

	def set_quantity(self, quantity: int) -> 'OrderItemAdd':
		"""
		Set Quantity.

		:param quantity: int
		:returns: OrderItemAdd
		"""

		self.quantity = quantity
		return self

	def set_price(self, price: float) -> 'OrderItemAdd':
		"""
		Set Price.

		:param price: float
		:returns: OrderItemAdd
		"""

		self.price = price
		return self

	def set_weight(self, weight: float) -> 'OrderItemAdd':
		"""
		Set Weight.

		:param weight: float
		:returns: OrderItemAdd
		"""

		self.weight = weight
		return self

	def set_taxable(self, taxable: bool) -> 'OrderItemAdd':
		"""
		Set Taxable.

		:param taxable: bool
		:returns: OrderItemAdd
		"""

		self.taxable = taxable
		return self

	def set_options(self, options: list) -> 'OrderItemAdd':
		"""
		Set Options.

		:param options: {OrderItemOption[]}
		:raises Exception:
		:returns: OrderItemAdd
		"""

		for e in options:
			if not isinstance(e, merchantapi.model.OrderItemOption):
				raise Exception("")
		self.options = options
		return self

	def add_option(self, option) -> 'OrderItemAdd':
		"""
		Add Options.

		:param option: OrderItemOption
		:raises Exception:
		:returns: {OrderItemAdd}
		"""

		if isinstance(option, merchantapi.model.OrderItemOption):
			self.options.append(option)
		elif isinstance(option, dict):
			self.options.append(merchantapi.model.OrderItemOption(option))
		else:
			raise Exception('Expected instance of OrderItemOption or dict')
		return self

	def add_options(self, options: list) -> 'OrderItemAdd':
		"""
		Add many OrderItemOption.

		:param options: List of OrderItemOption
		:raises Exception:
		:returns: OrderItemAdd
		"""

		for e in options:
			if not isinstance(e, merchantapi.model.OrderItemOption):
				raise Exception('')
			self.options.append(e)

		return self

	# noinspection PyTypeChecker
	def send(self) -> 'merchantapi.response.OrderItemAdd':
		return super().send()

	def create_response(self, data) -> 'OrderItemAdd':
		"""
		Create a response object from the response data

		:param data:
		:returns: Response
		"""

		return merchantapi.response.OrderItemAdd(self, data)

	def to_dict(self) -> dict:
		"""
		Reduce the request to a dict

		:override:
		:returns: dict
		"""

		data = super().to_dict()

		data['Order_ID'] = self.get_order_id()

		data['Code'] = self.code
		data['Name'] = self.name
		if self.sku is not None:
			data['Sku'] = self.sku
		data['Quantity'] = self.quantity
		if self.price is not None:
			data['Price'] = self.price
		if self.weight is not None:
			data['Weight'] = self.weight
		if self.taxable is not None:
			data['Taxable'] = self.taxable
		if len(self.options):
			data['Options'] = []

			for f in self.options:
				data['Options'].append(f.to_dict())
		return data


"""
Handles API Request OrderItem_Update.
Scope: Store.
:see: https://docs.miva.com/json-api/functions/orderitem_update
"""


class OrderItemUpdate(merchantapi.abstract.Request):
	def __init__(self, client: Client = None, order_item: merchantapi.model.OrderItem = None):
		"""
		OrderItemUpdate Constructor.

		:param client: Client
		:param order_item: OrderItem
		"""

		super().__init__(client)
		self.order_id = None
		self.line_id = None
		self.code = None
		self.name = None
		self.sku = None
		self.quantity = None
		self.price = None
		self.weight = None
		self.taxable = False
		self.options = []
		if isinstance(order_item, merchantapi.model.OrderItem):
			self.set_order_id(order_item.get_order_id())
			self.set_line_id(order_item.get_line_id())
			self.set_code(order_item.get_code())
			self.set_name(order_item.get_name())
			self.set_sku(order_item.get_sku())
			self.set_quantity(order_item.get_quantity())
			self.set_price(order_item.get_price())
			self.set_weight(order_item.get_weight())
			self.set_taxable(order_item.get_taxable())

			if len(order_item.get_options()):
				self.options = order_item.get_options()

	def get_function(self):
		"""
		Get the function of the request.

		:returns: str
		"""

		return 'OrderItem_Update'

	def get_order_id(self) -> int:
		"""
		Get Order_ID.

		:returns: int
		"""

		return self.order_id

	def get_line_id(self) -> int:
		"""
		Get Line_ID.

		:returns: int
		"""

		return self.line_id

	def get_code(self) -> str:
		"""
		Get Code.

		:returns: str
		"""

		return self.code

	def get_name(self) -> str:
		"""
		Get Name.

		:returns: str
		"""

		return self.name

	def get_sku(self) -> str:
		"""
		Get Sku.

		:returns: str
		"""

		return self.sku

	def get_quantity(self) -> int:
		"""
		Get Quantity.

		:returns: int
		"""

		return self.quantity

	def get_price(self) -> float:
		"""
		Get Price.

		:returns: float
		"""

		return self.price

	def get_weight(self) -> float:
		"""
		Get Weight.

		:returns: float
		"""

		return self.weight

	def get_taxable(self) -> bool:
		"""
		Get Taxable.

		:returns: bool
		"""

		return self.taxable

	def get_options(self) -> list:
		"""
		Get Options.

		:returns: List of OrderItemOption
		"""

		return self.options

	def set_order_id(self, order_id: int) -> 'OrderItemUpdate':
		"""
		Set Order_ID.

		:param order_id: int
		:returns: OrderItemUpdate
		"""

		self.order_id = order_id
		return self

	def set_line_id(self, line_id: int) -> 'OrderItemUpdate':
		"""
		Set Line_ID.

		:param line_id: int
		:returns: OrderItemUpdate
		"""

		self.line_id = line_id
		return self

	def set_code(self, code: str) -> 'OrderItemUpdate':
		"""
		Set Code.

		:param code: str
		:returns: OrderItemUpdate
		"""

		self.code = code
		return self

	def set_name(self, name: str) -> 'OrderItemUpdate':
		"""
		Set Name.

		:param name: str
		:returns: OrderItemUpdate
		"""

		self.name = name
		return self

	def set_sku(self, sku: str) -> 'OrderItemUpdate':
		"""
		Set Sku.

		:param sku: str
		:returns: OrderItemUpdate
		"""

		self.sku = sku
		return self

	def set_quantity(self, quantity: int) -> 'OrderItemUpdate':
		"""
		Set Quantity.

		:param quantity: int
		:returns: OrderItemUpdate
		"""

		self.quantity = quantity
		return self

	def set_price(self, price: float) -> 'OrderItemUpdate':
		"""
		Set Price.

		:param price: float
		:returns: OrderItemUpdate
		"""

		self.price = price
		return self

	def set_weight(self, weight: float) -> 'OrderItemUpdate':
		"""
		Set Weight.

		:param weight: float
		:returns: OrderItemUpdate
		"""

		self.weight = weight
		return self

	def set_taxable(self, taxable: bool) -> 'OrderItemUpdate':
		"""
		Set Taxable.

		:param taxable: bool
		:returns: OrderItemUpdate
		"""

		self.taxable = taxable
		return self

	def set_options(self, options: list) -> 'OrderItemUpdate':
		"""
		Set Options.

		:param options: {OrderItemOption[]}
		:raises Exception:
		:returns: OrderItemUpdate
		"""

		for e in options:
			if not isinstance(e, merchantapi.model.OrderItemOption):
				raise Exception("")
		self.options = options
		return self

	def add_option(self, option) -> 'OrderItemUpdate':
		"""
		Add Options.

		:param option: OrderItemOption
		:raises Exception:
		:returns: {OrderItemUpdate}
		"""

		if isinstance(option, merchantapi.model.OrderItemOption):
			self.options.append(option)
		elif isinstance(option, dict):
			self.options.append(merchantapi.model.OrderItemOption(option))
		else:
			raise Exception('Expected instance of OrderItemOption or dict')
		return self

	def add_options(self, options: list) -> 'OrderItemUpdate':
		"""
		Add many OrderItemOption.

		:param options: List of OrderItemOption
		:raises Exception:
		:returns: OrderItemUpdate
		"""

		for e in options:
			if not isinstance(e, merchantapi.model.OrderItemOption):
				raise Exception('')
			self.options.append(e)

		return self

	# noinspection PyTypeChecker
	def send(self) -> 'merchantapi.response.OrderItemUpdate':
		return super().send()

	def create_response(self, data) -> 'OrderItemUpdate':
		"""
		Create a response object from the response data

		:param data:
		:returns: Response
		"""

		return merchantapi.response.OrderItemUpdate(self, data)

	def to_dict(self) -> dict:
		"""
		Reduce the request to a dict

		:override:
		:returns: dict
		"""

		data = super().to_dict()

		data['Order_ID'] = self.get_order_id()

		data['Line_ID'] = self.get_line_id()

		if self.code is not None:
			data['Code'] = self.code
		if self.name is not None:
			data['Name'] = self.name
		if self.sku is not None:
			data['Sku'] = self.sku
		if self.quantity is not None:
			data['Quantity'] = self.quantity
		if self.price is not None:
			data['Price'] = self.price
		if self.weight is not None:
			data['Weight'] = self.weight
		if self.taxable is not None:
			data['Taxable'] = self.taxable
		if len(self.options):
			data['Options'] = []

			for f in self.options:
				data['Options'].append(f.to_dict())
		return data


"""
Handles API Request OrderList_Load_Query.
Scope: Store.
:see: https://docs.miva.com/json-api/functions/orderlist_load_query
"""


class OrderListLoadQuery(ListQueryRequest):
	# PAY_STATUS_FILTER constants.
	PAY_STATUS_FILTER_AUTH_ONLY = 'auth_0_capt'
	PAY_STATUS_FILTER_PARTIAL_CAPTURE = 'partial_capt'
	PAY_STATUS_FILTER_CAPTURED_NOT_SHIPPED = 'capt_not_ship'
	PAY_STATUS_FILTER_SHIPPED_NOT_CAPTURED = 'ship_not_capt'

	available_search_fields = [
		'id',
		'batch_id',
		'status',
		'pay_status',
		'orderdate',
		'dt_instock',
		'ship_res',
		'ship_fname',
		'ship_lname',
		'ship_email',
		'ship_comp',
		'ship_phone',
		'ship_fax',
		'ship_addr1',
		'ship_addr2',
		'ship_city',
		'ship_state',
		'ship_zip',
		'ship_cntry',
		'bill_fname',
		'bill_lname',
		'bill_email',
		'bill_comp',
		'bill_phone',
		'bill_fax',
		'bill_addr1',
		'bill_addr2',
		'bill_city',
		'bill_state',
		'bill_zip',
		'bill_cntry',
		'ship_id',
		'ship_data',
		'source',
		'source_id',
		'total',
		'total_ship',
		'total_tax',
		'total_auth',
		'total_capt',
		'total_rfnd',
		'net_capt',
		'pend_count',
		'bord_count',
		'cust_login',
		'cust_pw_email',
		'business_title',
		'note_count'
	]

	available_sort_fields = [
		'id',
		'batch_id',
		'status',
		'pay_status',
		'orderdate',
		'dt_instock',
		'ship_res',
		'ship_fname',
		'ship_lname',
		'ship_email',
		'ship_comp',
		'ship_phone',
		'ship_fax',
		'ship_addr1',
		'ship_addr2',
		'ship_city',
		'ship_state',
		'ship_zip',
		'ship_cntry',
		'bill_fname',
		'bill_lname',
		'bill_email',
		'bill_comp',
		'bill_phone',
		'bill_fax',
		'bill_addr1',
		'bill_addr2',
		'bill_city',
		'bill_state',
		'bill_zip',
		'bill_cntry',
		'ship_data',
		'source',
		'source_id',
		'total',
		'total_ship',
		'total_tax',
		'total_auth',
		'total_capt',
		'total_rfnd',
		'net_capt',
		'pend_count',
		'bord_count',
		'cust_login',
		'cust_pw_email',
		'business_title',
		'note_count',
		'payment_module'
	]

	available_on_demand_columns = [
		'ship_method',
		'cust_login',
		'cust_pw_email',
		'business_title',
		'payment_module',
		'customer',
		'items',
		'charges',
		'coupons',
		'discounts',
		'payments',
		'notes'
	]

	available_custom_filters = {
		'Customer_ID': 'int',
		'BusinessAccount_ID': 'int',
		'pay_id': 'int',
		'payment': [
			PAY_STATUS_FILTER_AUTH_ONLY,
			PAY_STATUS_FILTER_PARTIAL_CAPTURE,
			PAY_STATUS_FILTER_CAPTURED_NOT_SHIPPED,
			PAY_STATUS_FILTER_SHIPPED_NOT_CAPTURED
		],
		'product_code': 'str'
	}

	def __init__(self, client: Client = None):
		"""
		OrderListLoadQuery Constructor.

		:param client: Client
		"""

		super().__init__(client)
		self.passphrase = None

	def get_function(self):
		"""
		Get the function of the request.

		:returns: str
		"""

		return 'OrderList_Load_Query'

	def get_passphrase(self) -> str:
		"""
		Get Passphrase.

		:returns: str
		"""

		return self.passphrase

	def set_passphrase(self, passphrase: str) -> 'OrderListLoadQuery':
		"""
		Set Passphrase.

		:param passphrase: str
		:returns: OrderListLoadQuery
		"""

		self.passphrase = passphrase
		return self

	# noinspection PyTypeChecker
	def send(self) -> 'merchantapi.response.OrderListLoadQuery':
		return super().send()

	def create_response(self, data) -> 'OrderListLoadQuery':
		"""
		Create a response object from the response data

		:param data:
		:returns: Response
		"""

		return merchantapi.response.OrderListLoadQuery(self, data)

	def to_dict(self) -> dict:
		"""
		Reduce the request to a dict

		:override:
		:returns: dict
		"""

		data = super().to_dict()

		if self.passphrase is not None:
			data['Passphrase'] = self.passphrase
		return data


"""
Handles API Request OrderPayment_Capture.
Scope: Store.
:see: https://docs.miva.com/json-api/functions/orderpayment_capture
"""


class OrderPaymentCapture(merchantapi.abstract.Request):
	def __init__(self, client: Client = None, order_payment: merchantapi.model.OrderPayment = None):
		"""
		OrderPaymentCapture Constructor.

		:param client: Client
		:param order_payment: OrderPayment
		"""

		super().__init__(client)
		self.order_payment_id = None
		self.amount = None
		if isinstance(order_payment, merchantapi.model.OrderPayment):
			self.set_order_payment_id(order_payment.get_id())

	def get_function(self):
		"""
		Get the function of the request.

		:returns: str
		"""

		return 'OrderPayment_Capture'

	def get_order_payment_id(self) -> int:
		"""
		Get OrderPayment_ID.

		:returns: int
		"""

		return self.order_payment_id

	def get_amount(self) -> float:
		"""
		Get Amount.

		:returns: float
		"""

		return self.amount

	def set_order_payment_id(self, order_payment_id: int) -> 'OrderPaymentCapture':
		"""
		Set OrderPayment_ID.

		:param order_payment_id: int
		:returns: OrderPaymentCapture
		"""

		self.order_payment_id = order_payment_id
		return self

	def set_amount(self, amount: float) -> 'OrderPaymentCapture':
		"""
		Set Amount.

		:param amount: float
		:returns: OrderPaymentCapture
		"""

		self.amount = amount
		return self

	# noinspection PyTypeChecker
	def send(self) -> 'merchantapi.response.OrderPaymentCapture':
		return super().send()

	def create_response(self, data) -> 'OrderPaymentCapture':
		"""
		Create a response object from the response data

		:param data:
		:returns: Response
		"""

		return merchantapi.response.OrderPaymentCapture(self, data)

	def to_dict(self) -> dict:
		"""
		Reduce the request to a dict

		:override:
		:returns: dict
		"""

		data = super().to_dict()

		data['OrderPayment_ID'] = self.order_payment_id
		if self.amount is not None:
			data['Amount'] = self.amount
		return data


"""
Handles API Request OrderPayment_Refund.
Scope: Store.
:see: https://docs.miva.com/json-api/functions/orderpayment_refund
"""


class OrderPaymentRefund(merchantapi.abstract.Request):
	def __init__(self, client: Client = None, order_payment: merchantapi.model.OrderPayment = None):
		"""
		OrderPaymentRefund Constructor.

		:param client: Client
		:param order_payment: OrderPayment
		"""

		super().__init__(client)
		self.order_payment_id = None
		self.amount = None
		if isinstance(order_payment, merchantapi.model.OrderPayment):
			self.set_order_payment_id(order_payment.get_id())

	def get_function(self):
		"""
		Get the function of the request.

		:returns: str
		"""

		return 'OrderPayment_Refund'

	def get_order_payment_id(self) -> int:
		"""
		Get OrderPayment_ID.

		:returns: int
		"""

		return self.order_payment_id

	def get_amount(self) -> float:
		"""
		Get Amount.

		:returns: float
		"""

		return self.amount

	def set_order_payment_id(self, order_payment_id: int) -> 'OrderPaymentRefund':
		"""
		Set OrderPayment_ID.

		:param order_payment_id: int
		:returns: OrderPaymentRefund
		"""

		self.order_payment_id = order_payment_id
		return self

	def set_amount(self, amount: float) -> 'OrderPaymentRefund':
		"""
		Set Amount.

		:param amount: float
		:returns: OrderPaymentRefund
		"""

		self.amount = amount
		return self

	# noinspection PyTypeChecker
	def send(self) -> 'merchantapi.response.OrderPaymentRefund':
		return super().send()

	def create_response(self, data) -> 'OrderPaymentRefund':
		"""
		Create a response object from the response data

		:param data:
		:returns: Response
		"""

		return merchantapi.response.OrderPaymentRefund(self, data)

	def to_dict(self) -> dict:
		"""
		Reduce the request to a dict

		:override:
		:returns: dict
		"""

		data = super().to_dict()

		data['OrderPayment_ID'] = self.order_payment_id
		if self.amount is not None:
			data['Amount'] = self.amount
		return data


"""
Handles API Request OrderPayment_VOID.
Scope: Store.
:see: https://docs.miva.com/json-api/functions/orderpayment_void
"""


class OrderPaymentVoid(merchantapi.abstract.Request):
	def __init__(self, client: Client = None, order_payment: merchantapi.model.OrderPayment = None):
		"""
		OrderPaymentVoid Constructor.

		:param client: Client
		:param order_payment: OrderPayment
		"""

		super().__init__(client)
		self.order_payment_id = None
		self.amount = None
		if isinstance(order_payment, merchantapi.model.OrderPayment):
			self.set_order_payment_id(order_payment.get_id())

	def get_function(self):
		"""
		Get the function of the request.

		:returns: str
		"""

		return 'OrderPayment_VOID'

	def get_order_payment_id(self) -> int:
		"""
		Get OrderPayment_ID.

		:returns: int
		"""

		return self.order_payment_id

	def get_amount(self) -> float:
		"""
		Get Amount.

		:returns: float
		"""

		return self.amount

	def set_order_payment_id(self, order_payment_id: int) -> 'OrderPaymentVoid':
		"""
		Set OrderPayment_ID.

		:param order_payment_id: int
		:returns: OrderPaymentVoid
		"""

		self.order_payment_id = order_payment_id
		return self

	def set_amount(self, amount: float) -> 'OrderPaymentVoid':
		"""
		Set Amount.

		:param amount: float
		:returns: OrderPaymentVoid
		"""

		self.amount = amount
		return self

	# noinspection PyTypeChecker
	def send(self) -> 'merchantapi.response.OrderPaymentVoid':
		return super().send()

	def create_response(self, data) -> 'OrderPaymentVoid':
		"""
		Create a response object from the response data

		:param data:
		:returns: Response
		"""

		return merchantapi.response.OrderPaymentVoid(self, data)

	def to_dict(self) -> dict:
		"""
		Reduce the request to a dict

		:override:
		:returns: dict
		"""

		data = super().to_dict()

		data['OrderPayment_ID'] = self.order_payment_id
		if self.amount is not None:
			data['Amount'] = self.amount
		return data


"""
Handles API Request OrderShipmentList_Update.
Scope: Store.
:see: https://docs.miva.com/json-api/functions/ordershipmentlist_update
"""


class OrderShipmentListUpdate(merchantapi.abstract.Request):
	def __init__(self, client: Client = None):
		"""
		OrderShipmentListUpdate Constructor.

		:param client: Client
		"""

		super().__init__(client)
		self.shipment_updates = []

	def get_function(self):
		"""
		Get the function of the request.

		:returns: str
		"""

		return 'OrderShipmentList_Update'

	def get_shipment_updates(self) -> list:
		"""
		Get Shipment_Updates.

		:returns: List of OrderShipmentUpdate
		"""

		return self.shipment_updates

	def set_shipment_updates(self, shipment_updates: list) -> 'OrderShipmentListUpdate':
		"""
		Set Shipment_Updates.

		:param shipment_updates: {OrderShipmentUpdate[]}
		:raises Exception:
		:returns: OrderShipmentListUpdate
		"""

		for e in shipment_updates:
			if not isinstance(e, merchantapi.model.OrderShipmentUpdate):
				raise Exception("")
		self.shipment_updates = shipment_updates
		return self

	def add_shipment_update(self, shipment_update) -> 'OrderShipmentListUpdate':
		"""
		Add Shipment_Updates.

		:param shipment_update: OrderShipmentUpdate
		:raises Exception:
		:returns: {OrderShipmentListUpdate}
		"""

		if isinstance(shipment_update, merchantapi.model.OrderShipmentUpdate):
			self.shipment_updates.append(shipment_update)
		elif isinstance(shipment_update, dict):
			self.shipment_updates.append(merchantapi.model.OrderShipmentUpdate(shipment_update))
		else:
			raise Exception('Expected instance of OrderShipmentUpdate or dict')
		return self

	def add_shipment_updates(self, shipment_updates: list) -> 'OrderShipmentListUpdate':
		"""
		Add many OrderShipmentUpdate.

		:param shipment_updates: List of OrderShipmentUpdate
		:raises Exception:
		:returns: OrderShipmentListUpdate
		"""

		for e in shipment_updates:
			if not isinstance(e, merchantapi.model.OrderShipmentUpdate):
				raise Exception('')
			self.shipment_updates.append(e)

		return self

	# noinspection PyTypeChecker
	def send(self) -> 'merchantapi.response.OrderShipmentListUpdate':
		return super().send()

	def create_response(self, data) -> 'OrderShipmentListUpdate':
		"""
		Create a response object from the response data

		:param data:
		:returns: Response
		"""

		return merchantapi.response.OrderShipmentListUpdate(self, data)

	def to_dict(self) -> dict:
		"""
		Reduce the request to a dict

		:override:
		:returns: dict
		"""

		data = super().to_dict()

		if len(self.shipment_updates):
			data['Shipment_Updates'] = []

			for f in self.shipment_updates:
				data['Shipment_Updates'].append(f.to_dict())
		return data


"""
Handles API Request Order_Create.
Scope: Store.
:see: https://docs.miva.com/json-api/functions/order_create
"""


class OrderCreate(merchantapi.abstract.Request):
	def __init__(self, client: Client = None, customer: merchantapi.model.Customer = None):
		"""
		OrderCreate Constructor.

		:param client: Client
		:param customer: Customer
		"""

		super().__init__(client)
		self.customer_login = None
		self.customer_id = None
		self.ship_first_name = None
		self.ship_last_name = None
		self.ship_email = None
		self.ship_phone = None
		self.ship_fax = None
		self.ship_company = None
		self.ship_address1 = None
		self.ship_address2 = None
		self.ship_city = None
		self.ship_state = None
		self.ship_zip = None
		self.ship_country = None
		self.ship_residential = False
		self.bill_first_name = None
		self.bill_last_name = None
		self.bill_email = None
		self.bill_phone = None
		self.bill_fax = None
		self.bill_company = None
		self.bill_address1 = None
		self.bill_address2 = None
		self.bill_city = None
		self.bill_state = None
		self.bill_zip = None
		self.bill_country = None
		self.items = []
		self.products = []
		self.charges = []
		self.custom_field_values = merchantapi.model.CustomFieldValues()
		self.shipping_module_code = None
		self.shipping_module_data = None
		self.calculate_charges = False
		self.trigger_fulfillment_modules = False
		if isinstance(customer, merchantapi.model.Customer):
			if customer.get_id():
				self.set_customer_id(customer.get_id())
			elif customer.get_login():
				self.set_customer_login(customer.get_login())

	def get_function(self):
		"""
		Get the function of the request.

		:returns: str
		"""

		return 'Order_Create'

	def get_customer_login(self) -> str:
		"""
		Get Customer_Login.

		:returns: str
		"""

		return self.customer_login

	def get_customer_id(self) -> int:
		"""
		Get Customer_ID.

		:returns: int
		"""

		return self.customer_id

	def get_ship_first_name(self) -> str:
		"""
		Get ShipFirstName.

		:returns: str
		"""

		return self.ship_first_name

	def get_ship_last_name(self) -> str:
		"""
		Get ShipLastName.

		:returns: str
		"""

		return self.ship_last_name

	def get_ship_email(self) -> str:
		"""
		Get ShipEmail.

		:returns: str
		"""

		return self.ship_email

	def get_ship_phone(self) -> str:
		"""
		Get ShipPhone.

		:returns: str
		"""

		return self.ship_phone

	def get_ship_fax(self) -> str:
		"""
		Get ShipFax.

		:returns: str
		"""

		return self.ship_fax

	def get_ship_company(self) -> str:
		"""
		Get ShipCompany.

		:returns: str
		"""

		return self.ship_company

	def get_ship_address1(self) -> str:
		"""
		Get ShipAddress1.

		:returns: str
		"""

		return self.ship_address1

	def get_ship_address2(self) -> str:
		"""
		Get ShipAddress2.

		:returns: str
		"""

		return self.ship_address2

	def get_ship_city(self) -> str:
		"""
		Get ShipCity.

		:returns: str
		"""

		return self.ship_city

	def get_ship_state(self) -> str:
		"""
		Get ShipState.

		:returns: str
		"""

		return self.ship_state

	def get_ship_zip(self) -> str:
		"""
		Get ShipZip.

		:returns: str
		"""

		return self.ship_zip

	def get_ship_country(self) -> str:
		"""
		Get ShipCountry.

		:returns: str
		"""

		return self.ship_country

	def get_ship_residential(self) -> bool:
		"""
		Get ShipResidential.

		:returns: bool
		"""

		return self.ship_residential

	def get_bill_first_name(self) -> str:
		"""
		Get BillFirstName.

		:returns: str
		"""

		return self.bill_first_name

	def get_bill_last_name(self) -> str:
		"""
		Get BillLastName.

		:returns: str
		"""

		return self.bill_last_name

	def get_bill_email(self) -> str:
		"""
		Get BillEmail.

		:returns: str
		"""

		return self.bill_email

	def get_bill_phone(self) -> str:
		"""
		Get BillPhone.

		:returns: str
		"""

		return self.bill_phone

	def get_bill_fax(self) -> str:
		"""
		Get BillFax.

		:returns: str
		"""

		return self.bill_fax

	def get_bill_company(self) -> str:
		"""
		Get BillCompany.

		:returns: str
		"""

		return self.bill_company

	def get_bill_address1(self) -> str:
		"""
		Get BillAddress1.

		:returns: str
		"""

		return self.bill_address1

	def get_bill_address2(self) -> str:
		"""
		Get BillAddress2.

		:returns: str
		"""

		return self.bill_address2

	def get_bill_city(self) -> str:
		"""
		Get BillCity.

		:returns: str
		"""

		return self.bill_city

	def get_bill_state(self) -> str:
		"""
		Get BillState.

		:returns: str
		"""

		return self.bill_state

	def get_bill_zip(self) -> str:
		"""
		Get BillZip.

		:returns: str
		"""

		return self.bill_zip

	def get_bill_country(self) -> str:
		"""
		Get BillCountry.

		:returns: str
		"""

		return self.bill_country

	def get_items(self) -> list:
		"""
		Get Items.

		:returns: List of OrderItem
		"""

		return self.items

	def get_products(self) -> list:
		"""
		Get Products.

		:returns: List of OrderProduct
		"""

		return self.products

	def get_charges(self) -> list:
		"""
		Get Charges.

		:returns: List of OrderCharge
		"""

		return self.charges

	def get_custom_field_values(self) -> merchantapi.model.CustomFieldValues:
		"""
		Get CustomField_Values.

		:returns: CustomFieldValues}|None
		"""

		return self.custom_field_values

	def get_shipping_module_code(self) -> str:
		"""
		Get Shipping_Module_Code.

		:returns: str
		"""

		return self.shipping_module_code

	def get_shipping_module_data(self) -> str:
		"""
		Get Shipping_Module_Data.

		:returns: str
		"""

		return self.shipping_module_data

	def get_calculate_charges(self) -> bool:
		"""
		Get CalculateCharges.

		:returns: bool
		"""

		return self.calculate_charges

	def get_trigger_fulfillment_modules(self) -> bool:
		"""
		Get TriggerFulfillmentModules.

		:returns: bool
		"""

		return self.trigger_fulfillment_modules

	def set_customer_login(self, customer_login: str) -> 'OrderCreate':
		"""
		Set Customer_Login.

		:param customer_login: str
		:returns: OrderCreate
		"""

		self.customer_login = customer_login
		return self

	def set_customer_id(self, customer_id: int) -> 'OrderCreate':
		"""
		Set Customer_ID.

		:param customer_id: int
		:returns: OrderCreate
		"""

		self.customer_id = customer_id
		return self

	def set_ship_first_name(self, ship_first_name: str) -> 'OrderCreate':
		"""
		Set ShipFirstName.

		:param ship_first_name: str
		:returns: OrderCreate
		"""

		self.ship_first_name = ship_first_name
		return self

	def set_ship_last_name(self, ship_last_name: str) -> 'OrderCreate':
		"""
		Set ShipLastName.

		:param ship_last_name: str
		:returns: OrderCreate
		"""

		self.ship_last_name = ship_last_name
		return self

	def set_ship_email(self, ship_email: str) -> 'OrderCreate':
		"""
		Set ShipEmail.

		:param ship_email: str
		:returns: OrderCreate
		"""

		self.ship_email = ship_email
		return self

	def set_ship_phone(self, ship_phone: str) -> 'OrderCreate':
		"""
		Set ShipPhone.

		:param ship_phone: str
		:returns: OrderCreate
		"""

		self.ship_phone = ship_phone
		return self

	def set_ship_fax(self, ship_fax: str) -> 'OrderCreate':
		"""
		Set ShipFax.

		:param ship_fax: str
		:returns: OrderCreate
		"""

		self.ship_fax = ship_fax
		return self

	def set_ship_company(self, ship_company: str) -> 'OrderCreate':
		"""
		Set ShipCompany.

		:param ship_company: str
		:returns: OrderCreate
		"""

		self.ship_company = ship_company
		return self

	def set_ship_address1(self, ship_address1: str) -> 'OrderCreate':
		"""
		Set ShipAddress1.

		:param ship_address1: str
		:returns: OrderCreate
		"""

		self.ship_address1 = ship_address1
		return self

	def set_ship_address2(self, ship_address2: str) -> 'OrderCreate':
		"""
		Set ShipAddress2.

		:param ship_address2: str
		:returns: OrderCreate
		"""

		self.ship_address2 = ship_address2
		return self

	def set_ship_city(self, ship_city: str) -> 'OrderCreate':
		"""
		Set ShipCity.

		:param ship_city: str
		:returns: OrderCreate
		"""

		self.ship_city = ship_city
		return self

	def set_ship_state(self, ship_state: str) -> 'OrderCreate':
		"""
		Set ShipState.

		:param ship_state: str
		:returns: OrderCreate
		"""

		self.ship_state = ship_state
		return self

	def set_ship_zip(self, ship_zip: str) -> 'OrderCreate':
		"""
		Set ShipZip.

		:param ship_zip: str
		:returns: OrderCreate
		"""

		self.ship_zip = ship_zip
		return self

	def set_ship_country(self, ship_country: str) -> 'OrderCreate':
		"""
		Set ShipCountry.

		:param ship_country: str
		:returns: OrderCreate
		"""

		self.ship_country = ship_country
		return self

	def set_ship_residential(self, ship_residential: bool) -> 'OrderCreate':
		"""
		Set ShipResidential.

		:param ship_residential: bool
		:returns: OrderCreate
		"""

		self.ship_residential = ship_residential
		return self

	def set_bill_first_name(self, bill_first_name: str) -> 'OrderCreate':
		"""
		Set BillFirstName.

		:param bill_first_name: str
		:returns: OrderCreate
		"""

		self.bill_first_name = bill_first_name
		return self

	def set_bill_last_name(self, bill_last_name: str) -> 'OrderCreate':
		"""
		Set BillLastName.

		:param bill_last_name: str
		:returns: OrderCreate
		"""

		self.bill_last_name = bill_last_name
		return self

	def set_bill_email(self, bill_email: str) -> 'OrderCreate':
		"""
		Set BillEmail.

		:param bill_email: str
		:returns: OrderCreate
		"""

		self.bill_email = bill_email
		return self

	def set_bill_phone(self, bill_phone: str) -> 'OrderCreate':
		"""
		Set BillPhone.

		:param bill_phone: str
		:returns: OrderCreate
		"""

		self.bill_phone = bill_phone
		return self

	def set_bill_fax(self, bill_fax: str) -> 'OrderCreate':
		"""
		Set BillFax.

		:param bill_fax: str
		:returns: OrderCreate
		"""

		self.bill_fax = bill_fax
		return self

	def set_bill_company(self, bill_company: str) -> 'OrderCreate':
		"""
		Set BillCompany.

		:param bill_company: str
		:returns: OrderCreate
		"""

		self.bill_company = bill_company
		return self

	def set_bill_address1(self, bill_address1: str) -> 'OrderCreate':
		"""
		Set BillAddress1.

		:param bill_address1: str
		:returns: OrderCreate
		"""

		self.bill_address1 = bill_address1
		return self

	def set_bill_address2(self, bill_address2: str) -> 'OrderCreate':
		"""
		Set BillAddress2.

		:param bill_address2: str
		:returns: OrderCreate
		"""

		self.bill_address2 = bill_address2
		return self

	def set_bill_city(self, bill_city: str) -> 'OrderCreate':
		"""
		Set BillCity.

		:param bill_city: str
		:returns: OrderCreate
		"""

		self.bill_city = bill_city
		return self

	def set_bill_state(self, bill_state: str) -> 'OrderCreate':
		"""
		Set BillState.

		:param bill_state: str
		:returns: OrderCreate
		"""

		self.bill_state = bill_state
		return self

	def set_bill_zip(self, bill_zip: str) -> 'OrderCreate':
		"""
		Set BillZip.

		:param bill_zip: str
		:returns: OrderCreate
		"""

		self.bill_zip = bill_zip
		return self

	def set_bill_country(self, bill_country: str) -> 'OrderCreate':
		"""
		Set BillCountry.

		:param bill_country: str
		:returns: OrderCreate
		"""

		self.bill_country = bill_country
		return self

	def set_items(self, items: list) -> 'OrderCreate':
		"""
		Set Items.

		:param items: {OrderItem[]}
		:raises Exception:
		:returns: OrderCreate
		"""

		for e in items:
			if not isinstance(e, merchantapi.model.OrderItem):
				raise Exception("")
		self.items = items
		return self

	def set_products(self, products: list) -> 'OrderCreate':
		"""
		Set Products.

		:param products: {OrderProduct[]}
		:raises Exception:
		:returns: OrderCreate
		"""

		for e in products:
			if not isinstance(e, merchantapi.model.OrderProduct):
				raise Exception("")
		self.products = products
		return self

	def set_charges(self, charges: list) -> 'OrderCreate':
		"""
		Set Charges.

		:param charges: {OrderCharge[]}
		:raises Exception:
		:returns: OrderCreate
		"""

		for e in charges:
			if not isinstance(e, merchantapi.model.OrderCharge):
				raise Exception("")
		self.charges = charges
		return self

	def set_custom_field_values(self, custom_field_values: merchantapi.model.CustomFieldValues) -> 'OrderCreate':
		"""
		Set CustomField_Values.

		:param custom_field_values: CustomFieldValues}|None
		:raises Exception:
		:returns: OrderCreate
		"""

		if not isinstance(custom_field_values, merchantapi.model.CustomFieldValues):
			raise Exception("")
		self.custom_field_values = custom_field_values
		return self

	def set_shipping_module_code(self, shipping_module_code: str) -> 'OrderCreate':
		"""
		Set Shipping_Module_Code.

		:param shipping_module_code: str
		:returns: OrderCreate
		"""

		self.shipping_module_code = shipping_module_code
		return self

	def set_shipping_module_data(self, shipping_module_data: str) -> 'OrderCreate':
		"""
		Set Shipping_Module_Data.

		:param shipping_module_data: str
		:returns: OrderCreate
		"""

		self.shipping_module_data = shipping_module_data
		return self

	def set_calculate_charges(self, calculate_charges: bool) -> 'OrderCreate':
		"""
		Set CalculateCharges.

		:param calculate_charges: bool
		:returns: OrderCreate
		"""

		self.calculate_charges = calculate_charges
		return self

	def set_trigger_fulfillment_modules(self, trigger_fulfillment_modules: bool) -> 'OrderCreate':
		"""
		Set TriggerFulfillmentModules.

		:param trigger_fulfillment_modules: bool
		:returns: OrderCreate
		"""

		self.trigger_fulfillment_modules = trigger_fulfillment_modules
		return self

	def add_item(self, item) -> 'OrderCreate':
		"""
		Add Items.

		:param item: OrderItem
		:raises Exception:
		:returns: {OrderCreate}
		"""

		if isinstance(item, merchantapi.model.OrderItem):
			self.items.append(item)
		elif isinstance(item, dict):
			self.items.append(merchantapi.model.OrderItem(item))
		else:
			raise Exception('Expected instance of OrderItem or dict')
		return self

	def add_items(self, items: list) -> 'OrderCreate':
		"""
		Add many OrderItem.

		:param items: List of OrderItem
		:raises Exception:
		:returns: OrderCreate
		"""

		for e in items:
			if not isinstance(e, merchantapi.model.OrderItem):
				raise Exception('')
			self.items.append(e)

		return self

	def add_product(self, product) -> 'OrderCreate':
		"""
		Add Products.

		:param product: OrderProduct
		:raises Exception:
		:returns: {OrderCreate}
		"""

		if isinstance(product, merchantapi.model.OrderProduct):
			self.products.append(product)
		elif isinstance(product, dict):
			self.products.append(merchantapi.model.OrderProduct(product))
		else:
			raise Exception('Expected instance of OrderProduct or dict')
		return self

	def add_products(self, products: list) -> 'OrderCreate':
		"""
		Add many OrderProduct.

		:param products: List of OrderProduct
		:raises Exception:
		:returns: OrderCreate
		"""

		for e in products:
			if not isinstance(e, merchantapi.model.OrderProduct):
				raise Exception('')
			self.products.append(e)

		return self

	def add_charge(self, charge) -> 'OrderCreate':
		"""
		Add Charges.

		:param charge: OrderCharge
		:raises Exception:
		:returns: {OrderCreate}
		"""

		if isinstance(charge, merchantapi.model.OrderCharge):
			self.charges.append(charge)
		elif isinstance(charge, dict):
			self.charges.append(merchantapi.model.OrderCharge(charge))
		else:
			raise Exception('Expected instance of OrderCharge or dict')
		return self

	def add_charges(self, charges: list) -> 'OrderCreate':
		"""
		Add many OrderCharge.

		:param charges: List of OrderCharge
		:raises Exception:
		:returns: OrderCreate
		"""

		for e in charges:
			if not isinstance(e, merchantapi.model.OrderCharge):
				raise Exception('')
			self.charges.append(e)

		return self

	# noinspection PyTypeChecker
	def send(self) -> 'merchantapi.response.OrderCreate':
		return super().send()

	def create_response(self, data) -> 'OrderCreate':
		"""
		Create a response object from the response data

		:param data:
		:returns: Response
		"""

		return merchantapi.response.OrderCreate(self, data)

	def to_dict(self) -> dict:
		"""
		Reduce the request to a dict

		:override:
		:returns: dict
		"""

		data = super().to_dict()

		if self.customer_id is not None:
			data['Customer_ID'] = self.customer_id
		elif self.customer_login is not None:
			data['Customer_Login'] = self.customer_login

		if self.ship_first_name is not None:
			data['ShipFirstName'] = self.ship_first_name
		if self.ship_last_name is not None:
			data['ShipLastName'] = self.ship_last_name
		if self.ship_email is not None:
			data['ShipEmail'] = self.ship_email
		if self.ship_phone is not None:
			data['ShipPhone'] = self.ship_phone
		if self.ship_fax is not None:
			data['ShipFax'] = self.ship_fax
		if self.ship_company is not None:
			data['ShipCompany'] = self.ship_company
		if self.ship_address1 is not None:
			data['ShipAddress1'] = self.ship_address1
		if self.ship_address2 is not None:
			data['ShipAddress2'] = self.ship_address2
		if self.ship_city is not None:
			data['ShipCity'] = self.ship_city
		if self.ship_state is not None:
			data['ShipState'] = self.ship_state
		if self.ship_zip is not None:
			data['ShipZip'] = self.ship_zip
		if self.ship_country is not None:
			data['ShipCountry'] = self.ship_country
		if self.ship_residential is not None:
			data['ShipResidential'] = self.ship_residential
		if self.bill_first_name is not None:
			data['BillFirstName'] = self.bill_first_name
		if self.bill_last_name is not None:
			data['BillLastName'] = self.bill_last_name
		if self.bill_email is not None:
			data['BillEmail'] = self.bill_email
		if self.bill_phone is not None:
			data['BillPhone'] = self.bill_phone
		if self.bill_fax is not None:
			data['BillFax'] = self.bill_fax
		if self.bill_company is not None:
			data['BillCompany'] = self.bill_company
		if self.bill_address1 is not None:
			data['BillAddress1'] = self.bill_address1
		if self.bill_address2 is not None:
			data['BillAddress2'] = self.bill_address2
		if self.bill_city is not None:
			data['BillCity'] = self.bill_city
		if self.bill_state is not None:
			data['BillState'] = self.bill_state
		if self.bill_zip is not None:
			data['BillZip'] = self.bill_zip
		if self.bill_country is not None:
			data['BillCountry'] = self.bill_country
		if len(self.items):
			data['Items'] = []

			for f in self.items:
				data['Items'].append(f.to_dict())
		if len(self.products):
			data['Products'] = []

			for f in self.products:
				data['Products'].append(f.to_dict())
		if len(self.charges):
			data['Charges'] = []

			for f in self.charges:
				data['Charges'].append(f.to_dict())
		if self.custom_field_values is not None:
			data['CustomField_Values'] = self.custom_field_values.to_dict()
		if self.shipping_module_code is not None:
			data['Shipping_Module_Code'] = self.shipping_module_code
		if self.shipping_module_data is not None:
			data['Shipping_Module_Data'] = self.shipping_module_data
		if self.calculate_charges is not None:
			data['CalculateCharges'] = self.calculate_charges
		if self.trigger_fulfillment_modules is not None:
			data['TriggerFulfillmentModules'] = self.trigger_fulfillment_modules
		return data


"""
Handles API Request Order_Delete.
Scope: Store.
:see: https://docs.miva.com/json-api/functions/order_delete
"""


class OrderDelete(merchantapi.abstract.Request):
	def __init__(self, client: Client = None, order: merchantapi.model.Order = None):
		"""
		OrderDelete Constructor.

		:param client: Client
		:param order: Order
		"""

		super().__init__(client)
		self.order_id = None
		if isinstance(order, merchantapi.model.Order):
			self.set_order_id(order.get_id())

	def get_function(self):
		"""
		Get the function of the request.

		:returns: str
		"""

		return 'Order_Delete'

	def get_order_id(self) -> int:
		"""
		Get Order_ID.

		:returns: int
		"""

		return self.order_id

	def set_order_id(self, order_id: int) -> 'OrderDelete':
		"""
		Set Order_ID.

		:param order_id: int
		:returns: OrderDelete
		"""

		self.order_id = order_id
		return self

	# noinspection PyTypeChecker
	def send(self) -> 'merchantapi.response.OrderDelete':
		return super().send()

	def create_response(self, data) -> 'OrderDelete':
		"""
		Create a response object from the response data

		:param data:
		:returns: Response
		"""

		return merchantapi.response.OrderDelete(self, data)

	def to_dict(self) -> dict:
		"""
		Reduce the request to a dict

		:override:
		:returns: dict
		"""

		data = super().to_dict()

		data['Order_ID'] = self.order_id
		return data


"""
Handles API Request Order_Update_Customer_Information.
Scope: Store.
:see: https://docs.miva.com/json-api/functions/order_update_customer_information
"""


class OrderUpdateCustomerInformation(merchantapi.abstract.Request):
	def __init__(self, client: Client = None, order: merchantapi.model.Order = None):
		"""
		OrderUpdateCustomerInformation Constructor.

		:param client: Client
		:param order: Order
		"""

		super().__init__(client)
		self.order_id = None
		self.customer_id = None
		self.ship_residential = False
		self.ship_first_name = None
		self.ship_last_name = None
		self.ship_email = None
		self.ship_phone = None
		self.ship_fax = None
		self.ship_company = None
		self.ship_address1 = None
		self.ship_address2 = None
		self.ship_city = None
		self.ship_state = None
		self.ship_zip = None
		self.ship_country = None
		self.bill_first_name = None
		self.bill_last_name = None
		self.bill_email = None
		self.bill_phone = None
		self.bill_fax = None
		self.bill_company = None
		self.bill_address1 = None
		self.bill_address2 = None
		self.bill_city = None
		self.bill_state = None
		self.bill_zip = None
		self.bill_country = None
		if isinstance(order, merchantapi.model.Order):
			self.set_order_id(order.get_id())

	def get_function(self):
		"""
		Get the function of the request.

		:returns: str
		"""

		return 'Order_Update_Customer_Information'

	def get_order_id(self) -> int:
		"""
		Get Order_ID.

		:returns: int
		"""

		return self.order_id

	def get_customer_id(self) -> int:
		"""
		Get Customer_ID.

		:returns: int
		"""

		return self.customer_id

	def get_ship_residential(self) -> bool:
		"""
		Get Ship_Residential.

		:returns: bool
		"""

		return self.ship_residential

	def get_ship_first_name(self) -> str:
		"""
		Get Ship_FirstName.

		:returns: str
		"""

		return self.ship_first_name

	def get_ship_last_name(self) -> str:
		"""
		Get Ship_LastName.

		:returns: str
		"""

		return self.ship_last_name

	def get_ship_email(self) -> str:
		"""
		Get Ship_Email.

		:returns: str
		"""

		return self.ship_email

	def get_ship_phone(self) -> str:
		"""
		Get Ship_Phone.

		:returns: str
		"""

		return self.ship_phone

	def get_ship_fax(self) -> str:
		"""
		Get Ship_Fax.

		:returns: str
		"""

		return self.ship_fax

	def get_ship_company(self) -> str:
		"""
		Get Ship_Company.

		:returns: str
		"""

		return self.ship_company

	def get_ship_address1(self) -> str:
		"""
		Get Ship_Address1.

		:returns: str
		"""

		return self.ship_address1

	def get_ship_address2(self) -> str:
		"""
		Get Ship_Address2.

		:returns: str
		"""

		return self.ship_address2

	def get_ship_city(self) -> str:
		"""
		Get Ship_City.

		:returns: str
		"""

		return self.ship_city

	def get_ship_state(self) -> str:
		"""
		Get Ship_State.

		:returns: str
		"""

		return self.ship_state

	def get_ship_zip(self) -> str:
		"""
		Get Ship_Zip.

		:returns: str
		"""

		return self.ship_zip

	def get_ship_country(self) -> str:
		"""
		Get Ship_Country.

		:returns: str
		"""

		return self.ship_country

	def get_bill_first_name(self) -> str:
		"""
		Get Bill_FirstName.

		:returns: str
		"""

		return self.bill_first_name

	def get_bill_last_name(self) -> str:
		"""
		Get Bill_LastName.

		:returns: str
		"""

		return self.bill_last_name

	def get_bill_email(self) -> str:
		"""
		Get Bill_Email.

		:returns: str
		"""

		return self.bill_email

	def get_bill_phone(self) -> str:
		"""
		Get Bill_Phone.

		:returns: str
		"""

		return self.bill_phone

	def get_bill_fax(self) -> str:
		"""
		Get Bill_Fax.

		:returns: str
		"""

		return self.bill_fax

	def get_bill_company(self) -> str:
		"""
		Get Bill_Company.

		:returns: str
		"""

		return self.bill_company

	def get_bill_address1(self) -> str:
		"""
		Get Bill_Address1.

		:returns: str
		"""

		return self.bill_address1

	def get_bill_address2(self) -> str:
		"""
		Get Bill_Address2.

		:returns: str
		"""

		return self.bill_address2

	def get_bill_city(self) -> str:
		"""
		Get Bill_City.

		:returns: str
		"""

		return self.bill_city

	def get_bill_state(self) -> str:
		"""
		Get Bill_State.

		:returns: str
		"""

		return self.bill_state

	def get_bill_zip(self) -> str:
		"""
		Get Bill_Zip.

		:returns: str
		"""

		return self.bill_zip

	def get_bill_country(self) -> str:
		"""
		Get Bill_Country.

		:returns: str
		"""

		return self.bill_country

	def set_order_id(self, order_id: int) -> 'OrderUpdateCustomerInformation':
		"""
		Set Order_ID.

		:param order_id: int
		:returns: OrderUpdateCustomerInformation
		"""

		self.order_id = order_id
		return self

	def set_customer_id(self, customer_id: int) -> 'OrderUpdateCustomerInformation':
		"""
		Set Customer_ID.

		:param customer_id: int
		:returns: OrderUpdateCustomerInformation
		"""

		self.customer_id = customer_id
		return self

	def set_ship_residential(self, ship_residential: bool) -> 'OrderUpdateCustomerInformation':
		"""
		Set Ship_Residential.

		:param ship_residential: bool
		:returns: OrderUpdateCustomerInformation
		"""

		self.ship_residential = ship_residential
		return self

	def set_ship_first_name(self, ship_first_name: str) -> 'OrderUpdateCustomerInformation':
		"""
		Set Ship_FirstName.

		:param ship_first_name: str
		:returns: OrderUpdateCustomerInformation
		"""

		self.ship_first_name = ship_first_name
		return self

	def set_ship_last_name(self, ship_last_name: str) -> 'OrderUpdateCustomerInformation':
		"""
		Set Ship_LastName.

		:param ship_last_name: str
		:returns: OrderUpdateCustomerInformation
		"""

		self.ship_last_name = ship_last_name
		return self

	def set_ship_email(self, ship_email: str) -> 'OrderUpdateCustomerInformation':
		"""
		Set Ship_Email.

		:param ship_email: str
		:returns: OrderUpdateCustomerInformation
		"""

		self.ship_email = ship_email
		return self

	def set_ship_phone(self, ship_phone: str) -> 'OrderUpdateCustomerInformation':
		"""
		Set Ship_Phone.

		:param ship_phone: str
		:returns: OrderUpdateCustomerInformation
		"""

		self.ship_phone = ship_phone
		return self

	def set_ship_fax(self, ship_fax: str) -> 'OrderUpdateCustomerInformation':
		"""
		Set Ship_Fax.

		:param ship_fax: str
		:returns: OrderUpdateCustomerInformation
		"""

		self.ship_fax = ship_fax
		return self

	def set_ship_company(self, ship_company: str) -> 'OrderUpdateCustomerInformation':
		"""
		Set Ship_Company.

		:param ship_company: str
		:returns: OrderUpdateCustomerInformation
		"""

		self.ship_company = ship_company
		return self

	def set_ship_address1(self, ship_address1: str) -> 'OrderUpdateCustomerInformation':
		"""
		Set Ship_Address1.

		:param ship_address1: str
		:returns: OrderUpdateCustomerInformation
		"""

		self.ship_address1 = ship_address1
		return self

	def set_ship_address2(self, ship_address2: str) -> 'OrderUpdateCustomerInformation':
		"""
		Set Ship_Address2.

		:param ship_address2: str
		:returns: OrderUpdateCustomerInformation
		"""

		self.ship_address2 = ship_address2
		return self

	def set_ship_city(self, ship_city: str) -> 'OrderUpdateCustomerInformation':
		"""
		Set Ship_City.

		:param ship_city: str
		:returns: OrderUpdateCustomerInformation
		"""

		self.ship_city = ship_city
		return self

	def set_ship_state(self, ship_state: str) -> 'OrderUpdateCustomerInformation':
		"""
		Set Ship_State.

		:param ship_state: str
		:returns: OrderUpdateCustomerInformation
		"""

		self.ship_state = ship_state
		return self

	def set_ship_zip(self, ship_zip: str) -> 'OrderUpdateCustomerInformation':
		"""
		Set Ship_Zip.

		:param ship_zip: str
		:returns: OrderUpdateCustomerInformation
		"""

		self.ship_zip = ship_zip
		return self

	def set_ship_country(self, ship_country: str) -> 'OrderUpdateCustomerInformation':
		"""
		Set Ship_Country.

		:param ship_country: str
		:returns: OrderUpdateCustomerInformation
		"""

		self.ship_country = ship_country
		return self

	def set_bill_first_name(self, bill_first_name: str) -> 'OrderUpdateCustomerInformation':
		"""
		Set Bill_FirstName.

		:param bill_first_name: str
		:returns: OrderUpdateCustomerInformation
		"""

		self.bill_first_name = bill_first_name
		return self

	def set_bill_last_name(self, bill_last_name: str) -> 'OrderUpdateCustomerInformation':
		"""
		Set Bill_LastName.

		:param bill_last_name: str
		:returns: OrderUpdateCustomerInformation
		"""

		self.bill_last_name = bill_last_name
		return self

	def set_bill_email(self, bill_email: str) -> 'OrderUpdateCustomerInformation':
		"""
		Set Bill_Email.

		:param bill_email: str
		:returns: OrderUpdateCustomerInformation
		"""

		self.bill_email = bill_email
		return self

	def set_bill_phone(self, bill_phone: str) -> 'OrderUpdateCustomerInformation':
		"""
		Set Bill_Phone.

		:param bill_phone: str
		:returns: OrderUpdateCustomerInformation
		"""

		self.bill_phone = bill_phone
		return self

	def set_bill_fax(self, bill_fax: str) -> 'OrderUpdateCustomerInformation':
		"""
		Set Bill_Fax.

		:param bill_fax: str
		:returns: OrderUpdateCustomerInformation
		"""

		self.bill_fax = bill_fax
		return self

	def set_bill_company(self, bill_company: str) -> 'OrderUpdateCustomerInformation':
		"""
		Set Bill_Company.

		:param bill_company: str
		:returns: OrderUpdateCustomerInformation
		"""

		self.bill_company = bill_company
		return self

	def set_bill_address1(self, bill_address1: str) -> 'OrderUpdateCustomerInformation':
		"""
		Set Bill_Address1.

		:param bill_address1: str
		:returns: OrderUpdateCustomerInformation
		"""

		self.bill_address1 = bill_address1
		return self

	def set_bill_address2(self, bill_address2: str) -> 'OrderUpdateCustomerInformation':
		"""
		Set Bill_Address2.

		:param bill_address2: str
		:returns: OrderUpdateCustomerInformation
		"""

		self.bill_address2 = bill_address2
		return self

	def set_bill_city(self, bill_city: str) -> 'OrderUpdateCustomerInformation':
		"""
		Set Bill_City.

		:param bill_city: str
		:returns: OrderUpdateCustomerInformation
		"""

		self.bill_city = bill_city
		return self

	def set_bill_state(self, bill_state: str) -> 'OrderUpdateCustomerInformation':
		"""
		Set Bill_State.

		:param bill_state: str
		:returns: OrderUpdateCustomerInformation
		"""

		self.bill_state = bill_state
		return self

	def set_bill_zip(self, bill_zip: str) -> 'OrderUpdateCustomerInformation':
		"""
		Set Bill_Zip.

		:param bill_zip: str
		:returns: OrderUpdateCustomerInformation
		"""

		self.bill_zip = bill_zip
		return self

	def set_bill_country(self, bill_country: str) -> 'OrderUpdateCustomerInformation':
		"""
		Set Bill_Country.

		:param bill_country: str
		:returns: OrderUpdateCustomerInformation
		"""

		self.bill_country = bill_country
		return self

	# noinspection PyTypeChecker
	def send(self) -> 'merchantapi.response.OrderUpdateCustomerInformation':
		return super().send()

	def create_response(self, data) -> 'OrderUpdateCustomerInformation':
		"""
		Create a response object from the response data

		:param data:
		:returns: Response
		"""

		return merchantapi.response.OrderUpdateCustomerInformation(self, data)

	def to_dict(self) -> dict:
		"""
		Reduce the request to a dict

		:override:
		:returns: dict
		"""

		data = super().to_dict()

		data['Order_ID'] = self.order_id
		if self.customer_id is not None:
			data['Customer_ID'] = self.customer_id
		if self.ship_residential is not None:
			data['Ship_Residential'] = self.ship_residential
		if self.ship_first_name is not None:
			data['Ship_FirstName'] = self.ship_first_name
		if self.ship_last_name is not None:
			data['Ship_LastName'] = self.ship_last_name
		if self.ship_email is not None:
			data['Ship_Email'] = self.ship_email
		if self.ship_phone is not None:
			data['Ship_Phone'] = self.ship_phone
		if self.ship_fax is not None:
			data['Ship_Fax'] = self.ship_fax
		if self.ship_company is not None:
			data['Ship_Company'] = self.ship_company
		if self.ship_address1 is not None:
			data['Ship_Address1'] = self.ship_address1
		if self.ship_address2 is not None:
			data['Ship_Address2'] = self.ship_address2
		if self.ship_city is not None:
			data['Ship_City'] = self.ship_city
		if self.ship_state is not None:
			data['Ship_State'] = self.ship_state
		if self.ship_zip is not None:
			data['Ship_Zip'] = self.ship_zip
		if self.ship_country is not None:
			data['Ship_Country'] = self.ship_country
		if self.bill_first_name is not None:
			data['Bill_FirstName'] = self.bill_first_name
		if self.bill_last_name is not None:
			data['Bill_LastName'] = self.bill_last_name
		if self.bill_email is not None:
			data['Bill_Email'] = self.bill_email
		if self.bill_phone is not None:
			data['Bill_Phone'] = self.bill_phone
		if self.bill_fax is not None:
			data['Bill_Fax'] = self.bill_fax
		if self.bill_company is not None:
			data['Bill_Company'] = self.bill_company
		if self.bill_address1 is not None:
			data['Bill_Address1'] = self.bill_address1
		if self.bill_address2 is not None:
			data['Bill_Address2'] = self.bill_address2
		if self.bill_city is not None:
			data['Bill_City'] = self.bill_city
		if self.bill_state is not None:
			data['Bill_State'] = self.bill_state
		if self.bill_zip is not None:
			data['Bill_Zip'] = self.bill_zip
		if self.bill_country is not None:
			data['Bill_Country'] = self.bill_country
		return data


"""
Handles API Request PriceGroupCustomer_Update_Assigned.
Scope: Store.
:see: https://docs.miva.com/json-api/functions/pricegroupcustomer_update_assigned
"""


class PriceGroupCustomerUpdateAssigned(merchantapi.abstract.Request):
	def __init__(self, client: Client = None, price_group: merchantapi.model.PriceGroup = None):
		"""
		PriceGroupCustomerUpdateAssigned Constructor.

		:param client: Client
		:param price_group: PriceGroup
		"""

		super().__init__(client)
		self.price_group_id = None
		self.price_group_name = None
		self.edit_customer = None
		self.customer_id = None
		self.customer_login = None
		self.assigned = False
		if isinstance(price_group, merchantapi.model.PriceGroup):
			if price_group.get_id():
				self.set_price_group_id(price_group.get_id())
			elif price_group.get_name():
				self.set_price_group_name(price_group.get_name())

	def get_function(self):
		"""
		Get the function of the request.

		:returns: str
		"""

		return 'PriceGroupCustomer_Update_Assigned'

	def get_price_group_id(self) -> int:
		"""
		Get PriceGroup_ID.

		:returns: int
		"""

		return self.price_group_id

	def get_price_group_name(self) -> str:
		"""
		Get PriceGroup_Name.

		:returns: str
		"""

		return self.price_group_name

	def get_edit_customer(self) -> str:
		"""
		Get Edit_Customer.

		:returns: str
		"""

		return self.edit_customer

	def get_customer_id(self) -> int:
		"""
		Get Customer_ID.

		:returns: int
		"""

		return self.customer_id

	def get_customer_login(self) -> str:
		"""
		Get Customer_Login.

		:returns: str
		"""

		return self.customer_login

	def get_assigned(self) -> bool:
		"""
		Get Assigned.

		:returns: bool
		"""

		return self.assigned

	def set_price_group_id(self, price_group_id: int) -> 'PriceGroupCustomerUpdateAssigned':
		"""
		Set PriceGroup_ID.

		:param price_group_id: int
		:returns: PriceGroupCustomerUpdateAssigned
		"""

		self.price_group_id = price_group_id
		return self

	def set_price_group_name(self, price_group_name: str) -> 'PriceGroupCustomerUpdateAssigned':
		"""
		Set PriceGroup_Name.

		:param price_group_name: str
		:returns: PriceGroupCustomerUpdateAssigned
		"""

		self.price_group_name = price_group_name
		return self

	def set_edit_customer(self, edit_customer: str) -> 'PriceGroupCustomerUpdateAssigned':
		"""
		Set Edit_Customer.

		:param edit_customer: str
		:returns: PriceGroupCustomerUpdateAssigned
		"""

		self.edit_customer = edit_customer
		return self

	def set_customer_id(self, customer_id: int) -> 'PriceGroupCustomerUpdateAssigned':
		"""
		Set Customer_ID.

		:param customer_id: int
		:returns: PriceGroupCustomerUpdateAssigned
		"""

		self.customer_id = customer_id
		return self

	def set_customer_login(self, customer_login: str) -> 'PriceGroupCustomerUpdateAssigned':
		"""
		Set Customer_Login.

		:param customer_login: str
		:returns: PriceGroupCustomerUpdateAssigned
		"""

		self.customer_login = customer_login
		return self

	def set_assigned(self, assigned: bool) -> 'PriceGroupCustomerUpdateAssigned':
		"""
		Set Assigned.

		:param assigned: bool
		:returns: PriceGroupCustomerUpdateAssigned
		"""

		self.assigned = assigned
		return self

	# noinspection PyTypeChecker
	def send(self) -> 'merchantapi.response.PriceGroupCustomerUpdateAssigned':
		return super().send()

	def create_response(self, data) -> 'PriceGroupCustomerUpdateAssigned':
		"""
		Create a response object from the response data

		:param data:
		:returns: Response
		"""

		return merchantapi.response.PriceGroupCustomerUpdateAssigned(self, data)

	def to_dict(self) -> dict:
		"""
		Reduce the request to a dict

		:override:
		:returns: dict
		"""

		data = super().to_dict()

		if self.price_group_id is not None:
			data['PriceGroup_ID'] = self.price_group_id
		elif self.price_group_name is not None:
			data['PriceGroup_Name'] = self.price_group_name

		if self.customer_id is not None:
			data['Customer_ID'] = self.customer_id
		elif self.edit_customer is not None:
			data['Edit_Customer'] = self.edit_customer
		elif self.customer_login is not None:
			data['Customer_Login'] = self.customer_login

		if self.assigned is not None:
			data['Assigned'] = self.assigned
		return data


"""
Handles API Request PriceGroupList_Load_Query.
Scope: Store.
:see: https://docs.miva.com/json-api/functions/pricegrouplist_load_query
"""


class PriceGroupListLoadQuery(ListQueryRequest):

	available_search_fields = [
		'id',
		'name',
		'type',
		'module_id',
		'custscope',
		'rate',
		'discount',
		'markup',
		'dt_start',
		'dt_end',
		'priority',
		'exclusion',
		'descrip',
		'display',
		'qmn_subtot',
		'qmx_subtot',
		'qmn_quan',
		'qmx_quan',
		'qmn_weight',
		'qmx_weight',
		'bmn_subtot',
		'bmx_subtot',
		'bmn_quan',
		'bmx_quan',
		'bmn_weight',
		'bmx_weight'
	]

	available_sort_fields = [
		'id',
		'name',
		'type',
		'module_id',
		'custscope',
		'rate',
		'discount',
		'markup',
		'dt_start',
		'dt_end',
		'priority',
		'exclusion',
		'descrip',
		'display',
		'qmn_subtot',
		'qmx_subtot',
		'qmn_quan',
		'qmx_quan',
		'qmn_weight',
		'qmx_weight',
		'bmn_subtot',
		'bmx_subtot',
		'bmn_quan',
		'bmx_quan',
		'bmn_weight',
		'bmx_weight'
	]

	def __init__(self, client: Client = None):
		"""
		PriceGroupListLoadQuery Constructor.

		:param client: Client
		"""

		super().__init__(client)

	def get_function(self):
		"""
		Get the function of the request.

		:returns: str
		"""

		return 'PriceGroupList_Load_Query'

	# noinspection PyTypeChecker
	def send(self) -> 'merchantapi.response.PriceGroupListLoadQuery':
		return super().send()

	def create_response(self, data) -> 'PriceGroupListLoadQuery':
		"""
		Create a response object from the response data

		:param data:
		:returns: Response
		"""

		return merchantapi.response.PriceGroupListLoadQuery(self, data)


"""
Handles API Request PriceGroupProduct_Update_Assigned.
Scope: Store.
:see: https://docs.miva.com/json-api/functions/pricegroupproduct_update_assigned
"""


class PriceGroupProductUpdateAssigned(merchantapi.abstract.Request):
	def __init__(self, client: Client = None, price_group: merchantapi.model.PriceGroup = None):
		"""
		PriceGroupProductUpdateAssigned Constructor.

		:param client: Client
		:param price_group: PriceGroup
		"""

		super().__init__(client)
		self.price_group_id = None
		self.price_group_name = None
		self.edit_product = None
		self.product_id = None
		self.product_code = None
		self.product_sku = None
		self.assigned = False
		if isinstance(price_group, merchantapi.model.PriceGroup):
			if price_group.get_id():
				self.set_price_group_id(price_group.get_id())
			elif price_group.get_name():
				self.set_price_group_name(price_group.get_name())

			self.set_price_group_name(price_group.get_name())

	def get_function(self):
		"""
		Get the function of the request.

		:returns: str
		"""

		return 'PriceGroupProduct_Update_Assigned'

	def get_price_group_id(self) -> int:
		"""
		Get PriceGroup_ID.

		:returns: int
		"""

		return self.price_group_id

	def get_price_group_name(self) -> str:
		"""
		Get PriceGroup_Name.

		:returns: str
		"""

		return self.price_group_name

	def get_edit_product(self) -> str:
		"""
		Get Edit_Product.

		:returns: str
		"""

		return self.edit_product

	def get_product_id(self) -> int:
		"""
		Get Product_ID.

		:returns: int
		"""

		return self.product_id

	def get_product_code(self) -> str:
		"""
		Get Product_Code.

		:returns: str
		"""

		return self.product_code

	def get_product_sku(self) -> str:
		"""
		Get Product_SKU.

		:returns: str
		"""

		return self.product_sku

	def get_assigned(self) -> bool:
		"""
		Get Assigned.

		:returns: bool
		"""

		return self.assigned

	def set_price_group_id(self, price_group_id: int) -> 'PriceGroupProductUpdateAssigned':
		"""
		Set PriceGroup_ID.

		:param price_group_id: int
		:returns: PriceGroupProductUpdateAssigned
		"""

		self.price_group_id = price_group_id
		return self

	def set_price_group_name(self, price_group_name: str) -> 'PriceGroupProductUpdateAssigned':
		"""
		Set PriceGroup_Name.

		:param price_group_name: str
		:returns: PriceGroupProductUpdateAssigned
		"""

		self.price_group_name = price_group_name
		return self

	def set_edit_product(self, edit_product: str) -> 'PriceGroupProductUpdateAssigned':
		"""
		Set Edit_Product.

		:param edit_product: str
		:returns: PriceGroupProductUpdateAssigned
		"""

		self.edit_product = edit_product
		return self

	def set_product_id(self, product_id: int) -> 'PriceGroupProductUpdateAssigned':
		"""
		Set Product_ID.

		:param product_id: int
		:returns: PriceGroupProductUpdateAssigned
		"""

		self.product_id = product_id
		return self

	def set_product_code(self, product_code: str) -> 'PriceGroupProductUpdateAssigned':
		"""
		Set Product_Code.

		:param product_code: str
		:returns: PriceGroupProductUpdateAssigned
		"""

		self.product_code = product_code
		return self

	def set_product_sku(self, product_sku: str) -> 'PriceGroupProductUpdateAssigned':
		"""
		Set Product_SKU.

		:param product_sku: str
		:returns: PriceGroupProductUpdateAssigned
		"""

		self.product_sku = product_sku
		return self

	def set_assigned(self, assigned: bool) -> 'PriceGroupProductUpdateAssigned':
		"""
		Set Assigned.

		:param assigned: bool
		:returns: PriceGroupProductUpdateAssigned
		"""

		self.assigned = assigned
		return self

	# noinspection PyTypeChecker
	def send(self) -> 'merchantapi.response.PriceGroupProductUpdateAssigned':
		return super().send()

	def create_response(self, data) -> 'PriceGroupProductUpdateAssigned':
		"""
		Create a response object from the response data

		:param data:
		:returns: Response
		"""

		return merchantapi.response.PriceGroupProductUpdateAssigned(self, data)

	def to_dict(self) -> dict:
		"""
		Reduce the request to a dict

		:override:
		:returns: dict
		"""

		data = super().to_dict()

		if self.price_group_id is not None:
			data['PriceGroup_ID'] = self.price_group_id
		elif self.price_group_name is not None:
			data['PriceGroup_Name'] = self.price_group_name

		if self.product_id is not None:
			data['Product_ID'] = self.product_id
		elif self.edit_product is not None:
			data['Edit_Product'] = self.edit_product
		elif self.product_id is not None:
			data['Product_ID'] = self.product_id
		elif self.product_code is not None:
			data['Product_Code'] = self.product_code
		elif self.product_sku is not None:
			data['Product_SKU'] = self.product_sku

		if self.price_group_name is not None:
			data['PriceGroup_Name'] = self.price_group_name
		if self.assigned is not None:
			data['Assigned'] = self.assigned
		return data


"""
Handles API Request ProductImage_Add.
Scope: Store.
:see: https://docs.miva.com/json-api/functions/productimage_add
"""


class ProductImageAdd(merchantapi.abstract.Request):
	def __init__(self, client: Client = None, product: merchantapi.model.Product = None):
		"""
		ProductImageAdd Constructor.

		:param client: Client
		:param product: Product
		"""

		super().__init__(client)
		self.product_code = None
		self.product_id = None
		self.edit_product = None
		self.product_sku = None
		self.filepath = None
		self.image_type_id = None
		if isinstance(product, merchantapi.model.Product):
			if product.get_id():
				self.set_product_id(product.get_id())
			elif product.get_code():
				self.set_edit_product(product.get_code())
			elif product.get_sku():
				self.set_product_sku(product.get_sku())

	def get_function(self):
		"""
		Get the function of the request.

		:returns: str
		"""

		return 'ProductImage_Add'

	def get_product_code(self) -> str:
		"""
		Get Product_Code.

		:returns: str
		"""

		return self.product_code

	def get_product_id(self) -> int:
		"""
		Get Product_ID.

		:returns: int
		"""

		return self.product_id

	def get_edit_product(self) -> str:
		"""
		Get Edit_Product.

		:returns: str
		"""

		return self.edit_product

	def get_product_sku(self) -> str:
		"""
		Get Product_SKU.

		:returns: str
		"""

		return self.product_sku

	def get_filepath(self) -> str:
		"""
		Get Filepath.

		:returns: str
		"""

		return self.filepath

	def get_image_type_id(self) -> int:
		"""
		Get ImageType_ID.

		:returns: int
		"""

		return self.image_type_id

	def set_product_code(self, product_code: str) -> 'ProductImageAdd':
		"""
		Set Product_Code.

		:param product_code: str
		:returns: ProductImageAdd
		"""

		self.product_code = product_code
		return self

	def set_product_id(self, product_id: int) -> 'ProductImageAdd':
		"""
		Set Product_ID.

		:param product_id: int
		:returns: ProductImageAdd
		"""

		self.product_id = product_id
		return self

	def set_edit_product(self, edit_product: str) -> 'ProductImageAdd':
		"""
		Set Edit_Product.

		:param edit_product: str
		:returns: ProductImageAdd
		"""

		self.edit_product = edit_product
		return self

	def set_product_sku(self, product_sku: str) -> 'ProductImageAdd':
		"""
		Set Product_SKU.

		:param product_sku: str
		:returns: ProductImageAdd
		"""

		self.product_sku = product_sku
		return self

	def set_filepath(self, filepath: str) -> 'ProductImageAdd':
		"""
		Set Filepath.

		:param filepath: str
		:returns: ProductImageAdd
		"""

		self.filepath = filepath
		return self

	def set_image_type_id(self, image_type_id: int) -> 'ProductImageAdd':
		"""
		Set ImageType_ID.

		:param image_type_id: int
		:returns: ProductImageAdd
		"""

		self.image_type_id = image_type_id
		return self

	# noinspection PyTypeChecker
	def send(self) -> 'merchantapi.response.ProductImageAdd':
		return super().send()

	def create_response(self, data) -> 'ProductImageAdd':
		"""
		Create a response object from the response data

		:param data:
		:returns: Response
		"""

		return merchantapi.response.ProductImageAdd(self, data)

	def to_dict(self) -> dict:
		"""
		Reduce the request to a dict

		:override:
		:returns: dict
		"""

		data = super().to_dict()

		if self.product_id is not None:
			data['Product_ID'] = self.product_id
		elif self.edit_product is not None:
			data['Edit_Product'] = self.edit_product
		elif self.product_code is not None:
			data['Product_Code'] = self.product_code
		elif self.product_sku is not None:
			data['Product_SKU'] = self.product_sku

		data['Filepath'] = self.filepath
		data['ImageType_ID'] = self.image_type_id
		return data


"""
Handles API Request ProductImage_Delete.
Scope: Store.
:see: https://docs.miva.com/json-api/functions/productimage_delete
"""


class ProductImageDelete(merchantapi.abstract.Request):
	def __init__(self, client: Client = None, product_image_data: merchantapi.model.ProductImageData = None):
		"""
		ProductImageDelete Constructor.

		:param client: Client
		:param product_image_data: ProductImageData
		"""

		super().__init__(client)
		self.product_image_id = None
		if isinstance(product_image_data, merchantapi.model.ProductImageData):
			self.set_product_image_id(product_image_data.get_id())

	def get_function(self):
		"""
		Get the function of the request.

		:returns: str
		"""

		return 'ProductImage_Delete'

	def get_product_image_id(self) -> int:
		"""
		Get ProductImage_ID.

		:returns: int
		"""

		return self.product_image_id

	def set_product_image_id(self, product_image_id: int) -> 'ProductImageDelete':
		"""
		Set ProductImage_ID.

		:param product_image_id: int
		:returns: ProductImageDelete
		"""

		self.product_image_id = product_image_id
		return self

	# noinspection PyTypeChecker
	def send(self) -> 'merchantapi.response.ProductImageDelete':
		return super().send()

	def create_response(self, data) -> 'ProductImageDelete':
		"""
		Create a response object from the response data

		:param data:
		:returns: Response
		"""

		return merchantapi.response.ProductImageDelete(self, data)

	def to_dict(self) -> dict:
		"""
		Reduce the request to a dict

		:override:
		:returns: dict
		"""

		data = super().to_dict()

		data['ProductImage_ID'] = self.product_image_id
		return data


"""
Handles API Request ProductList_Adjust_Inventory.
Scope: Store.
:see: https://docs.miva.com/json-api/functions/productlist_adjust_inventory
"""


class ProductListAdjustInventory(merchantapi.abstract.Request):
	def __init__(self, client: Client = None):
		"""
		ProductListAdjustInventory Constructor.

		:param client: Client
		"""

		super().__init__(client)
		self.inventory_adjustments = []

	def get_function(self):
		"""
		Get the function of the request.

		:returns: str
		"""

		return 'ProductList_Adjust_Inventory'

	def get_inventory_adjustments(self) -> list:
		"""
		Get Inventory_Adjustments.

		:returns: List of ProductInventoryAdjustment
		"""

		return self.inventory_adjustments

	def set_inventory_adjustments(self, inventory_adjustments: list) -> 'ProductListAdjustInventory':
		"""
		Set Inventory_Adjustments.

		:param inventory_adjustments: {ProductInventoryAdjustment[]}
		:raises Exception:
		:returns: ProductListAdjustInventory
		"""

		for e in inventory_adjustments:
			if not isinstance(e, merchantapi.model.ProductInventoryAdjustment):
				raise Exception("")
		self.inventory_adjustments = inventory_adjustments
		return self

	def add_inventory_adjustment(self, inventory_adjustment) -> 'ProductListAdjustInventory':
		"""
		Add Inventory_Adjustments.

		:param inventory_adjustment: ProductInventoryAdjustment
		:raises Exception:
		:returns: {ProductListAdjustInventory}
		"""

		if isinstance(inventory_adjustment, merchantapi.model.ProductInventoryAdjustment):
			self.inventory_adjustments.append(inventory_adjustment)
		elif isinstance(inventory_adjustment, dict):
			self.inventory_adjustments.append(merchantapi.model.ProductInventoryAdjustment(inventory_adjustment))
		else:
			raise Exception('Expected instance of ProductInventoryAdjustment or dict')
		return self

	def add_inventory_adjustments(self, inventory_adjustments: list) -> 'ProductListAdjustInventory':
		"""
		Add many ProductInventoryAdjustment.

		:param inventory_adjustments: List of ProductInventoryAdjustment
		:raises Exception:
		:returns: ProductListAdjustInventory
		"""

		for e in inventory_adjustments:
			if not isinstance(e, merchantapi.model.ProductInventoryAdjustment):
				raise Exception('')
			self.inventory_adjustments.append(e)

		return self

	# noinspection PyTypeChecker
	def send(self) -> 'merchantapi.response.ProductListAdjustInventory':
		return super().send()

	def create_response(self, data) -> 'ProductListAdjustInventory':
		"""
		Create a response object from the response data

		:param data:
		:returns: Response
		"""

		return merchantapi.response.ProductListAdjustInventory(self, data)

	def to_dict(self) -> dict:
		"""
		Reduce the request to a dict

		:override:
		:returns: dict
		"""

		data = super().to_dict()

		if len(self.inventory_adjustments):
			data['Inventory_Adjustments'] = []

			for f in self.inventory_adjustments:
				data['Inventory_Adjustments'].append(f.to_dict())
		return data


"""
Handles API Request ProductList_Load_Query.
Scope: Store.
:see: https://docs.miva.com/json-api/functions/productlist_load_query
"""


class ProductListLoadQuery(ListQueryRequest):
	# PRODUCT_SHOW constants.
	PRODUCT_SHOW_ALL = 'All'
	PRODUCT_SHOW_UNCATEGORIZED = 'Uncategorized'
	PRODUCT_SHOW_ACTIVE = 'Active'

	available_search_fields = [
		'id',
		'code',
		'sku',
		'cancat_code',
		'page_code',
		'name',
		'thumbnail',
		'image',
		'price',
		'cost',
		'descrip',
		'weight',
		'taxable',
		'active',
		'page_title',
		'dt_created',
		'dt_updated',
		'category',
		'product_inventory'
	]

	available_sort_fields = [
		'id',
		'code',
		'sku',
		'cancat_code',
		'page_code',
		'name',
		'thumbnail',
		'image',
		'price',
		'cost',
		'descrip',
		'weight',
		'taxable',
		'active',
		'page_title',
		'dt_created',
		'dt_updated'
	]

	available_on_demand_columns = [
		'descrip',
		'catcount',
		'productinventorysettings',
		'attributes',
		'productimagedata',
		'categories',
		'productshippingrules',
		'relatedproducts',
		'uris'
	]

	available_custom_filters = {
		'Product_Show': [
			PRODUCT_SHOW_ALL,
			PRODUCT_SHOW_UNCATEGORIZED,
			PRODUCT_SHOW_ACTIVE
		]
	}

	def __init__(self, client: Client = None):
		"""
		ProductListLoadQuery Constructor.

		:param client: Client
		"""

		super().__init__(client)

	def get_function(self):
		"""
		Get the function of the request.

		:returns: str
		"""

		return 'ProductList_Load_Query'

	# noinspection PyTypeChecker
	def send(self) -> 'merchantapi.response.ProductListLoadQuery':
		return super().send()

	def create_response(self, data) -> 'ProductListLoadQuery':
		"""
		Create a response object from the response data

		:param data:
		:returns: Response
		"""

		return merchantapi.response.ProductListLoadQuery(self, data)


"""
Handles API Request ProductVariantList_Load_Product.
Scope: Store.
:see: https://docs.miva.com/json-api/functions/productvariantlist_load_product
"""


class ProductVariantListLoadProduct(merchantapi.abstract.Request):
	def __init__(self, client: Client = None, product: merchantapi.model.Product = None):
		"""
		ProductVariantListLoadProduct Constructor.

		:param client: Client
		:param product: Product
		"""

		super().__init__(client)
		self.product_id = None
		self.product_code = None
		self.edit_product = None
		self.product_sku = None
		self.include_default_variant = False
		self.limits = []
		self.exclusions = []
		if isinstance(product, merchantapi.model.Product):
			if product.get_id():
				self.set_product_id(product.get_id())
			elif product.get_code():
				self.set_edit_product(product.get_code())
			elif product.get_sku():
				self.set_product_sku(product.get_sku())

	def get_function(self):
		"""
		Get the function of the request.

		:returns: str
		"""

		return 'ProductVariantList_Load_Product'

	def get_product_id(self) -> int:
		"""
		Get Product_ID.

		:returns: int
		"""

		return self.product_id

	def get_product_code(self) -> str:
		"""
		Get Product_Code.

		:returns: str
		"""

		return self.product_code

	def get_edit_product(self) -> str:
		"""
		Get Edit_Product.

		:returns: str
		"""

		return self.edit_product

	def get_product_sku(self) -> str:
		"""
		Get Product_SKU.

		:returns: str
		"""

		return self.product_sku

	def get_include_default_variant(self) -> bool:
		"""
		Get Include_Default_Variant.

		:returns: bool
		"""

		return self.include_default_variant

	def get_limits(self) -> list:
		"""
		Get Limits.

		:returns: List of ProductVariantLimit
		"""

		return self.limits

	def get_exclusions(self) -> list:
		"""
		Get Exclusions.

		:returns: List of ProductVariantExclusion
		"""

		return self.exclusions

	def set_product_id(self, product_id: int) -> 'ProductVariantListLoadProduct':
		"""
		Set Product_ID.

		:param product_id: int
		:returns: ProductVariantListLoadProduct
		"""

		self.product_id = product_id
		return self

	def set_product_code(self, product_code: str) -> 'ProductVariantListLoadProduct':
		"""
		Set Product_Code.

		:param product_code: str
		:returns: ProductVariantListLoadProduct
		"""

		self.product_code = product_code
		return self

	def set_edit_product(self, edit_product: str) -> 'ProductVariantListLoadProduct':
		"""
		Set Edit_Product.

		:param edit_product: str
		:returns: ProductVariantListLoadProduct
		"""

		self.edit_product = edit_product
		return self

	def set_product_sku(self, product_sku: str) -> 'ProductVariantListLoadProduct':
		"""
		Set Product_SKU.

		:param product_sku: str
		:returns: ProductVariantListLoadProduct
		"""

		self.product_sku = product_sku
		return self

	def set_include_default_variant(self, include_default_variant: bool) -> 'ProductVariantListLoadProduct':
		"""
		Set Include_Default_Variant.

		:param include_default_variant: bool
		:returns: ProductVariantListLoadProduct
		"""

		self.include_default_variant = include_default_variant
		return self

	def set_limits(self, limits: list) -> 'ProductVariantListLoadProduct':
		"""
		Set Limits.

		:param limits: {ProductVariantLimit[]}
		:raises Exception:
		:returns: ProductVariantListLoadProduct
		"""

		for e in limits:
			if not isinstance(e, merchantapi.model.ProductVariantLimit):
				raise Exception("")
		self.limits = limits
		return self

	def set_exclusions(self, exclusions: list) -> 'ProductVariantListLoadProduct':
		"""
		Set Exclusions.

		:param exclusions: {ProductVariantExclusion[]}
		:raises Exception:
		:returns: ProductVariantListLoadProduct
		"""

		for e in exclusions:
			if not isinstance(e, merchantapi.model.ProductVariantExclusion):
				raise Exception("")
		self.exclusions = exclusions
		return self

	def add_limit(self, limit) -> 'ProductVariantListLoadProduct':
		"""
		Add Limits.

		:param limit: ProductVariantLimit
		:raises Exception:
		:returns: {ProductVariantListLoadProduct}
		"""

		if isinstance(limit, merchantapi.model.ProductVariantLimit):
			self.limits.append(limit)
		elif isinstance(limit, dict):
			self.limits.append(merchantapi.model.ProductVariantLimit(limit))
		else:
			raise Exception('Expected instance of ProductVariantLimit or dict')
		return self

	def add_limits(self, limits: list) -> 'ProductVariantListLoadProduct':
		"""
		Add many ProductVariantLimit.

		:param limits: List of ProductVariantLimit
		:raises Exception:
		:returns: ProductVariantListLoadProduct
		"""

		for e in limits:
			if not isinstance(e, merchantapi.model.ProductVariantLimit):
				raise Exception('')
			self.limits.append(e)

		return self

	def add_exclusion(self, exclusion) -> 'ProductVariantListLoadProduct':
		"""
		Add Exclusions.

		:param exclusion: ProductVariantExclusion
		:raises Exception:
		:returns: {ProductVariantListLoadProduct}
		"""

		if isinstance(exclusion, merchantapi.model.ProductVariantExclusion):
			self.exclusions.append(exclusion)
		elif isinstance(exclusion, dict):
			self.exclusions.append(merchantapi.model.ProductVariantExclusion(exclusion))
		else:
			raise Exception('Expected instance of ProductVariantExclusion or dict')
		return self

	def add_exclusions(self, exclusions: list) -> 'ProductVariantListLoadProduct':
		"""
		Add many ProductVariantExclusion.

		:param exclusions: List of ProductVariantExclusion
		:raises Exception:
		:returns: ProductVariantListLoadProduct
		"""

		for e in exclusions:
			if not isinstance(e, merchantapi.model.ProductVariantExclusion):
				raise Exception('')
			self.exclusions.append(e)

		return self

	# noinspection PyTypeChecker
	def send(self) -> 'merchantapi.response.ProductVariantListLoadProduct':
		return super().send()

	def create_response(self, data) -> 'ProductVariantListLoadProduct':
		"""
		Create a response object from the response data

		:param data:
		:returns: Response
		"""

		return merchantapi.response.ProductVariantListLoadProduct(self, data)

	def to_dict(self) -> dict:
		"""
		Reduce the request to a dict

		:override:
		:returns: dict
		"""

		data = super().to_dict()

		if self.product_id is not None:
			data['Product_ID'] = self.product_id
		elif self.product_code is not None:
			data['Product_Code'] = self.product_code
		elif self.edit_product is not None:
			data['Edit_Product'] = self.edit_product
		elif self.product_sku is not None:
			data['Product_SKU'] = self.product_sku

		if self.include_default_variant is not None:
			data['Include_Default_Variant'] = self.include_default_variant
		if len(self.limits):
			data['Limits'] = []

			for f in self.limits:
				data['Limits'].append(f.to_dict())
		if len(self.exclusions):
			data['Exclusions'] = []

			for f in self.exclusions:
				data['Exclusions'].append(f.to_dict())
		return data


"""
Handles API Request Product_Insert.
Scope: Store.
:see: https://docs.miva.com/json-api/functions/product_insert
"""


class ProductInsert(merchantapi.abstract.Request):
	def __init__(self, client: Client = None, product: merchantapi.model.Product = None):
		"""
		ProductInsert Constructor.

		:param client: Client
		:param product: Product
		"""

		super().__init__(client)
		self.product_code = None
		self.product_sku = None
		self.product_name = None
		self.product_description = None
		self.product_canonical_category_code = None
		self.product_alternate_display_page = None
		self.product_page_title = None
		self.product_thumbnail = None
		self.product_image = None
		self.product_price = None
		self.product_cost = None
		self.product_weight = None
		self.product_inventory = None
		self.product_taxable = False
		self.product_active = False
		self.custom_field_values = merchantapi.model.CustomFieldValues()
		if isinstance(product, merchantapi.model.Product):
			self.set_product_code(product.get_code())
			self.set_product_sku(product.get_sku())
			self.set_product_name(product.get_name())
			self.set_product_description(product.get_description())
			self.set_product_canonical_category_code(product.get_canonical_category_code())
			self.set_product_alternate_display_page(product.get_page_code())
			self.set_product_page_title(product.get_page_title())
			self.set_product_thumbnail(product.get_thumbnail())
			self.set_product_image(product.get_image())
			self.set_product_price(product.get_price())
			self.set_product_cost(product.get_cost())
			self.set_product_weight(product.get_weight())
			self.set_product_inventory(product.get_product_inventory())
			self.set_product_taxable(product.get_taxable())
			self.set_product_active(product.get_active())

			if product.get_custom_field_values():
				self.set_custom_field_values(product.get_custom_field_values())

	def get_function(self):
		"""
		Get the function of the request.

		:returns: str
		"""

		return 'Product_Insert'

	def get_product_code(self) -> str:
		"""
		Get Product_Code.

		:returns: str
		"""

		return self.product_code

	def get_product_sku(self) -> str:
		"""
		Get Product_SKU.

		:returns: str
		"""

		return self.product_sku

	def get_product_name(self) -> str:
		"""
		Get Product_Name.

		:returns: str
		"""

		return self.product_name

	def get_product_description(self) -> str:
		"""
		Get Product_Description.

		:returns: str
		"""

		return self.product_description

	def get_product_canonical_category_code(self) -> str:
		"""
		Get Product_Canonical_Category_Code.

		:returns: str
		"""

		return self.product_canonical_category_code

	def get_product_alternate_display_page(self) -> str:
		"""
		Get Product_Alternate_Display_Page.

		:returns: str
		"""

		return self.product_alternate_display_page

	def get_product_page_title(self) -> str:
		"""
		Get Product_Page_Title.

		:returns: str
		"""

		return self.product_page_title

	def get_product_thumbnail(self) -> str:
		"""
		Get Product_Thumbnail.

		:returns: str
		"""

		return self.product_thumbnail

	def get_product_image(self) -> str:
		"""
		Get Product_Image.

		:returns: str
		"""

		return self.product_image

	def get_product_price(self) -> float:
		"""
		Get Product_Price.

		:returns: float
		"""

		return self.product_price

	def get_product_cost(self) -> float:
		"""
		Get Product_Cost.

		:returns: float
		"""

		return self.product_cost

	def get_product_weight(self) -> float:
		"""
		Get Product_Weight.

		:returns: float
		"""

		return self.product_weight

	def get_product_inventory(self) -> int:
		"""
		Get Product_Inventory.

		:returns: int
		"""

		return self.product_inventory

	def get_product_taxable(self) -> bool:
		"""
		Get Product_Taxable.

		:returns: bool
		"""

		return self.product_taxable

	def get_product_active(self) -> bool:
		"""
		Get Product_Active.

		:returns: bool
		"""

		return self.product_active

	def get_custom_field_values(self) -> merchantapi.model.CustomFieldValues:
		"""
		Get CustomField_Values.

		:returns: CustomFieldValues}|None
		"""

		return self.custom_field_values

	def set_product_code(self, product_code: str) -> 'ProductInsert':
		"""
		Set Product_Code.

		:param product_code: str
		:returns: ProductInsert
		"""

		self.product_code = product_code
		return self

	def set_product_sku(self, product_sku: str) -> 'ProductInsert':
		"""
		Set Product_SKU.

		:param product_sku: str
		:returns: ProductInsert
		"""

		self.product_sku = product_sku
		return self

	def set_product_name(self, product_name: str) -> 'ProductInsert':
		"""
		Set Product_Name.

		:param product_name: str
		:returns: ProductInsert
		"""

		self.product_name = product_name
		return self

	def set_product_description(self, product_description: str) -> 'ProductInsert':
		"""
		Set Product_Description.

		:param product_description: str
		:returns: ProductInsert
		"""

		self.product_description = product_description
		return self

	def set_product_canonical_category_code(self, product_canonical_category_code: str) -> 'ProductInsert':
		"""
		Set Product_Canonical_Category_Code.

		:param product_canonical_category_code: str
		:returns: ProductInsert
		"""

		self.product_canonical_category_code = product_canonical_category_code
		return self

	def set_product_alternate_display_page(self, product_alternate_display_page: str) -> 'ProductInsert':
		"""
		Set Product_Alternate_Display_Page.

		:param product_alternate_display_page: str
		:returns: ProductInsert
		"""

		self.product_alternate_display_page = product_alternate_display_page
		return self

	def set_product_page_title(self, product_page_title: str) -> 'ProductInsert':
		"""
		Set Product_Page_Title.

		:param product_page_title: str
		:returns: ProductInsert
		"""

		self.product_page_title = product_page_title
		return self

	def set_product_thumbnail(self, product_thumbnail: str) -> 'ProductInsert':
		"""
		Set Product_Thumbnail.

		:param product_thumbnail: str
		:returns: ProductInsert
		"""

		self.product_thumbnail = product_thumbnail
		return self

	def set_product_image(self, product_image: str) -> 'ProductInsert':
		"""
		Set Product_Image.

		:param product_image: str
		:returns: ProductInsert
		"""

		self.product_image = product_image
		return self

	def set_product_price(self, product_price: float) -> 'ProductInsert':
		"""
		Set Product_Price.

		:param product_price: float
		:returns: ProductInsert
		"""

		self.product_price = product_price
		return self

	def set_product_cost(self, product_cost: float) -> 'ProductInsert':
		"""
		Set Product_Cost.

		:param product_cost: float
		:returns: ProductInsert
		"""

		self.product_cost = product_cost
		return self

	def set_product_weight(self, product_weight: float) -> 'ProductInsert':
		"""
		Set Product_Weight.

		:param product_weight: float
		:returns: ProductInsert
		"""

		self.product_weight = product_weight
		return self

	def set_product_inventory(self, product_inventory: int) -> 'ProductInsert':
		"""
		Set Product_Inventory.

		:param product_inventory: int
		:returns: ProductInsert
		"""

		self.product_inventory = product_inventory
		return self

	def set_product_taxable(self, product_taxable: bool) -> 'ProductInsert':
		"""
		Set Product_Taxable.

		:param product_taxable: bool
		:returns: ProductInsert
		"""

		self.product_taxable = product_taxable
		return self

	def set_product_active(self, product_active: bool) -> 'ProductInsert':
		"""
		Set Product_Active.

		:param product_active: bool
		:returns: ProductInsert
		"""

		self.product_active = product_active
		return self

	def set_custom_field_values(self, custom_field_values: merchantapi.model.CustomFieldValues) -> 'ProductInsert':
		"""
		Set CustomField_Values.

		:param custom_field_values: CustomFieldValues}|None
		:raises Exception:
		:returns: ProductInsert
		"""

		if not isinstance(custom_field_values, merchantapi.model.CustomFieldValues):
			raise Exception("")
		self.custom_field_values = custom_field_values
		return self

	# noinspection PyTypeChecker
	def send(self) -> 'merchantapi.response.ProductInsert':
		return super().send()

	def create_response(self, data) -> 'ProductInsert':
		"""
		Create a response object from the response data

		:param data:
		:returns: Response
		"""

		return merchantapi.response.ProductInsert(self, data)

	def to_dict(self) -> dict:
		"""
		Reduce the request to a dict

		:override:
		:returns: dict
		"""

		data = super().to_dict()

		data['Product_Code'] = self.product_code
		data['Product_SKU'] = self.product_sku
		data['Product_Name'] = self.product_name
		if self.product_description is not None:
			data['Product_Description'] = self.product_description
		if self.product_canonical_category_code is not None:
			data['Product_Canonical_Category_Code'] = self.product_canonical_category_code
		if self.product_alternate_display_page is not None:
			data['Product_Alternate_Display_Page'] = self.product_alternate_display_page
		if self.product_page_title is not None:
			data['Product_Page_Title'] = self.product_page_title
		if self.product_thumbnail is not None:
			data['Product_Thumbnail'] = self.product_thumbnail
		if self.product_image is not None:
			data['Product_Image'] = self.product_image
		if self.product_price is not None:
			data['Product_Price'] = self.product_price
		if self.product_cost is not None:
			data['Product_Cost'] = self.product_cost
		if self.product_weight is not None:
			data['Product_Weight'] = self.product_weight
		if self.product_inventory is not None:
			data['Product_Inventory'] = self.product_inventory
		if self.product_taxable is not None:
			data['Product_Taxable'] = self.product_taxable
		if self.product_active is not None:
			data['Product_Active'] = self.product_active
		if self.custom_field_values is not None:
			data['CustomField_Values'] = self.custom_field_values.to_dict()
		return data


"""
Handles API Request Product_Delete.
Scope: Store.
:see: https://docs.miva.com/json-api/functions/product_delete
"""


class ProductDelete(merchantapi.abstract.Request):
	def __init__(self, client: Client = None, product: merchantapi.model.Product = None):
		"""
		ProductDelete Constructor.

		:param client: Client
		:param product: Product
		"""

		super().__init__(client)
		self.product_code = None
		self.product_id = None
		self.edit_product = None
		self.product_sku = None
		if isinstance(product, merchantapi.model.Product):
			if product.get_id():
				self.set_product_id(product.get_id())
			elif product.get_code():
				self.set_edit_product(product.get_code())
			elif product.get_sku():
				self.set_product_sku(product.get_sku())

	def get_function(self):
		"""
		Get the function of the request.

		:returns: str
		"""

		return 'Product_Delete'

	def get_product_code(self) -> str:
		"""
		Get Product_Code.

		:returns: str
		"""

		return self.product_code

	def get_product_id(self) -> int:
		"""
		Get Product_ID.

		:returns: int
		"""

		return self.product_id

	def get_edit_product(self) -> str:
		"""
		Get Edit_Product.

		:returns: str
		"""

		return self.edit_product

	def get_product_sku(self) -> str:
		"""
		Get Product_SKU.

		:returns: str
		"""

		return self.product_sku

	def set_product_code(self, product_code: str) -> 'ProductDelete':
		"""
		Set Product_Code.

		:param product_code: str
		:returns: ProductDelete
		"""

		self.product_code = product_code
		return self

	def set_product_id(self, product_id: int) -> 'ProductDelete':
		"""
		Set Product_ID.

		:param product_id: int
		:returns: ProductDelete
		"""

		self.product_id = product_id
		return self

	def set_edit_product(self, edit_product: str) -> 'ProductDelete':
		"""
		Set Edit_Product.

		:param edit_product: str
		:returns: ProductDelete
		"""

		self.edit_product = edit_product
		return self

	def set_product_sku(self, product_sku: str) -> 'ProductDelete':
		"""
		Set Product_SKU.

		:param product_sku: str
		:returns: ProductDelete
		"""

		self.product_sku = product_sku
		return self

	# noinspection PyTypeChecker
	def send(self) -> 'merchantapi.response.ProductDelete':
		return super().send()

	def create_response(self, data) -> 'ProductDelete':
		"""
		Create a response object from the response data

		:param data:
		:returns: Response
		"""

		return merchantapi.response.ProductDelete(self, data)

	def to_dict(self) -> dict:
		"""
		Reduce the request to a dict

		:override:
		:returns: dict
		"""

		data = super().to_dict()

		if self.product_id is not None:
			data['Product_ID'] = self.product_id
		elif self.edit_product is not None:
			data['Edit_Product'] = self.edit_product
		elif self.product_code is not None:
			data['Product_Code'] = self.product_code
		elif self.product_sku is not None:
			data['Product_SKU'] = self.product_sku

		return data


"""
Handles API Request Product_Update.
Scope: Store.
:see: https://docs.miva.com/json-api/functions/product_update
"""


class ProductUpdate(merchantapi.abstract.Request):
	def __init__(self, client: Client = None, product: merchantapi.model.Product = None):
		"""
		ProductUpdate Constructor.

		:param client: Client
		:param product: Product
		"""

		super().__init__(client)
		self.product_id = None
		self.product_code = None
		self.edit_product = None
		self.product_sku = None
		self.product_name = None
		self.product_description = None
		self.product_canonical_category_code = None
		self.product_alternate_display_page = None
		self.product_page_title = None
		self.product_thumbnail = None
		self.product_image = None
		self.product_price = None
		self.product_cost = None
		self.product_weight = None
		self.product_inventory = None
		self.product_taxable = False
		self.product_active = False
		self.custom_field_values = merchantapi.model.CustomFieldValues()
		if isinstance(product, merchantapi.model.Product):
			if product.get_id():
				self.set_product_id(product.get_id())
			elif product.get_code():
				self.set_edit_product(product.get_code())

			self.set_product_code(product.get_code())
			self.set_product_sku(product.get_sku())
			self.set_product_name(product.get_name())
			self.set_product_description(product.get_description())
			self.set_product_canonical_category_code(product.get_canonical_category_code())
			self.set_product_alternate_display_page(product.get_page_code())
			self.set_product_page_title(product.get_page_title())
			self.set_product_thumbnail(product.get_thumbnail())
			self.set_product_image(product.get_image())
			self.set_product_price(product.get_price())
			self.set_product_cost(product.get_cost())
			self.set_product_weight(product.get_weight())
			self.set_product_inventory(product.get_product_inventory())
			self.set_product_taxable(product.get_taxable())
			self.set_product_active(product.get_active())

			if product.get_custom_field_values():
				self.set_custom_field_values(product.get_custom_field_values())

	def get_function(self):
		"""
		Get the function of the request.

		:returns: str
		"""

		return 'Product_Update'

	def get_product_id(self) -> int:
		"""
		Get Product_ID.

		:returns: int
		"""

		return self.product_id

	def get_product_code(self) -> str:
		"""
		Get Product_Code.

		:returns: str
		"""

		return self.product_code

	def get_edit_product(self) -> str:
		"""
		Get Edit_Product.

		:returns: str
		"""

		return self.edit_product

	def get_product_sku(self) -> str:
		"""
		Get Product_SKU.

		:returns: str
		"""

		return self.product_sku

	def get_product_name(self) -> str:
		"""
		Get Product_Name.

		:returns: str
		"""

		return self.product_name

	def get_product_description(self) -> str:
		"""
		Get Product_Description.

		:returns: str
		"""

		return self.product_description

	def get_product_canonical_category_code(self) -> str:
		"""
		Get Product_Canonical_Category_Code.

		:returns: str
		"""

		return self.product_canonical_category_code

	def get_product_alternate_display_page(self) -> str:
		"""
		Get Product_Alternate_Display_Page.

		:returns: str
		"""

		return self.product_alternate_display_page

	def get_product_page_title(self) -> str:
		"""
		Get Product_Page_Title.

		:returns: str
		"""

		return self.product_page_title

	def get_product_thumbnail(self) -> str:
		"""
		Get Product_Thumbnail.

		:returns: str
		"""

		return self.product_thumbnail

	def get_product_image(self) -> str:
		"""
		Get Product_Image.

		:returns: str
		"""

		return self.product_image

	def get_product_price(self) -> float:
		"""
		Get Product_Price.

		:returns: float
		"""

		return self.product_price

	def get_product_cost(self) -> float:
		"""
		Get Product_Cost.

		:returns: float
		"""

		return self.product_cost

	def get_product_weight(self) -> float:
		"""
		Get Product_Weight.

		:returns: float
		"""

		return self.product_weight

	def get_product_inventory(self) -> int:
		"""
		Get Product_Inventory.

		:returns: int
		"""

		return self.product_inventory

	def get_product_taxable(self) -> bool:
		"""
		Get Product_Taxable.

		:returns: bool
		"""

		return self.product_taxable

	def get_product_active(self) -> bool:
		"""
		Get Product_Active.

		:returns: bool
		"""

		return self.product_active

	def get_custom_field_values(self) -> merchantapi.model.CustomFieldValues:
		"""
		Get CustomField_Values.

		:returns: CustomFieldValues}|None
		"""

		return self.custom_field_values

	def set_product_id(self, product_id: int) -> 'ProductUpdate':
		"""
		Set Product_ID.

		:param product_id: int
		:returns: ProductUpdate
		"""

		self.product_id = product_id
		return self

	def set_product_code(self, product_code: str) -> 'ProductUpdate':
		"""
		Set Product_Code.

		:param product_code: str
		:returns: ProductUpdate
		"""

		self.product_code = product_code
		return self

	def set_edit_product(self, edit_product: str) -> 'ProductUpdate':
		"""
		Set Edit_Product.

		:param edit_product: str
		:returns: ProductUpdate
		"""

		self.edit_product = edit_product
		return self

	def set_product_sku(self, product_sku: str) -> 'ProductUpdate':
		"""
		Set Product_SKU.

		:param product_sku: str
		:returns: ProductUpdate
		"""

		self.product_sku = product_sku
		return self

	def set_product_name(self, product_name: str) -> 'ProductUpdate':
		"""
		Set Product_Name.

		:param product_name: str
		:returns: ProductUpdate
		"""

		self.product_name = product_name
		return self

	def set_product_description(self, product_description: str) -> 'ProductUpdate':
		"""
		Set Product_Description.

		:param product_description: str
		:returns: ProductUpdate
		"""

		self.product_description = product_description
		return self

	def set_product_canonical_category_code(self, product_canonical_category_code: str) -> 'ProductUpdate':
		"""
		Set Product_Canonical_Category_Code.

		:param product_canonical_category_code: str
		:returns: ProductUpdate
		"""

		self.product_canonical_category_code = product_canonical_category_code
		return self

	def set_product_alternate_display_page(self, product_alternate_display_page: str) -> 'ProductUpdate':
		"""
		Set Product_Alternate_Display_Page.

		:param product_alternate_display_page: str
		:returns: ProductUpdate
		"""

		self.product_alternate_display_page = product_alternate_display_page
		return self

	def set_product_page_title(self, product_page_title: str) -> 'ProductUpdate':
		"""
		Set Product_Page_Title.

		:param product_page_title: str
		:returns: ProductUpdate
		"""

		self.product_page_title = product_page_title
		return self

	def set_product_thumbnail(self, product_thumbnail: str) -> 'ProductUpdate':
		"""
		Set Product_Thumbnail.

		:param product_thumbnail: str
		:returns: ProductUpdate
		"""

		self.product_thumbnail = product_thumbnail
		return self

	def set_product_image(self, product_image: str) -> 'ProductUpdate':
		"""
		Set Product_Image.

		:param product_image: str
		:returns: ProductUpdate
		"""

		self.product_image = product_image
		return self

	def set_product_price(self, product_price: float) -> 'ProductUpdate':
		"""
		Set Product_Price.

		:param product_price: float
		:returns: ProductUpdate
		"""

		self.product_price = product_price
		return self

	def set_product_cost(self, product_cost: float) -> 'ProductUpdate':
		"""
		Set Product_Cost.

		:param product_cost: float
		:returns: ProductUpdate
		"""

		self.product_cost = product_cost
		return self

	def set_product_weight(self, product_weight: float) -> 'ProductUpdate':
		"""
		Set Product_Weight.

		:param product_weight: float
		:returns: ProductUpdate
		"""

		self.product_weight = product_weight
		return self

	def set_product_inventory(self, product_inventory: int) -> 'ProductUpdate':
		"""
		Set Product_Inventory.

		:param product_inventory: int
		:returns: ProductUpdate
		"""

		self.product_inventory = product_inventory
		return self

	def set_product_taxable(self, product_taxable: bool) -> 'ProductUpdate':
		"""
		Set Product_Taxable.

		:param product_taxable: bool
		:returns: ProductUpdate
		"""

		self.product_taxable = product_taxable
		return self

	def set_product_active(self, product_active: bool) -> 'ProductUpdate':
		"""
		Set Product_Active.

		:param product_active: bool
		:returns: ProductUpdate
		"""

		self.product_active = product_active
		return self

	def set_custom_field_values(self, custom_field_values: merchantapi.model.CustomFieldValues) -> 'ProductUpdate':
		"""
		Set CustomField_Values.

		:param custom_field_values: CustomFieldValues}|None
		:raises Exception:
		:returns: ProductUpdate
		"""

		if not isinstance(custom_field_values, merchantapi.model.CustomFieldValues):
			raise Exception("")
		self.custom_field_values = custom_field_values
		return self

	# noinspection PyTypeChecker
	def send(self) -> 'merchantapi.response.ProductUpdate':
		return super().send()

	def create_response(self, data) -> 'ProductUpdate':
		"""
		Create a response object from the response data

		:param data:
		:returns: Response
		"""

		return merchantapi.response.ProductUpdate(self, data)

	def to_dict(self) -> dict:
		"""
		Reduce the request to a dict

		:override:
		:returns: dict
		"""

		data = super().to_dict()

		if self.product_id is not None:
			data['Product_ID'] = self.product_id
		elif self.edit_product is not None:
			data['Edit_Product'] = self.edit_product

		if self.product_code is not None:
			data['Product_Code'] = self.product_code
		if self.product_sku is not None:
			data['Product_SKU'] = self.product_sku
		if self.product_name is not None:
			data['Product_Name'] = self.product_name
		if self.product_description is not None:
			data['Product_Description'] = self.product_description
		if self.product_canonical_category_code is not None:
			data['Product_Canonical_Category_Code'] = self.product_canonical_category_code
		if self.product_alternate_display_page is not None:
			data['Product_Alternate_Display_Page'] = self.product_alternate_display_page
		if self.product_page_title is not None:
			data['Product_Page_Title'] = self.product_page_title
		if self.product_thumbnail is not None:
			data['Product_Thumbnail'] = self.product_thumbnail
		if self.product_image is not None:
			data['Product_Image'] = self.product_image
		if self.product_price is not None:
			data['Product_Price'] = self.product_price
		if self.product_cost is not None:
			data['Product_Cost'] = self.product_cost
		if self.product_weight is not None:
			data['Product_Weight'] = self.product_weight
		if self.product_inventory is not None:
			data['Product_Inventory'] = self.product_inventory
		if self.product_taxable is not None:
			data['Product_Taxable'] = self.product_taxable
		if self.product_active is not None:
			data['Product_Active'] = self.product_active
		if self.custom_field_values is not None:
			data['CustomField_Values'] = self.custom_field_values.to_dict()
		return data


"""
Handles API Request Provision_Domain.
Scope: Domain.
:see: https://docs.miva.com/json-api/functions/provision_domain
"""


class ProvisionDomain(merchantapi.abstract.Request):
	def __init__(self, client: Client = None):
		"""
		ProvisionDomain Constructor.

		:param client: Client
		"""

		super().__init__(client)
		self.xml = None

	def get_function(self):
		"""
		Get the function of the request.

		:returns: str
		"""

		return 'Provision_Domain'

	def get_xml(self) -> str:
		"""
		Get xml.

		:returns: str
		"""

		return self.xml

	def set_xml(self, xml: str) -> 'ProvisionDomain':
		"""
		Set xml.

		:param xml: str
		:returns: ProvisionDomain
		"""

		self.xml = xml
		return self

	# noinspection PyTypeChecker
	def send(self) -> 'merchantapi.response.ProvisionDomain':
		return super().send()

	def create_response(self, data) -> 'ProvisionDomain':
		"""
		Create a response object from the response data

		:param data:
		:returns: Response
		"""

		return merchantapi.response.ProvisionDomain(self, data)

	def to_dict(self) -> dict:
		"""
		Reduce the request to a dict

		:override:
		:returns: dict
		"""

		data = super().to_dict()

		data['XML'] = self.xml
		return data


"""
Handles API Request Provision_Store.
Scope: Store.
:see: https://docs.miva.com/json-api/functions/provision_store
"""


class ProvisionStore(merchantapi.abstract.Request):
	def __init__(self, client: Client = None):
		"""
		ProvisionStore Constructor.

		:param client: Client
		"""

		super().__init__(client)
		self.xml = None

	def get_function(self):
		"""
		Get the function of the request.

		:returns: str
		"""

		return 'Provision_Store'

	def get_xml(self) -> str:
		"""
		Get xml.

		:returns: str
		"""

		return self.xml

	def set_xml(self, xml: str) -> 'ProvisionStore':
		"""
		Set xml.

		:param xml: str
		:returns: ProvisionStore
		"""

		self.xml = xml
		return self

	# noinspection PyTypeChecker
	def send(self) -> 'merchantapi.response.ProvisionStore':
		return super().send()

	def create_response(self, data) -> 'ProvisionStore':
		"""
		Create a response object from the response data

		:param data:
		:returns: Response
		"""

		return merchantapi.response.ProvisionStore(self, data)

	def to_dict(self) -> dict:
		"""
		Reduce the request to a dict

		:override:
		:returns: dict
		"""

		data = super().to_dict()

		data['XML'] = self.xml
		return data


"""
Handles API Request CustomerAddressList_Load_Query.
Scope: Store.
:see: https://docs.miva.com/json-api/functions/customeraddresslist_load_query
"""


class CustomerAddressListLoadQuery(ListQueryRequest):

	available_search_fields = [
		'cust_id',
		'id',
		'descrip',
		'fname',
		'lname',
		'email',
		'comp',
		'phone',
		'fax',
		'addr1',
		'addr2',
		'city',
		'state',
		'zip',
		'cntry',
		'resdntl'
	]

	available_sort_fields = [
		'cust_id',
		'id',
		'descrip',
		'fname',
		'lname',
		'email',
		'comp',
		'phone',
		'fax',
		'addr1',
		'addr2',
		'city',
		'state',
		'zip',
		'cntry',
		'resdntl'
	]

	def __init__(self, client: Client = None, customer: merchantapi.model.Customer = None):
		"""
		CustomerAddressListLoadQuery Constructor.

		:param client: Client
		:param customer: Customer
		"""

		super().__init__(client)
		self.customer_id = None
		self.edit_customer = None
		self.customer_login = None
		if isinstance(customer, merchantapi.model.Customer):
			if customer.get_id():
				self.set_customer_id(customer.get_id())
			elif customer.get_login():
				self.set_edit_customer(customer.get_login())

	def get_function(self):
		"""
		Get the function of the request.

		:returns: str
		"""

		return 'CustomerAddressList_Load_Query'

	def get_customer_id(self) -> int:
		"""
		Get Customer_ID.

		:returns: int
		"""

		return self.customer_id

	def get_edit_customer(self) -> str:
		"""
		Get Edit_Customer.

		:returns: str
		"""

		return self.edit_customer

	def get_customer_login(self) -> str:
		"""
		Get Customer_Login.

		:returns: str
		"""

		return self.customer_login

	def set_customer_id(self, customer_id: int) -> 'CustomerAddressListLoadQuery':
		"""
		Set Customer_ID.

		:param customer_id: int
		:returns: CustomerAddressListLoadQuery
		"""

		self.customer_id = customer_id
		return self

	def set_edit_customer(self, edit_customer: str) -> 'CustomerAddressListLoadQuery':
		"""
		Set Edit_Customer.

		:param edit_customer: str
		:returns: CustomerAddressListLoadQuery
		"""

		self.edit_customer = edit_customer
		return self

	def set_customer_login(self, customer_login: str) -> 'CustomerAddressListLoadQuery':
		"""
		Set Customer_Login.

		:param customer_login: str
		:returns: CustomerAddressListLoadQuery
		"""

		self.customer_login = customer_login
		return self

	# noinspection PyTypeChecker
	def send(self) -> 'merchantapi.response.CustomerAddressListLoadQuery':
		return super().send()

	def create_response(self, data) -> 'CustomerAddressListLoadQuery':
		"""
		Create a response object from the response data

		:param data:
		:returns: Response
		"""

		return merchantapi.response.CustomerAddressListLoadQuery(self, data)

	def to_dict(self) -> dict:
		"""
		Reduce the request to a dict

		:override:
		:returns: dict
		"""

		data = super().to_dict()

		if self.customer_id is not None:
			data['Customer_ID'] = self.customer_id
		elif self.edit_customer is not None:
			data['Edit_Customer'] = self.edit_customer
		elif self.customer_login is not None:
			data['Customer_Login'] = self.customer_login

		return data


"""
Handles API Request PrintQueueList_Load_Query.
Scope: Domain.
:see: https://docs.miva.com/json-api/functions/printqueuelist_load_query
"""


class PrintQueueListLoadQuery(ListQueryRequest):

	available_search_fields = [
		'descrip'
	]

	available_sort_fields = [
		'descrip'
	]

	def __init__(self, client: Client = None):
		"""
		PrintQueueListLoadQuery Constructor.

		:param client: Client
		"""

		super().__init__(client)

	def get_function(self):
		"""
		Get the function of the request.

		:returns: str
		"""

		return 'PrintQueueList_Load_Query'

	# noinspection PyTypeChecker
	def send(self) -> 'merchantapi.response.PrintQueueListLoadQuery':
		return super().send()

	def create_response(self, data) -> 'PrintQueueListLoadQuery':
		"""
		Create a response object from the response data

		:param data:
		:returns: Response
		"""

		return merchantapi.response.PrintQueueListLoadQuery(self, data)


"""
Handles API Request PrintQueueJobList_Load_Query.
Scope: Domain.
:see: https://docs.miva.com/json-api/functions/printqueuejoblist_load_query
"""


class PrintQueueJobListLoadQuery(ListQueryRequest):

	available_search_fields = [
		'id',
		'queue_id',
		'store_id',
		'user_id',
		'descrip',
		'job_fmt',
		'job_data',
		'dt_created'
	]

	available_sort_fields = [
		'id',
		'queue_id',
		'store_id',
		'user_id',
		'descrip',
		'job_fmt',
		'job_data',
		'dt_created'
	]

	available_on_demand_columns = [
		'job_data'
	]

	def __init__(self, client: Client = None, print_queue: merchantapi.model.PrintQueue = None):
		"""
		PrintQueueJobListLoadQuery Constructor.

		:param client: Client
		:param print_queue: PrintQueue
		"""

		super().__init__(client)
		self.print_queue_id = None
		self.edit_print_queue = None
		self.print_queue_description = None
		if isinstance(print_queue, merchantapi.model.PrintQueue):
			if print_queue.get_id():
				self.set_print_queue_id(print_queue.get_id())
			elif print_queue.get_description():
				self.set_edit_print_queue(print_queue.get_description())

	def get_function(self):
		"""
		Get the function of the request.

		:returns: str
		"""

		return 'PrintQueueJobList_Load_Query'

	def get_print_queue_id(self) -> int:
		"""
		Get PrintQueue_ID.

		:returns: int
		"""

		return self.print_queue_id

	def get_edit_print_queue(self) -> str:
		"""
		Get Edit_PrintQueue.

		:returns: str
		"""

		return self.edit_print_queue

	def get_print_queue_description(self) -> str:
		"""
		Get PrintQueue_Description.

		:returns: str
		"""

		return self.print_queue_description

	def set_print_queue_id(self, print_queue_id: int) -> 'PrintQueueJobListLoadQuery':
		"""
		Set PrintQueue_ID.

		:param print_queue_id: int
		:returns: PrintQueueJobListLoadQuery
		"""

		self.print_queue_id = print_queue_id
		return self

	def set_edit_print_queue(self, edit_print_queue: str) -> 'PrintQueueJobListLoadQuery':
		"""
		Set Edit_PrintQueue.

		:param edit_print_queue: str
		:returns: PrintQueueJobListLoadQuery
		"""

		self.edit_print_queue = edit_print_queue
		return self

	def set_print_queue_description(self, print_queue_description: str) -> 'PrintQueueJobListLoadQuery':
		"""
		Set PrintQueue_Description.

		:param print_queue_description: str
		:returns: PrintQueueJobListLoadQuery
		"""

		self.print_queue_description = print_queue_description
		return self

	# noinspection PyTypeChecker
	def send(self) -> 'merchantapi.response.PrintQueueJobListLoadQuery':
		return super().send()

	def create_response(self, data) -> 'PrintQueueJobListLoadQuery':
		"""
		Create a response object from the response data

		:param data:
		:returns: Response
		"""

		return merchantapi.response.PrintQueueJobListLoadQuery(self, data)

	def to_dict(self) -> dict:
		"""
		Reduce the request to a dict

		:override:
		:returns: dict
		"""

		data = super().to_dict()

		if self.print_queue_id is not None:
			data['PrintQueue_ID'] = self.print_queue_id
		elif self.edit_print_queue is not None:
			data['Edit_PrintQueue'] = self.edit_print_queue
		elif self.print_queue_description is not None:
			data['PrintQueue_Description'] = self.print_queue_description

		return data


"""
Handles API Request PrintQueueJob_Delete.
Scope: Store.
:see: https://docs.miva.com/json-api/functions/printqueuejob_delete
"""


class PrintQueueJobDelete(merchantapi.abstract.Request):
	def __init__(self, client: Client = None, print_queue_job: merchantapi.model.PrintQueueJob = None):
		"""
		PrintQueueJobDelete Constructor.

		:param client: Client
		:param print_queue_job: PrintQueueJob
		"""

		super().__init__(client)
		self.print_queue_job_id = None
		if isinstance(print_queue_job, merchantapi.model.PrintQueueJob):
			if print_queue_job.get_id():
				self.set_print_queue_job_id(print_queue_job.get_id())

	def get_function(self):
		"""
		Get the function of the request.

		:returns: str
		"""

		return 'PrintQueueJob_Delete'

	def get_print_queue_job_id(self) -> int:
		"""
		Get PrintQueueJob_ID.

		:returns: int
		"""

		return self.print_queue_job_id

	def set_print_queue_job_id(self, print_queue_job_id: int) -> 'PrintQueueJobDelete':
		"""
		Set PrintQueueJob_ID.

		:param print_queue_job_id: int
		:returns: PrintQueueJobDelete
		"""

		self.print_queue_job_id = print_queue_job_id
		return self

	# noinspection PyTypeChecker
	def send(self) -> 'merchantapi.response.PrintQueueJobDelete':
		return super().send()

	def create_response(self, data) -> 'PrintQueueJobDelete':
		"""
		Create a response object from the response data

		:param data:
		:returns: Response
		"""

		return merchantapi.response.PrintQueueJobDelete(self, data)

	def to_dict(self) -> dict:
		"""
		Reduce the request to a dict

		:override:
		:returns: dict
		"""

		data = super().to_dict()

		if self.print_queue_job_id is not None:
			data['PrintQueueJob_ID'] = self.print_queue_job_id

		return data


"""
Handles API Request PrintQueueJob_Insert.
Scope: Store.
:see: https://docs.miva.com/json-api/functions/printqueuejob_insert
"""


class PrintQueueJobInsert(merchantapi.abstract.Request):
	def __init__(self, client: Client = None, print_queue: merchantapi.model.PrintQueue = None):
		"""
		PrintQueueJobInsert Constructor.

		:param client: Client
		:param print_queue: PrintQueue
		"""

		super().__init__(client)
		self.print_queue_id = None
		self.edit_print_queue = None
		self.print_queue_description = None
		self.print_queue_job_description = None
		self.print_queue_job_format = None
		self.print_queue_job_data = None
		if isinstance(print_queue, merchantapi.model.PrintQueue):
			if print_queue.get_id():
				self.set_print_queue_id(print_queue.get_id())
			elif print_queue.get_description():
				self.set_edit_print_queue(print_queue.get_description())

	def get_function(self):
		"""
		Get the function of the request.

		:returns: str
		"""

		return 'PrintQueueJob_Insert'

	def get_print_queue_id(self) -> int:
		"""
		Get PrintQueue_ID.

		:returns: int
		"""

		return self.print_queue_id

	def get_edit_print_queue(self) -> str:
		"""
		Get Edit_PrintQueue.

		:returns: str
		"""

		return self.edit_print_queue

	def get_print_queue_description(self) -> str:
		"""
		Get PrintQueue_Description.

		:returns: str
		"""

		return self.print_queue_description

	def get_print_queue_job_description(self) -> str:
		"""
		Get PrintQueueJob_Description.

		:returns: str
		"""

		return self.print_queue_job_description

	def get_print_queue_job_format(self) -> str:
		"""
		Get PrintQueueJob_Format.

		:returns: str
		"""

		return self.print_queue_job_format

	def get_print_queue_job_data(self) -> str:
		"""
		Get PrintQueueJob_Data.

		:returns: str
		"""

		return self.print_queue_job_data

	def set_print_queue_id(self, print_queue_id: int) -> 'PrintQueueJobInsert':
		"""
		Set PrintQueue_ID.

		:param print_queue_id: int
		:returns: PrintQueueJobInsert
		"""

		self.print_queue_id = print_queue_id
		return self

	def set_edit_print_queue(self, edit_print_queue: str) -> 'PrintQueueJobInsert':
		"""
		Set Edit_PrintQueue.

		:param edit_print_queue: str
		:returns: PrintQueueJobInsert
		"""

		self.edit_print_queue = edit_print_queue
		return self

	def set_print_queue_description(self, print_queue_description: str) -> 'PrintQueueJobInsert':
		"""
		Set PrintQueue_Description.

		:param print_queue_description: str
		:returns: PrintQueueJobInsert
		"""

		self.print_queue_description = print_queue_description
		return self

	def set_print_queue_job_description(self, print_queue_job_description: str) -> 'PrintQueueJobInsert':
		"""
		Set PrintQueueJob_Description.

		:param print_queue_job_description: str
		:returns: PrintQueueJobInsert
		"""

		self.print_queue_job_description = print_queue_job_description
		return self

	def set_print_queue_job_format(self, print_queue_job_format: str) -> 'PrintQueueJobInsert':
		"""
		Set PrintQueueJob_Format.

		:param print_queue_job_format: str
		:returns: PrintQueueJobInsert
		"""

		self.print_queue_job_format = print_queue_job_format
		return self

	def set_print_queue_job_data(self, print_queue_job_data: str) -> 'PrintQueueJobInsert':
		"""
		Set PrintQueueJob_Data.

		:param print_queue_job_data: str
		:returns: PrintQueueJobInsert
		"""

		self.print_queue_job_data = print_queue_job_data
		return self

	# noinspection PyTypeChecker
	def send(self) -> 'merchantapi.response.PrintQueueJobInsert':
		return super().send()

	def create_response(self, data) -> 'PrintQueueJobInsert':
		"""
		Create a response object from the response data

		:param data:
		:returns: Response
		"""

		return merchantapi.response.PrintQueueJobInsert(self, data)

	def to_dict(self) -> dict:
		"""
		Reduce the request to a dict

		:override:
		:returns: dict
		"""

		data = super().to_dict()

		if self.print_queue_id is not None:
			data['PrintQueue_ID'] = self.print_queue_id
		elif self.edit_print_queue is not None:
			data['Edit_PrintQueue'] = self.edit_print_queue
		elif self.print_queue_description is not None:
			data['PrintQueue_Description'] = self.print_queue_description

		if self.print_queue_job_description is not None:
			data['PrintQueueJob_Description'] = self.print_queue_job_description
		if self.print_queue_job_format is not None:
			data['PrintQueueJob_Format'] = self.print_queue_job_format
		if self.print_queue_job_data is not None:
			data['PrintQueueJob_Data'] = self.print_queue_job_data
		return data


"""
Handles API Request PrintQueueJob_Status.
Scope: Store.
:see: https://docs.miva.com/json-api/functions/printqueuejob_status
"""


class PrintQueueJobStatus(merchantapi.abstract.Request):
	def __init__(self, client: Client = None, print_queue_job: merchantapi.model.PrintQueueJob = None):
		"""
		PrintQueueJobStatus Constructor.

		:param client: Client
		:param print_queue_job: PrintQueueJob
		"""

		super().__init__(client)
		self.print_queue_job_id = None
		if isinstance(print_queue_job, merchantapi.model.PrintQueueJob):
			if print_queue_job.get_id():
				self.set_print_queue_job_id(print_queue_job.get_id())

	def get_function(self):
		"""
		Get the function of the request.

		:returns: str
		"""

		return 'PrintQueueJob_Status'

	def get_print_queue_job_id(self) -> int:
		"""
		Get PrintQueueJob_ID.

		:returns: int
		"""

		return self.print_queue_job_id

	def set_print_queue_job_id(self, print_queue_job_id: int) -> 'PrintQueueJobStatus':
		"""
		Set PrintQueueJob_ID.

		:param print_queue_job_id: int
		:returns: PrintQueueJobStatus
		"""

		self.print_queue_job_id = print_queue_job_id
		return self

	# noinspection PyTypeChecker
	def send(self) -> 'merchantapi.response.PrintQueueJobStatus':
		return super().send()

	def create_response(self, data) -> 'PrintQueueJobStatus':
		"""
		Create a response object from the response data

		:param data:
		:returns: Response
		"""

		return merchantapi.response.PrintQueueJobStatus(self, data)

	def to_dict(self) -> dict:
		"""
		Reduce the request to a dict

		:override:
		:returns: dict
		"""

		data = super().to_dict()

		if self.print_queue_job_id is not None:
			data['PrintQueueJob_ID'] = self.print_queue_job_id

		return data


"""
Handles API Request PaymentMethodList_Load.
Scope: Store.
:see: https://docs.miva.com/json-api/functions/paymentmethodlist_load
"""


class PaymentMethodListLoad(merchantapi.abstract.Request):
	def __init__(self, client: Client = None, order: merchantapi.model.Order = None):
		"""
		PaymentMethodListLoad Constructor.

		:param client: Client
		:param order: Order
		"""

		super().__init__(client)
		self.order_id = None
		if isinstance(order, merchantapi.model.Order):
			self.set_order_id(order.get_id())

	def get_function(self):
		"""
		Get the function of the request.

		:returns: str
		"""

		return 'PaymentMethodList_Load'

	def get_order_id(self) -> int:
		"""
		Get Order_ID.

		:returns: int
		"""

		return self.order_id

	def set_order_id(self, order_id: int) -> 'PaymentMethodListLoad':
		"""
		Set Order_ID.

		:param order_id: int
		:returns: PaymentMethodListLoad
		"""

		self.order_id = order_id
		return self

	# noinspection PyTypeChecker
	def send(self) -> 'merchantapi.response.PaymentMethodListLoad':
		return super().send()

	def create_response(self, data) -> 'PaymentMethodListLoad':
		"""
		Create a response object from the response data

		:param data:
		:returns: Response
		"""

		return merchantapi.response.PaymentMethodListLoad(self, data)

	def to_dict(self) -> dict:
		"""
		Reduce the request to a dict

		:override:
		:returns: dict
		"""

		data = super().to_dict()

		if self.order_id is not None:
			data['Order_ID'] = self.order_id
		return data


"""
Handles API Request Order_Create_FromOrder.
Scope: Store.
:see: https://docs.miva.com/json-api/functions/order_create_fromorder
"""


class OrderCreateFromOrder(merchantapi.abstract.Request):
	def __init__(self, client: Client = None, order: merchantapi.model.Order = None):
		"""
		OrderCreateFromOrder Constructor.

		:param client: Client
		:param order: Order
		"""

		super().__init__(client)
		self.order_id = None
		if isinstance(order, merchantapi.model.Order):
			if order.get_id():
				self.set_order_id(order.get_id())

	def get_function(self):
		"""
		Get the function of the request.

		:returns: str
		"""

		return 'Order_Create_FromOrder'

	def get_order_id(self) -> int:
		"""
		Get Order_ID.

		:returns: int
		"""

		return self.order_id

	def set_order_id(self, order_id: int) -> 'OrderCreateFromOrder':
		"""
		Set Order_ID.

		:param order_id: int
		:returns: OrderCreateFromOrder
		"""

		self.order_id = order_id
		return self

	# noinspection PyTypeChecker
	def send(self) -> 'merchantapi.response.OrderCreateFromOrder':
		return super().send()

	def create_response(self, data) -> 'OrderCreateFromOrder':
		"""
		Create a response object from the response data

		:param data:
		:returns: Response
		"""

		return merchantapi.response.OrderCreateFromOrder(self, data)

	def to_dict(self) -> dict:
		"""
		Reduce the request to a dict

		:override:
		:returns: dict
		"""

		data = super().to_dict()

		if self.order_id is not None:
			data['Order_ID'] = self.order_id

		return data


"""
Handles API Request Order_Authorize.
Scope: Store.
:see: https://docs.miva.com/json-api/functions/order_authorize
"""


class OrderAuthorize(merchantapi.abstract.Request):
	def __init__(self, client: Client = None, order: merchantapi.model.Order = None):
		"""
		OrderAuthorize Constructor.

		:param client: Client
		:param order: Order
		"""

		super().__init__(client)
		self.order_id = None
		self.module_id = None
		self.module_data = None
		self.amount = None
		self.module_fields = {}
		if isinstance(order, merchantapi.model.Order):
			if order.get_id():
				self.set_order_id(order.get_id())

	def get_function(self):
		"""
		Get the function of the request.

		:returns: str
		"""

		return 'Order_Authorize'

	def get_order_id(self) -> int:
		"""
		Get Order_ID.

		:returns: int
		"""

		return self.order_id

	def get_module_id(self) -> int:
		"""
		Get Module_ID.

		:returns: int
		"""

		return self.module_id

	def get_module_data(self) -> str:
		"""
		Get Module_Data.

		:returns: str
		"""

		return self.module_data

	def get_amount(self) -> float:
		"""
		Get Amount.

		:returns: float
		"""

		return self.amount

	def get_module_fields(self):
		"""
		Get Module_Fields.

		:returns: dict
		"""

		return self.module_fields

	def set_order_id(self, order_id: int) -> 'OrderAuthorize':
		"""
		Set Order_ID.

		:param order_id: int
		:returns: OrderAuthorize
		"""

		self.order_id = order_id
		return self

	def set_module_id(self, module_id: int) -> 'OrderAuthorize':
		"""
		Set Module_ID.

		:param module_id: int
		:returns: OrderAuthorize
		"""

		self.module_id = module_id
		return self

	def set_module_data(self, module_data: str) -> 'OrderAuthorize':
		"""
		Set Module_Data.

		:param module_data: str
		:returns: OrderAuthorize
		"""

		self.module_data = module_data
		return self

	def set_amount(self, amount: float) -> 'OrderAuthorize':
		"""
		Set Amount.

		:param amount: float
		:returns: OrderAuthorize
		"""

		self.amount = amount
		return self

	def set_module_fields(self, module_fields) -> 'OrderAuthorize':
		"""
		Set Module_Fields.

		:param module_fields: dict
		:returns: OrderAuthorize
		"""

		self.module_fields = module_fields
		return self

	def set_module_field(self, field: str, value) -> 'OrderAuthorize':
		"""
		Add custom data to the request.

		:param field: str
		:param value: mixed
		:returns: {OrderAuthorize}
		"""

		self.module_fields[field] = value
		return self

	# noinspection PyTypeChecker
	def send(self) -> 'merchantapi.response.OrderAuthorize':
		return super().send()

	def create_response(self, data) -> 'OrderAuthorize':
		"""
		Create a response object from the response data

		:param data:
		:returns: Response
		"""

		return merchantapi.response.OrderAuthorize(self, data)

	def to_dict(self) -> dict:
		"""
		Reduce the request to a dict

		:override:
		:returns: dict
		"""

		data = super().to_dict()
		data.update(self.get_module_fields())

		if self.order_id is not None:
			data['Order_ID'] = self.order_id

		if self.module_id is not None:
			data['Module_ID'] = self.module_id
		if self.module_data is not None:
			data['Module_Data'] = self.module_data
		data['Amount'] = self.amount
		return data


"""
Handles API Request CustomerPaymentCardList_Load_Query.
Scope: Store.
:see: https://docs.miva.com/json-api/functions/customerpaymentcardlist_load_query
"""


class CustomerPaymentCardListLoadQuery(ListQueryRequest):

	available_search_fields = [
		'fname',
		'lname',
		'exp_month',
		'exp_year',
		'lastfour',
		'lastused',
		'type',
		'addr1',
		'addr2',
		'city',
		'state',
		'zip',
		'cntry',
		'refcount',
		'mod_code',
		'meth_code',
		'id'
	]

	available_sort_fields = [
		'fname',
		'lname',
		'expires',
		'lastfour',
		'lastused',
		'type',
		'addr1',
		'addr2',
		'city',
		'state',
		'zip',
		'cntry',
		'refcount',
		'mod_code',
		'meth_code',
		'id'
	]

	def __init__(self, client: Client = None, customer: merchantapi.model.Customer = None):
		"""
		CustomerPaymentCardListLoadQuery Constructor.

		:param client: Client
		:param customer: Customer
		"""

		super().__init__(client)
		self.customer_id = None
		self.edit_customer = None
		self.customer_login = None
		if isinstance(customer, merchantapi.model.Customer):
			if customer.get_id():
				self.set_customer_id(customer.get_id())
			elif customer.get_login():
				self.set_customer_login(customer.get_login())

	def get_function(self):
		"""
		Get the function of the request.

		:returns: str
		"""

		return 'CustomerPaymentCardList_Load_Query'

	def get_customer_id(self) -> int:
		"""
		Get Customer_ID.

		:returns: int
		"""

		return self.customer_id

	def get_edit_customer(self) -> str:
		"""
		Get Edit_Customer.

		:returns: str
		"""

		return self.edit_customer

	def get_customer_login(self) -> str:
		"""
		Get Customer_Login.

		:returns: str
		"""

		return self.customer_login

	def set_customer_id(self, customer_id: int) -> 'CustomerPaymentCardListLoadQuery':
		"""
		Set Customer_ID.

		:param customer_id: int
		:returns: CustomerPaymentCardListLoadQuery
		"""

		self.customer_id = customer_id
		return self

	def set_edit_customer(self, edit_customer: str) -> 'CustomerPaymentCardListLoadQuery':
		"""
		Set Edit_Customer.

		:param edit_customer: str
		:returns: CustomerPaymentCardListLoadQuery
		"""

		self.edit_customer = edit_customer
		return self

	def set_customer_login(self, customer_login: str) -> 'CustomerPaymentCardListLoadQuery':
		"""
		Set Customer_Login.

		:param customer_login: str
		:returns: CustomerPaymentCardListLoadQuery
		"""

		self.customer_login = customer_login
		return self

	# noinspection PyTypeChecker
	def send(self) -> 'merchantapi.response.CustomerPaymentCardListLoadQuery':
		return super().send()

	def create_response(self, data) -> 'CustomerPaymentCardListLoadQuery':
		"""
		Create a response object from the response data

		:param data:
		:returns: Response
		"""

		return merchantapi.response.CustomerPaymentCardListLoadQuery(self, data)

	def to_dict(self) -> dict:
		"""
		Reduce the request to a dict

		:override:
		:returns: dict
		"""

		data = super().to_dict()

		if self.customer_id is not None:
			data['Customer_ID'] = self.customer_id
		elif self.edit_customer is not None:
			data['Edit_Customer'] = self.edit_customer
		elif self.customer_login is not None:
			data['Customer_Login'] = self.customer_login

		return data


"""
Handles API Request CategoryProductList_Load_Query.
Scope: Store.
:see: https://docs.miva.com/json-api/functions/categoryproductlist_load_query
"""


class CategoryProductListLoadQuery(ProductListLoadQuery):
	def __init__(self, client: Client = None, category: merchantapi.model.Category = None):
		"""
		CategoryProductListLoadQuery Constructor.

		:param client: Client
		:param category: Category
		"""

		super().__init__(client)
		self.category_id = None
		self.category_code = None
		self.edit_category = None
		self.assigned = False
		self.unassigned = False
		if isinstance(category, merchantapi.model.Category):
			if category.get_id():
				self.set_category_id(category.get_id())
			elif category.get_code():
				self.set_edit_category(category.get_code())

	def get_function(self):
		"""
		Get the function of the request.

		:returns: str
		"""

		return 'CategoryProductList_Load_Query'

	def get_category_id(self) -> int:
		"""
		Get Category_ID.

		:returns: int
		"""

		return self.category_id

	def get_category_code(self) -> str:
		"""
		Get Category_Code.

		:returns: str
		"""

		return self.category_code

	def get_edit_category(self) -> str:
		"""
		Get Edit_Category.

		:returns: str
		"""

		return self.edit_category

	def get_assigned(self) -> bool:
		"""
		Get Assigned.

		:returns: bool
		"""

		return self.assigned

	def get_unassigned(self) -> bool:
		"""
		Get Unassigned.

		:returns: bool
		"""

		return self.unassigned

	def set_category_id(self, category_id: int) -> 'CategoryProductListLoadQuery':
		"""
		Set Category_ID.

		:param category_id: int
		:returns: CategoryProductListLoadQuery
		"""

		self.category_id = category_id
		return self

	def set_category_code(self, category_code: str) -> 'CategoryProductListLoadQuery':
		"""
		Set Category_Code.

		:param category_code: str
		:returns: CategoryProductListLoadQuery
		"""

		self.category_code = category_code
		return self

	def set_edit_category(self, edit_category: str) -> 'CategoryProductListLoadQuery':
		"""
		Set Edit_Category.

		:param edit_category: str
		:returns: CategoryProductListLoadQuery
		"""

		self.edit_category = edit_category
		return self

	def set_assigned(self, assigned: bool) -> 'CategoryProductListLoadQuery':
		"""
		Set Assigned.

		:param assigned: bool
		:returns: CategoryProductListLoadQuery
		"""

		self.assigned = assigned
		return self

	def set_unassigned(self, unassigned: bool) -> 'CategoryProductListLoadQuery':
		"""
		Set Unassigned.

		:param unassigned: bool
		:returns: CategoryProductListLoadQuery
		"""

		self.unassigned = unassigned
		return self

	# noinspection PyTypeChecker
	def send(self) -> 'merchantapi.response.CategoryProductListLoadQuery':
		return super().send()

	def create_response(self, data) -> 'CategoryProductListLoadQuery':
		"""
		Create a response object from the response data

		:param data:
		:returns: Response
		"""

		return merchantapi.response.CategoryProductListLoadQuery(self, data)

	def to_dict(self) -> dict:
		"""
		Reduce the request to a dict

		:override:
		:returns: dict
		"""

		data = super().to_dict()

		if self.category_id is not None:
			data['Category_ID'] = self.category_id
		elif self.edit_category is not None:
			data['Edit_Category'] = self.edit_category
		elif self.category_code is not None:
			data['Category_Code'] = self.category_code

		if self.assigned is not None:
			data['Assigned'] = self.assigned
		if self.unassigned is not None:
			data['Unassigned'] = self.unassigned
		return data


"""
Handles API Request CouponPriceGroupList_Load_Query.
Scope: Store.
:see: https://docs.miva.com/json-api/functions/couponpricegrouplist_load_query
"""


class CouponPriceGroupListLoadQuery(PriceGroupListLoadQuery):
	def __init__(self, client: Client = None, coupon: merchantapi.model.Coupon = None):
		"""
		CouponPriceGroupListLoadQuery Constructor.

		:param client: Client
		:param coupon: Coupon
		"""

		super().__init__(client)
		self.coupon_id = None
		self.edit_coupon = None
		self.coupon_code = None
		self.assigned = False
		self.unassigned = False
		if isinstance(coupon, merchantapi.model.Coupon):
			if coupon.get_id():
				self.set_coupon_id(coupon.get_id())
			elif coupon.get_code():
				self.set_edit_coupon(coupon.get_code())

	def get_function(self):
		"""
		Get the function of the request.

		:returns: str
		"""

		return 'CouponPriceGroupList_Load_Query'

	def get_coupon_id(self) -> int:
		"""
		Get Coupon_ID.

		:returns: int
		"""

		return self.coupon_id

	def get_edit_coupon(self) -> str:
		"""
		Get Edit_Coupon.

		:returns: str
		"""

		return self.edit_coupon

	def get_coupon_code(self) -> str:
		"""
		Get Coupon_Code.

		:returns: str
		"""

		return self.coupon_code

	def get_assigned(self) -> bool:
		"""
		Get Assigned.

		:returns: bool
		"""

		return self.assigned

	def get_unassigned(self) -> bool:
		"""
		Get Unassigned.

		:returns: bool
		"""

		return self.unassigned

	def set_coupon_id(self, coupon_id: int) -> 'CouponPriceGroupListLoadQuery':
		"""
		Set Coupon_ID.

		:param coupon_id: int
		:returns: CouponPriceGroupListLoadQuery
		"""

		self.coupon_id = coupon_id
		return self

	def set_edit_coupon(self, edit_coupon: str) -> 'CouponPriceGroupListLoadQuery':
		"""
		Set Edit_Coupon.

		:param edit_coupon: str
		:returns: CouponPriceGroupListLoadQuery
		"""

		self.edit_coupon = edit_coupon
		return self

	def set_coupon_code(self, coupon_code: str) -> 'CouponPriceGroupListLoadQuery':
		"""
		Set Coupon_Code.

		:param coupon_code: str
		:returns: CouponPriceGroupListLoadQuery
		"""

		self.coupon_code = coupon_code
		return self

	def set_assigned(self, assigned: bool) -> 'CouponPriceGroupListLoadQuery':
		"""
		Set Assigned.

		:param assigned: bool
		:returns: CouponPriceGroupListLoadQuery
		"""

		self.assigned = assigned
		return self

	def set_unassigned(self, unassigned: bool) -> 'CouponPriceGroupListLoadQuery':
		"""
		Set Unassigned.

		:param unassigned: bool
		:returns: CouponPriceGroupListLoadQuery
		"""

		self.unassigned = unassigned
		return self

	# noinspection PyTypeChecker
	def send(self) -> 'merchantapi.response.CouponPriceGroupListLoadQuery':
		return super().send()

	def create_response(self, data) -> 'CouponPriceGroupListLoadQuery':
		"""
		Create a response object from the response data

		:param data:
		:returns: Response
		"""

		return merchantapi.response.CouponPriceGroupListLoadQuery(self, data)

	def to_dict(self) -> dict:
		"""
		Reduce the request to a dict

		:override:
		:returns: dict
		"""

		data = super().to_dict()

		if self.coupon_id is not None:
			data['Coupon_ID'] = self.coupon_id
		elif self.edit_coupon is not None:
			data['Edit_Coupon'] = self.edit_coupon
		elif self.coupon_code is not None:
			data['Coupon_Code'] = self.coupon_code

		if self.assigned is not None:
			data['Assigned'] = self.assigned
		if self.unassigned is not None:
			data['Unassigned'] = self.unassigned
		return data


"""
Handles API Request PriceGroupCustomerList_Load_Query.
Scope: Store.
:see: https://docs.miva.com/json-api/functions/pricegroupcustomerlist_load_query
"""


class PriceGroupCustomerListLoadQuery(CustomerListLoadQuery):
	def __init__(self, client: Client = None, price_group: merchantapi.model.PriceGroup = None):
		"""
		PriceGroupCustomerListLoadQuery Constructor.

		:param client: Client
		:param price_group: PriceGroup
		"""

		super().__init__(client)
		self.price_group_id = None
		self.price_group_name = None
		self.assigned = False
		self.unassigned = False
		if isinstance(price_group, merchantapi.model.PriceGroup):
			if price_group.get_id():
				self.set_price_group_id(price_group.get_id())
			elif price_group.get_name():
				self.set_price_group_name(price_group.get_name())

	def get_function(self):
		"""
		Get the function of the request.

		:returns: str
		"""

		return 'PriceGroupCustomerList_Load_Query'

	def get_price_group_id(self) -> int:
		"""
		Get PriceGroup_ID.

		:returns: int
		"""

		return self.price_group_id

	def get_price_group_name(self) -> str:
		"""
		Get PriceGroup_Name.

		:returns: str
		"""

		return self.price_group_name

	def get_assigned(self) -> bool:
		"""
		Get Assigned.

		:returns: bool
		"""

		return self.assigned

	def get_unassigned(self) -> bool:
		"""
		Get Unassigned.

		:returns: bool
		"""

		return self.unassigned

	def set_price_group_id(self, price_group_id: int) -> 'PriceGroupCustomerListLoadQuery':
		"""
		Set PriceGroup_ID.

		:param price_group_id: int
		:returns: PriceGroupCustomerListLoadQuery
		"""

		self.price_group_id = price_group_id
		return self

	def set_price_group_name(self, price_group_name: str) -> 'PriceGroupCustomerListLoadQuery':
		"""
		Set PriceGroup_Name.

		:param price_group_name: str
		:returns: PriceGroupCustomerListLoadQuery
		"""

		self.price_group_name = price_group_name
		return self

	def set_assigned(self, assigned: bool) -> 'PriceGroupCustomerListLoadQuery':
		"""
		Set Assigned.

		:param assigned: bool
		:returns: PriceGroupCustomerListLoadQuery
		"""

		self.assigned = assigned
		return self

	def set_unassigned(self, unassigned: bool) -> 'PriceGroupCustomerListLoadQuery':
		"""
		Set Unassigned.

		:param unassigned: bool
		:returns: PriceGroupCustomerListLoadQuery
		"""

		self.unassigned = unassigned
		return self

	# noinspection PyTypeChecker
	def send(self) -> 'merchantapi.response.PriceGroupCustomerListLoadQuery':
		return super().send()

	def create_response(self, data) -> 'PriceGroupCustomerListLoadQuery':
		"""
		Create a response object from the response data

		:param data:
		:returns: Response
		"""

		return merchantapi.response.PriceGroupCustomerListLoadQuery(self, data)

	def to_dict(self) -> dict:
		"""
		Reduce the request to a dict

		:override:
		:returns: dict
		"""

		data = super().to_dict()

		if self.price_group_id is not None:
			data['PriceGroup_ID'] = self.price_group_id
		elif self.price_group_name is not None:
			data['PriceGroup_Name'] = self.price_group_name

		if self.assigned is not None:
			data['Assigned'] = self.assigned
		if self.unassigned is not None:
			data['Unassigned'] = self.unassigned
		return data


"""
Handles API Request PriceGroupProductList_Load_Query.
Scope: Store.
:see: https://docs.miva.com/json-api/functions/pricegroupproductlist_load_query
"""


class PriceGroupProductListLoadQuery(ProductListLoadQuery):
	def __init__(self, client: Client = None, price_group: merchantapi.model.PriceGroup = None):
		"""
		PriceGroupProductListLoadQuery Constructor.

		:param client: Client
		:param price_group: PriceGroup
		"""

		super().__init__(client)
		self.price_group_id = None
		self.price_group_name = None
		self.assigned = False
		self.unassigned = False
		if isinstance(price_group, merchantapi.model.PriceGroup):
			if price_group.get_id():
				self.set_price_group_id(price_group.get_id())
			elif price_group.get_name():
				self.set_price_group_name(price_group.get_name())

	def get_function(self):
		"""
		Get the function of the request.

		:returns: str
		"""

		return 'PriceGroupProductList_Load_Query'

	def get_price_group_id(self) -> int:
		"""
		Get PriceGroup_ID.

		:returns: int
		"""

		return self.price_group_id

	def get_price_group_name(self) -> str:
		"""
		Get PriceGroup_Name.

		:returns: str
		"""

		return self.price_group_name

	def get_assigned(self) -> bool:
		"""
		Get Assigned.

		:returns: bool
		"""

		return self.assigned

	def get_unassigned(self) -> bool:
		"""
		Get Unassigned.

		:returns: bool
		"""

		return self.unassigned

	def set_price_group_id(self, price_group_id: int) -> 'PriceGroupProductListLoadQuery':
		"""
		Set PriceGroup_ID.

		:param price_group_id: int
		:returns: PriceGroupProductListLoadQuery
		"""

		self.price_group_id = price_group_id
		return self

	def set_price_group_name(self, price_group_name: str) -> 'PriceGroupProductListLoadQuery':
		"""
		Set PriceGroup_Name.

		:param price_group_name: str
		:returns: PriceGroupProductListLoadQuery
		"""

		self.price_group_name = price_group_name
		return self

	def set_assigned(self, assigned: bool) -> 'PriceGroupProductListLoadQuery':
		"""
		Set Assigned.

		:param assigned: bool
		:returns: PriceGroupProductListLoadQuery
		"""

		self.assigned = assigned
		return self

	def set_unassigned(self, unassigned: bool) -> 'PriceGroupProductListLoadQuery':
		"""
		Set Unassigned.

		:param unassigned: bool
		:returns: PriceGroupProductListLoadQuery
		"""

		self.unassigned = unassigned
		return self

	# noinspection PyTypeChecker
	def send(self) -> 'merchantapi.response.PriceGroupProductListLoadQuery':
		return super().send()

	def create_response(self, data) -> 'PriceGroupProductListLoadQuery':
		"""
		Create a response object from the response data

		:param data:
		:returns: Response
		"""

		return merchantapi.response.PriceGroupProductListLoadQuery(self, data)

	def to_dict(self) -> dict:
		"""
		Reduce the request to a dict

		:override:
		:returns: dict
		"""

		data = super().to_dict()

		if self.price_group_id is not None:
			data['PriceGroup_ID'] = self.price_group_id
		elif self.price_group_name is not None:
			data['PriceGroup_Name'] = self.price_group_name

		if self.assigned is not None:
			data['Assigned'] = self.assigned
		if self.unassigned is not None:
			data['Unassigned'] = self.unassigned
		return data


"""
Handles API Request CustomerPriceGroupList_Load_Query.
Scope: Store.
:see: https://docs.miva.com/json-api/functions/customerpricegrouplist_load_query
"""


class CustomerPriceGroupListLoadQuery(PriceGroupListLoadQuery):
	def __init__(self, client: Client = None, customer: merchantapi.model.Customer = None):
		"""
		CustomerPriceGroupListLoadQuery Constructor.

		:param client: Client
		:param customer: Customer
		"""

		super().__init__(client)
		self.customer_id = None
		self.edit_customer = None
		self.customer_login = None
		self.assigned = False
		self.unassigned = False
		if isinstance(customer, merchantapi.model.Customer):
			if customer.get_id():
				self.set_customer_id(customer.get_id())
			elif customer.get_login():
				self.set_edit_customer(customer.get_login())

	def get_function(self):
		"""
		Get the function of the request.

		:returns: str
		"""

		return 'CustomerPriceGroupList_Load_Query'

	def get_customer_id(self) -> int:
		"""
		Get Customer_ID.

		:returns: int
		"""

		return self.customer_id

	def get_edit_customer(self) -> str:
		"""
		Get Edit_Customer.

		:returns: str
		"""

		return self.edit_customer

	def get_customer_login(self) -> str:
		"""
		Get Customer_Login.

		:returns: str
		"""

		return self.customer_login

	def get_assigned(self) -> bool:
		"""
		Get Assigned.

		:returns: bool
		"""

		return self.assigned

	def get_unassigned(self) -> bool:
		"""
		Get Unassigned.

		:returns: bool
		"""

		return self.unassigned

	def set_customer_id(self, customer_id: int) -> 'CustomerPriceGroupListLoadQuery':
		"""
		Set Customer_ID.

		:param customer_id: int
		:returns: CustomerPriceGroupListLoadQuery
		"""

		self.customer_id = customer_id
		return self

	def set_edit_customer(self, edit_customer: str) -> 'CustomerPriceGroupListLoadQuery':
		"""
		Set Edit_Customer.

		:param edit_customer: str
		:returns: CustomerPriceGroupListLoadQuery
		"""

		self.edit_customer = edit_customer
		return self

	def set_customer_login(self, customer_login: str) -> 'CustomerPriceGroupListLoadQuery':
		"""
		Set Customer_Login.

		:param customer_login: str
		:returns: CustomerPriceGroupListLoadQuery
		"""

		self.customer_login = customer_login
		return self

	def set_assigned(self, assigned: bool) -> 'CustomerPriceGroupListLoadQuery':
		"""
		Set Assigned.

		:param assigned: bool
		:returns: CustomerPriceGroupListLoadQuery
		"""

		self.assigned = assigned
		return self

	def set_unassigned(self, unassigned: bool) -> 'CustomerPriceGroupListLoadQuery':
		"""
		Set Unassigned.

		:param unassigned: bool
		:returns: CustomerPriceGroupListLoadQuery
		"""

		self.unassigned = unassigned
		return self

	# noinspection PyTypeChecker
	def send(self) -> 'merchantapi.response.CustomerPriceGroupListLoadQuery':
		return super().send()

	def create_response(self, data) -> 'CustomerPriceGroupListLoadQuery':
		"""
		Create a response object from the response data

		:param data:
		:returns: Response
		"""

		return merchantapi.response.CustomerPriceGroupListLoadQuery(self, data)

	def to_dict(self) -> dict:
		"""
		Reduce the request to a dict

		:override:
		:returns: dict
		"""

		data = super().to_dict()

		if self.customer_id is not None:
			data['Customer_ID'] = self.customer_id
		elif self.edit_customer is not None:
			data['Edit_Customer'] = self.edit_customer
		elif self.customer_login is not None:
			data['Customer_Login'] = self.customer_login

		if self.assigned is not None:
			data['Assigned'] = self.assigned
		if self.unassigned is not None:
			data['Unassigned'] = self.unassigned
		return data


"""
RequestBuilder can be used to build out custom request objects to send to the API
"""


class RequestBuilder(merchantapi.abstract.Request):
	def __init__(self, client: Client, function: str, data: dict = None):
		"""
		RequestBuilder Constructor.

		:param client: Client
		:param function: str
		:param data: dict
		"""
		super().__init__(client)

		if data is not dict:
			data = {}

		self.data = data
		self.set_scope(merchantapi.abstract.Request.SCOPE_STORE)
		self.set_function(function)

	def set_function(self, function: str) -> 'RequestBuilder':
		"""
		Set the request function

		:param function: str
		"""

		self.function = function
		return self

	def set_scope(self, scope: int) -> 'RequestBuilder':
		"""
		Set the request scope

		:param scope: int
		"""

		self.scope = scope
		return self

	def set(self, field: str, value) -> 'RequestBuilder':
		"""
		Set a field value

		:param field: str
		:param value: mixed
		"""

		self.data[field] = value
		return self

	def get(self, field: str, default_value=None):
		"""
		Get a field value

		:param field: str
		:param default_value: mixed
		:returns: mixed
		"""

		if field in self.data:
			return self.data[field]
		return default_value

	def has(self, field: str) -> bool:
		"""
		Check if a field exists

		:param field: str
		:returns: bool
		"""

		return field in self.data

	def remove(self, field: str) -> 'RequestBuilder':
		"""
		Remove a field if it exists

		:param field: str
		"""

		if field in self.data:
			self.data.pop(field, None)
		return self

	# noinspection PyTypeChecker
	def send(self) -> 'merchantapi.response.RequestBuilder':
		return super().send()

	def create_response(self, data) -> 'merchantapi.response.RequestBuilder':
		"""
		Create a response object from the response data

		:param data:
		:returns: Response
		"""

		return merchantapi.response.RequestBuilder(self, data)

	def to_dict(self) -> dict:
		"""
		Reduce the request to a dict

		:override:
		:returns: dict
		"""

		return super().to_dict().update(self.data)
