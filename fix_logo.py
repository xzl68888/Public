import re

# Read the new logo base64
with open(r'C:\Users\djp30\.qclaw\workspace\burn-chat-deploy\logo_b64.txt', 'r') as f:
    logo_b64 = f.read().strip()

# Read index.html
with open(r'C:\Users\djp30\.qclaw\workspace\burn-chat-deploy\public\index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace ALL remaining fire emojis in the file
fire_emoji = '\U0001f525'

# Find all occurrences and their context
positions = []
start = 0
while True:
    pos = content.find(fire_emoji, start)
    if pos == -1:
        break
    positions.append(pos)
    start = pos + 1

print(f'Found {len(positions)} fire emojis')

# Replace each one based on context
for pos in positions:
    context = content[pos-50:pos+50]
    print(f'Context: {context[:30]}...{context[-20:]}')
    
    # Check if it's in a div (auth-logo-icon or nav-logo)
    if 'auth-logo-icon' in content[pos-100:pos]:
        old = '<div class="auth-logo-icon">' + fire_emoji + '</div>'
        new = f'<img class="auth-logo-icon" src="{logo_b64}" alt="BURN" style="width:70px;height:70px;border-radius:20px;object-fit:cover;box-shadow:var(--glow-red);">'
        content = content.replace(old, new)
        print('  -> Replaced auth-logo-icon')
    elif 'nav-logo' in content[pos-100:pos]:
        old = '<div class="nav-logo">' + fire_emoji + '</div>'
        new = f'<img class="nav-logo" src="{logo_b64}" alt="BURN" style="width:32px;height:32px;border-radius:10px;object-fit:cover;">'
        content = content.replace(old, new)
        print('  -> Replaced nav-logo')
    else:
        # Just remove or replace with text
        content = content.replace(fire_emoji, 'BURN')
        print('  -> Replaced with BURN text')

# Write back
with open(r'C:\Users\djp30\.qclaw\workspace\burn-chat-deploy\public\index.html', 'w', encoding='utf-8') as f:
    f.write(content)

# Verify
remaining = content.count(fire_emoji)
print(f'\nRemaining fire emojis: {remaining}')
print('Done!')
