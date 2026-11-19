import assert from 'node:assert/strict';
import {createSidebar} from '../dist/sidebar.js';

// Controlled DOM with scroll geometry, not a browser/pixel test.
function fixture(mobile=false) {
  const doc={body:{style:{overflow:''}},activeElement:null},events={},mediaEvents={};
  function element(name){
    const attrs=new Map(),classes=new Set();
    return {name,attrs,dataset:{},hidden:false,offsetParent:{},isConnected:true,inert:false,
      classList:{toggle(k,on){on?classes.add(k):classes.delete(k)},contains:k=>classes.has(k)},
      focus(options){doc.activeElement=this;this.focusOptions=options},
      setAttribute:(k,v)=>attrs.set(k,v),removeAttribute:k=>attrs.delete(k),hasAttribute:k=>attrs.has(k)};
  }
  const trigger=element('trigger'),sidebar=element('sidebar'),main=element('main'),backdrop=element('backdrop'),hint=element('hint');
  const close=element('close'),company=element('company'),viewport=element('viewport');
  company.id='company-selector';close.setAttribute('data-sidebar-close','');
  Object.assign(viewport,{scrollTop:0,scrollHeight:800,clientHeight:430,
    getBoundingClientRect:()=>({top:180,bottom:610}),
    addEventListener:(name,fn)=>events['scroll:'+name]=fn});
  const links=['home','flow','obligations','tasks','companies','banks','assets','contracts','documents','accounting'].map((id,i)=>{
    const link=element(id);link.dataset.go=id;
    link.getBoundingClientRect=()=>({top:180+i*50-viewport.scrollTop,bottom:224+i*50-viewport.scrollTop});
    return link;
  });
  let active=links[0];
  const children=[close,company,viewport,...links];
  sidebar.contains=node=>children.includes(node);
  sidebar.querySelector=selector=>selector==='[aria-current="page"]'?active:selector==='[data-sidebar-close]'?close:selector==='#company-selector'?company:links.find(link=>selector===`[data-go="${link.dataset.go}"]`);
  sidebar.querySelectorAll=()=>children.filter(x=>x!==close||media.matches);
  const mapping={'#primary-sidebar':sidebar,'[data-sidebar-scroll]':viewport,'[data-sidebar-hint]':hint,'[data-action="menu"]':trigger,'[data-sidebar-backdrop]':backdrop,'.main':main};
  doc.querySelector=selector=>mapping[selector]||null;
  const media={matches:mobile,addEventListener:(name,fn)=>mediaEvents[name]=fn};
  let pageScrolled=0;
  const win={addEventListener:(name,fn)=>events[name]=fn,scrollTo(){pageScrolled++}};
  doc.activeElement=trigger;
  const ui=createSidebar({doc,win,media});ui.mount();
  function key(key,shiftKey=false){const event={key,shiftKey,prevented:false,preventDefault(){this.prevented=true}};ui.keydown(event);return event;}
  return {ui,doc,sidebar,main,trigger,backdrop,hint,viewport,company,links,close,media,key,events,
    setActive(index){active=links[index]},pageScrolled:()=>pageScrolled,
    resize(mobile){media.matches=mobile;mediaEvents.change()}};
}

// Short desktop: lower links can be revealed by scrolling only the menu.
const desktop=fixture();
assert.equal(desktop.sidebar.inert,false);
assert.equal(desktop.backdrop.hidden,true);
assert.equal(desktop.hint.hidden,false);
desktop.setActive(9);desktop.ui.revealActive();
assert.ok(desktop.viewport.scrollTop>0);
const end=desktop.links[9].getBoundingClientRect();
assert.ok(end.bottom<=desktop.viewport.getBoundingClientRect().bottom-8);
assert.equal(desktop.pageScrolled(),0,'Revealing a menu item must not move the page/chart');
desktop.viewport.scrollTop=300;desktop.company.focus();desktop.ui.capture();
desktop.viewport.scrollTop=0;desktop.doc.activeElement=desktop.main;desktop.ui.mount();
assert.equal(desktop.viewport.scrollTop,300,'Unrelated renders preserve independent menu scroll');
assert.equal(desktop.doc.activeElement,desktop.company,'Changing company does not lose keyboard focus');
desktop.viewport.scrollTop=370;desktop.events['scroll:scroll']();assert.equal(desktop.hint.hidden,true);
desktop.viewport.scrollTop=0;desktop.events['scroll:scroll']();assert.equal(desktop.hint.hidden,false);
desktop.setActive(0);desktop.ui.revealActive();assert.equal(desktop.pageScrolled(),0);
desktop.ui.toggle();assert.equal(desktop.main.inert,false,'Desktop does not become a modal drawer');

// Mobile: opening and closing touch only menu state, with a focus-contained dialog.
const mobile=fixture(true);
assert.equal(mobile.sidebar.inert,true);
mobile.ui.toggle();
assert.equal(mobile.sidebar.inert,false);
assert.equal(mobile.sidebar.classList.contains('mobile-open'),true);
assert.equal(mobile.sidebar.attrs.get('aria-modal'),'true');
assert.equal(mobile.trigger.attrs.get('aria-expanded'),'true');
assert.equal(mobile.main.inert,true);assert.equal(mobile.backdrop.hidden,false);
assert.equal(mobile.doc.body.style.overflow,'hidden');assert.equal(mobile.doc.activeElement,mobile.close);
assert.equal(mobile.key('Tab',true).prevented,true);assert.equal(mobile.doc.activeElement,mobile.links.at(-1));
assert.equal(mobile.key('Tab').prevented,true);assert.equal(mobile.doc.activeElement,mobile.close);
assert.equal(mobile.key('Escape').prevented,true);
assert.equal(mobile.main.inert,false);assert.equal(mobile.sidebar.inert,true);
assert.equal(mobile.backdrop.hidden,true);assert.equal(mobile.doc.body.style.overflow,'');
assert.equal(mobile.doc.activeElement,mobile.trigger);
assert.equal(mobile.trigger.attrs.get('aria-expanded'),'false');
mobile.ui.toggle();mobile.ui.close(); // Same close path used by X and backdrop.
assert.equal(mobile.doc.activeElement,mobile.trigger);
mobile.ui.toggle();mobile.ui.close({restoreFocus:false}); // Destination controls focus on navigation.
assert.notEqual(mobile.doc.activeElement,mobile.trigger);
assert.equal(mobile.main.inert,false);
mobile.ui.toggle();mobile.resize(false);
assert.equal(mobile.sidebar.inert,false);assert.equal(mobile.main.inert,false);
assert.equal(mobile.doc.body.style.overflow,'');assert.equal(mobile.sidebar.attrs.has('aria-modal'),false);
mobile.company.focus();mobile.resize(true);assert.equal(mobile.doc.activeElement,mobile.trigger);
assert.equal(mobile.pageScrolled(),0);
mobile.doc.body.style.overflow='clip';mobile.ui.toggle();mobile.ui.close();
assert.equal(mobile.doc.body.style.overflow,'clip','Close restores the previous overflow setting');
console.log('PASS sidebar: scroll reach, retained position/focus, responsive drawer, backdrop close path, Escape, focus trap, resize cleanup and no page scroll. Controlled DOM only.');
