/**
 * BURN CHAT - 加密自毁聊天服务器
 * 多人实时社交版 (纯JS实现)
 */

const express = require('express');
const http = require('http');
const WebSocket = require('ws');
const initSqlJs = require('sql.js');
const { v4: uuidv4 } = require('uuid');
const path = require('path');
const fs = require('fs');

const app = express();
const server = http.createServer(app);
const wss = new WebSocket.Server({ server });

// 数据库
let db;
const DB_PATH = path.join(__dirname, 'burnchat.db');

async function initDB() {
  const SQL = await initSqlJs();
  
  if (fs.existsSync(DB_PATH)) {
    const fileBuffer = fs.readFileSync(DB_PATH);
    db = new SQL.Database(fileBuffer);
  } else {
    db = new SQL.Database();
  }
  
  db.run(`
    CREATE TABLE IF NOT EXISTS users (
      id TEXT PRIMARY KEY,
      username TEXT UNIQUE NOT NULL,
      password TEXT NOT NULL,
      avatar TEXT DEFAULT '👤',
      color TEXT DEFAULT '#6366f1',
      created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
  `);
  
  saveDB();
}

function saveDB() {
  const data = db.export();
  const buffer = Buffer.from(data);
  fs.writeFileSync(DB_PATH, buffer);
}

// 在线用户
const onlineUsers = new Map();

// 静态文件 + CORS（允许 APP 跨域访问）
app.use(express.static(path.join(__dirname, 'public')));
app.use(express.json());

// 允许跨域
app.use((req, res, next) => {
  res.header('Access-Control-Allow-Origin', '*');
  res.header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.header('Access-Control-Allow-Headers', 'Content-Type');
  if (req.method === 'OPTIONS') return res.sendStatus(200);
  next();
});

// ===== API =====

// 注册
app.post('/api/register', (req, res) => {
  const { username, password, avatar, color } = req.body;
  
  if (!username || !password) {
    return res.status(400).json({ error: '用户名和密码不能为空' });
  }
  
  if (username.length < 2 || username.length > 20) {
    return res.status(400).json({ error: '用户名需要2-20字符' });
  }
  
  try {
    const id = uuidv4();
    const userColor = color || randomColor();
    db.run(
      'INSERT INTO users (id, username, password, avatar, color) VALUES (?, ?, ?, ?, ?)',
      [id, username, password, avatar || '👤', userColor]
    );
    saveDB();
    
    res.json({ 
      success: true, 
      user: { id, username, avatar: avatar || '👤', color: userColor } 
    });
  } catch (err) {
    if (err.message.includes('UNIQUE')) {
      res.status(400).json({ error: '用户名已被占用' });
    } else {
      res.status(500).json({ error: '注册失败' });
    }
  }
});

// 登录
app.post('/api/login', (req, res) => {
  const { username, password } = req.body;
  
  const rows = db.exec(
    'SELECT * FROM users WHERE username = ? AND password = ?',
    [username, password]
  );
  
  if (rows.length === 0 || rows[0].values.length === 0) {
    return res.status(401).json({ error: '用户名或密码错误' });
  }
  
  const cols = rows[0].columns;
  const vals = rows[0].values[0];
  const user = {};
  cols.forEach((c, i) => user[c] = vals[i]);
  
  res.json({ 
    success: true, 
    user: { 
      id: user.id, 
      username: user.username, 
      avatar: user.avatar, 
      color: user.color 
    } 
  });
});

// 获取在线用户
app.get('/api/online', (req, res) => {
  const users = Array.from(onlineUsers.values()).map(u => ({
    id: u.id,
    username: u.username,
    avatar: u.avatar,
    color: u.color
  }));
  res.json(users);
});

// ===== WebSocket =====

