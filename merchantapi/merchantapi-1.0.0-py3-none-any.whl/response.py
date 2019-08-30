"""
This file is part of the MerchantAPI package.

(c) Miva Inc <https://www.miva.com/>

For the full copyright and license information, please view the LICENSE
file that was distributed with this source code.

$Id: response.py 77709 2019-08-30 16:41:54Z gidriss $
"""

import merchantapi.model
import merchantapi.request
from merchantapi.abstract import Request
from merchantapi.abstract import Response
from merchantapi.listquery import ListQueryRequest
from merchantapi.listquery import ListQueryResponse


"""
API Response for AvailabilityGroupBusinessAccount_Update_Assigned.

:see: https://docs.miva.com/json-api/functions/availabilitygroupbusinessaccount_update_assigned
"""


class AvailabilityGroupBusinessAccountUpdateAssigned(Response):
	def __init__(self, request: Request, data: dict):
		"""
		AvailabilityGroupBusinessAccountUpdateAssigned Constructor.

		:param request: Request
		:param data: dict
		"""

		super().__init__(request, data)


"""
API Response for AvailabilityGroupCustomer_Update_Assigned.

:see: https://docs.miva.com/json-api/functions/availabilitygroupcustomer_update_assigned
"""


class AvailabilityGroupCustomerUpdateAssigned(Response):
	def __init__(self, request: Request, data: dict):
		"""
		AvailabilityGroupCustomerUpdateAssigned Constructor.

		:param request: Request
		:param data: dict
		"""

		super().__init__(request, data)


"""
API Response for AvailabilityGroupList_Load_Query.

:see: https://docs.miva.com/json-api/functions/availabilitygrouplist_load_query
"""


class AvailabilityGroupListLoadQuery(ListQueryResponse):
	def __init__(self, request: ListQueryRequest, data: dict):
		"""
		AvailabilityGroupListLoadQuery Constructor.

		:param request: ListQueryRequest
		:param data: dict
		"""

		super().__init__(request, data)
		if not self.is_success():
			return

		if 'data' in self.data and 'data' in self.data['data'] and isinstance(self.data['data']['data'], list):
			for i, e in enumerate(self.data['data']['data'], 0):
				self.data['data']['data'][i] = merchantapi.model.AvailabilityGroup(e)

	def get_availability_groups(self):
		"""
		Get availability_groups.

		:returns: list of AvailabilityGroup
		"""

		if self.data['data'] is None or not isinstance(self.data['data']['data'], list):
			return []

		return self.data['data']['data']


"""
API Response for AvailabilityGroupPaymentMethod_Update_Assigned.

:see: https://docs.miva.com/json-api/functions/availabilitygrouppaymentmethod_update_assigned
"""


class AvailabilityGroupPaymentMethodUpdateAssigned(Response):
	def __init__(self, request: Request, data: dict):
		"""
		AvailabilityGroupPaymentMethodUpdateAssigned Constructor.

		:param request: Request
		:param data: dict
		"""

		super().__init__(request, data)


"""
API Response for AvailabilityGroupProduct_Update_Assigned.

:see: https://docs.miva.com/json-api/functions/availabilitygroupproduct_update_assigned
"""


class AvailabilityGroupProductUpdateAssigned(Response):
	def __init__(self, request: Request, data: dict):
		"""
		AvailabilityGroupProductUpdateAssigned Constructor.

		:param request: Request
		:param data: dict
		"""

		super().__init__(request, data)


"""
API Response for AvailabilityGroupShippingMethod_Update_Assigned.

:see: https://docs.miva.com/json-api/functions/availabilitygroupshippingmethod_update_assigned
"""


class AvailabilityGroupShippingMethodUpdateAssigned(Response):
	def __init__(self, request: Request, data: dict):
		"""
		AvailabilityGroupShippingMethodUpdateAssigned Constructor.

		:param request: Request
		:param data: dict
		"""

		super().__init__(request, data)


"""
API Response for CategoryList_Load_Parent.

:see: https://docs.miva.com/json-api/functions/categorylist_load_parent
"""


class CategoryListLoadParent(Response):
	def __init__(self, request: Request, data: dict):
		"""
		CategoryListLoadParent Constructor.

		:param request: Request
		:param data: dict
		"""

		super().__init__(request, data)
		if not self.is_success():
			return

		if 'data' in self.data and isinstance(self.data['data'], list):
			for i, e in enumerate(self.data['data'], 0):
				self.data['data'][i] = merchantapi.model.Category(e)

	def get_categories(self):
		"""
		Get categories.

		:returns: list of Category
		"""

		return self.data['data'] if self.data['data'] is not None else []


"""
API Response for CategoryList_Load_Query.

:see: https://docs.miva.com/json-api/functions/categorylist_load_query
"""


class CategoryListLoadQuery(ListQueryResponse):
	def __init__(self, request: ListQueryRequest, data: dict):
		"""
		CategoryListLoadQuery Constructor.

		:param request: ListQueryRequest
		:param data: dict
		"""

		super().__init__(request, data)
		if not self.is_success():
			return

		if 'data' in self.data and 'data' in self.data['data'] and isinstance(self.data['data']['data'], list):
			for i, e in enumerate(self.data['data']['data'], 0):
				self.data['data']['data'][i] = merchantapi.model.Category(e)

	def get_categories(self):
		"""
		Get categories.

		:returns: list of Category
		"""

		if self.data['data'] is None or not isinstance(self.data['data']['data'], list):
			return []

		return self.data['data']['data']


