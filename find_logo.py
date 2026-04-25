import re

with open(r'C:\Users\djp30\.qclaw\workspace\burn-chat-deploy\public\index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Find auth-logo-icon sections
pattern = r'class="auth-logo-icon"[^>]*>([^<]*)<'
matches = list(re.finditer(pattern, content))
print(f"Found {len(matches)} matches for auth-logo-icon")

for m in matches:
    print(f"Content: {repr(m.group(1))}")
    print(f"Position: {m.start()}-{m.end()}")

# Also find nav-logo
pattern2 = r'class="nav-logo"[^>]*>([^<]*)<'
matches2 = list(re.finditer(pattern2, content))
print(f"\nFound {len(matches2)} matches for nav-logo")

for m in matches2:
    print(f"Content: {repr(m.group(1))}")
    print(f"Position: {m.start()}-{m.end()}")
