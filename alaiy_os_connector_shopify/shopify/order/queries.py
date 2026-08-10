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
        createdAt
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

_ORDER_TAGS_QUERY = """
query GetOrderTags($id: ID!) {
  order(id: $id) {
    tags
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

# fulfillmentCreate needs a fulfillment order id, not the order id itself --
# an order can have multiple fulfillment orders (split shipments across
# locations, or a prior partial fulfillment already closed one out), so this
# walks the full paginated connection rather than assuming the first page
# covers every order -- caller filters to OPEN ones with remainingQuantity > 0.
_FULFILLMENT_ORDERS_QUERY = """
query GetFulfillmentOrders($id: ID!, $after: String) {
  order(id: $id) {
    fulfillmentOrders(first: 50, after: $after) {
      nodes {
        id
        status
        lineItems(first: 250) {
          nodes {
            id
            remainingQuantity
            totalQuantity
            sku
            variant {
              legacyResourceId
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
}
"""

# fulfillmentCreateV2 is deprecated in favor of fulfillmentCreate (same
# FulfillmentInput shape minus the V2 suffix) -- using the non-deprecated one.
_FULFILLMENT_CREATE_MUTATION = """
mutation CreateFulfillment($fulfillment: FulfillmentInput!) {
  fulfillmentCreate(fulfillment: $fulfillment) {
    fulfillment {
      id
      status
      trackingInfo {
        number
        company
        url
      }
      createdAt
    }
    userErrors {
      field
      message
    }
  }
}
"""

_FULFILLMENT_CANCEL_MUTATION = """
mutation CancelFulfillment($id: ID!) {
  fulfillmentCancel(id: $id) {
    fulfillment {
      id
      status
    }
    userErrors {
      field
      message
    }
  }
}
"""

# fulfillmentTrackingInfoUpdateV2 is deprecated in favor of
# fulfillmentTrackingInfoUpdate (same shape minus the V2 suffix).
_FULFILLMENT_TRACKING_UPDATE_MUTATION = """
mutation UpdateFulfillmentTracking($fulfillmentId: ID!, $trackingInfoInput: FulfillmentTrackingInput!, $notifyCustomer: Boolean) {
  fulfillmentTrackingInfoUpdate(fulfillmentId: $fulfillmentId, trackingInfoInput: $trackingInfoInput, notifyCustomer: $notifyCustomer) {
    fulfillment {
      id
      trackingInfo {
        number
        company
        url
      }
    }
    userErrors {
      field
      message
    }
  }
}
"""