"""
API Response for CategoryProduct_Update_Assigned.

:see: https://docs.miva.com/json-api/functions/categoryproduct_update_assigned
"""


class CategoryProductUpdateAssigned(Response):
	def __init__(self, request: Request, data: dict):
		"""
		CategoryProductUpdateAssigned Constructor.

		:param request: Request
		:param data: dict
		"""

		super().__init__(request, data)


"""
API Response for Category_Insert.

:see: https://docs.miva.com/json-api/functions/category_insert
"""


class CategoryInsert(Response):
	def __init__(self, request: Request, data: dict):
		"""
		CategoryInsert Constructor.

		:param request: Request
		:param data: dict
		"""

		super().__init__(request, data)


"""
API Response for Category_Delete.

:see: https://docs.miva.com/json-api/functions/category_delete
"""


class CategoryDelete(Response):
	def __init__(self, request: Request, data: dict):
		"""
		CategoryDelete Constructor.

		:param request: Request
		:param data: dict
		"""

		super().__init__(request, data)


"""
API Response for Category_Update.

:see: https://docs.miva.com/json-api/functions/category_update
"""


class CategoryUpdate(Response):
	def __init__(self, request: Request, data: dict):
		"""
		CategoryUpdate Constructor.

		:param request: Request
		:param data: dict
		"""

		super().__init__(request, data)


"""
API Response for CouponList_Delete.

:see: https://docs.miva.com/json-api/functions/couponlist_delete
"""


class CouponListDelete(Response):
	def __init__(self, request: Request, data: dict):
		"""
		CouponListDelete Constructor.

		:param request: Request
		:param data: dict
		"""

		super().__init__(request, data)

	def get_processed(self):
		"""
		Get processed.

		:returns: int
		"""

		if 'processed' in self.data:
			return self.data['processed']
		return 0


"""
API Response for CouponList_Load_Query.

:see: https://docs.miva.com/json-api/functions/couponlist_load_query
"""


class CouponListLoadQuery(ListQueryResponse):
	def __init__(self, request: ListQueryRequest, data: dict):
		"""
		CouponListLoadQuery Constructor.

		:param request: ListQueryRequest
		:param data: dict
		"""

		super().__init__(request, data)
		if not self.is_success():
			return

		if 'data' in self.data and 'data' in self.data['data'] and isinstance(self.data['data']['data'], list):
			for i, e in enumerate(self.data['data']['data'], 0):
				self.data['data']['data'][i] = merchantapi.model.Coupon(e)

	def get_coupons(self):
		"""
		Get coupons.

		:returns: list of Coupon
		"""

		if self.data['data'] is None or not isinstance(self.data['data']['data'], list):
			return []

		return self.data['data']['data']


"""
API Response for CouponPriceGroup_Update_Assigned.

:see: https://docs.miva.com/json-api/functions/couponpricegroup_update_assigned
"""


class CouponPriceGroupUpdateAssigned(Response):
	def __init__(self, request: Request, data: dict):
		"""
		CouponPriceGroupUpdateAssigned Constructor.

		:param request: Request
		:param data: dict
		"""

		super().__init__(request, data)


"""
API Response for Coupon_Insert.

:see: https://docs.miva.com/json-api/functions/coupon_insert
"""


class CouponInsert(Response):
	def __init__(self, request: Request, data: dict):
		"""
		CouponInsert Constructor.

		:param request: Request
		:param data: dict
		"""

		super().__init__(request, data)

	def get_id(self):
		"""
		Get id.

		:returns: int
		"""

		if 'data' in self.data and 'id' in self.data['data']:
			return self.data['data']['id']
		return 0


"""
API Response for Coupon_Update.

:see: https://docs.miva.com/json-api/functions/coupon_update
"""


class CouponUpdate(Response):
	def __init__(self, request: Request, data: dict):
		"""
		CouponUpdate Constructor.

		:param request: Request
		:param data: dict
		"""

		super().__init__(request, data)


"""
API Response for CustomerList_Load_Query.

:see: https://docs.miva.com/json-api/functions/customerlist_load_query
"""


class CustomerListLoadQuery(ListQueryResponse):
	def __init__(self, request: ListQueryRequest, data: dict):
		"""
		CustomerListLoadQuery Constructor.

		:param request: ListQueryRequest
		:param data: dict
		"""

		super().__init__(request, data)
		if not self.is_success():
			return

		if 'data' in self.data and 'data' in self.data['data'] and isinstance(self.data['data']['data'], list):
			for i, e in enumerate(self.data['data']['data'], 0):
				self.data['data']['data'][i] = merchantapi.model.Customer(e)

	def get_customers(self):
		"""
		Get customers.

		:returns: list of Customer
		"""

		if self.data['data'] is None or not isinstance(self.data['data']['data'], list):
			return []

		return self.data['data']['data']


"""
API Response for Customer_Delete.

:see: https://docs.miva.com/json-api/functions/customer_delete
"""


class CustomerDelete(Response):
	def __init__(self, request: Request, data: dict):
		"""
		CustomerDelete Constructor.

		:param request: Request
		:param data: dict
		"""

		super().__init__(request, data)


