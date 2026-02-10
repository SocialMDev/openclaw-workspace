import { v } from "convex/values";
import { query, mutation } from "./_generated/server";

// Get activities with pagination and filtering
export const list = query({
  args: {
    limit: v.optional(v.number()),
    cursor: v.optional(v.string()),
    type: v.optional(v.union(v.literal("file"), v.literal("command"), v.literal("api"), v.literal("message"), v.literal("task"))),
    sessionId: v.optional(v.string()),
  },
  handler: async (ctx, args) => {
    let query = ctx.db.query("activities").order("desc");
    
    if (args.type) {
      query = query.withIndex("by_type", (q) => q.eq("type", args.type));
    }
    
    if (args.sessionId) {
      query = query.withIndex("by_session", (q) => q.eq("sessionId", args.sessionId));
    }

    const limit = args.limit ?? 50;
    const { page, continueCursor, isDone } = await query.paginate({
      cursor: args.cursor,
      numItems: limit,
    });

    return {
      activities: page,
      cursor: continueCursor,
      hasMore: !isDone,
    };
  },
});

// Get a single activity by ID
export const get = query({
  args: { id: v.id("activities") },
  handler: async (ctx, args) => {
    return await ctx.db.get(args.id);
  },
});

// Create a new activity
export const create = mutation({
  args: {
    type: v.union(v.literal("file"), v.literal("command"), v.literal("api"), v.literal("message"), v.literal("task")),
    description: v.string(),
    metadata: v.optional(v.record(v.string(), v.any())),
    sessionId: v.string(),
    status: v.optional(v.union(v.literal("success"), v.literal("error"), v.literal("pending"))),
  },
  handler: async (ctx, args) => {
    return await ctx.db.insert("activities", {
      ...args,
      timestamp: Date.now(),
    });
  },
});

// Update activity status
export const updateStatus = mutation({
  args: {
    id: v.id("activities"),
    status: v.union(v.literal("success"), v.literal("error"), v.literal("pending")),
  },
  handler: async (ctx, args) => {
    return await ctx.db.patch(args.id, { status: args.status });
  },
});

// Get activity statistics
export const getStats = query({
  args: {},
  handler: async (ctx) => {
    const allActivities = await ctx.db.query("activities").collect();
    
    const stats = {
      total: allActivities.length,
      byType: {
        file: 0,
        command: 0,
        api: 0,
        message: 0,
        task: 0,
      },
      byStatus: {
        success: 0,
        error: 0,
        pending: 0,
      },
    };

    for (const activity of allActivities) {
      stats.byType[activity.type]++;
      if (activity.status) {
        stats.byStatus[activity.status]++;
      }
    }

    return stats;
  },
});

// Get recent activities (last 24 hours)
export const getRecent = query({
  args: { hours: v.optional(v.number()) },
  handler: async (ctx, args) => {
    const hours = args.hours ?? 24;
    const cutoff = Date.now() - hours * 60 * 60 * 1000;
    
    return await ctx.db
      .query("activities")
      .withIndex("by_timestamp", (q) => q.gte("timestamp", cutoff))
      .order("desc")
      .take(100);
  },
});
