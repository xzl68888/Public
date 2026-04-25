import re

# Read the new logo base64
with open(r'C:\Users\djp30\.qclaw\workspace\burn-chat-deploy\logo_b64.txt', 'r') as f:
    logo_b64 = f.read().strip()

# Read index.html
with open(r'C:\Users\djp30\.qclaw\workspace\burn-chat-deploy\public\index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace auth-logo-icon div with image
# Pattern: <div class="auth-logo-icon">...</div>
old_auth_logo = '<div class="auth-logo-icon">🔥</div>'
new_auth_logo = f'<img class="auth-logo-icon" src="{logo_b64}" alt="BURN" style="width:70px;height:70px;border-radius:20px;object-fit:cover;box-shadow:var(--glow-red);">'

content = content.replace(old_auth_logo, new_auth_logo)

# Replace nav-logo div with image  
old_nav_logo = '<div class="nav-logo">🔥</div>'
new_nav_logo = f'<img class="nav-logo" src="{logo_b64}" alt="BURN" style="width:32px;height:32px;border-radius:10px;object-fit:cover;">'

content = content.replace(old_nav_logo, new_nav_logo)

# Write back
with open(r'C:\Users\djp30\.qclaw\workspace\burn-chat-deploy\public\index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print('Logo updated in index.html')
print('Replaced auth-logo-icon and nav-logo')
