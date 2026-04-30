async function initCrypto() {
    if (!window.isSecureContext) {
        alert("🚨 安全警告：\n加密模块需要在 HTTPS 环境下启动。");
        document.getElementById('status').innerText = "❌ 环境不安全";
        return;
    }

    if (!window.crypto || !window.crypto.subtle) {
        alert("🚫 浏览器版本过低，不支持加密 API。");
        return;
    }

    let keyData;
    const hash = decodeURIComponent(window.location.hash.substring(1));

    if (hash && hash.length >= 32) {
        keyData = new TextEncoder().encode(hash.substring(0, 32));
        try {
            window.history.replaceState(null, null, window.location.pathname);
        } catch (e) {
            window.location.hash = "";
        }
    } else {
        const randomKey = Array.from(window.crypto.getRandomValues(new Uint8Array(16)))
                               .map(b => b.toString(16).padStart(2, '0')).join('');
        keyData = new TextEncoder().encode(randomKey);
        
        const shareLink = `${window.location.origin}${window.location.pathname}#${randomKey}`;
        showShareModal(shareLink); 
    }

    try {
        sharedKey = await window.crypto.subtle.importKey(
            "raw", keyData, { name: "AES-GCM" }, false, ["encrypt", "decrypt"]
        );
        document.getElementById('status').innerText = "● 安全通道已加密";
    } catch (err) {
        document.getElementById('status').innerText = "❌ 密钥解析错误";
    }
}