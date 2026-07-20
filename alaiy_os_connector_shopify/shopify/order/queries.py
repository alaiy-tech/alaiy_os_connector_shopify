"""
GraphQL query/mutation string constants for order sync -- moved
verbatim from order_sync.py / order_push.py, unchanged.
"""

_ORDERS_COUNT_QUERY = """
query { ordersCount { count } }
"""

_ORDERS_QUERY = """
query PullOrders($after: String, $queryString: String!) {
  orders(first: 50, after: $after, query: $queryString, sortKey: CREATED_AT) {
    edges {
      node {
        legacyResourceId
        name
        note
        currencyCode
        displayFinancialStatus
        displayFulfillmentStatus
        taxesIncluded
        taxLines {
          title
          rate
          priceSet {
            shopMoney {
              amount
            }
          }
        }
        customer {
          legacyResourceId
          firstName
          lastName
          email
        }
        totalDiscountsSet {
          shopMoney {
            amount
          }
        }
        shippingLine {
          title
          originalPriceSet {
            shopMoney {
              amount
            }
          }
        }
        shippingAddress {
          name
          address1
          address2
          city
          province
          country
          zip
          phone
        }
        billingAddress {
          name
          address1
          address2
          city
          province
          country
          zip
          phone
        }
        lineItems(first: 100) {
          nodes {
            sku
            title
            quantity
            variant {
              legacyResourceId
            }
            originalUnitPriceSet {
              shopMoney {
                amount
              }
            }
          }
        }
      }
    }
    pageInfo {
      hasNextPage
      endCursor
    }
  }
}
"""

_ORDER_MARK_PAID_MUTATION = """
mutation OrderMarkAsPaid($input: OrderMarkAsPaidInput!) {
  orderMarkAsPaid(input: $input) {
    order {
      id
      displayFinancialStatus
    }
    userErrors {
      field
      message
    }
  }
}
"""

_ORDER_UPDATE_MUTATION = """
mutation PushOrderUpdate($input: OrderInput!) {
  orderUpdate(input: $input) {
    order {
      id
    }
    userErrors {
      field
      message
    }
  }
}
"""

_ORDER_CANCEL_MUTATION = """
mutation PushOrderCancel($orderId: ID!, $reason: OrderCancelReason!, $refund: Boolean!, $restock: Boolean!, $notifyCustomer: Boolean!) {
  orderCancel(orderId: $orderId, reason: $reason, refund: $refund, restock: $restock, notifyCustomer: $notifyCustomer) {
    job {
      id
    }
    orderCancelUserErrors {
      field
      message
    }
  }
}
"""

_ORDER_CREATE_MUTATION = """
mutation PushOrderCreate($order: OrderCreateOrderInput!, $options: OrderCreateOptionsInput) {
  orderCreate(order: $order, options: $options) {
    order {
      id
      legacyResourceId
      name
    }
    userErrors {
      field
      message
    }
  }
}
"""

# orderUpdate has no line-item support at all -- removing a line requires
# Shopify's separate Order Editing API (begin a calculated edit session, set
# the line's quantity to 0, commit).
_ORDER_EDIT_BEGIN_MUTATION = """
mutation BeginOrderEdit($id: ID!) {
  orderEditBegin(id: $id) {
    calculatedOrder {
      id
      lineItems(first: 100) {
        nodes {
          id
          variant {
            legacyResourceId
          }
        }
      }
    }
    userErrors {
      field
      message
    }
  }
}
"""

_ORDER_EDIT_SET_QUANTITY_MUTATION = """
mutation SetOrderEditQuantity($id: ID!, $lineItemId: ID!, $quantity: Int!) {
  orderEditSetQuantity(id: $id, lineItemId: $lineItemId, quantity: $quantity) {
    calculatedOrder {
      id
    }
    userErrors {
      field
      message
    }
  }
}
"""

_ORDER_EDIT_ADD_VARIANT_MUTATION = """
mutation AddOrderEditVariant($id: ID!, $variantId: ID!, $quantity: Int!) {
  orderEditAddVariant(id: $id, variantId: $variantId, quantity: $quantity) {
    calculatedLineItem {
      id
    }
    calculatedOrder {
      id
    }
    userErrors {
      field
      message
    }
  }
}
"""

_ORDER_EDIT_COMMIT_MUTATION = """
mutation CommitOrderEdit($id: ID!, $notifyCustomer: Boolean) {
  orderEditCommit(id: $id, notifyCustomer: $notifyCustomer) {
    order {
      id
    }
    userErrors {
      field
      message
    }
  }
}
"""
