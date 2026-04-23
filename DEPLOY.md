# 🔥 BURN CHAT - 部署指南

## 方式一：Render.com（推荐，免费）

### 步骤 1：推送代码到 GitHub
```bash
# 在 burn-chat-deploy 目录操作
cd burn-chat-deploy
git init
git add .
git commit -m "burn-chat server"
# 创建 GitHub 仓库后
git remote add origin https://github.com/你的用户名/burn-chat.git
git push -u origin main
```

### 步骤 2：在 Render.com 创建服务
1. 访问 https://dashboard.render.com
2. 用 GitHub 登录
3. 点击 "New +" → "Web Service"
4. 选择你的 burn-chat 仓库
5. 配置：
   - **Name**: burn-chat
   - **Environment**: Node
   - **Build Command**: npm install
   - **Start Command**: node server.js
6. 点击 "Create Web Service"

### 步骤 3：获取访问地址
部署完成后，Render 会给你一个 URL，例如：
`https://burn-chat.onrender.com`

---

## 方式二：Railway.app

### 步骤 1：推送代码到 GitHub（同上）

### 步骤 2：在 Railway 创建项目
1. 访问 https://railway.app
2. 用 GitHub 登录
3. 点击 "New Project"
4. 选择 "Deploy from GitHub repo"
5. 选择 burn-chat 仓库
6. 点击 "Deploy"

### 步骤 3：配置环境变量
在 Railway 项目的 Settings 中添加：
- `PORT`: 3000

---

## 方式三：Fly.io

```bash
# 安装 flyctl
winget install Flyctl.Flyctl

# 登录
flyctl auth login

# 部署
cd burn-chat-deploy
flyctl launch --name burn-chat --org personal
```

---

## APP 连接配置

部署后，在手机 APP 中设置服务器地址：
- Render: `https://burn-chat-xxx.onrender.com`
- Railway: `https://burn-chat.railway.app`
- Fly: `https://burn-chat.fly.dev`

---

## 本地测试

```bash
cd burn-chat-deploy
npm install
npm start
# 访问 http://localhost:3000
```