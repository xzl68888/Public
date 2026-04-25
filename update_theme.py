import json
import re

# 读取图片数据
with open(r'C:\Users\djp30\.qclaw\workspace\burn-chat-deploy\images_b64.json', 'r', encoding='utf-8') as f:
    images = json.load(f)

# 读取 index.html
with open(r'C:\Users\djp30\.qclaw\workspace\burn-chat-deploy\public\index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 生成图片数据 JS
backgrounds_js = json.dumps(images['backgrounds'])
avatars_js = json.dumps(images['avatars'])

# 在 </body> 前添加脚本
script = f'''
<script>
// 主题图片数据
const THEME_BACKGROUNDS = {backgrounds_js};
const THEME_AVATARS = {avatars_js};

// 获取保存的主题设置
function getThemeSettings() {{
  const saved = localStorage.getItem('burnchat_theme');
  return saved ? JSON.parse(saved) : {{ background: null, avatar: null }};
}}

// 保存主题设置
function saveThemeSettings(settings) {{
  localStorage.setItem('burnchat_theme', JSON.stringify(settings));
}}

// 应用背景
function applyBackground(bgKey) {{
  if (!bgKey) return;
  const bg = THEME_BACKGROUNDS.find(b => b.key === bgKey);
  if (bg) {{
    document.body.style.backgroundImage = `url(${{bg.data}})`;
    document.body.style.backgroundSize = 'cover';
    document.body.style.backgroundPosition = 'center';
    document.body.style.backgroundAttachment = 'fixed';
  }}
}}

// 应用头像
function applyAvatar(avatarKey) {{
  if (!avatarKey) return;
  const avatar = THEME_AVATARS.find(a => a.key === avatarKey);
  if (avatar) {{
    // 更新用户头像显示
    const userAvatar = document.querySelector('.user-avatar');
    if (userAvatar) {{
      userAvatar.style.backgroundImage = `url(${{avatar.data}})`;
      userAvatar.style.backgroundSize = 'cover';
    }}
  }}
}}

// 显示主题选择器
function showThemeSelector() {{
  const existing = document.querySelector('.theme-selector');
  if (existing) existing.remove();
  
  const settings = getThemeSettings();
  
  const selector = document.createElement('div');
  selector.className = 'theme-selector';
  selector.innerHTML = `
    <div class="theme-overlay" onclick="closeThemeSelector()"></div>
    <div class="theme-panel">
      <div class="theme-header">
        <h3>个性化设置</h3>
        <button class="close-btn" onclick="closeThemeSelector()">×</button>
      </div>
      <div class="theme-section">
        <h4>聊天背景</h4>
        <div class="theme-grid">
          <div class="theme-item ${{{{settings.background === null ? 'active' : ''}}}}" onclick="selectBackground(null)">
            <div class="theme-preview default-bg">默认</div>
          </div>
          ${{THEME_BACKGROUNDS.map(bg => `
            <div class="theme-item ${{{{settings.background === bg.key ? 'active' : ''}}}}" onclick="selectBackground('${{bg.key}}')">
              <img class="theme-preview" src="${{bg.data}}" alt="${{bg.name}}">
            </div>
          `).join('')}}
        </div>
      </div>
      <div class="theme-section">
        <h4>头像</h4>
        <div class="theme-grid">
          <div class="theme-item ${{{{settings.avatar === null ? 'active' : ''}}}}" onclick="selectAvatar(null)">
            <div class="theme-preview default-avatar">默认</div>
          </div>
          ${{THEME_AVATARS.map(av => `
            <div class="theme-item ${{{{settings.avatar === av.key ? 'active' : ''}}}}" onclick="selectAvatar('${{av.key}}')">
              <img class="theme-preview avatar-preview" src="${{av.data}}" alt="${{av.name}}">
            </div>
          `).join('')}}
        </div>
      </div>
    </div>
  `;
  document.body.appendChild(selector);
}}

function closeThemeSelector() {{
  const selector = document.querySelector('.theme-selector');
  if (selector) selector.remove();
}}

function selectBackground(bgKey) {{
  const settings = getThemeSettings();
  settings.background = bgKey;
  saveThemeSettings(settings);
  applyBackground(bgKey);
  showThemeSelector(); // 刷新界面
}}

function selectAvatar(avatarKey) {{
  const settings = getThemeSettings();
  settings.avatar = avatarKey;
  saveThemeSettings(settings);
  applyAvatar(avatarKey);
  showThemeSelector(); // 刷新界面
}}

// 页面加载时应用主题
document.addEventListener('DOMContentLoaded', () => {{
  const settings = getThemeSettings();
  applyBackground(settings.background);
  applyAvatar(settings.avatar);
}});
</script>

<style>
.theme-selector {{
  position: fixed;
  inset: 0;
  z-index: 9999;
  display: flex;
  align-items: flex-end;
  justify-content: center;
}}

.theme-overlay {{
  position: absolute;
  inset: 0;
  background: rgba(0,0,0,0.8);
}}

.theme-panel {{
  position: relative;
  background: var(--bg-deep);
  border-radius: 20px 20px 0 0;
  width: 100%;
  max-width: 500px;
  max-height: 80vh;
  overflow-y: auto;
  padding: 20px;
  animation: slideUp 0.3s ease;
}}

@keyframes slideUp {{
  from {{ transform: translateY(100%); }}
  to {{ transform: translateY(0); }}
}}

.theme-header {{
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}}

.theme-header h3 {{
  font-size: 18px;
  font-weight: 600;
}}

.close-btn {{
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: var(--bg-card);
  border: none;
  color: var(--text-primary);
  font-size: 20px;
  cursor: pointer;
}}

.theme-section {{
  margin-bottom: 24px;
}}

.theme-section h4 {{
  font-size: 14px;
  color: var(--text-dim);
  margin-bottom: 12px;
  text-transform: uppercase;
  letter-spacing: 1px;
}}

.theme-grid {{
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
}}

.theme-item {{
  aspect-ratio: 1;
  border-radius: 12px;
  overflow: hidden;
  cursor: pointer;
  border: 2px solid transparent;
  transition: all 0.2s;
}}

.theme-item.active {{
  border-color: var(--accent-red);
  box-shadow: var(--glow-red);
}}

.theme-preview {{
  width: 100%;
  height: 100%;
  object-fit: cover;
}}

.default-bg, .default-avatar {{
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-card);
  font-size: 12px;
  color: var(--text-dim);
}}

.avatar-preview {{
  border-radius: 50%;
}}
</style>
'''

# 在 </body> 前插入脚本
if '</body>' in html:
    html = html.replace('</body>', script + '\n</body>')
    print('Script inserted before </body>')
else:
    print('Warning: </body> not found')

# 在设置页面添加主题按钮
# 查找设置按钮或添加新的设置项
settings_pattern = r'(class="setting-item".*?加密状态.*?</view>)'
match = re.search(settings_pattern, html, re.DOTALL)
if match:
    insert_pos = match.end()
    theme_button = '''
      <view class="setting-item" onclick="showThemeSelector()">
        <text class="label">🎨 个性化主题</text>
        <text class="value">点击设置 ></text>
      </view>
'''
    html = html[:insert_pos] + theme_button + html[insert_pos:]
    print('Theme button added to settings')
else:
    print('Warning: Could not find settings section')

# 保存
with open(r'C:\Users\djp30\.qclaw\workspace\burn-chat-deploy\public\index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print('Done!')
