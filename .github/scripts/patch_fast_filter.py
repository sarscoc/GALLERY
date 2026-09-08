from pathlib import Path
p=Path('index.html')
s=p.read_text(encoding='utf-8')

def once(old,new,label):
    global s
    if old not in s:
        raise SystemExit(f'patch target not found: {label}')
    s=s.replace(old,new,1)

old='''function preloadImage(src,priority="auto"){
  return new Promise(resolve=>{
    const img=new Image();
    img.decoding="async";
    img.fetchPriority=priority;
    img.onload=()=>resolve({ok:true,img});
    img.onerror=()=>resolve({ok:false,img});
    img.src=src
  })
}
'''
new='''function preloadImage(src,priority="auto"){
  return new Promise(resolve=>{
    const img=new Image();
    img.decoding="async";
    img.fetchPriority=priority;
    img.onload=()=>resolve({ok:true,img,src});
    img.onerror=()=>resolve({ok:false,img,src});
    img.src=src
  })
}
async function preloadImageCandidates(candidates,priority="auto"){
  const unique=[...new Set((candidates||[]).filter(Boolean))];
  for(const src of unique){
    const loaded=await preloadImage(src,priority);
    if(loaded.ok)return loaded
  }
  return {ok:false,img:null,src:""}
}
'''
once(old,new,'preload image fallback')

old='''async function appendItem(item,index,serial,priority="auto"){
  const src=item.thumbUrl||item.url||item.originalUrl;
  const key=retainedThumbKey(item,src);
  let retained=retainedThumbs.get(key)||null;

  if(!retained){
    const loaded=await preloadImage(src,priority);
    if(serial!==requestSerial||!loaded.ok)return;
    retained=makeRetainedThumbnail(loaded.img,item);
    retainedThumbs.set(key,retained)
  }
'''
new='''async function appendItem(item,index,serial,priority="auto"){
  const candidates=[item.thumbUrl,item.url,item.originalUrl];
  const src=candidates.find(Boolean)||"";
  const key=retainedThumbKey(item,src);
  let retained=retainedThumbs.get(key)||null;

  if(!retained){
    const loaded=await preloadImageCandidates(candidates,priority);
    if(serial!==requestSerial||!loaded.ok)return;
    retained=makeRetainedThumbnail(loaded.img,item);
    retainedThumbs.set(key,retained)
  }
'''
once(old,new,'append item fallback')

old='''function viewerSource(item){
  return item?.previewUrl||item?.url||item?.originalUrl||""
}
function originalSource(item){
  return item?.originalUrl||item?.url||item?.previewUrl||""
}
'''
new='''function viewerSource(item){
  return item?.previewUrl||item?.url||item?.originalUrl||""
}
function originalSource(item){
  return item?.originalUrl||item?.url||item?.previewUrl||""
}
function setViewerSourceWithFallback(primary,fallback=""){
  const first=primary||fallback||"";
  els.viewerImage.dataset.fallbackSrc=(fallback&&fallback!==first)?fallback:"";
  if(first&&els.viewerImage.src!==first)els.viewerImage.src=first
}
'''
once(old,new,'viewer fallback helper')

old='''function ensureOriginalImage(){
  const item=loadedItems[currentIndex];
  if(!item)return;
  const original=originalSource(item);
  if(original&&els.viewerImage.src!==original){
    els.viewerImage.src=original
  }
}
'''
new='''function ensureOriginalImage(){
  const item=loadedItems[currentIndex];
  if(!item)return;
  const original=originalSource(item);
  els.viewerImage.dataset.fallbackSrc="";
  if(original&&els.viewerImage.src!==original){
    els.viewerImage.src=original
  }
}
'''
once(old,new,'ensure original')

old='''    const src=viewerSource(loadedItems[currentIndex]);
    if(src&&els.viewerImage.src!==src)els.viewerImage.src=src
'''
new='''    const item=loadedItems[currentIndex];
    setViewerSourceWithFallback(
      viewerSource(item),
      originalSource(item)
    )
'''
once(old,new,'restore preview fallback')

old='''  els.viewerImage.style.opacity=".45";
  els.viewerImage.src=document.fullscreenElement
    ? originalSource(item)
    : viewerSource(item);
  els.viewerImage.alt=item.title||"";
'''
new='''  els.viewerImage.style.opacity=".45";
  setViewerSourceWithFallback(
    document.fullscreenElement
      ? originalSource(item)
      : viewerSource(item),
    originalSource(item)
  );
  els.viewerImage.alt=item.title||"";
'''
once(old,new,'viewer source assignment')

marker='''/* Desktop: buttons / keyboard / double-click zoom */
'''
insert='''els.viewerImage.addEventListener("error",()=>{
  const fallback=els.viewerImage.dataset.fallbackSrc||"";
  if(!fallback)return;
  els.viewerImage.dataset.fallbackSrc="";
  els.viewerImage.src=fallback
});

/* Desktop: buttons / keyboard / double-click zoom */
'''
once(marker,insert,'viewer error fallback')

p.write_text(s,encoding='utf-8')
