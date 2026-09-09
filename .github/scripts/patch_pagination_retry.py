from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')

def once(old,new,label):
    global s
    if old not in s:
        raise SystemExit(f'patch target not found: {label}')
    s=s.replace(old,new,1)

once(
    'const PAGE_SIZE = 12;\n',
    'const PAGE_SIZE = 12;\nconst LOAD_AHEAD_PX = 500;\n',
    'load ahead constant'
)

once(
    'const PAGE_CACHE_PREFIX="notion-image-gallery-page-v3:";',
    'const PAGE_CACHE_PREFIX="notion-image-gallery-page-v4:";',
    'invalidate old first page cache'
)

once(
    '''async function loadNextPage(force=false){\n  if(loadingPage||!hasMore)return;\n  loadingPage=true;\n\n  const serial=requestSerial;\n''',
    '''async function loadNextPage(force=false){\n  if(loadingPage||!hasMore)return;\n  loadingPage=true;\n  let pageSucceeded=false;\n\n  const serial=requestSerial;\n''',
    'page success state'
)

once(
    '''    if(!loadedItems.length&&!hasMore){\n      els.gallery.innerHTML='<div class="empty">該当する画像がありません。</div>'\n    }\n  }catch(err){\n''',
    '''    if(!loadedItems.length&&!hasMore){\n      els.gallery.innerHTML='<div class="empty">該当する画像がありません。</div>'\n    }\n    pageSucceeded=true;\n  }catch(err){\n''',
    'mark successful page'
)

once(
    '''  }finally{\n    if(firstPage)els.status.hidden=true;\n    loadingPage=false;\n    els.loadMoreStatus.classList.add("hidden")\n  }\n}\n''',
    '''  }finally{\n    if(firstPage)els.status.hidden=true;\n    loadingPage=false;\n    els.loadMoreStatus.classList.add("hidden");\n\n    /* IntersectionObserver can miss the next edge while a page is loading.\n       Re-check after every successful page so pagination never silently stops. */\n    if(pageSucceeded&&hasMore){\n      requestAnimationFrame(scheduleLoadMoreCheck)\n    }\n  }\n}\n''',
    'post-load pagination recheck'
)

once(
    '''/* 下に近づいたら次ページ */\nconst observer=new IntersectionObserver(entries=>{\n  if(entries.some(x=>x.isIntersecting))loadNextPage()\n},{root:null,rootMargin:"200px 0px",threshold:0});\nobserver.observe(els.sentinel);\n''',
    '''/* 下に近づいたら次ページ。\n   Observerだけに任せると、読み込み中にsentinelが交差したままになった時\n   次の通知を取りこぼすため、scroll + 読み込み完了後の再判定も併用する。 */\nlet loadMoreCheckQueued=false;\nfunction scheduleLoadMoreCheck(){\n  if(loadMoreCheckQueued)return;\n  loadMoreCheckQueued=true;\n\n  requestAnimationFrame(()=>{\n    loadMoreCheckQueued=false;\n    if(loadingPage||!hasMore)return;\n\n    const rect=els.sentinel.getBoundingClientRect();\n    if(rect.top<=window.innerHeight+LOAD_AHEAD_PX){\n      loadNextPage()\n    }\n  })\n}\nconst observer=new IntersectionObserver(entries=>{\n  if(entries.some(x=>x.isIntersecting))scheduleLoadMoreCheck()\n},{root:null,rootMargin:`${LOAD_AHEAD_PX}px 0px`,threshold:0});\nobserver.observe(els.sentinel);\nwindow.addEventListener("scroll",scheduleLoadMoreCheck,{passive:true});\n''',
    'robust load-more observer'
)

p.write_text(s,encoding='utf-8')
