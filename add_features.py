import re

# 读取 index.html
with open(r'C:\Users\djp30\.qclaw\workspace\burn-chat-deploy\public\index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# ===== 1. 添加防截屏录屏功能 =====
anti_capture_script = '''
<script>
// ===== 防截屏录屏功能 =====
(function() {
  let captureWarningShown = false;
  
  // 检测截屏 (PrintScreen 键)
  document.addEventListener('keydown', (e) => {
    if (e.key === 'PrintScreen' || e.keyCode === 44) {
      e.preventDefault();
      showCaptureWarning('截屏');
      // 清空剪贴板
      if (navigator.clipboard) {
        navigator.clipboard.writeText('');
      }
    }
  });
  
  // 检测录屏 (检测 mediaRecorder API 使用)
  const originalMediaRecorder = window.MediaRecorder;
  if (originalMediaRecorder) {
    window.MediaRecorder = function(...args) {
      showCaptureWarning('录屏');
      throw new Error('录屏功能已被禁用');
    };
    window.MediaRecorder.prototype = originalMediaRecorder.prototype;
    window.MediaRecorder.isTypeSupported = originalMediaRecorder.isTypeSupported;
  }
  
  // 检测屏幕共享
  const originalGetDisplayMedia = navigator.mediaDevices?.getDisplayMedia;
  if (originalGetDisplayMedia) {
    navigator.mediaDevices.getDisplayMedia = function(...args) {
      showCaptureWarning('屏幕共享');
      return Promise.reject(new Error('屏幕共享已被禁用'));
    };
  }
  
  // 检测 DevTools 打开 (可选警告)
  let devtoolsOpen = false;
  const threshold = 160;
  setInterval(() => {
    if (window.outerHeight - window.innerHeight > threshold || 
        window.outerWidth - window.innerWidth > threshold) {
      if (!devtoolsOpen) {
        devtoolsOpen = true;
        console.warn('⚠️ 检测到开发者工具已打开');
      }
    } else {
      devtoolsOpen = false;
    }
  }, 1000);
  
  // 显示警告
  function showCaptureWarning(action) {
    if (captureWarningShown) return;
    captureWarningShown = true;
    
    const warning = document.createElement('div');
    warning.className = 'capture-warning';
    warning.innerHTML = `
      <div class="capture-warning-content">
        <div class="capture-icon">🛡️</div>
        <div class="capture-title">安全警告</div>
        <div class="capture-text">检测到 ${action} 操作</div>
        <div class="capture-desc">为保护隐私，${action}功能已被禁用</div>
        <button class="capture-close" onclick="this.parentElement.parentElement.remove()">我知道了</button>
      </div>
    `;
    document.body.appendChild(warning);
    
    setTimeout(() => {
      captureWarningShown = false;
    }, 3000);
  }
  
  // 将函数暴露到全局
  window.showCaptureWarning = showCaptureWarning;
})();
</script>

<style>
.capture-warning {
  position: fixed;
  inset: 0;
  z-index: 99999;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0, 0, 0, 0.9);
  animation: fadeIn 0.3s ease;
}

.capture-warning-content {
  background: linear-gradient(135deg, #1a1a2e, #16213e);
  border: 2px solid #ff2d55;
  border-radius: 20px;
  padding: 40px;
  text-align: center;
  max-width: 400px;
  animation: scaleIn 0.3s ease;
}

@keyframes scaleIn {
  from { transform: scale(0.8); opacity: 0; }
  to { transform: scale(1); opacity: 1; }
}

.capture-icon {
  font-size: 60px;
  margin-bottom: 16px;
}

.capture-title {
  font-size: 24px;
  font-weight: 700;
  color: #ff2d55;
  margin-bottom: 8px;
}

.capture-text {
  font-size: 18px;
  color: #e8e6f0;
  margin-bottom: 8px;
}

.capture-desc {
  font-size: 14px;
  color: #6b6880;
  margin-bottom: 24px;
}

.capture-close {
  background: linear-gradient(135deg, #ff2d55, #ff6b35);
  border: none;
  border-radius: 10px;
  padding: 12px 32px;
  color: white;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
}

.capture-close:hover {
  opacity: 0.9;
}
</style>
'''

# ===== 2. 添加媒体发送功能 =====
media_input_html = '''
      <div class="media-actions">
        <button class="media-btn" id="imageBtn" title="发送图片">🖼️</button>
        <button class="media-btn" id="videoBtn" title="发送视频">🎬</button>
        <input type="file" id="imageInput" accept="image/*" style="display:none">
        <input type="file" id="videoInput" accept="video/*" style="display:none">
      </div>
'''

media_script = '''
<script>
// ===== 媒体发送功能 =====
(function() {
  const imageBtn = document.getElementById('imageBtn');
  const videoBtn = document.getElementById('videoBtn');
  const imageInput = document.getElementById('imageInput');
  const videoInput = document.getElementById('videoInput');
  
  if (!imageBtn || !videoBtn) return;
  
  // 图片按钮
  imageBtn.addEventListener('click', () => {
    imageInput.click();
  });
  
  // 视频按钮
  videoBtn.addEventListener('click', () => {
    videoInput.click();
  });
  
  // 图片选择处理
  imageInput.addEventListener('change', (e) => {
    const file = e.target.files[0];
    if (!file) return;
    
    // 检查文件大小 (最大 5MB)
    if (file.size > 5 * 1024 * 1024) {
      alert('图片大小不能超过 5MB');
      return;
    }
    
    const reader = new FileReader();
    reader.onload = (event) => {
      sendMediaMessage('image', event.target.result, file.name);
    };
    reader.readAsDataURL(file);
    imageInput.value = ''; // 清空以便再次选择
  });
  
  // 视频选择处理
  videoInput.addEventListener('change', (e) => {
    const file = e.target.files[0];
    if (!file) return;
    
    // 检查文件大小 (最大 10MB)
    if (file.size > 10 * 1024 * 1024) {
      alert('视频大小不能超过 10MB');
      return;
    }
    
    const reader = new FileReader();
    reader.onload = (event) => {
      sendMediaMessage('video', event.target.result, file.name);
    };
    reader.readAsDataURL(file);
    videoInput.value = '';
  });
  
  // 发送媒体消息
  function sendMediaMessage(type, data, filename) {
    if (!activeChat || !ws || ws.readyState !== WebSocket.OPEN) {
      alert('未连接到服务器');
      return;
    }
    
    ws.send(JSON.stringify({
      type: 'chat',
      toId: activeChat,
      mediaType: type,
      mediaData: data,
      mediaName: filename,
      burnAfter: burnTime
    }));
    
    // 本地显示
    displayMediaMessage(type, data, true);
  }
  
  // 显示媒体消息
  function displayMediaMessage(type, data, isSent) {
    const container = document.getElementById('chatMessages');
    const msgId = 'msg-' + Date.now();
    const time = new Date().toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' });
    
    let content = '';
    if (type === 'image') {
      content = `<img src="${data}" class="msg-image" onclick="previewMedia(this.src)" style="max-width:100%;border-radius:12px;cursor:pointer;">`;
    } else if (type === 'video') {
      content = `<video src="${data}" class="msg-video" controls style="max-width:100%;border-radius:12px;"></video>`;
    }
    
    const msgHTML = `
      <div class="msg-row ${isSent ? 'sent' : 'received'}" id="${msgId}">
        <div class="msg-bubble msg-media">
          ${content}
          <div class="msg-meta">
            <span class="msg-time">${time}</span>
            <span class="msg-burn burning">BURN ${burnTime}s</span>
          </div>
        </div>
      </div>
    `;
    
    container.insertAdjacentHTML('beforeend', msgHTML);
    container.scrollTop = container.scrollHeight;
    
    startBurnTimer(msgId, burnTime);
  }
  
  // 媒体预览
  window.previewMedia = function(src) {
    const overlay = document.createElement('div');
    overlay.className = 'media-preview-overlay';
    overlay.innerHTML = `
      <div class="media-preview-content">
        <img src="${src}" style="max-width:90vw;max-height:90vh;border-radius:12px;">
        <button class="media-preview-close" onclick="this.parentElement.parentElement.remove()">×</button>
      </div>
    `;
    overlay.addEventListener('click', (e) => {
      if (e.target === overlay) overlay.remove();
    });
    document.body.appendChild(overlay);
  };
  
  // 暴露到全局
  window.displayMediaMessage = displayMediaMessage;
})();
</script>

<style>
.media-actions {
  display: flex;
  gap: 8px;
  margin-right: 8px;
}

.media-btn {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: var(--bg-card);
  border: 1px solid var(--border-subtle);
  color: var(--text-primary);
  font-size: 18px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.media-btn:hover {
  background: var(--accent-red);
  border-color: var(--accent-red);
}

.msg-media {
  max-width: 300px;
  padding: 8px;
}

.msg-media .msg-bubble {
  background: transparent !important;
  border: none !important;
}

.media-preview-overlay {
  position: fixed;
  inset: 0;
  z-index: 99998;
  background: rgba(0, 0, 0, 0.95);
  display: flex;
  align-items: center;
  justify-content: center;
  animation: fadeIn 0.2s ease;
}

.media-preview-content {
  position: relative;
}

.media-preview-close {
  position: absolute;
  top: -40px;
  right: 0;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.2);
  border: none;
  color: white;
  font-size: 24px;
  cursor: pointer;
}
</style>
'''

# ===== 3. 修改接收消息函数以支持媒体 =====
receive_message_patch = '''
function receiveMessage(data) {
  const container = document.getElementById('chatMessages');
  const isSent = data.sent;
  const time = new Date(data.timestamp).toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' });

  const msgId = 'msg-' + Date.now();
  
  let content = '';
  if (data.mediaType === 'image') {
    content = `<img src="${data.mediaData}" class="msg-image" onclick="previewMedia(this.src)" style="max-width:100%;border-radius:12px;cursor:pointer;">`;
  } else if (data.mediaType === 'video') {
    content = `<video src="${data.mediaData}" class="msg-video" controls style="max-width:100%;border-radius:12px;"></video>`;
  } else {
    content = data.content;
  }

  const msgHTML = `
    <div class="msg-row ${isSent ? 'sent' : 'received'}" id="${msgId}">
      <div class="msg-bubble ${data.mediaType ? 'msg-media' : ''}">
        ${content}
        <div class="msg-meta">
          <span class="msg-time">${time}</span>
          <span class="msg-burn burning">BURN ${data.burnAfter}s</span>
        </div>
      </div>
    </div>
  `;

  container.insertAdjacentHTML('beforeend', msgHTML);
  container.scrollTop = container.scrollHeight;

  startBurnTimer(msgId, data.burnAfter);
}
'''

# ===== 应用修改 =====

# 1. 在 </head> 前添加防截屏脚本
if '</head>' in html:
    html = html.replace('</head>', anti_capture_script + '\n</head>')
    print('[OK] Anti-capture feature added')

# 2. 在输入区域添加媒体按钮
# 查找 <div class="input-row"> 并在 <textarea 前添加按钮
input_row_pattern = r'(<div class="input-row">)'
if re.search(input_row_pattern, html):
    html = re.sub(input_row_pattern, r'\\1\n' + media_input_html, html)
    print('[OK] Media buttons added')

# 3. 在 </body> 前添加媒体脚本
if '</body>' in html:
    html = html.replace('</body>', media_script + '\n</body>')
    print('[OK] Media send feature added')

# 4. 替换 receiveMessage 函数以支持媒体
old_receive_pattern = r'function receiveMessage\(data\) \{[^}]+const isSent = data\.sent;[^}]+const time = [^}]+const msgId = [^}]+const msgHTML = `[^`]+`;\s+container\.insertAdjacentHTML[^;]+;\s+container\.scrollTop[^;]+;\s+startBurnTimer[^;]+;\s+\}'

if re.search(old_receive_pattern, html, re.DOTALL):
    html = re.sub(old_receive_pattern, receive_message_patch.strip(), html, flags=re.DOTALL)
    print('[OK] receiveMessage updated for media')
else:
    print('[WARN] receiveMessage not found, trying other method')
    # 简单替换
    if 'function receiveMessage(data)' in html:
        # 找到函数开始
        start = html.find('function receiveMessage(data)')
        # 找到函数结束 (下一个 function 或 // =====)
        end = html.find('\n\n// =====', start)
        if end == -1:
            end = html.find('\nfunction ', start + 1)
        if end > start:
            old_func = html[start:end]
            html = html[:start] + receive_message_patch.strip() + html[end:]
            print('[OK] receiveMessage replaced')

# 5. 在设置页面添加防截屏开关
settings_pattern = r'(<div class="settings-item" onclick="showThemeSelector\(\)">.*?</div>\s+</div>)'
match = re.search(settings_pattern, html, re.DOTALL)
if match:
    insert_pos = match.end()
    anti_capture_setting = '''
      <div class="settings-item">
        <div class="settings-icon">🛡️</div>
        <div class="settings-label">防截屏录屏</div>
        <div class="settings-value" style="color: var(--accent-green);">已启用</div>
      </div>
'''
    html = html[:insert_pos] + anti_capture_setting + html[insert_pos:]
    print('[OK] Anti-capture setting added')

# 保存
with open(r'C:\Users\djp30\.qclaw\workspace\burn-chat-deploy\public\index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print('Done! All features added.')
