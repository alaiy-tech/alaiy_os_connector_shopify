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
        status
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
