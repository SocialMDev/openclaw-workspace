import { v } from "convex/values";
import { query, mutation } from "./_generated/server";

// Get all scheduled tasks
export const list = query({
  args: {
    enabledOnly: v.optional(v.boolean()),
  },
  handler: async (ctx, args) => {
    let query = ctx.db.query("scheduledTasks").order("asc");
    
    if (args.enabledOnly) {
      query = query.withIndex("by_enabled", (q) => q.eq("enabled", true));
    }

    return await query.collect();
  },
});

// Get tasks for a specific time range
export const getByTimeRange = query({
  args: {
    startTime: v.number(),
    endTime: v.number(),
  },
  handler: async (ctx, args) => {
    return await ctx.db
      .query("scheduledTasks")
      .withIndex("by_next_run", (q) => 
        q.gte("nextRun", args.startTime).lte("nextRun", args.endTime)
      )
      .collect();
  },
});

// Get a single task by ID
export const get = query({
  args: { id: v.id("scheduledTasks") },
  handler: async (ctx, args) => {
    return await ctx.db.get(args.id);
  },
});

// Create a new scheduled task
export const create = mutation({
  args: {
    name: v.string(),
    description: v.string(),
    cronExpression: v.string(),
    nextRun: v.number(),
    enabled: v.boolean(),
    color: v.optional(v.string()),
  },
  handler: async (ctx, args) => {
    return await ctx.db.insert("scheduledTasks", {
      ...args,
      createdAt: Date.now(),
      runCount: 0,
    });
  },
});

// Update a scheduled task
export const update = mutation({
  args: {
    id: v.id("scheduledTasks"),
    name: v.optional(v.string()),
    description: v.optional(v.string()),
    cronExpression: v.optional(v.string()),
    nextRun: v.optional(v.number()),
    enabled: v.optional(v.boolean()),
    color: v.optional(v.string()),
  },
  handler: async (ctx, args) => {
    const { id, ...updates } = args;
    return await ctx.db.patch(id, updates);
  },
});

// Delete a scheduled task
export const remove = mutation({
  args: { id: v.id("scheduledTasks") },
  handler: async (ctx, args) => {
    return await ctx.db.delete(args.id);
  },
});

// Mark task as run (update lastRun and runCount)
export const markRun = mutation({
  args: { id: v.id("scheduledTasks") },
  handler: async (ctx, args) => {
    const task = await ctx.db.get(args.id);
    if (!task) return null;
    
    return await ctx.db.patch(args.id, {
      lastRun: Date.now(),
      runCount: (task.runCount ?? 0) + 1,
    });
  },
});

// Get upcoming tasks
export const getUpcoming = query({
  args: { limit: v.optional(v.number()) },
  handler: async (ctx, args) => {
    const now = Date.now();
    const limit = args.limit ?? 10;
    
    return await ctx.db
      .query("scheduledTasks")
      .withIndex("by_next_run", (q) => q.gte("nextRun", now))
      .filter((q) => q.eq(q.field("enabled"), true))
      .order("asc")
      .take(limit);
  },
});