wss.on('connection', (ws, req) => {
  let currentUser = null;
  
  // 获取客户端 IP
  const clientIp = req.socket.remoteAddress;
  
  ws.on('message', (data) => {
    try {
      const msg = JSON.parse(data);
      
      switch (msg.type) {
        case 'auth': {
          const rows = db.exec('SELECT * FROM users WHERE id = ?', [msg.userId]);
          if (rows.length > 0 && rows[0].values.length > 0) {
            const cols = rows[0].columns;
            const vals = rows[0].values[0];
            const user = {};
            cols.forEach((c, i) => user[c] = vals[i]);
            
            currentUser = {
              id: user.id,
              username: user.username,
              avatar: user.avatar,
              color: user.color,
              ws,
              ip: clientIp
            };
            onlineUsers.set(user.id, currentUser);
            
            broadcast({
              type: 'user_online',
              user: { 
                id: user.id, 
                username: user.username, 
                avatar: user.avatar, 
                color: user.color 
              }
            });
            
            ws.send(JSON.stringify({
              type: 'online_list',
              users: Array.from(onlineUsers.values())
                .filter(u => u.id !== currentUser.id)
                .map(u => ({
                  id: u.id,
                  username: u.username,
                  avatar: u.avatar,
                  color: u.color
                }))
            }));
            
            console.log(`✅ ${user.username} 已连接 (${clientIp})`);
          }
          break;
        }
        
        case 'chat': {
          if (!currentUser || !msg.toId) return;
          
          const targetUser = onlineUsers.get(msg.toId);
          const msgData = {
            type: 'message',
            id: uuidv4(),
            fromId: currentUser.id,
            fromName: currentUser.username,
            fromAvatar: currentUser.avatar,
            fromColor: currentUser.color,
            content: msg.content,
            burnAfter: msg.burnAfter || 10,
            timestamp: Date.now()
          };
          
          if (targetUser && targetUser.ws.readyState === WebSocket.OPEN) {
            targetUser.ws.send(JSON.stringify(msgData));
          }
          
          ws.send(JSON.stringify({ ...msgData, sent: true }));
          break;
        }
      }
    } catch (err) {
      console.error('消息处理错误:', err);
    }
  });
  
  ws.on('close', () => {
    if (currentUser) {
      onlineUsers.delete(currentUser.id);
      broadcast({
        type: 'user_offline',
        userId: currentUser.id
      });
      console.log(`❌ ${currentUser.username} 已断开`);
    }
  });
});

function broadcast(data) {
  const msg = JSON.stringify(data);
  onlineUsers.forEach(user => {
    if (user.ws.readyState === WebSocket.OPEN) {
      user.ws.send(msg);
    }
  });
}

function randomColor() {
  const colors = ['#6366f1', '#8b5cf6', '#06b6d4', '#f59e0b', '#ef4444', '#10b981', '#ec4899'];
  return colors[Math.floor(Math.random() * colors.length)];
}

// 启动
initDB().then(() => {
  const PORT = process.env.PORT || 3000;
  server.listen(PORT, '0.0.0.0', () => {
    const os = require('os');
    const interfaces = os.networkInterfaces();
    const ips = [];
    
    Object.values(interfaces).forEach(iface => {
      iface.forEach(addr => {
        if (addr.family === 'IPv4' && !addr.internal) {
          ips.push(addr.address);
        }
      });
    });
    
    console.log(`
╔══════════════════════════════════════════════════════╗
║                                                      ║
║   🔥 BURN CHAT APP 服务器已启动                       ║
║                                                      ║
║   本地访问:   http://localhost:${PORT}                  ║
${ips.map(ip => `║   局域网:     http://${ip}:${PORT}                  ║`).join('\n')}
║                                                      ║
║   📱 APP 使用方法：                                   ║
║   1. 在 APP 设置中填入服务器地址                      ║
║      http://<你的IP>:${PORT}                           ║
║   2. 注册/登录后即可使用                              ║
║                                                      ║
╚══════════════════════════════════════════════════════╝
    `);
  });
});
