import { shopifyClient } from './client';
import type { Article, ArticleAuthorConnection, ArticleBlogInput, ArticleConnection, ArticleCreateInput, ArticleCreatePayload, ArticleDeletePayload, ArticleSortKeys, ArticleTagSort, ArticleUpdateInput, ArticleUpdatePayload, Blog, BlogConnection, BlogCreateInput, BlogCreatePayload, BlogDeletePayload, BlogSortKeys, BlogUpdateInput, BlogUpdatePayload, Comment, CommentApprovePayload, CommentConnection, CommentDeletePayload, CommentNotSpamPayload, CommentSortKeys, CommentSpamPayload, Count, Menu, MenuConnection, MenuCreatePayload, MenuDeletePayload, MenuItemCreateInput, MenuItemUpdateInput, MenuSortKeys, MenuUpdatePayload, Page, PageConnection, PageCreateInput, PageCreatePayload, PageDeletePayload, PageSortKeys, PageUpdateInput, PageUpdatePayload, SavedSearchCreateInput, SavedSearchCreatePayload, SavedSearchDeleteInput, SavedSearchDeletePayload, SavedSearchUpdateInput, SavedSearchUpdatePayload, ScriptTagConnection, ScriptTagCreatePayload, ScriptTagDeletePayload, ScriptTagInput, ScriptTagUpdatePayload } from './types';

// ============================================================
// Content Management (Articles, Blogs, Pages, Menus)
// 38 operations
// ============================================================

/** Returns a `Article` resource by ID. */
export interface ArticleArgs {
  id: string;
}

export async function article(args: ArticleArgs): Promise<Article | null> {
  const gql = `#graphql
    query article($id: ID!) {
      article(id: $id) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ article: Article | null }>(gql, args);
  return data.article;
}

/** Requires `read_content` access scope or `read_online_store_pages` access scope. */
export interface ArticleAuthorsArgs {
  after?: string;
  before?: string;
  first?: number;
  last?: number;
  reverse?: boolean;
}

export async function articleAuthors(args?: ArticleAuthorsArgs): Promise<ArticleAuthorConnection> {
  const gql = `#graphql
    query articleAuthors($after: String, $before: String, $first: Int, $last: Int, $reverse: Boolean) {
      articleAuthors(after: $after, before: $before, first: $first, last: $last, reverse: $reverse) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ articleAuthors: ArticleAuthorConnection }>(gql, args);
  return data.articleAuthors;
}

/** Returns a paginated list of articles from the shop's blogs. [`Article`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Article) objects are blog posts that contain content like text, images, and tags. */
export interface ArticlesArgs {
  after?: string;
  before?: string;
  first?: number;
  last?: number;
  query?: string;
  reverse?: boolean;
  sortKey?: ArticleSortKeys;
}

export async function articles(args?: ArticlesArgs): Promise<ArticleConnection> {
  const gql = `#graphql
    query articles($after: String, $before: String, $first: Int, $last: Int, $query: String, $reverse: Boolean, $sortKey: ArticleSortKeys) {
      articles(after: $after, before: $before, first: $first, last: $last, query: $query, reverse: $reverse, sortKey: $sortKey) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ articles: ArticleConnection }>(gql, args);
  return data.articles;
}

/** Requires `read_content` access scope or `read_online_store_pages` access scope. */
export interface ArticleTagsArgs {
  limit: number;
  sort?: ArticleTagSort;
}

export async function articleTags(args: ArticleTagsArgs): Promise<string[]> {
  const gql = `#graphql
    query articleTags($limit: Int!, $sort: ArticleTagSort) {
      articleTags(limit: $limit, sort: $sort) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ articleTags: string[] }>(gql, args);
  return data.articleTags;
}

/** Returns a `Blog` resource by ID. */
export interface BlogArgs {
  id: string;
}

