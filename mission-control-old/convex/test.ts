// Test file to verify Convex connection and functionality
// Run with: npx convex run test:ping

import { query } from "./_generated/server";

export const ping = query({
  args: {},
  handler: async (ctx) => {
    // Test database connection
    const activities = await ctx.db.query("activities").take(5);
    const tasks = await ctx.db.query("scheduledTasks").take(5);
    
    return {
      status: "ok",
      message: "Convex is connected and working!",
      stats: {
        activitiesCount: activities.length,
        tasksCount: tasks.length,
      },
      timestamp: Date.now(),
    };
  },
});