"""
API Response for Customer_Insert.

:see: https://docs.miva.com/json-api/functions/customer_insert
"""


class CustomerInsert(Response):
	def __init__(self, request: Request, data: dict):
		"""
		CustomerInsert Constructor.

		:param request: Request
		:param data: dict
		"""

		super().__init__(request, data)
		if not self.is_success():
			return

		self.data['data'] = merchantapi.model.Customer(self.data['data'])

	def get_customer(self) -> merchantapi.model.Customer:
		"""
		Get customer.

		:returns: Customer
		"""

		return {} if 'data' not in self.data else self.data['data']


"""
API Response for Customer_Update.

:see: https://docs.miva.com/json-api/functions/customer_update
"""


class CustomerUpdate(Response):
	def __init__(self, request: Request, data: dict):
		"""
		CustomerUpdate Constructor.

		:param request: Request
		:param data: dict
		"""

		super().__init__(request, data)


"""
API Response for CustomerPaymentCard_Register.

:see: https://docs.miva.com/json-api/functions/customerpaymentcard_register
"""


class CustomerPaymentCardRegister(Response):
	def __init__(self, request: Request, data: dict):
		"""
		CustomerPaymentCardRegister Constructor.

		:param request: Request
		:param data: dict
		"""

		super().__init__(request, data)
		if not self.is_success():
			return

		self.data['data'] = merchantapi.model.CustomerPaymentCard(self.data['data'])

	def get_customer_payment_card(self) -> merchantapi.model.CustomerPaymentCard:
		"""
		Get customer_payment_card.

		:returns: CustomerPaymentCard
		"""

		return {} if 'data' not in self.data else self.data['data']


"""
API Response for Module.

:see: https://docs.miva.com/json-api/functions/module
"""


class Module(Response):
	def __init__(self, request: Request, data: dict):
		"""
		Module Constructor.

		:param request: Request
		:param data: dict
		"""

		super().__init__(request, data)


"""
API Response for NoteList_Load_Query.

:see: https://docs.miva.com/json-api/functions/notelist_load_query
"""


class NoteListLoadQuery(ListQueryResponse):
	def __init__(self, request: ListQueryRequest, data: dict):
		"""
		NoteListLoadQuery Constructor.

		:param request: ListQueryRequest
		:param data: dict
		"""

		super().__init__(request, data)
		if not self.is_success():
			return

		if 'data' in self.data and 'data' in self.data['data'] and isinstance(self.data['data']['data'], list):
			for i, e in enumerate(self.data['data']['data'], 0):
				self.data['data']['data'][i] = merchantapi.model.Note(e)

	def get_notes(self):
		"""
		Get notes.

		:returns: list of Note
		"""

		if self.data['data'] is None or not isinstance(self.data['data']['data'], list):
			return []

		return self.data['data']['data']


"""
API Response for Note_Delete.

:see: https://docs.miva.com/json-api/functions/note_delete
"""


class NoteDelete(Response):
	def __init__(self, request: Request, data: dict):
		"""
		NoteDelete Constructor.

		:param request: Request
		:param data: dict
		"""

		super().__init__(request, data)


"""
API Response for Note_Insert.

:see: https://docs.miva.com/json-api/functions/note_insert
"""


class NoteInsert(Response):
	def __init__(self, request: Request, data: dict):
		"""
		NoteInsert Constructor.

		:param request: Request
		:param data: dict
		"""

		super().__init__(request, data)


"""
API Response for Note_Update.

:see: https://docs.miva.com/json-api/functions/note_update
"""


class NoteUpdate(Response):
	def __init__(self, request: Request, data: dict):
		"""
		NoteUpdate Constructor.

		:param request: Request
		:param data: dict
		"""

		super().__init__(request, data)


"""
API Response for OrderCustomFieldList_Load.

:see: https://docs.miva.com/json-api/functions/ordercustomfieldlist_load
"""


class OrderCustomFieldListLoad(Response):
	def __init__(self, request: Request, data: dict):
		"""
		OrderCustomFieldListLoad Constructor.

		:param request: Request
		:param data: dict
		"""

		super().__init__(request, data)
		if not self.is_success():
			return

		if 'data' in self.data and isinstance(self.data['data'], list):
			for i, e in enumerate(self.data['data'], 0):
				self.data['data'][i] = merchantapi.model.OrderCustomField(e)

	def get_order_custom_fields(self):
		"""
		Get order_custom_fields.

		:returns: list of OrderCustomField
		"""

		return self.data['data'] if self.data['data'] is not None else []


"""
API Response for OrderCustomFields_Update.

:see: https://docs.miva.com/json-api/functions/ordercustomfields_update
"""


class OrderCustomFieldsUpdate(Response):
	def __init__(self, request: Request, data: dict):
		"""
		OrderCustomFieldsUpdate Constructor.

		:param request: Request
		:param data: dict
		"""

		super().__init__(request, data)


"""
API Response for OrderItemList_BackOrder.

:see: https://docs.miva.com/json-api/functions/orderitemlist_backorder
"""


class OrderItemListBackOrder(Response):
	def __init__(self, request: Request, data: dict):
		"""
		OrderItemListBackOrder Constructor.

		:param request: Request
		:param data: dict
		"""

		super().__init__(request, data)