export async function blog(args: BlogArgs): Promise<Blog | null> {
  const gql = `#graphql
    query blog($id: ID!) {
      blog(id: $id) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ blog: Blog | null }>(gql, args);
  return data.blog;
}

/** Returns a paginated list of the shop's [`Blog`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Blog) objects. Blogs serve as containers for [`Article`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Article) objects and provide content management capabili... */
export interface BlogsArgs {
  after?: string;
  before?: string;
  first?: number;
  last?: number;
  query?: string;
  reverse?: boolean;
  sortKey?: BlogSortKeys;
}

export async function blogs(args?: BlogsArgs): Promise<BlogConnection> {
  const gql = `#graphql
    query blogs($after: String, $before: String, $first: Int, $last: Int, $query: String, $reverse: Boolean, $sortKey: BlogSortKeys) {
      blogs(after: $after, before: $before, first: $first, last: $last, query: $query, reverse: $reverse, sortKey: $sortKey) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ blogs: BlogConnection }>(gql, args);
  return data.blogs;
}

/** Requires `read_content` access scope or `read_online_store_pages` access scope. */
export interface BlogsCountArgs {
  limit?: number;
  query?: string;
}

export async function blogsCount(args?: BlogsCountArgs): Promise<Count | null> {
  const gql = `#graphql
    query blogsCount($limit: Int, $query: String) {
      blogsCount(limit: $limit, query: $query) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ blogsCount: Count | null }>(gql, args);
  return data.blogsCount;
}

/** Returns a `Comment` resource by ID. */
export interface CommentArgs {
  id: string;
}

export async function comment(args: CommentArgs): Promise<Comment | null> {
  const gql = `#graphql
    query comment($id: ID!) {
      comment(id: $id) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ comment: Comment | null }>(gql, args);
  return data.comment;
}

/** List of the shop's comments. */
export interface CommentsArgs {
  after?: string;
  before?: string;
  first?: number;
  last?: number;
  query?: string;
  reverse?: boolean;
  sortKey?: CommentSortKeys;
}

export async function comments(args?: CommentsArgs): Promise<CommentConnection> {
  const gql = `#graphql
    query comments($after: String, $before: String, $first: Int, $last: Int, $query: String, $reverse: Boolean, $sortKey: CommentSortKeys) {
      comments(after: $after, before: $before, first: $first, last: $last, query: $query, reverse: $reverse, sortKey: $sortKey) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ comments: CommentConnection }>(gql, args);
  return data.comments;
}

/** Returns a `Menu` resource by ID. */
export interface MenuArgs {
  id: string;
}

export async function menu(args: MenuArgs): Promise<Menu | null> {
  const gql = `#graphql
    query menu($id: ID!) {
      menu(id: $id) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ menu: Menu | null }>(gql, args);
  return data.menu;
}

/** Retrieves navigation menus. Menus organize content into hierarchical navigation structures that merchants can display in the online store (for example, in headers, footers, and sidebars) and customer accounts. */
export interface MenusArgs {
  after?: string;
  before?: string;
  first?: number;
  last?: number;
  query?: string;
  reverse?: boolean;
  sortKey?: MenuSortKeys;
}

export async function menus(args?: MenusArgs): Promise<MenuConnection> {
  const gql = `#graphql
    query menus($after: String, $before: String, $first: Int, $last: Int, $query: String, $reverse: Boolean, $sortKey: MenuSortKeys) {
      menus(after: $after, before: $before, first: $first, last: $last, query: $query, reverse: $reverse, sortKey: $sortKey) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ menus: MenuConnection }>(gql, args);
  return data.menus;
}

/** Returns a `Page` resource by ID. */
export interface PageArgs {
  id: string;
}

export async function page(args: PageArgs): Promise<Page | null> {
  const gql = `#graphql
    query page($id: ID!) {
      page(id: $id) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ page: Page | null }>(gql, args);
  return data.page;
}

/** A paginated list of pages from the online store. [`Page`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Page) objects are content pages that merchants create to provide information to customers, such as 'About Us', 'Contact', or policy pages. */
export interface PagesArgs {
  after?: string;
  before?: string;
  first?: number;
  last?: number;
  query?: string;
  reverse?: boolean;
  savedSearchId?: string;
  sortKey?: PageSortKeys;
}

