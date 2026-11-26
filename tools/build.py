"""Turns the offline Field Manual into the phone app.

Usage:  python3 tools/build.py [path/to/Space_Knights_Field_Manual_offline.html]
With no path it uses tools/field-manual-source.html. Writes index.html and sw.js
at the repo root. Re-run it whenever the Field Manual changes, then push.
"""
import hashlib, os, re, sys, shutil

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SRC = os.path.join(ROOT, "tools", "field-manual-source.html")
if len(sys.argv) > 1:
    shutil.copyfile(sys.argv[1], SRC)
html = open(SRC, encoding="utf-8").read()

HEAD = """
<link rel="manifest" href="manifest.webmanifest">
<meta name="theme-color" content="#111820">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-title" content="Field Manual">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<link rel="apple-touch-icon" href="icons/apple-touch-icon.png">
<link rel="icon" type="image/png" sizes="32x32" href="icons/favicon-32.png">
<script>
/* Phone app: saved armies and scenarios live on this device (localStorage).
   This stands in for the claude.ai account storage the online page uses. */
(function(){
  if (window.claude && window.claude.use) return;
  var PFX = "sk-app-lib:";
  function load(p){ try { return JSON.parse(localStorage.getItem(PFX+p)) || {}; } catch(e){ return {}; } }
  function store(p, v){ localStorage.setItem(PFX+p, JSON.stringify(v)); }
  var listeners = {};
  function newId(){ return Date.now().toString(36) + Math.random().toString(36).slice(2,8); }
  function snapshot(p, field){
    var all = load(p);
    var docs = Object.keys(all).map(function(id){ var v = all[id];
      return { id: id, data: function(){ return JSON.parse(JSON.stringify(v)); } }; });
    if (field) docs.sort(function(a,b){ return String(a.data()[field]||"").localeCompare(String(b.data()[field]||"")); });
    return { docs: docs, metadata: { fromCache: false } };
  }
  function notify(p){ (listeners[p]||[]).forEach(function(l){ try { l.cb(snapshot(p, l.field)); } catch(e){} }); }
  function collection(p){
    var col = {
      doc: function(id){ id = id || newId(); return {
        id: id,
        set: function(body){ return new Promise(function(res, rej){ try { var all = load(p); all[id] = JSON.parse(JSON.stringify(body)); store(p, all); notify(p); res(); } catch(e){ rej(e); } }); },
        delete: function(){ return new Promise(function(res){ var all = load(p); delete all[id]; store(p, all); notify(p); res(); }); }
      }; },
      orderBy: function(field){ return { onSnapshot: function(cb){
        var l = { cb: cb, field: field }; (listeners[p] = listeners[p] || []).push(l);
        setTimeout(function(){ cb(snapshot(p, field)); }, 0);
        return function(){ listeners[p] = listeners[p].filter(function(x){ return x !== l; }); };
      }}; },
      onSnapshot: function(cb){ return col.orderBy(null).onSnapshot(cb); }
    };
    return col;
  }
  var db = { doc: function(base){ return { collection: function(name){ return collection(base + "/" + name); } }; } };
  var user = { id: function(){ return Promise.resolve("device"); } };
  window.claude = { use: function(cap){ return Promise.resolve(cap === "db" ? db : cap === "user" ? user : null); } };
  window.addEventListener("storage", function(e){ if (e.key && e.key.indexOf(PFX) === 0) notify(e.key.slice(PFX.length)); });
})();
if ("serviceWorker" in navigator) {
  window.addEventListener("load", function(){ navigator.serviceWorker.register("sw.js").catch(function(){}); });
}
</script>
"""

marker = '<meta name="viewport"'
i = html.index(marker)
j = html.index(">", i) + 1
html = html[:j] + HEAD + html[j:]
html = html.replace('<meta name="claude:viewport-fit-sides" content="cover">\n', "")

# Wording: account storage becomes on-phone storage.
REPL = [
    ("Saved to your account, on every device.", "Saved on this phone. Use an army code to share a force or move it to another device."),
    ("Saved to your account.", "Saved on this phone. Use a scenario code to share it."),
    ("between devices, or between the online page and the offline file.", "between phones, or between this app and the online Field Manual."),
]
for a, b in REPL:
    if a not in html:
        print("warning: text not found, skipped:", a)
    html = html.replace(a, b)

open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8").write(html)

ver = hashlib.sha256(html.encode()).hexdigest()[:10]
sw = open(os.path.join(ROOT, "tools", "sw-template.js"), encoding="utf-8").read().replace("__VERSION__", ver)
open(os.path.join(ROOT, "sw.js"), "w", encoding="utf-8").write(sw)
m = re.search(r'id="verline">([^<]*)<', html)
print("built", ver, "|", m.group(1) if m else "")
