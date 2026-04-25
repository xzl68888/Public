/**
 * BURN CHAT - 加密自毁聊天服务器 (云部署版 v2)
 * 纯内存存储，无任何原生依赖，适配所有云平台
 */

const express = require('express');
const http = require('http');
const WebSocket = require('ws');
const { v4: uuidv4 } = require('uuid');
const path = require('path');

const app = express();
const server = http.createServer(app);
const wss = new WebSocket.Server({ server });

// ===== 纯内存数据库 =====
const users = new Map();       // username -> user object
const usersById = new Map();   // id -> user object
const onlineUsers = new Map(); // id -> { ...user, ws }

function createUser(username, password, avatar, color) {
  if (users.has(username)) return null;
  const id = uuidv4();
  const user = {
    id,
    username,
    password,
    avatar: avatar || '👤',
    color: color || randomColor(),
    createdAt: Date.now()
  };
  users.set(username, user);
  usersById.set(id, user);
  return user;
}

function findUser(username, password) {
  const user = users.get(username);
  if (!user || user.password !== password) return null;
  return user;
}

function randomColor() {
  const colors = ['#6366f1', '#8b5cf6', '#06b6d4', '#f59e0b', '#ef4444', '#10b981', '#ec4899'];
  return colors[Math.floor(Math.random() * colors.length)];
}

// ===== 中间件 =====
app.use(express.static(path.join(__dirname, 'public')));
app.use(express.json());

app.use((req, res, next) => {
  res.header('Access-Control-Allow-Origin', '*');
  res.header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.header('Access-Control-Allow-Headers', 'Content-Type, Authorization');
  if (req.method === 'OPTIONS') return res.sendStatus(200);
  next();
});

// ===== 路由 =====

app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

app.get('/health', (req, res) => {
  res.json({ status: 'ok', service: 'burn-chat', online: onlineUsers.size, registered: users.size });
});

app.get('/api/ping', (req, res) => {
  res.json({ pong: true, time: Date.now() });
});

// 注册
app.post('/api/register', (req, res) => {
  const { username, password, avatar, color } = req.body;

  if (!username || !password) {
    return res.status(400).json({ error: '用户名和密码不能为空' });
  }
  if (username.length < 2 || username.length > 20) {
    return res.status(400).json({ error: '用户名需要2-20字符' });
  }

  const user = createUser(username, password, avatar, color);
  if (!user) {
    return res.status(400).json({ error: '用户名已被占用' });
  }

  res.json({
    success: true,
    user: { id: user.id, username: user.username, avatar: user.avatar, color: user.color }
  });
});

// 登录
app.post('/api/login', (req, res) => {
  const { username, password } = req.body;
  const user = findUser(username, password);

  if (!user) {
    return res.status(401).json({ error: '用户名或密码错误' });
  }

  res.json({
    success: true,
    user: { id: user.id, username: user.username, avatar: user.avatar, color: user.color }
  });
});

// 在线用户列表
app.get('/api/online', (req, res) => {
  const list = Array.from(onlineUsers.values()).map(u => ({
    id: u.id, username: u.username, avatar: u.avatar, color: u.color
  }));
  res.json(list);
});

// ===== WebSocket =====

wss.on('connection', (ws) => {
  let currentUser = null;

  ws.on('message', (data) => {
    try {
      const msg = JSON.parse(data);

      switch (msg.type) {
        case 'auth': {
          const user = usersById.get(msg.userId);
          if (!user) return;

          currentUser = { ...user, ws };
          onlineUsers.set(user.id, currentUser);

          // 通知所有人：新用户上线
          broadcast({
            type: 'user_online',
            user: { id: user.id, username: user.username, avatar: user.avatar, color: user.color }
          }, user.id);

          // 发送当前在线列表给新用户
          ws.send(JSON.stringify({
            type: 'online_list',
            users: Array.from(onlineUsers.values())
              .filter(u => u.id !== user.id)
              .map(u => ({ id: u.id, username: u.username, avatar: u.avatar, color: u.color }))
          }));

          console.log(`✅ ${user.username} 已连接，在线: ${onlineUsers.size}`);
          break;
        }

        case 'chat': {
          if (!currentUser || !msg.toId) return;

          const target = onlineUsers.get(msg.toId);
          const msgData = {
            type: 'message',
            id: uuidv4(),
            fromId: currentUser.id,
            fromName: currentUser.username,
            fromAvatar: currentUser.avatar,
            fromColor: currentUser.color,
            content: msg.content,
            mediaType: msg.mediaType || null,
            mediaData: msg.mediaData || null,
            mediaName: msg.mediaName || null,
            burnAfter: msg.burnAfter || 10,
            timestamp: Date.now()
          };

          // 发给对方
          if (target && target.ws.readyState === WebSocket.OPEN) {
            target.ws.send(JSON.stringify(msgData));
          }

          // 发回给自己（确认已发送）
          ws.send(JSON.stringify({ ...msgData, sent: true }));
          break;
        }
      }
    } catch (err) {
      console.error('消息处理错误:', err.message);
    }
  });

  ws.on('close', () => {
    if (currentUser) {
      onlineUsers.delete(currentUser.id);
      broadcast({ type: 'user_offline', userId: currentUser.id });
      console.log(`❌ ${currentUser.username} 已断开，在线: ${onlineUsers.size}`);
    }
  });

  ws.on('error', (err) => {
    console.error('WebSocket 错误:', err.message);
  });
});

function broadcast(data, excludeId) {
  const msg = JSON.stringify(data);
  onlineUsers.forEach((user) => {
    if (user.id !== excludeId && user.ws.readyState === WebSocket.OPEN) {
      user.ws.send(msg);
    }
  });
}

// ===== 启动 =====
const PORT = process.env.PORT || 3000;
server.listen(PORT, '0.0.0.0', () => {
  console.log(`🔥 BURN CHAT 已启动 | 端口: ${PORT} | 环境: ${process.env.RENDER ? '云部署(Render)' : '本地'}`);
});
