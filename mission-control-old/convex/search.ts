import { v } from "convex/values";
import { query, mutation } from "./_generated/server";

// Search across all indexed content
export const search = query({
  args: {
    query: v.string(),
    source: v.optional(v.union(v.literal("memory"), v.literal("document"), v.literal("conversation"), v.literal("activity"))),
    limit: v.optional(v.number()),
  },
  handler: async (ctx, args) => {
    const limit = args.limit ?? 20;
    
    let searchQuery = ctx.db
      .query("searchIndex")
      .withSearchIndex("search_content", (q) => q.search("content", args.query));
    
    if (args.source) {
      searchQuery = searchQuery.filter((q) => q.eq(q.field("source"), args.source));
    }

    const results = await searchQuery.order("desc").take(limit);
    
    return results.map((item) => ({
      ...item,
      relevance: calculateRelevance(item.content, args.query),
    }));
  },
});

// Simple relevance scoring
function calculateRelevance(content: string, query: string): number {
  const contentLower = content.toLowerCase();
  const queryLower = query.toLowerCase();
  const queryWords = queryLower.split(/\s+/);
  
  let score = 0;
  
  // Exact match gets highest score
  if (contentLower.includes(queryLower)) {
    score += 10;
  }
  
  // Word matches
  for (const word of queryWords) {
    if (contentLower.includes(word)) {
      score += 1;
    }
  }
  
  return score;
}

// Add content to search index
export const index = mutation({
  args: {
    content: v.string(),
    source: v.union(v.literal("memory"), v.literal("document"), v.literal("conversation"), v.literal("activity")),
    sourceId: v.string(),
    title: v.optional(v.string()),
  },
  handler: async (ctx, args) => {
    return await ctx.db.insert("searchIndex", {
      ...args,
      timestamp: Date.now(),
    });
  },
});

// Remove content from search index
export const remove = mutation({
  args: { sourceId: v.string() },
  handler: async (ctx, args) => {
    const items = await ctx.db
      .query("searchIndex")
      .filter((q) => q.eq(q.field("sourceId"), args.sourceId))
      .collect();
    
    for (const item of items) {
      await ctx.db.delete(item._id);
    }
    
    return items.length;
  },
});

// Get recent indexed items
export const getRecent = query({
  args: {
    source: v.optional(v.union(v.literal("memory"), v.literal("document"), v.literal("conversation"), v.literal("activity"))),
    limit: v.optional(v.number()),
  },
  handler: async (ctx, args) => {
    let query = ctx.db.query("searchIndex").order("desc");
    
    if (args.source) {
      query = query.withIndex("by_source", (q) => q.eq("source", args.source));
    }

    return await query.take(args.limit ?? 50);
  },
});

// Get search statistics
export const getStats = query({
  args: {},
  handler: async (ctx) => {
    const allItems = await ctx.db.query("searchIndex").collect();
    
    const stats = {
      total: allItems.length,
      bySource: {
        memory: 0,
        document: 0,
        conversation: 0,
        activity: 0,
      },
    };

    for (const item of allItems) {
      stats.bySource[item.source]++;
    }

    return stats;
  },
});
