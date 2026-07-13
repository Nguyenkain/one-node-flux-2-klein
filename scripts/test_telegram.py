"""Standalone Telegram config check — isolates config errors from the node.

Run:  python scripts/test_telegram.py <BOT_TOKEN> <CHAT_ID> [MESSAGE_THREAD_ID]

Prints the raw Telegram API response so you see the real error
(wrong chat_id, bot not in group, topic id invalid, etc.).
"""
import sys
import requests


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    token, chat = sys.argv[1].strip(), sys.argv[2].strip()
    thread = sys.argv[3].strip() if len(sys.argv) > 3 else ""

    # 1) verify token
    r = requests.get("https://api.telegram.org/bot%s/getMe" % token, timeout=30)
    print("getMe:", r.status_code, r.text[:300])
    if not r.ok:
        print("→ Token sai hoặc mạng chặn api.telegram.org.")
        return

    # 2) send a plain message to the exact chat/topic
    data = {"chat_id": chat, "text": "✅ TelegramNotify test OK"}
    if thread:
        data["message_thread_id"] = thread
    r = requests.post("https://api.telegram.org/bot%s/sendMessage" % token, data=data, timeout=30)
    print("sendMessage:", r.status_code, r.text[:500])
    if r.ok and r.json().get("ok"):
        print("→ Config OK. Nếu node vẫn không gửi: node bị cache (xem IS_CHANGED) hoặc input rỗng.")
    else:
        print("→ Đọc field 'description' ở trên. Thường: chat_id sai dấu/thiếu -100, "
              "bot chưa vào group, hoặc message_thread_id không tồn tại.")


if __name__ == "__main__":
    main()
