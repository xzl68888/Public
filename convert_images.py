import base64
from PIL import Image
import io
import os

# 图片配置
images = [
    ("55呃呃.jpg", "bg1", "background"),  # 金色神兽
    ("23.jpg", "bg2", "background"),       # 宇宙星球
    ("为.jpg", "avatar1", "avatar"),       # 金色神兽
    ("额外.jpg", "avatar2", "avatar"),     # 悟空星空
    ("热4.jpg", "avatar3", "avatar"),      # 悟空剪影
    ("悄悄.jpg", "bg3", "background"),     # 抽象图案
    ("热.jpg", "avatar4", "avatar"),       # 虎战士
    ("玩.jpg", "avatar5", "avatar"),       # 悟空特写
]

base_path = r"C:\Users\djp30\Pictures"
output_path = r"C:\Users\djp30\.qclaw\workspace\burn-chat-deploy\images_b64.json"

result = {"backgrounds": [], "avatars": []}

for filename, key, img_type in images:
    filepath = os.path.join(base_path, filename)
    if not os.path.exists(filepath):
        print(f"Missing: {filename}")
        continue
    
    try:
        img = Image.open(filepath)
        
        # 根据类型调整尺寸
        if img_type == "avatar":
            img = img.resize((200, 200), Image.Resampling.LANCZOS)
        else:
            # 背景图保持原比例，但限制最大尺寸
            img.thumbnail((1080, 1920), Image.Resampling.LANCZOS)
        
        # 转为 base64
        output = io.BytesIO()
        img.save(output, format='JPEG', quality=85)
        base64_data = base64.b64encode(output.getvalue()).decode('utf-8')
        
        data_url = f"data:image/jpeg;base64,{base64_data}"
        
        item = {
            "key": key,
            "name": filename.replace(".jpg", ""),
            "data": data_url
        }
        
        if img_type == "background":
            result["backgrounds"].append(item)
        else:
            result["avatars"].append(item)
        
        print(f"Converted: {filename} -> {key} ({len(data_url)} chars)")
        
    except Exception as e:
        print(f"Error converting {filename}: {e}")

# 保存为 JSON
import json
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False)

print(f"\nTotal: {len(result['backgrounds'])} backgrounds, {len(result['avatars'])} avatars")
print(f"Saved to: {output_path}")