export async function pages(args?: PagesArgs): Promise<PageConnection> {
  const gql = `#graphql
    query pages($after: String, $before: String, $first: Int, $last: Int, $query: String, $reverse: Boolean, $savedSearchId: ID, $sortKey: PageSortKeys) {
      pages(after: $after, before: $before, first: $first, last: $last, query: $query, reverse: $reverse, savedSearchId: $savedSearchId, sortKey: $sortKey) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ pages: PageConnection }>(gql, args);
  return data.pages;
}

/** Requires `read_content` access scope or `read_online_store_pages` access scope. */
export interface PagesCountArgs {
  limit?: number;
}

export async function pagesCount(args?: PagesCountArgs): Promise<Count | null> {
  const gql = `#graphql
    query pagesCount($limit: Int) {
      pagesCount(limit: $limit) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ pagesCount: Count | null }>(gql, args);
  return data.pagesCount;
}

export interface ScriptTagArgs {
  id: string;
}

export async function scriptTag(args: ScriptTagArgs): Promise<boolean> {
  const gql = `#graphql
    query scriptTag($id: ID!) {
      scriptTag(id: $id) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ scriptTag: boolean }>(gql, args);
  return data.scriptTag;
}

export interface ScriptTagsArgs {
  after?: string;
  before?: string;
  first?: number;
  last?: number;
  query?: string;
  reverse?: boolean;
  src?: string;
}

export async function scriptTags(args?: ScriptTagsArgs): Promise<ScriptTagConnection> {
  const gql = `#graphql
    query scriptTags($after: String, $before: String, $first: Int, $last: Int, $query: String, $reverse: Boolean, $src: URL) {
      scriptTags(after: $after, before: $before, first: $first, last: $last, query: $query, reverse: $reverse, src: $src) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ scriptTags: ScriptTagConnection }>(gql, args);
  return data.scriptTags;
}

/** Requires Any of `write_content`, `write_online_store_pages` access scopes. */
export interface ArticleCreateArgs {
  article: ArticleCreateInput;
  blog?: ArticleBlogInput;
}

export async function articleCreate(args: ArticleCreateArgs): Promise<ArticleCreatePayload> {
  const gql = `#graphql
    mutation articleCreate($article: ArticleCreateInput!, $blog: ArticleBlogInput) {
      articleCreate(article: $article, blog: $blog) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ articleCreate: ArticleCreatePayload }>(gql, args);
  return data.articleCreate;
}

/** Requires Any of `write_content`, `write_online_store_pages` access scopes. */
export interface ArticleDeleteArgs {
  id: string;
}

export async function articleDelete(args: ArticleDeleteArgs): Promise<ArticleDeletePayload> {
  const gql = `#graphql
    mutation articleDelete($id: ID!) {
      articleDelete(id: $id) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ articleDelete: ArticleDeletePayload }>(gql, args);
  return data.articleDelete;
}

/** Requires Any of `write_content`, `write_online_store_pages` access scopes. */
export interface ArticleUpdateArgs {
  article: ArticleUpdateInput;
  blog?: ArticleBlogInput;
  id: string;
}

export async function articleUpdate(args: ArticleUpdateArgs): Promise<ArticleUpdatePayload> {
  const gql = `#graphql
    mutation articleUpdate($article: ArticleUpdateInput!, $blog: ArticleBlogInput, $id: ID!) {
      articleUpdate(article: $article, blog: $blog, id: $id) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ articleUpdate: ArticleUpdatePayload }>(gql, args);
  return data.articleUpdate;
}

/** Requires Any of `write_content`, `write_online_store_pages` access scopes. */
export interface BlogCreateArgs {
  blog: BlogCreateInput;
}

export async function blogCreate(args: BlogCreateArgs): Promise<BlogCreatePayload> {
  const gql = `#graphql
    mutation blogCreate($blog: BlogCreateInput!) {
      blogCreate(blog: $blog) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ blogCreate: BlogCreatePayload }>(gql, args);
  return data.blogCreate;
}

/** Requires Any of `write_content`, `write_online_store_pages` access scopes. */
export interface BlogDeleteArgs {
  id: string;
}

