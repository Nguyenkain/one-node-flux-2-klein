import { app } from "../../scripts/app.js";
import { api } from "../../scripts/api.js";

// Auto-fill Telegram widgets when a profile is picked from the `profile` dropdown.
// Backend still reads the profile at run time; this is just UI convenience.
app.registerExtension({
  name: "one_node.telegram_notify",
  async nodeCreated(node) {
    if (node.comfyClass !== "TelegramNotify") return;
    const w = (name) => node.widgets?.find((x) => x.name === name);
    const profile = w("profile");
    if (!profile) return;

    const fill = async (name) => {
      if (!name || name === "(none)") return;
      try {
        const r = await api.fetchApi(
          `/flux_klein/telegram_profile?name=${encodeURIComponent(name)}`
        );
        const p = await r.json();
        const set = (wn, key) => {
          const wd = w(wn);
          if (wd && p[key] != null) {
            wd.value = p[key];
            wd.callback?.(wd.value);
          }
        };
        set("bot_token", "bot_token");
        set("chat_id", "chat_id");
        set("message_thread_id", "message_thread_id");
        node.setDirtyCanvas(true, true);
      } catch (e) {
        console.error("[TelegramNotify] load profile failed", e);
      }
    };

    const prev = profile.callback;
    profile.callback = function (v) {
      prev?.apply(this, arguments);
      fill(v);
    };
  },
});
