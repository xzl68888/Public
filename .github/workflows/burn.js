let sharedKey = null;

// 1. 加密模块初始化[cite: 2]
async function initCrypto() {
    if (!window.isSecureContext) {
        alert("🚨 安全警告：\n加密模块需要在 HTTPS 环境下启动。");[cite: 2]
        document.getElementById('status').innerText = "❌ 环境不安全";[cite: 2]
        return;
    }

    if (!window.crypto || !window.crypto.subtle) {
        alert("🚫 浏览器版本过低，不支持加密 API。");[cite: 2]
        return;
    }

    let keyData;
    const hash = decodeURIComponent(window.location.hash.substring(1));[cite: 2]

    if (hash && hash.length >= 32) {
        // 从 URL Hash 恢复密钥并清除痕迹[cite: 2]
        keyData = new TextEncoder().encode(hash.substring(0, 32));[cite: 2]
        try {
            window.history.replaceState(null, null, window.location.pathname);[cite: 2]
        } catch (e) {
            window.location.hash = "";[cite: 2]
        }
    } else {
        // 生成随机新密钥[cite: 2]
        const randomKey = Array.from(window.crypto.getRandomValues(new Uint8Array(16)))
                               .map(b => b.toString(16).padStart(2, '0')).join('');[cite: 2]
        keyData = new TextEncoder().encode(randomKey);[cite: 2]
        const shareLink = `${window.location.origin}${window.location.pathname}#${randomKey}`;[cite: 2]
        console.log("分享链接:", shareLink); // 可以在此处添加弹出层逻辑显示链接
    }

    try {
        sharedKey = await window.crypto.subtle.importKey(
            "raw", keyData, { name: "AES-GCM" }, false, ["encrypt", "decrypt"]
        );[cite: 2]
        document.getElementById('status').innerText = "● 安全通道已加密";[cite: 2]
    } catch (err) {
        document.getElementById('status').innerText = "❌ 密钥解析错误";[cite: 2]
    }
}

// 2. 消息渲染与自焚动画
function appendMessage(sender, text, ttl) {
    const chatMessages = document.getElementById('chatMessages');
    const msgDiv = document.createElement('div');
    msgDiv.className = `message ${sender}`;
    
    msgDiv.innerHTML = `
        <div class="content">${text}</div>
        <div class="burn-timer-bar"><div class="fill"></div></div>
    `;
    
    chatMessages.appendChild(msgDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;

    let remaining = 100;
    const fill = msgDiv.querySelector('.fill');
    const interval = setInterval(() => {
        remaining -= (100 / (ttl * 10)); // 每 100ms 计算一次减少比例
        fill.style.width = `${remaining}%`;
        
        if (remaining <= 0) {
            clearInterval(interval);
            // 触发自焚消散动画
            msgDiv.style.filter = "blur(15px)";
            msgDiv.style.opacity = "0";
            msgDiv.style.transform = "scale(0.8)";
            setTimeout(() => msgDiv.remove(), 500); // 动画结束后从 DOM 移除
        }
    }, 100);
}

// 3. 事件驱动
document.getElementById('sendBtn').onclick = () => {
    const input = document.getElementById('chatInput');
    const ttlInput = document.querySelector('input[name="ttl"]:checked');
    const ttl = ttlInput ? parseInt(ttlInput.value) : 60;

    if (input.value.trim()) {
        // 在此处添加 WebSocket 发送逻辑（需配合加密使用）
        appendMessage('me', input.value, ttl);
        input.value = '';
    }
};

// 页面加载自动初始化[cite: 2]
initCrypto();