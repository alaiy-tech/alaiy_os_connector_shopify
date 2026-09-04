"""
GraphQL query/mutation string constants for product sync -- moved
verbatim from product_import.py / product_sync.py, unchanged.
"""

_PRODUCTS_COUNT_QUERY = """
query { productsCount { count } }
"""

# How many inventory levels (locations) each variant returns.
#
# This is nested inside products(50) x variants(100), so its page size
# multiplies rather than adds, and Shopify charges the whole query against a
# 1000-point single-query limit. Measured live on this store:
#     first: 3   -> under the limit (the long-standing value)
#     first: 10  -> 1325, MAX_COST_EXCEEDED
#     first: 50  -> 1892, MAX_COST_EXCEEDED
# So three is not a comfortable default here, it is close to the ceiling.
# Raising it is not possible without restructuring the query (or moving to
# bulk operations); pull_stock_from_shopify.py affords first: 50 only because
# it queries ONE variant at a time, with no products x variants multiplier
# above it.
#
# Three is enough for the intended case -- an item at one supplier location,
# optionally also at the store's default location. An item at more locations than
# this comes back truncated, and Shopify reports no error for it, so
# variants._variant_location_levels logs whenever a variant returns exactly
# this many.
INVENTORY_LEVELS_PAGE_SIZE = 3

_PRODUCTS_QUERY = """
query PullProducts($after: String, $query: String) {
  products(first: 50, after: $after, sortKey: CREATED_AT, query: $query) {
    edges {
      node {
        legacyResourceId
        handle
        title
        descriptionHtml
        vendor
        productType
        status
        publishedAt
        createdAt
        updatedAt
        hasOnlyDefaultVariant
        isGiftCard
        variantsCount { count }
        mediaCount { count }
        tracksInventory
        totalInventory
        tags
        category {
          name
          fullName
        }
        seo {
          title
          description
        }
        collections(first: 50) {
          nodes {
            title
          }
        }
        options {
          name
          values
        }
        images(first: 10) {
          nodes {
            id
            src
          }
        }
        variants(first: 100) {
          nodes {
            legacyResourceId
            sku
            barcode
            title
            price
            compareAtPrice
            position
            taxable
            availableForSale
            inventoryPolicy
            inventoryQuantity
            inventoryItem {
              legacyResourceId
              tracked
              duplicateSkuCount
              requiresShipping
              countryCodeOfOrigin
              harmonizedSystemCode
              unitCost {
                amount
              }
              measurement {
                weight {
                  value
                  unit
                }
              }
              inventoryLevels(first: 3) {
                nodes {
                  location {
                    legacyResourceId
                  }
                  quantities(names: ["available"]) {
                    quantity
                  }
                }
              }
            }
            selectedOptions {
              name
              value
            }
          }
        }
        metafields(first: 250) {
          nodes {
            namespace
            key
            value
            type
          }
          pageInfo {
            hasNextPage
            endCursor
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

# Continuation fetch for the rare product with more than 250 metafields --
# _PRODUCTS_QUERY's inline metafields(first: 250) already covers the
# overwhelming majority; this only runs when that page's hasNextPage is true.
_PRODUCT_METAFIELDS_PAGE_QUERY = """
query GetProductMetafieldsPage($id: ID!, $after: String) {
  product(id: $id) {
    metafields(first: 250, after: $after) {
      nodes {
        namespace
        key
        value
        type
      }
      pageInfo {
        hasNextPage
        endCursor
      }
    }
  }
}
"""

_METAFIELDS_SET_MUTATION = """
mutation SetMetafields($metafields: [MetafieldsSetInput!]!) {
  metafieldsSet(metafields: $metafields) {
    metafields {
      id
      namespace
      key
    }
    userErrors {
      field
      message
    }
  }
}
"""

_PRODUCT_SET_MUTATION = """
mutation PushProduct($input: ProductSetInput!, $identifier: ProductSetIdentifiers, $synchronous: Boolean!) {
  productSet(input: $input, identifier: $identifier, synchronous: $synchronous) {
    product {
      id
      legacyResourceId
      variants(first: 100) {
        nodes {
          id
          legacyResourceId
          sku
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

_TAXONOMY_SEARCH_QUERY = """
query SearchTaxonomy($search: String!) {
  taxonomy {
    categories(search: $search, first: 5) {
      edges {
        node {
          id
          name
        }
      }
    }
  }
}
"""

_TAXONOMY_TREE_QUERY = """
query GetTaxonomyTree($after: String) {
  taxonomy {
    categories(first: 250, after: $after) {
      edges {
        node {
          id
          name
          level
          fullName
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

# taxonomy.categories() only ever returns the 26 ROOT (level-1) nodes --
# confirmed live via introspection, Shopify's full multi-thousand-node tree
# is only reachable by walking each node's childrenIds recursively. This
# bulk node-by-id lookup (up to 250 ids per call) is what a BFS traversal
# uses to fetch each next level in as few round trips as possible.
_TAXONOMY_NODES_BY_ID_QUERY = """
query GetTaxonomyNodesByIds($ids: [ID!]!) {
  nodes(ids: $ids) {
    ... on TaxonomyCategory {
      id
      name
      level
      fullName
      childrenIds
      isLeaf
    }
  }
}
"""

_PRODUCT_TAGS_QUERY = """
query GetProductTags($after: String) {
  productTags(first: 250, after: $after) {
    edges {
      node
    }
    pageInfo {
      hasNextPage
      endCursor
    }
  }
}
"""

_PRODUCT_UPDATE_MUTATION = """
mutation productUpdate($input: ProductInput!) {
  productUpdate(input: $input) {
    product {
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


# Stock-only product page, for the inventory reconcile sweep.
#
# _PRODUCTS_QUERY carries everything an IMPORT needs -- descriptions, SEO,
# metafields(250), collections(50), media counts -- which is far more than a
# stock comparison reads, and expensive enough that walking the whole
# catalogue with it cannot finish inside the scheduler's job timeout.
# Confirmed live: the daily reconcile died with JobTimeoutException at 300s
# every single run, having written nothing, leaving local stock to drift with
# no backstop under the webhook.
#
# Same variant/inventoryLevels shape as the full query, so
# _variant_location_levels reads it unchanged.
#
# Page sizes are deliberately small. Shopify costs nested connections
# MULTIPLICATIVELY, so products x variants x inventoryLevels is what the
# limit is charged against, not the fields. Confirmed live: 100 x 100 x 10
# was rejected outright at cost 1325 against a 1000 ceiling. Raising any of
# the three to make the sweep "faster" will fail every request instead.
_PRODUCTS_STOCK_QUERY = """
query PullProductStock($after: String, $query: String) {
  products(first: 25, after: $after, sortKey: CREATED_AT, query: $query) {
    edges {
      node {
        legacyResourceId
        variants(first: 20) {
          nodes {
            legacyResourceId
            inventoryItem {
              inventoryLevels(first: 5) {
                nodes {
                  location {
                    legacyResourceId
                  }
                  quantities(names: ["available"]) {
                    quantity
                  }
                }
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
