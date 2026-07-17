"""
GraphQL query/mutation string constants for product sync -- moved
verbatim from product_import.py / product_sync.py, unchanged.
"""

_PRODUCTS_COUNT_QUERY = """
query { productsCount { count } }
"""

_PRODUCTS_QUERY = """
query PullProducts($after: String) {
  products(first: 50, after: $after, sortKey: CREATED_AT) {
    edges {
      node {
        legacyResourceId
        title
        bodyHtml
        vendor
        productType
        tags
        category {
          name
          fullName
        }
        seo {
          title
          description
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
            title
            price
            compareAtPrice
            inventoryItem {
              unitCost {
                amount
              }
              measurement {
                weight {
                  value
                  unit
                }
              }
              inventoryLevels(first: 1) {
                nodes {
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
      }
    }
    pageInfo {
      hasNextPage
      endCursor
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
