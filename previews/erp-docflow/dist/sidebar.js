// Keep menu interaction independent of page rendering (and of chart instances).
export function createSidebar({doc=document,win=window,media=matchMedia('(max-width:850px)')}={}) {
  let opened=false,scrollTop=0,previousOverflow='',returnFocus=null,pendingFocus=null;
  const find=selector=>doc.querySelector(selector);
  const focus=node=>node?.focus({preventScroll:true});
  const menu=()=>find('#primary-sidebar');
  const scroll=()=>find('[data-sidebar-scroll]');
  const focusables=()=>[...(menu()?.querySelectorAll('button:not(:disabled),select,a[href],[tabindex="0"]')||[])]
    .filter(node=>!node.hidden&&node.offsetParent!==null);

  function sync() {
    const sidebar=menu(),mobile=media.matches,visible=opened&&mobile;
    sidebar?.classList.toggle('mobile-open',visible);
    if(sidebar){
      sidebar.inert=mobile&&!visible;
      sidebar.setAttribute('aria-hidden',String(mobile&&!visible));
      if(visible){sidebar.setAttribute('role','dialog');sidebar.setAttribute('aria-modal','true');}
      else{sidebar.removeAttribute('role');sidebar.removeAttribute('aria-modal');}
    }
    const backdrop=find('[data-sidebar-backdrop]');
    if(backdrop)backdrop.hidden=!visible;
    const main=find('.main');if(main)main.inert=visible;
    const trigger=find('[data-action="menu"]');
    trigger?.setAttribute('aria-expanded',String(visible));
    trigger?.setAttribute('aria-label',visible?'Fechar menu':'Abrir menu');
    if(visible)doc.body.style.overflow='hidden';
    updateScrollHint();
  }

  function updateScrollHint() {
    const viewport=scroll(),hint=find('[data-sidebar-hint]');
    if(viewport&&hint)hint.hidden=viewport.scrollHeight-viewport.clientHeight-viewport.scrollTop<8;
  }

  function revealActive() {
    // Adjust only the menu's scroll, never the document or the chart's position.
    const viewport=scroll(),active=menu()?.querySelector('[aria-current="page"]');
    if(!viewport||!active||!viewport.clientHeight)return;
    const box=viewport.getBoundingClientRect(),item=active.getBoundingClientRect();
    if(item.top<box.top+8)viewport.scrollTop-=box.top+8-item.top;
    else if(item.bottom>box.bottom-8)viewport.scrollTop+=item.bottom-box.bottom+8;
    scrollTop=viewport.scrollTop;
    updateScrollHint();
  }

  function close({restoreFocus=true}={}) {
    if(!opened)return;
    opened=false;
    doc.body.style.overflow=previousOverflow;
    sync();
    if(restoreFocus)focus(returnFocus?.isConnected?returnFocus:find('[data-action="menu"]'));
    returnFocus=null;
  }

  function toggle() {
    if(opened){close();return;}
    if(!media.matches)return;
    previousOverflow=doc.body.style.overflow;
    returnFocus=doc.activeElement;
    opened=true;sync();revealActive();
    focus(menu()?.querySelector('[data-sidebar-close]'));
  }

  function capture() {
    const viewport=scroll();if(viewport)scrollTop=viewport.scrollTop;
    pendingFocus=null;
    const active=doc.activeElement;
    if(menu()?.contains(active)){
      if(active.id==='company-selector')pendingFocus='#company-selector';
      else if(active.dataset?.go)pendingFocus=`[data-go="${active.dataset.go}"]`;
      else if(active.hasAttribute('data-sidebar-close'))pendingFocus='[data-sidebar-close]';
    }
  }

  function mount() {
    sync();
    const viewport=scroll();
    if(viewport){
      viewport.scrollTop=scrollTop;
      viewport.addEventListener('scroll',updateScrollHint,{passive:true});
    }
    if(pendingFocus&&(!media.matches||opened))focus(menu()?.querySelector(pendingFocus));
    pendingFocus=null;updateScrollHint();
  }

  function keydown(event) {
    if(!opened)return false;
    if(event.key==='Escape'){event.preventDefault();close();return true;}
    if(event.key!=='Tab')return false;
    const nodes=focusables(),first=nodes[0],last=nodes.at(-1);
    if(!first)return false;
    if(event.shiftKey&&(doc.activeElement===first||!menu()?.contains(doc.activeElement))){event.preventDefault();focus(last);}
    else if(!event.shiftKey&&(doc.activeElement===last||!menu()?.contains(doc.activeElement))){event.preventDefault();focus(first);}
    return true;
  }

  media.addEventListener?.('change',()=>{
    if(!media.matches)close({restoreFocus:false});
    sync();revealActive();
    if(media.matches&&!opened&&menu()?.contains(doc.activeElement))focus(find('[data-action="menu"]'));
  });
  win.addEventListener('resize',updateScrollHint,{passive:true});
  return {capture,mount,toggle,close,keydown,revealActive};
}