"""
API Response for OrderItemList_Cancel.

:see: https://docs.miva.com/json-api/functions/orderitemlist_cancel
"""


class OrderItemListCancel(Response):
	def __init__(self, request: Request, data: dict):
		"""
		OrderItemListCancel Constructor.

		:param request: Request
		:param data: dict
		"""

		super().__init__(request, data)


"""
API Response for OrderItemList_CreateShipment.

:see: https://docs.miva.com/json-api/functions/orderitemlist_createshipment
"""


class OrderItemListCreateShipment(Response):
	def __init__(self, request: Request, data: dict):
		"""
		OrderItemListCreateShipment Constructor.

		:param request: Request
		:param data: dict
		"""

		super().__init__(request, data)
		if not self.is_success():
			return

		self.data['data'] = merchantapi.model.OrderShipment(self.data['data'])

	def get_order_shipment(self) -> merchantapi.model.OrderShipment:
		"""
		Get order_shipment.

		:returns: OrderShipment
		"""

		return {} if 'data' not in self.data else self.data['data']


"""
API Response for OrderItemList_Delete.

:see: https://docs.miva.com/json-api/functions/orderitemlist_delete
"""


class OrderItemListDelete(Response):
	def __init__(self, request: Request, data: dict):
		"""
		OrderItemListDelete Constructor.

		:param request: Request
		:param data: dict
		"""

		super().__init__(request, data)


"""
API Response for OrderItem_Add.

:see: https://docs.miva.com/json-api/functions/orderitem_add
"""


class OrderItemAdd(Response):
	def __init__(self, request: Request, data: dict):
		"""
		OrderItemAdd Constructor.

		:param request: Request
		:param data: dict
		"""

		super().__init__(request, data)
		if not self.is_success():
			return

		self.data['data'] = merchantapi.model.OrderTotal(self.data['data'])

	def get_order_total(self) -> merchantapi.model.OrderTotal:
		"""
		Get order_total.

		:returns: OrderTotal
		"""

		return {} if 'data' not in self.data else self.data['data']


"""
API Response for OrderItem_Update.

:see: https://docs.miva.com/json-api/functions/orderitem_update
"""


class OrderItemUpdate(Response):
	def __init__(self, request: Request, data: dict):
		"""
		OrderItemUpdate Constructor.

		:param request: Request
		:param data: dict
		"""

		super().__init__(request, data)
		if not self.is_success():
			return

		self.data['data'] = merchantapi.model.OrderTotal(self.data['data'])

	def get_order_total(self) -> merchantapi.model.OrderTotal:
		"""
		Get order_total.

		:returns: OrderTotal
		"""

		return {} if 'data' not in self.data else self.data['data']


"""
API Response for OrderList_Load_Query.

:see: https://docs.miva.com/json-api/functions/orderlist_load_query
"""


class OrderListLoadQuery(ListQueryResponse):
	def __init__(self, request: ListQueryRequest, data: dict):
		"""
		OrderListLoadQuery Constructor.

		:param request: ListQueryRequest
		:param data: dict
		"""

		super().__init__(request, data)
		if not self.is_success():
			return

		if 'data' in self.data and 'data' in self.data['data'] and isinstance(self.data['data']['data'], list):
			for i, e in enumerate(self.data['data']['data'], 0):
				self.data['data']['data'][i] = merchantapi.model.Order(e)

	def get_orders(self):
		"""
		Get orders.

		:returns: list of Order
		"""

		if self.data['data'] is None or not isinstance(self.data['data']['data'], list):
			return []

		return self.data['data']['data']


"""
API Response for OrderPayment_Capture.

:see: https://docs.miva.com/json-api/functions/orderpayment_capture
"""


class OrderPaymentCapture(Response):
	def __init__(self, request: Request, data: dict):
		"""
		OrderPaymentCapture Constructor.

		:param request: Request
		:param data: dict
		"""

		super().__init__(request, data)
		if not self.is_success():
			return

		self.data['data'] = merchantapi.model.OrderPaymentTotal(self.data['data'])

	def get_order_payment_total(self) -> merchantapi.model.OrderPaymentTotal:
		"""
		Get order_payment_total.

		:returns: OrderPaymentTotal
		"""

		return {} if 'data' not in self.data else self.data['data']


"""
API Response for OrderPayment_Refund.

:see: https://docs.miva.com/json-api/functions/orderpayment_refund
"""


class OrderPaymentRefund(Response):
	def __init__(self, request: Request, data: dict):
		"""
		OrderPaymentRefund Constructor.

		:param request: Request
		:param data: dict
		"""

		super().__init__(request, data)
		if not self.is_success():
			return

		self.data['data'] = merchantapi.model.OrderPaymentTotal(self.data['data'])

	def get_order_payment_total(self) -> merchantapi.model.OrderPaymentTotal:
		"""
		Get order_payment_total.

		:returns: OrderPaymentTotal
		"""

		return {} if 'data' not in self.data else self.data['data']


"""
API Response for OrderPayment_VOID.

:see: https://docs.miva.com/json-api/functions/orderpayment_void
"""