export async function blogDelete(args: BlogDeleteArgs): Promise<BlogDeletePayload> {
  const gql = `#graphql
    mutation blogDelete($id: ID!) {
      blogDelete(id: $id) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ blogDelete: BlogDeletePayload }>(gql, args);
  return data.blogDelete;
}

/** Requires Any of `write_content`, `write_online_store_pages` access scopes. */
export interface BlogUpdateArgs {
  blog: BlogUpdateInput;
  id: string;
}

export async function blogUpdate(args: BlogUpdateArgs): Promise<BlogUpdatePayload> {
  const gql = `#graphql
    mutation blogUpdate($blog: BlogUpdateInput!, $id: ID!) {
      blogUpdate(blog: $blog, id: $id) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ blogUpdate: BlogUpdatePayload }>(gql, args);
  return data.blogUpdate;
}

/** Requires Any of `write_content`, `write_online_store_pages` access scopes. */
export interface CommentApproveArgs {
  id: string;
}

export async function commentApprove(args: CommentApproveArgs): Promise<CommentApprovePayload> {
  const gql = `#graphql
    mutation commentApprove($id: ID!) {
      commentApprove(id: $id) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ commentApprove: CommentApprovePayload }>(gql, args);
  return data.commentApprove;
}

/** Requires Any of `write_content`, `write_online_store_pages` access scopes. */
export interface CommentDeleteArgs {
  id: string;
}

export async function commentDelete(args: CommentDeleteArgs): Promise<CommentDeletePayload> {
  const gql = `#graphql
    mutation commentDelete($id: ID!) {
      commentDelete(id: $id) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ commentDelete: CommentDeletePayload }>(gql, args);
  return data.commentDelete;
}

/** Requires Any of `write_content`, `write_online_store_pages` access scopes. */
export interface CommentNotSpamArgs {
  id: string;
}

export async function commentNotSpam(args: CommentNotSpamArgs): Promise<CommentNotSpamPayload> {
  const gql = `#graphql
    mutation commentNotSpam($id: ID!) {
      commentNotSpam(id: $id) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ commentNotSpam: CommentNotSpamPayload }>(gql, args);
  return data.commentNotSpam;
}

/** Requires Any of `write_content`, `write_online_store_pages` access scopes. */
export interface CommentSpamArgs {
  id: string;
}

export async function commentSpam(args: CommentSpamArgs): Promise<CommentSpamPayload> {
  const gql = `#graphql
    mutation commentSpam($id: ID!) {
      commentSpam(id: $id) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ commentSpam: CommentSpamPayload }>(gql, args);
  return data.commentSpam;
}

/** Requires `write_online_store_navigation` access scope. */
export interface MenuCreateArgs {
  handle: string;
  items: MenuItemCreateInput[];
  title: string;
}

export async function menuCreate(args: MenuCreateArgs): Promise<MenuCreatePayload> {
  const gql = `#graphql
    mutation menuCreate($handle: String!, $items: [MenuItemCreateInput!]!, $title: String!) {
      menuCreate(handle: $handle, items: $items, title: $title) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ menuCreate: MenuCreatePayload }>(gql, args);
  return data.menuCreate;
}

/** Requires `write_online_store_navigation` access scope. */
export interface MenuDeleteArgs {
  id: string;
}

export async function menuDelete(args: MenuDeleteArgs): Promise<MenuDeletePayload> {
  const gql = `#graphql
    mutation menuDelete($id: ID!) {
      menuDelete(id: $id) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ menuDelete: MenuDeletePayload }>(gql, args);
  return data.menuDelete;
}

/** Requires `write_online_store_navigation` access scope. */
export interface MenuUpdateArgs {
  handle?: string;
  id: string;
  items: MenuItemUpdateInput[];
  title: string;
}

export async function menuUpdate(args: MenuUpdateArgs): Promise<MenuUpdatePayload> {
  const gql = `#graphql
    mutation menuUpdate($handle: String, $id: ID!, $items: [MenuItemUpdateInput!]!, $title: String!) {
      menuUpdate(handle: $handle, id: $id, items: $items, title: $title) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ menuUpdate: MenuUpdatePayload }>(gql, args);
  return data.menuUpdate;
}

/** Requires Any of `write_content`, `write_online_store_pages` access scopes. */
export interface PageCreateArgs {
  page: PageCreateInput;
}

export async function pageCreate(args: PageCreateArgs): Promise<PageCreatePayload> {
  const gql = `#graphql
    mutation pageCreate($page: PageCreateInput!) {
      pageCreate(page: $page) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ pageCreate: PageCreatePayload }>(gql, args);
  return data.pageCreate;
}

