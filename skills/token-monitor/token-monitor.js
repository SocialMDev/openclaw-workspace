#!/usr/bin/env node
/**
 * Token Monitor - Analyze OpenClaw token usage across sessions
 * 
 * Usage: node token-monitor.js [--limit N] [--detail] [--days N]
 */

const fs = require('fs');
const path = require('path');
const os = require('os');

// Parse arguments
const args = process.argv.slice(2);
const limit = parseInt(getArg(args, '--limit', '20'), 10);
const detail = args.includes('--detail');
const days = parseInt(getArg(args, '--days', '0'), 10); // 0 = all time

function getArg(args, flag, defaultVal) {
  const idx = args.indexOf(flag);
  if (idx !== -1 && args[idx + 1]) {
    return args[idx + 1];
  }
  return defaultVal;
}

// Paths
const OPENCLAW_HOME = path.join(os.homedir(), '.openclaw');
const AGENTS_DIR = path.join(OPENCLAW_HOME, 'agents');
const LOGS_DIR = '/tmp/openclaw';

// Colors for terminal output
const colors = {
  reset: '\x1b[0m',
  bright: '\x1b[1m',
  dim: '\x1b[2m',
  red: '\x1b[31m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  magenta: '\x1b[35m',
  cyan: '\x1b[36m',
};

function colorize(text, color) {
  return `${colors[color]}${text}${colors.reset}`;
}

function formatNumber(num) {
  if (!num && num !== 0) return '-';
  return num.toLocaleString();
}

function formatCost(cost) {
  if (!cost && cost !== 0) return '-';
  if (cost < 0.01) return `<$0.01`;
  return `$${cost.toFixed(2)}`;
}

function truncate(str, len) {
  if (!str) return '';
  if (str.length <= len) return str;
  return str.slice(0, len - 3) + '...';
}

function formatDate(ts) {
  if (!ts) return '-';
  const date = new Date(ts);
  const now = new Date();
  const diff = now - date;
  const hours = Math.floor(diff / (1000 * 60 * 60));
  const days = Math.floor(hours / 24);
  
  if (hours < 1) return 'just now';
  if (hours < 24) return `${hours}h ago`;
  if (days < 7) return `${days}d ago`;
  return date.toLocaleDateString();
}

// Main analysis
async function analyzeTokens() {
  console.log(colorize('🔥 Token Burner Analysis', 'bright'));
  console.log(colorize('═'.repeat(70), 'dim'));
  
  // Check if agents directory exists
  if (!fs.existsSync(AGENTS_DIR)) {
    console.error(colorize('❌ No agents directory found at:', 'red'), AGENTS_DIR);
    process.exit(1);
  }
  
  // Get all agent directories
  const agents = fs.readdirSync(AGENTS_DIR).filter(f => {
    const agentPath = path.join(AGENTS_DIR, f);
    return fs.statSync(agentPath).isDirectory();
  });
  
  if (agents.length === 0) {
    console.log(colorize('No agents found.', 'yellow'));
    return;
  }
  
  let allSessions = [];
  let totalInput = 0;
  let totalOutput = 0;
  let totalCost = 0;
  
  for (const agentId of agents) {
    const sessionsPath = path.join(AGENTS_DIR, agentId, 'sessions', 'sessions.json');
    
    if (!fs.existsSync(sessionsPath)) {
      continue;
    }
    
    try {
      const sessionsData = JSON.parse(fs.readFileSync(sessionsPath, 'utf8'));
      
      for (const [sessionKey, session] of Object.entries(sessionsData)) {
        // Filter by date if specified
        if (days > 0 && session.updatedAt) {
          const cutoff = Date.now() - (days * 24 * 60 * 60 * 1000);
          if (session.updatedAt < cutoff) {
            continue;
          }
        }
        
        const inputTokens = session.inputTokens || 0;
        const outputTokens = session.outputTokens || 0;
        const totalTokens = inputTokens + outputTokens;
        
        // Estimate cost (rough approximation)
        // Assuming average pricing: $2.50/m input, $10/m output
        const estimatedCost = (inputTokens * 2.50 + outputTokens * 10) / 1_000_000;
        
        allSessions.push({
          agentId,
          sessionKey,
          sessionId: session.sessionId,
          inputTokens,
          outputTokens,
          totalTokens,
          contextTokens: session.contextTokens || 0,
          updatedAt: session.updatedAt,
          compactionCount: session.compactionCount || 0,
          estimatedCost,
        });
        
        totalInput += inputTokens;
        totalOutput += outputTokens;
        totalCost += estimatedCost;
      }
    } catch (err) {
      console.error(colorize(`⚠️  Error reading sessions for ${agentId}:`, 'yellow'), err.message);
    }
  }
  
  // Sort by total tokens (descending)
  allSessions.sort((a, b) => b.totalTokens - a.totalTokens);
  
  // Display summary
  console.log(`\n${colorize('📊 Summary', 'bright')}`);
  console.log(`   Agents analyzed: ${colorize(agents.length.toString(), 'cyan')}`);
  console.log(`   Total sessions: ${colorize(allSessions.length.toString(), 'cyan')}`);
  console.log(`   Total input tokens: ${colorize(formatNumber(totalInput), 'green')}`);
  console.log(`   Total output tokens: ${colorize(formatNumber(totalOutput), 'green')}`);
  console.log(`   Combined tokens: ${colorize(formatNumber(totalInput + totalOutput), 'bright')}`);
  console.log(`   Estimated cost: ${colorize(formatCost(totalCost), 'yellow')}`);
  
  if (allSessions.length === 0) {
    console.log(colorize('\nNo sessions found matching criteria.', 'yellow'));
    return;
  }
  
  // Display top sessions table
  console.log(`\n${colorize('🔥 Top Token Burners', 'bright')} (showing top ${Math.min(limit, allSessions.length)})`);
  console.log(colorize('─'.repeat(100), 'dim'));
  
  // Header
  console.log(
    `${colorize('Rank', 'bright').padEnd(5)} ` +
    `${colorize('Session', 'bright').padEnd(40)} ` +
    `${colorize('Input', 'bright').padStart(10)} ` +
    `${colorize('Output', 'bright').padStart(10)} ` +
    `${colorize('Total', 'bright').padStart(10)} ` +
    `${colorize('Context', 'bright').padStart(10)} ` +
    `${colorize('Cost', 'bright').padStart(8)} ` +
    `${colorize('Last Active', 'bright').padStart(12)}`
  );
  console.log(colorize('─'.repeat(100), 'dim'));
  
  // Rows
  const topSessions = allSessions.slice(0, limit);
  topSessions.forEach((s, idx) => {
    const rank = (idx + 1).toString().padEnd(5);
    const sessionName = truncate(s.sessionKey, 37).padEnd(40);
    const input = formatNumber(s.inputTokens).padStart(10);
    const output = formatNumber(s.outputTokens).padStart(10);
    const total = colorize(formatNumber(s.totalTokens).padStart(10), s.totalTokens > 100000 ? 'red' : s.totalTokens > 50000 ? 'yellow' : 'reset');
    const context = formatNumber(s.contextTokens).padStart(10);
    const cost = formatCost(s.estimatedCost).padStart(8);
    const lastActive = formatDate(s.updatedAt).padStart(12);
    
    console.log(`${rank} ${sessionName} ${input} ${output} ${total} ${context} ${cost} ${lastActive}`);
  });
  
  console.log(colorize('─'.repeat(100), 'dim'));
  
  // Show distribution
  if (allSessions.length > 1) {
    console.log(`\n${colorize('📈 Token Distribution', 'bright')}`);
    const avgTokens = (totalInput + totalOutput) / allSessions.length;
    const medianTokens = allSessions[Math.floor(allSessions.length / 2)].totalTokens;
    const maxTokens = allSessions[0].totalTokens;
    
    console.log(`   Average per session: ${colorize(formatNumber(Math.round(avgTokens)), 'cyan')}`);
    console.log(`   Median per session: ${colorize(formatNumber(medianTokens), 'cyan')}`);
    console.log(`   Heaviest session: ${colorize(formatNumber(maxTokens), 'red')} (${allSessions[0].sessionKey})`);
    
    // Calculate percentiles
    const p90Idx = Math.floor(allSessions.length * 0.9);
    const p95Idx = Math.floor(allSessions.length * 0.95);
    const p99Idx = Math.floor(allSessions.length * 0.99);
    
    console.log(`   90th percentile: ${colorize(formatNumber(allSessions[p90Idx]?.totalTokens || 0), 'cyan')}`);
    console.log(`   95th percentile: ${colorize(formatNumber(allSessions[p95Idx]?.totalTokens || 0), 'cyan')}`);
    console.log(`   99th percentile: ${colorize(formatNumber(allSessions[p99Idx]?.totalTokens || 0), 'cyan')}`);
  }
  
  // Detailed analysis if requested
  if (detail) {
    await analyzeTranscripts(allSessions.slice(0, 10));
  }
  
  // Recent gateway logs summary
  await analyzeGatewayLogs();
}

async function analyzeTranscripts(topSessions) {
  console.log(`\n${colorize('🔍 Detailed Analysis (Top Sessions)', 'bright')}`);
  
  for (const session of topSessions.slice(0, 5)) {
    const transcriptPath = path.join(
      AGENTS_DIR, 
      session.agentId, 
      'sessions', 
      `${session.sessionId}.jsonl`
    );
    
    if (!fs.existsSync(transcriptPath)) {
      continue;
    }
    
    try {
      const content = fs.readFileSync(transcriptPath, 'utf8');
      const lines = content.trim().split('\n').filter(l => l.trim());
      
      let toolCalls = 0;
      let userMessages = 0;
      let assistantMessages = 0;
      const toolTypes = {};
      
      for (const line of lines) {
        try {
          const entry = JSON.parse(line);
          
          if (entry.type === 'message') {
            if (entry.role === 'user') userMessages++;
            if (entry.role === 'assistant') assistantMessages++;
          }
          
          if (entry.tool_calls) {
            toolCalls += entry.tool_calls.length;
            for (const tc of entry.tool_calls) {
              const toolName = tc.function?.name || 'unknown';
              toolTypes[toolName] = (toolTypes[toolName] || 0) + 1;
            }
          }
        } catch (e) {
          // Skip malformed lines
        }
      }
      
      console.log(`\n   ${colorize(truncate(session.sessionKey, 40), 'bright')} (${formatNumber(session.totalTokens)} tokens)`);
      console.log(`   └─ Messages: ${userMessages} user, ${assistantMessages} assistant`);
      console.log(`   └─ Tool calls: ${toolCalls}`);
      
      if (Object.keys(toolTypes).length > 0) {
        const sortedTools = Object.entries(toolTypes)
          .sort((a, b) => b[1] - a[1])
          .slice(0, 5);
        console.log(`   └─ Top tools: ${sortedTools.map(([name, count]) => `${name}(${count})`).join(', ')}`);
      }
      
    } catch (err) {
      // Skip errors
    }
  }
}

async function analyzeGatewayLogs() {
  if (!fs.existsSync(LOGS_DIR)) {
    return;
  }
  
  const logFiles = fs.readdirSync(LOGS_DIR)
    .filter(f => f.startsWith('openclaw-') && f.endsWith('.log'))
    .sort()
    .reverse()
    .slice(0, 3); // Last 3 days
  
  if (logFiles.length === 0) {
    return;
  }
  
  console.log(`\n${colorize('📜 Recent Gateway Activity', 'bright')}`);
  
  let totalRequests = 0;
  let errors = 0;
  
  for (const logFile of logFiles) {
    const logPath = path.join(LOGS_DIR, logFile);
    
    try {
      const content = fs.readFileSync(logPath, 'utf8');
      const lines = content.trim().split('\n').filter(l => l.trim());
      
      for (const line of lines) {
        try {
          const entry = JSON.parse(line);
          if (entry.msg && entry.msg.includes('inference')) {
            totalRequests++;
          }
          if (entry.level === 'error' || (entry.msg && entry.msg.includes('error'))) {
            errors++;
          }
        } catch (e) {}
      }
    } catch (err) {}
  }
  
  console.log(`   Log files analyzed: ${logFiles.length}`);
  console.log(`   Inference requests: ${colorize(formatNumber(totalRequests), 'cyan')}`);
  if (errors > 0) {
    console.log(`   Errors logged: ${colorize(formatNumber(errors), 'red')}`);
  }
}

// Run
analyzeTokens().catch(err => {
  console.error(colorize('Error:', 'red'), err.message);
  process.exit(1);
});