class OrderPaymentVoid(Response):
	def __init__(self, request: Request, data: dict):
		"""
		OrderPaymentVoid Constructor.

		:param request: Request
		:param data: dict
		"""

		super().__init__(request, data)
		if not self.is_success():
			return

		self.data['data'] = merchantapi.model.OrderPaymentTotal(self.data['data'])

	def get_order_payment_total(self) -> merchantapi.model.OrderPaymentTotal:
		"""
		Get order_payment_total.

		:returns: OrderPaymentTotal
		"""

		return {} if 'data' not in self.data else self.data['data']


"""
API Response for OrderShipmentList_Update.

:see: https://docs.miva.com/json-api/functions/ordershipmentlist_update
"""


class OrderShipmentListUpdate(Response):
	def __init__(self, request: Request, data: dict):
		"""
		OrderShipmentListUpdate Constructor.

		:param request: Request
		:param data: dict
		"""

		super().__init__(request, data)


"""
API Response for Order_Create.

:see: https://docs.miva.com/json-api/functions/order_create
"""


class OrderCreate(Response):
	def __init__(self, request: Request, data: dict):
		"""
		OrderCreate Constructor.

		:param request: Request
		:param data: dict
		"""

		super().__init__(request, data)
		if not self.is_success():
			return

		self.data['data'] = merchantapi.model.Order(self.data['data'])

	def get_order(self) -> merchantapi.model.Order:
		"""
		Get order.

		:returns: Order
		"""

		return {} if 'data' not in self.data else self.data['data']


"""
API Response for Order_Delete.

:see: https://docs.miva.com/json-api/functions/order_delete
"""


class OrderDelete(Response):
	def __init__(self, request: Request, data: dict):
		"""
		OrderDelete Constructor.

		:param request: Request
		:param data: dict
		"""

		super().__init__(request, data)


"""
API Response for Order_Update_Customer_Information.

:see: https://docs.miva.com/json-api/functions/order_update_customer_information
"""


class OrderUpdateCustomerInformation(Response):
	def __init__(self, request: Request, data: dict):
		"""
		OrderUpdateCustomerInformation Constructor.

		:param request: Request
		:param data: dict
		"""

		super().__init__(request, data)


"""
API Response for PriceGroupCustomer_Update_Assigned.

:see: https://docs.miva.com/json-api/functions/pricegroupcustomer_update_assigned
"""


class PriceGroupCustomerUpdateAssigned(Response):
	def __init__(self, request: Request, data: dict):
		"""
		PriceGroupCustomerUpdateAssigned Constructor.

		:param request: Request
		:param data: dict
		"""

		super().__init__(request, data)


"""
API Response for PriceGroupList_Load_Query.

:see: https://docs.miva.com/json-api/functions/pricegrouplist_load_query
"""


class PriceGroupListLoadQuery(ListQueryResponse):
	def __init__(self, request: ListQueryRequest, data: dict):
		"""
		PriceGroupListLoadQuery Constructor.

		:param request: ListQueryRequest
		:param data: dict
		"""

		super().__init__(request, data)
		if not self.is_success():
			return

		if 'data' in self.data and 'data' in self.data['data'] and isinstance(self.data['data']['data'], list):
			for i, e in enumerate(self.data['data']['data'], 0):
				self.data['data']['data'][i] = merchantapi.model.PriceGroup(e)

	def get_price_groups(self):
		"""
		Get price_groups.

		:returns: list of PriceGroup
		"""

		if self.data['data'] is None or not isinstance(self.data['data']['data'], list):
			return []

		return self.data['data']['data']


"""
API Response for PriceGroupProduct_Update_Assigned.

:see: https://docs.miva.com/json-api/functions/pricegroupproduct_update_assigned
"""


class PriceGroupProductUpdateAssigned(Response):
	def __init__(self, request: Request, data: dict):
		"""
		PriceGroupProductUpdateAssigned Constructor.

		:param request: Request
		:param data: dict
		"""

		super().__init__(request, data)


"""
API Response for ProductImage_Add.

:see: https://docs.miva.com/json-api/functions/productimage_add
"""


class ProductImageAdd(Response):
	def __init__(self, request: Request, data: dict):
		"""
		ProductImageAdd Constructor.

		:param request: Request
		:param data: dict
		"""

		super().__init__(request, data)


"""
API Response for ProductImage_Delete.

:see: https://docs.miva.com/json-api/functions/productimage_delete
"""


class ProductImageDelete(Response):
	def __init__(self, request: Request, data: dict):
		"""
		ProductImageDelete Constructor.

		:param request: Request
		:param data: dict
		"""

		super().__init__(request, data)


"""
API Response for ProductList_Adjust_Inventory.

:see: https://docs.miva.com/json-api/functions/productlist_adjust_inventory
"""


class ProductListAdjustInventory(Response):
	def __init__(self, request: Request, data: dict):
		"""
		ProductListAdjustInventory Constructor.

		:param request: Request
		:param data: dict
		"""

		super().__init__(request, data)


"""
API Response for ProductList_Load_Query.

:see: https://docs.miva.com/json-api/functions/productlist_load_query
"""


class ProductListLoadQuery(ListQueryResponse):
	def __init__(self, request: ListQueryRequest, data: dict):
		"""
		ProductListLoadQuery Constructor.

		:param request: ListQueryRequest
		:param data: dict
		"""

		super().__init__(request, data)
		if not self.is_success():
			return

		if 'data' in self.data and 'data' in self.data['data'] and isinstance(self.data['data']['data'], list):
			for i, e in enumerate(self.data['data']['data'], 0):
				self.data['data']['data'][i] = merchantapi.model.Product(e)

	def get_products(self):
		"""
		Get products.

		:returns: list of Product
		"""

		if self.data['data'] is None or not isinstance(self.data['data']['data'], list):
			return []

		return self.data['data']['data']


