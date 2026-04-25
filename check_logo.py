import re

with open(r'C:\Users\djp30\.qclaw\workspace\burn-chat-deploy\public\index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Find auth-logo-icon
matches = list(re.finditer(r'class="auth-logo-icon"[^>]*>', content))
print('auth-logo-icon matches:', len(matches))
for m in matches:
    snippet = content[m.start():m.start()+150]
    print('  Position', m.start(), ':', snippet[:80])

# Find nav-logo  
matches = list(re.finditer(r'class="nav-logo"[^>]*>', content))
print('\nnav-logo matches:', len(matches))
for m in matches:
    snippet = content[m.start():m.start()+150]
    print('  Position', m.start(), ':', snippet[:80])

# Check if they are img tags or div tags
if 'class="auth-logo-icon" src=' in content:
    print('\nauth-logo-icon is already an img tag with src')
else:
    print('\nauth-logo-icon is still a div')
    
if 'class="nav-logo" src=' in content:
    print('nav-logo is already an img tag with src')
else:
    print('nav-logo is still a div')
