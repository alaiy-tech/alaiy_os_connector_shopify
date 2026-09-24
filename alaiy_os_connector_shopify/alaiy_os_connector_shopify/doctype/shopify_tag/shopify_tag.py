import frappe
from frappe.model.document import Document


class ShopifyTag(Document):
	def autoname(self):
		from alaiy_os_connector_shopify.shopify.scoping import tag_doc_name

		self.name = tag_doc_name(self.connection, self.tag_name)
