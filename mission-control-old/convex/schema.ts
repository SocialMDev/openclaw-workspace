import { defineSchema, defineTable } from "convex/server";
import { v } from "convex/values";

export default defineSchema({
  activities: defineTable({
    type: v.union(v.literal("file"), v.literal("command"), v.literal("api"), v.literal("message"), v.literal("task")),
    description: v.string(),
    metadata: v.optional(v.record(v.string(), v.any())),
    timestamp: v.number(),
    sessionId: v.string(),
    status: v.optional(v.union(v.literal("success"), v.literal("error"), v.literal("pending"))),
  })
    .index("by_timestamp", ["timestamp"])
    .index("by_type", ["type"])
    .index("by_session", ["sessionId"]),

  scheduledTasks: defineTable({
    name: v.string(),
    description: v.string(),
    cronExpression: v.string(),
    nextRun: v.number(),
    enabled: v.boolean(),
    createdAt: v.number(),
    lastRun: v.optional(v.number()),
    runCount: v.optional(v.number()),
    color: v.optional(v.string()),
  })
    .index("by_next_run", ["nextRun"])
    .index("by_enabled", ["enabled"]),

  searchIndex: defineTable({
    content: v.string(),
    source: v.union(v.literal("memory"), v.literal("document"), v.literal("conversation"), v.literal("activity")),
    sourceId: v.string(),
    timestamp: v.number(),
    title: v.optional(v.string()),
  })
    .index("by_source", ["source"])
    .index("by_timestamp", ["timestamp"])
    .searchIndex("search_content", {
      searchField: "content",
      filterFields: ["source"],
    }),
});