"""
API Response for ProductVariantList_Load_Product.

:see: https://docs.miva.com/json-api/functions/productvariantlist_load_product
"""


class ProductVariantListLoadProduct(Response):
	def __init__(self, request: Request, data: dict):
		"""
		ProductVariantListLoadProduct Constructor.

		:param request: Request
		:param data: dict
		"""

		super().__init__(request, data)
		if not self.is_success():
			return

		if 'data' in self.data and isinstance(self.data['data'], list):
			for i, e in enumerate(self.data['data'], 0):
				self.data['data'][i] = merchantapi.model.ProductVariant(e)

	def get_product_variants(self):
		"""
		Get product_variants.

		:returns: list of ProductVariant
		"""

		return self.data['data'] if self.data['data'] is not None else []


"""
API Response for Product_Insert.

:see: https://docs.miva.com/json-api/functions/product_insert
"""


class ProductInsert(Response):
	def __init__(self, request: Request, data: dict):
		"""
		ProductInsert Constructor.

		:param request: Request
		:param data: dict
		"""

		super().__init__(request, data)


"""
API Response for Product_Delete.

:see: https://docs.miva.com/json-api/functions/product_delete
"""


class ProductDelete(Response):
	def __init__(self, request: Request, data: dict):
		"""
		ProductDelete Constructor.

		:param request: Request
		:param data: dict
		"""

		super().__init__(request, data)


"""
API Response for Product_Update.

:see: https://docs.miva.com/json-api/functions/product_update
"""


class ProductUpdate(Response):
	def __init__(self, request: Request, data: dict):
		"""
		ProductUpdate Constructor.

		:param request: Request
		:param data: dict
		"""

		super().__init__(request, data)


"""
API Response for Provision_Domain.

:see: https://docs.miva.com/json-api/functions/provision_domain
"""


class ProvisionDomain(Response):
	def __init__(self, request: Request, data: dict):
		"""
		ProvisionDomain Constructor.

		:param request: Request
		:param data: dict
		"""

		super().__init__(request, data)
		if not self.is_success():
			return

		if 'data' in self.data and isinstance(self.data['data'], list):
			for i, e in enumerate(self.data['data'], 0):
				self.data['data'][i] = merchantapi.model.ProvisionMessage(e)

	def get_provision_messages(self):
		"""
		Get provision_messages.

		:returns: list of ProvisionMessage
		"""

		return self.data['data'] if self.data['data'] is not None else []


"""
API Response for Provision_Store.

:see: https://docs.miva.com/json-api/functions/provision_store
"""


class ProvisionStore(Response):
	def __init__(self, request: Request, data: dict):
		"""
		ProvisionStore Constructor.

		:param request: Request
		:param data: dict
		"""

		super().__init__(request, data)
		if not self.is_success():
			return

		if 'data' in self.data and isinstance(self.data['data'], list):
			for i, e in enumerate(self.data['data'], 0):
				self.data['data'][i] = merchantapi.model.ProvisionMessage(e)

	def get_provision_messages(self):
		"""
		Get provision_messages.

		:returns: list of ProvisionMessage
		"""

		return self.data['data'] if self.data['data'] is not None else []


"""
API Response for CustomerAddressList_Load_Query.

:see: https://docs.miva.com/json-api/functions/customeraddresslist_load_query
"""


class CustomerAddressListLoadQuery(ListQueryResponse):
	def __init__(self, request: ListQueryRequest, data: dict):
		"""
		CustomerAddressListLoadQuery Constructor.

		:param request: ListQueryRequest
		:param data: dict
		"""

		super().__init__(request, data)
		if not self.is_success():
			return

		if 'data' in self.data and 'data' in self.data['data'] and isinstance(self.data['data']['data'], list):
			for i, e in enumerate(self.data['data']['data'], 0):
				self.data['data']['data'][i] = merchantapi.model.CustomerAddress(e)

	def get_customer_addresses(self):
		"""
		Get customer_addresses.

		:returns: list of CustomerAddress
		"""

		if self.data['data'] is None or not isinstance(self.data['data']['data'], list):
			return []

		return self.data['data']['data']


"""
API Response for PrintQueueList_Load_Query.

:see: https://docs.miva.com/json-api/functions/printqueuelist_load_query
"""


class PrintQueueListLoadQuery(ListQueryResponse):
	def __init__(self, request: ListQueryRequest, data: dict):
		"""
		PrintQueueListLoadQuery Constructor.

		:param request: ListQueryRequest
		:param data: dict
		"""

		super().__init__(request, data)
		if not self.is_success():
			return

		if 'data' in self.data and 'data' in self.data['data'] and isinstance(self.data['data']['data'], list):
			for i, e in enumerate(self.data['data']['data'], 0):
				self.data['data']['data'][i] = merchantapi.model.PrintQueue(e)

	def get_print_queues(self):
		"""
		Get print_queues.

		:returns: list of PrintQueue
		"""

		if self.data['data'] is None or not isinstance(self.data['data']['data'], list):
			return []

		return self.data['data']['data']


