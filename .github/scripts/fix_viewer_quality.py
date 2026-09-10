from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')

old='''function setViewerSourceProgressive(item){
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
'''
new='''function setViewerSourceProgressive(item){
  if(!item)return;

  const token=++viewerLoadToken;
  const lowSrc=thumbSource(item);
  const highSrc=originalSource(item);

  els.viewerImage.alt=item.title||"";
  els.viewerImage.dataset.fallbackSrc="";

  /* Once the R2 original is already on screen, never downgrade it back to
     the 420px thumbnail when zoom/fullscreen logic asks for the source again. */
  if(highSrc&&els.viewerImage.src===highSrc){
    els.viewerImage.style.opacity="1";
    return
  }

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
'''
if old not in s:
    raise SystemExit('progressive viewer target not found')
s=s.replace(old,new,1)

old='const PAGE_CACHE_PREFIX="notion-image-gallery-page-v4:";'
new='const PAGE_CACHE_PREFIX="notion-image-gallery-page-v5:";'
if old not in s:
    raise SystemExit('cache prefix target not found')
s=s.replace(old,new,1)

p.write_text(s,encoding='utf-8')
