# BURN CHAT - Render.com 部署配置

# 使用官方 Node.js 18 镜像
FROM node:18-alpine

# 工作目录
WORKDIR /app

# 复制 package 文件
COPY package.json ./
RUN npm install

# 复制应用文件
COPY . .

# 暴露端口
EXPOSE 3000

# 启动命令
CMD ["node", "server.js"]