"""
API Response for PrintQueueJobList_Load_Query.

:see: https://docs.miva.com/json-api/functions/printqueuejoblist_load_query
"""


class PrintQueueJobListLoadQuery(ListQueryResponse):
	def __init__(self, request: ListQueryRequest, data: dict):
		"""
		PrintQueueJobListLoadQuery Constructor.

		:param request: ListQueryRequest
		:param data: dict
		"""

		super().__init__(request, data)
		if not self.is_success():
			return

		if 'data' in self.data and 'data' in self.data['data'] and isinstance(self.data['data']['data'], list):
			for i, e in enumerate(self.data['data']['data'], 0):
				self.data['data']['data'][i] = merchantapi.model.PrintQueueJob(e)

	def get_print_queue_jobs(self):
		"""
		Get print_queue_jobs.

		:returns: list of PrintQueueJob
		"""

		if self.data['data'] is None or not isinstance(self.data['data']['data'], list):
			return []

		return self.data['data']['data']


"""
API Response for PrintQueueJob_Delete.

:see: https://docs.miva.com/json-api/functions/printqueuejob_delete
"""


class PrintQueueJobDelete(Response):
	def __init__(self, request: Request, data: dict):
		"""
		PrintQueueJobDelete Constructor.

		:param request: Request
		:param data: dict
		"""

		super().__init__(request, data)


"""
API Response for PrintQueueJob_Insert.

:see: https://docs.miva.com/json-api/functions/printqueuejob_insert
"""


class PrintQueueJobInsert(Response):
	def __init__(self, request: Request, data: dict):
		"""
		PrintQueueJobInsert Constructor.

		:param request: Request
		:param data: dict
		"""

		super().__init__(request, data)

	def get_id(self):
		"""
		Get id.

		:returns: int
		"""

		if 'data' in self.data and 'id' in self.data['data']:
			return self.data['data']['id']
		return 0


"""
API Response for PrintQueueJob_Status.

:see: https://docs.miva.com/json-api/functions/printqueuejob_status
"""


class PrintQueueJobStatus(Response):
	def __init__(self, request: Request, data: dict):
		"""
		PrintQueueJobStatus Constructor.

		:param request: Request
		:param data: dict
		"""

		super().__init__(request, data)

	def get_status(self):
		"""
		Get status.

		:returns: string
		"""

		if 'data' in self.data and 'status' in self.data['data']:
			return self.data['data']['status']
		return None


"""
API Response for PaymentMethodList_Load.

:see: https://docs.miva.com/json-api/functions/paymentmethodlist_load
"""


class PaymentMethodListLoad(Response):
	def __init__(self, request: Request, data: dict):
		"""
		PaymentMethodListLoad Constructor.

		:param request: Request
		:param data: dict
		"""

		super().__init__(request, data)
		if not self.is_success():
			return

		if 'data' in self.data and isinstance(self.data['data'], list):
			for i, e in enumerate(self.data['data'], 0):
				self.data['data'][i] = merchantapi.model.PaymentMethod(e)

	def get_payment_methods(self):
		"""
		Get payment_methods.

		:returns: list of PaymentMethod
		"""

		return self.data['data'] if self.data['data'] is not None else []


"""
API Response for Order_Create_FromOrder.

:see: https://docs.miva.com/json-api/functions/order_create_fromorder
"""


class OrderCreateFromOrder(Response):
	def __init__(self, request: Request, data: dict):
		"""
		OrderCreateFromOrder Constructor.

		:param request: Request
		:param data: dict
		"""

		super().__init__(request, data)
		if not self.is_success():
			return

		self.data['data'] = merchantapi.model.Order(self.data['data'])

	def get_order(self) -> merchantapi.model.Order:
		"""
		Get order.

		:returns: Order
		"""

		return {} if 'data' not in self.data else self.data['data']


"""
API Response for Order_Authorize.

:see: https://docs.miva.com/json-api/functions/order_authorize
"""


class OrderAuthorize(Response):
	def __init__(self, request: Request, data: dict):
		"""
		OrderAuthorize Constructor.

		:param request: Request
		:param data: dict
		"""

		super().__init__(request, data)
		if not self.is_success():
			return

		self.data['data'] = merchantapi.model.OrderPaymentAuthorize(self.data['data'])

	def get_order_payment_authorize(self) -> merchantapi.model.OrderPaymentAuthorize:
		"""
		Get order_payment_authorize.

		:returns: OrderPaymentAuthorize
		"""

		return {} if 'data' not in self.data else self.data['data']


"""
API Response for CustomerPaymentCardList_Load_Query.

:see: https://docs.miva.com/json-api/functions/customerpaymentcardlist_load_query
"""


class CustomerPaymentCardListLoadQuery(ListQueryResponse):
	def __init__(self, request: ListQueryRequest, data: dict):
		"""
		CustomerPaymentCardListLoadQuery Constructor.

		:param request: ListQueryRequest
		:param data: dict
		"""

		super().__init__(request, data)
		if not self.is_success():
			return

		if 'data' in self.data and 'data' in self.data['data'] and isinstance(self.data['data']['data'], list):
			for i, e in enumerate(self.data['data']['data'], 0):
				self.data['data']['data'][i] = merchantapi.model.CustomerPaymentCard(e)

	def get_customer_payment_cards(self):
		"""
		Get customer_payment_cards.

		:returns: list of CustomerPaymentCard
		"""

		if self.data['data'] is None or not isinstance(self.data['data']['data'], list):
			return []

		return self.data['data']['data']


