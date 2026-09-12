from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')

old='''els.reload.addEventListener("click",async()=>{\n  await Promise.all([loadMeta(true),resetAndLoad(true)]);\n  showToast("最新データに更新しました")\n});'''
new='''els.reload.addEventListener("click",async()=>{\n  /* Rebuild the persistent gallery snapshot exactly once.\n     Then read metadata from that freshly written R2 snapshot instead of\n     triggering a second forced Notion rebuild in parallel. */\n  await resetAndLoad(true);\n  await loadMeta(false);\n  showToast("最新データに更新しました")\n});'''
if old not in s:
    raise SystemExit('reload handler target not found')
s=s.replace(old,new,1)
p.write_text(s,encoding='utf-8')