/** Requires Any of `write_content`, `write_online_store_pages` access scopes. */
export interface PageDeleteArgs {
  id: string;
}

export async function pageDelete(args: PageDeleteArgs): Promise<PageDeletePayload> {
  const gql = `#graphql
    mutation pageDelete($id: ID!) {
      pageDelete(id: $id) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ pageDelete: PageDeletePayload }>(gql, args);
  return data.pageDelete;
}

/** Requires Any of `write_content`, `write_online_store_pages` access scopes. */
export interface PageUpdateArgs {
  id: string;
  page: PageUpdateInput;
}

export async function pageUpdate(args: PageUpdateArgs): Promise<PageUpdatePayload> {
  const gql = `#graphql
    mutation pageUpdate($id: ID!, $page: PageUpdateInput!) {
      pageUpdate(id: $id, page: $page) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ pageUpdate: PageUpdatePayload }>(gql, args);
  return data.pageUpdate;
}

/** Creates a saved search. */
export interface SavedSearchCreateArgs {
  input: SavedSearchCreateInput;
}

export async function savedSearchCreate(args: SavedSearchCreateArgs): Promise<SavedSearchCreatePayload> {
  const gql = `#graphql
    mutation savedSearchCreate($input: SavedSearchCreateInput!) {
      savedSearchCreate(input: $input) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ savedSearchCreate: SavedSearchCreatePayload }>(gql, args);
  return data.savedSearchCreate;
}

/** Delete a saved search. */
export interface SavedSearchDeleteArgs {
  input: SavedSearchDeleteInput;
}

export async function savedSearchDelete(args: SavedSearchDeleteArgs): Promise<SavedSearchDeletePayload> {
  const gql = `#graphql
    mutation savedSearchDelete($input: SavedSearchDeleteInput!) {
      savedSearchDelete(input: $input) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ savedSearchDelete: SavedSearchDeletePayload }>(gql, args);
  return data.savedSearchDelete;
}

/** Updates a saved search. */
export interface SavedSearchUpdateArgs {
  input: SavedSearchUpdateInput;
}

export async function savedSearchUpdate(args: SavedSearchUpdateArgs): Promise<SavedSearchUpdatePayload> {
  const gql = `#graphql
    mutation savedSearchUpdate($input: SavedSearchUpdateInput!) {
      savedSearchUpdate(input: $input) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ savedSearchUpdate: SavedSearchUpdatePayload }>(gql, args);
  return data.savedSearchUpdate;
}

/** Requires `write_script_tags` access scope. Also: Requires access to script tags. */
export interface ScriptTagCreateArgs {
  input: ScriptTagInput;
}

export async function scriptTagCreate(args: ScriptTagCreateArgs): Promise<ScriptTagCreatePayload> {
  const gql = `#graphql
    mutation scriptTagCreate($input: ScriptTagInput!) {
      scriptTagCreate(input: $input) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ scriptTagCreate: ScriptTagCreatePayload }>(gql, args);
  return data.scriptTagCreate;
}

/** Requires `write_script_tags` access scope. Also: Requires access to script tags. */
export interface ScriptTagDeleteArgs {
  id: string;
}

export async function scriptTagDelete(args: ScriptTagDeleteArgs): Promise<ScriptTagDeletePayload> {
  const gql = `#graphql
    mutation scriptTagDelete($id: ID!) {
      scriptTagDelete(id: $id) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ scriptTagDelete: ScriptTagDeletePayload }>(gql, args);
  return data.scriptTagDelete;
}

/** Requires `write_script_tags` access scope. Also: Requires access to script tags. */
export interface ScriptTagUpdateArgs {
  id: string;
  input: ScriptTagInput;
}

export async function scriptTagUpdate(args: ScriptTagUpdateArgs): Promise<ScriptTagUpdatePayload> {
  const gql = `#graphql
    mutation scriptTagUpdate($id: ID!, $input: ScriptTagInput!) {
      scriptTagUpdate(id: $id, input: $input) {
        # Specify the fields you need returned
      }
    }
  `;
  const data = await shopifyClient.request<{ scriptTagUpdate: ScriptTagUpdatePayload }>(gql, args);
  return data.scriptTagUpdate;
}

