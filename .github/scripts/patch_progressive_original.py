from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')

def once(old,new,label):
    global s
    if old not in s:
        raise SystemExit(f'patch target not found: {label}')
    s=s.replace(old,new,1)

once(
'''function originalSource(item){
  return item?.originalUrl||item?.url||item?.previewUrl||""
}
function setViewerSourceWithFallback(primary,fallback=""){
''',
'''function originalSource(item){
  return item?.originalUrl||item?.url||item?.previewUrl||""
}
function thumbSource(item){
  return item?.thumbUrl||item?.url||item?.originalUrl||item?.previewUrl||""
}

let viewerLoadToken=0;
const originalWarmups=new Map();

function warmOriginal(item,priority="low"){
  const src=originalSource(item);
  if(!src)return Promise.resolve(false);

  const existing=originalWarmups.get(src);
  if(existing)return existing;

  const promise=new Promise(resolve=>{
    const img=new Image();
    img.decoding="async";
    img.fetchPriority=priority;
    img.onload=()=>resolve(true);
    img.onerror=()=>{
      originalWarmups.delete(src);
      resolve(false)
    };
    img.src=src
  });

  originalWarmups.set(src,promise);
  return promise
}

function warmViewerNeighbors(index){
  const run=()=>{
    warmOriginal(loadedItems[index-1],"low");
    warmOriginal(loadedItems[index+1],"low")
  };

  if("requestIdleCallback" in window){
    requestIdleCallback(run,{timeout:900})
  }else{
    setTimeout(run,350)
  }
}

function setViewerSourceProgressive(item){
  if(!item)return;

  const token=++viewerLoadToken;
  const lowSrc=thumbSource(item);
  const highSrc=originalSource(item);

  els.viewerImage.alt=item.title||"";
  els.viewerImage.dataset.fallbackSrc="";

  if(lowSrc&&els.viewerImage.src!==lowSrc){
    els.viewerImage.src=lowSrc
  }
  els.viewerImage.style.opacity="1";

  if(!highSrc||highSrc===lowSrc)return;

  warmOriginal(item,"high").then(ok=>{
    if(!ok||token!==viewerLoadToken)return;
    if(els.viewerImage.src!==highSrc){
      els.viewerImage.src=highSrc
    }
  })
}

function setViewerSourceWithFallback(primary,fallback=""){
''',
    'progressive viewer helpers'
)

once(
'''  btn.appendChild(visual);
  btn.addEventListener("click",()=>openViewer(index));
  shortestColumn().appendChild(btn)
''',
'''  btn.appendChild(visual);

  /* Start fetching the R2 original shortly before it is likely to be opened.
     This uses bandwidth/cache only; it does not create another Images transform. */
  btn.addEventListener("pointerenter",e=>{
    if(e.pointerType==="mouse"||e.pointerType==="pen"){
      warmOriginal(item,"low")
    }
  },{passive:true});
  btn.addEventListener("pointerdown",()=>{
    warmOriginal(item,"high")
  },{passive:true});

  btn.addEventListener("click",()=>openViewer(index));
  shortestColumn().appendChild(btn)
''',
    'card original prefetch'
)

once(
'''function ensureOriginalImage(){
  const item=loadedItems[currentIndex];
  if(!item)return;
  const original=originalSource(item);
  els.viewerImage.dataset.fallbackSrc="";
  if(original&&els.viewerImage.src!==original){
    els.viewerImage.src=original
  }
}
''',
'''function ensureOriginalImage(){
  const item=loadedItems[currentIndex];
  if(!item)return;
  setViewerSourceProgressive(item)
}
''',
    'ensure original progressive'
)

once(
'''    const item=loadedItems[currentIndex];
    setViewerSourceWithFallback(
      viewerSource(item),
      originalSource(item)
    )
''',
'''    const item=loadedItems[currentIndex];
    setViewerSourceProgressive(item)
''',
    'restore progressive source'
)

once(
'''  els.viewerImage.style.opacity=".45";
  setViewerSourceWithFallback(
    document.fullscreenElement
      ? originalSource(item)
      : viewerSource(item),
    originalSource(item)
  );
  els.viewerImage.alt=item.title||"";
  els.viewerCount.textContent=`${currentIndex+1} / ${loadedItems.length}${hasMore?" +":""}`;

  requestAnimationFrame(()=>els.viewerImage.style.opacity="1");
  loadViewerTags(item);
''',
'''  /* Show the already-cached 420px thumb immediately, then swap to the R2
     original only after it has finished loading. No blank wait on click. */
  setViewerSourceProgressive(item);
  els.viewerCount.textContent=`${currentIndex+1} / ${loadedItems.length}${hasMore?" +":""}`;

  loadViewerTags(item);
  warmViewerNeighbors(currentIndex);
''',
    'viewer progressive display'
)

p.write_text(s,encoding='utf-8')