"""
API Response for CategoryProductList_Load_Query.

:see: https://docs.miva.com/json-api/functions/categoryproductlist_load_query
"""


class CategoryProductListLoadQuery(ListQueryResponse):
	def __init__(self, request: ListQueryRequest, data: dict):
		"""
		CategoryProductListLoadQuery Constructor.

		:param request: ListQueryRequest
		:param data: dict
		"""

		super().__init__(request, data)
		if not self.is_success():
			return

		if 'data' in self.data and 'data' in self.data['data'] and isinstance(self.data['data']['data'], list):
			for i, e in enumerate(self.data['data']['data'], 0):
				self.data['data']['data'][i] = merchantapi.model.CategoryProduct(e)

	def get_category_products(self):
		"""
		Get category_products.

		:returns: list of CategoryProduct
		"""

		if self.data['data'] is None or not isinstance(self.data['data']['data'], list):
			return []

		return self.data['data']['data']


"""
API Response for CouponPriceGroupList_Load_Query.

:see: https://docs.miva.com/json-api/functions/couponpricegrouplist_load_query
"""


class CouponPriceGroupListLoadQuery(ListQueryResponse):
	def __init__(self, request: ListQueryRequest, data: dict):
		"""
		CouponPriceGroupListLoadQuery Constructor.

		:param request: ListQueryRequest
		:param data: dict
		"""

		super().__init__(request, data)
		if not self.is_success():
			return

		if 'data' in self.data and 'data' in self.data['data'] and isinstance(self.data['data']['data'], list):
			for i, e in enumerate(self.data['data']['data'], 0):
				self.data['data']['data'][i] = merchantapi.model.CouponPriceGroup(e)

	def get_coupon_price_groups(self):
		"""
		Get coupon_price_groups.

		:returns: list of CouponPriceGroup
		"""

		if self.data['data'] is None or not isinstance(self.data['data']['data'], list):
			return []

		return self.data['data']['data']


"""
API Response for PriceGroupCustomerList_Load_Query.

:see: https://docs.miva.com/json-api/functions/pricegroupcustomerlist_load_query
"""


class PriceGroupCustomerListLoadQuery(ListQueryResponse):
	def __init__(self, request: ListQueryRequest, data: dict):
		"""
		PriceGroupCustomerListLoadQuery Constructor.

		:param request: ListQueryRequest
		:param data: dict
		"""

		super().__init__(request, data)
		if not self.is_success():
			return

		if 'data' in self.data and 'data' in self.data['data'] and isinstance(self.data['data']['data'], list):
			for i, e in enumerate(self.data['data']['data'], 0):
				self.data['data']['data'][i] = merchantapi.model.PriceGroupCustomer(e)

	def get_price_group_customers(self):
		"""
		Get price_group_customers.

		:returns: list of PriceGroupCustomer
		"""

		if self.data['data'] is None or not isinstance(self.data['data']['data'], list):
			return []

		return self.data['data']['data']


"""
API Response for PriceGroupProductList_Load_Query.

:see: https://docs.miva.com/json-api/functions/pricegroupproductlist_load_query
"""


class PriceGroupProductListLoadQuery(ListQueryResponse):
	def __init__(self, request: ListQueryRequest, data: dict):
		"""
		PriceGroupProductListLoadQuery Constructor.

		:param request: ListQueryRequest
		:param data: dict
		"""

		super().__init__(request, data)
		if not self.is_success():
			return

		if 'data' in self.data and 'data' in self.data['data'] and isinstance(self.data['data']['data'], list):
			for i, e in enumerate(self.data['data']['data'], 0):
				self.data['data']['data'][i] = merchantapi.model.PriceGroupProduct(e)

	def get_price_group_products(self):
		"""
		Get price_group_products.

		:returns: list of PriceGroupProduct
		"""

		if self.data['data'] is None or not isinstance(self.data['data']['data'], list):
			return []

		return self.data['data']['data']


"""
API Response for CustomerPriceGroupList_Load_Query.

:see: https://docs.miva.com/json-api/functions/customerpricegrouplist_load_query
"""


class CustomerPriceGroupListLoadQuery(ListQueryResponse):
	def __init__(self, request: ListQueryRequest, data: dict):
		"""
		CustomerPriceGroupListLoadQuery Constructor.

		:param request: ListQueryRequest
		:param data: dict
		"""

		super().__init__(request, data)
		if not self.is_success():
			return

		if 'data' in self.data and 'data' in self.data['data'] and isinstance(self.data['data']['data'], list):
			for i, e in enumerate(self.data['data']['data'], 0):
				self.data['data']['data'][i] = merchantapi.model.CustomerPriceGroup(e)

	def get_customer_price_groups(self):
		"""
		Get customer_price_groups.

		:returns: list of CustomerPriceGroup
		"""

		if self.data['data'] is None or not isinstance(self.data['data']['data'], list):
			return []

		return self.data['data']['data']


"""
RequestBuilder response class
"""


class RequestBuilder(Response):
	pass
