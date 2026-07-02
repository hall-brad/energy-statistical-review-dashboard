#!/usr/bin/env python3
"""Build the single self-contained EI Statistical Review dashboard HTML."""
import json

DATA = "/sessions/zealous-beautiful-hypatia/mnt/outputs/ei_data.json"
OUT  = "/sessions/zealous-beautiful-hypatia/mnt/outputs/EI-Statistical-Review-Dashboard.html"

with open(DATA) as f:
    data_str = f.read()
# make safe to embed inside a <script> block
data_str = data_str.replace("</", "<\\/")

HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>EI Statistical Review of World Energy 2026 — Interactive Dashboard</title>
<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.min.js"></script>
<style>
:root{
  --bg:#f6f7f5; --panel:#ffffff; --ink:#13201c; --muted:#5d6b66; --line:#e3e7e3;
  --accent:#1f8a70; --accent2:#0f6e8c; --accent3:#c46a1b; --warn:#b4452f;
  --chip:#eef2ef; --shadow:0 1px 3px rgba(0,0,0,.06),0 1px 2px rgba(0,0,0,.04);
  --sidebar:300px;
}
[data-theme="dark"]{
  --bg:#0f1513; --panel:#161e1b; --ink:#e7efea; --muted:#9bada6; --line:#26302c;
  --accent:#37b894; --accent2:#3aa6c9; --accent3:#e08a3c; --warn:#e2705a;
  --chip:#1d2723; --shadow:0 1px 3px rgba(0,0,0,.4);
}
*{box-sizing:border-box}
html,body{margin:0;padding:0}
body{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;
  background:var(--bg); color:var(--ink); font-size:14px; line-height:1.45;}
a{color:var(--accent2);text-decoration:none}
button{font-family:inherit;cursor:pointer}
header{position:sticky;top:0;z-index:30;background:var(--panel);border-bottom:1px solid var(--line);
  display:flex;align-items:center;gap:14px;padding:10px 18px;box-shadow:var(--shadow)}
.brand{display:flex;flex-direction:column;line-height:1.15}
.brand b{font-size:15px;letter-spacing:.2px}
.brand span{font-size:11px;color:var(--muted)}
.modes{display:flex;gap:4px;margin-left:6px}
.modebtn{background:transparent;border:1px solid var(--line);color:var(--muted);padding:6px 13px;border-radius:7px;font-size:13px;font-weight:600}
.modebtn.active{background:var(--accent);border-color:var(--accent);color:#fff}
.grow{flex:1}
.gsearch{position:relative}
.gsearch input{width:230px;padding:7px 11px 7px 30px;border:1px solid var(--line);border-radius:8px;background:var(--bg);color:var(--ink);font-size:13px}
.gsearch svg{position:absolute;left:9px;top:8px;width:15px;height:15px;opacity:.5}
.iconbtn{background:var(--chip);border:1px solid var(--line);color:var(--ink);width:34px;height:34px;border-radius:8px;font-size:15px;display:flex;align-items:center;justify-content:center}
.layout{display:flex;min-height:calc(100vh - 56px)}
aside{width:var(--sidebar);flex:0 0 var(--sidebar);background:var(--panel);border-right:1px solid var(--line);
  overflow-y:auto;height:calc(100vh - 56px);position:sticky;top:56px;padding:8px 0 40px}
.catgroup{border-bottom:1px solid var(--line)}
.cathead{display:flex;align-items:center;gap:8px;padding:9px 16px;font-weight:700;font-size:12.5px;
  text-transform:uppercase;letter-spacing:.4px;color:var(--ink);user-select:none}
.cathead .count{margin-left:auto;font-size:11px;color:var(--muted);font-weight:600}
.cathead .tw{transition:transform .15s;font-size:10px;color:var(--muted)}
.catgroup.collapsed .catlist{display:none}
.catgroup.collapsed .tw{transform:rotate(-90deg)}
.catlist{padding:2px 0 8px}
.tlink{display:block;padding:6px 16px 6px 30px;font-size:12.7px;color:var(--muted);border-left:3px solid transparent;cursor:pointer}
.tlink:hover{background:var(--chip);color:var(--ink)}
.tlink.active{color:var(--ink);border-left-color:var(--accent);background:var(--chip);font-weight:600}
.catdot{width:8px;height:8px;border-radius:2px;flex:0 0 8px}
main{flex:1;min-width:0;padding:18px 22px 60px}
.sheethead h1{margin:0 0 3px;font-size:21px;letter-spacing:-.2px}
.sheethead .meta{color:var(--muted);font-size:12.5px;margin-bottom:2px}
.badge{display:inline-block;background:var(--chip);border:1px solid var(--line);border-radius:20px;
  padding:2px 10px;font-size:11px;color:var(--muted);margin-right:6px}
.subtabs{display:flex;gap:4px;margin:16px 0 14px;border-bottom:1px solid var(--line)}
.subtab{background:transparent;border:none;border-bottom:2px solid transparent;color:var(--muted);
  padding:8px 14px;font-size:13.5px;font-weight:600;margin-bottom:-1px}
.subtab.active{color:var(--accent);border-bottom-color:var(--accent)}
.panel{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:16px;box-shadow:var(--shadow);margin-bottom:16px}
.controls{display:flex;flex-wrap:wrap;gap:14px;align-items:flex-end}
.ctl{display:flex;flex-direction:column;gap:5px}
.ctl label{font-size:11px;text-transform:uppercase;letter-spacing:.4px;color:var(--muted);font-weight:700}
select,input[type=number]{padding:7px 9px;border:1px solid var(--line);border-radius:7px;background:var(--bg);color:var(--ink);font-size:13px}
input[type=range]{accent-color:var(--accent)}
.btn{background:var(--chip);border:1px solid var(--line);color:var(--ink);padding:7px 12px;border-radius:7px;font-size:12.5px;font-weight:600}
.btn:hover{border-color:var(--accent)}
.btn.primary{background:var(--accent);border-color:var(--accent);color:#fff}
.chartwrap{position:relative;height:440px;margin-top:6px}
.chartwrap.short{height:360px}
.rankwrap{position:relative;margin-top:6px}
.entpicker{max-height:260px;overflow:auto;border:1px solid var(--line);border-radius:8px;padding:6px;background:var(--bg);min-width:240px}
.entpicker .row{display:flex;align-items:center;gap:7px;padding:3px 4px;border-radius:5px;font-size:12.7px}
.entpicker .row:hover{background:var(--chip)}
.entpicker .row.agg label{color:var(--accent2)}
.entpicker input{accent-color:var(--accent)}
.pickbar{display:flex;gap:6px;flex-wrap:wrap;margin-bottom:8px}
.pickbar input[type=text]{flex:1;min-width:140px;padding:6px 9px;border:1px solid var(--line);border-radius:7px;background:var(--bg);color:var(--ink);font-size:12.5px}
.tablescroll{overflow:auto;max-height:70vh;border:1px solid var(--line);border-radius:10px}
table.data{border-collapse:separate;border-spacing:0;font-size:12.3px;width:100%}
table.data th,table.data td{padding:5px 9px;white-space:nowrap;border-bottom:1px solid var(--line)}
table.data thead th{position:sticky;top:0;background:var(--panel);z-index:2;text-align:right;font-weight:700;cursor:pointer;border-bottom:2px solid var(--line)}
table.data thead th:first-child{text-align:left;left:0;z-index:3}
table.data td{text-align:right;font-variant-numeric:tabular-nums}
table.data td:first-child,table.data th.rowhead{text-align:left;position:sticky;left:0;background:var(--panel);font-weight:600;z-index:1}
table.data tr.agg td{font-weight:700;background:color-mix(in srgb,var(--accent) 7%,var(--panel))}
table.data tr.agg td:first-child{background:color-mix(in srgb,var(--accent) 9%,var(--panel))}
table.data tr.spacer td{height:7px;padding:0;background:var(--bg);border:none}
table.data tbody tr:hover td{background:var(--chip)}
table.data td.na{color:var(--muted)}
.raw th,.raw td{border:1px solid var(--line);padding:4px 8px;font-size:12px;white-space:nowrap}
.raw td.num{text-align:right;font-variant-numeric:tabular-nums}
.raw tr:first-child td{font-weight:700;font-size:13px}
/* custom-layout (raw) tables: natural column widths + horizontal scroll so nothing gets crushed */
table.rawtbl{border-collapse:separate;border-spacing:0;width:auto;font-size:12.3px}
table.rawtbl td,table.rawtbl th{padding:5px 12px;white-space:nowrap;border-bottom:1px solid var(--line);border-right:1px solid var(--line)}
table.rawtbl td.num{text-align:right;font-variant-numeric:tabular-nums}
table.rawtbl th{position:sticky;top:0;z-index:3;background:var(--panel);font-weight:700;text-align:right;border-bottom:2px solid var(--line)}
table.rawtbl th.rh{text-align:left;left:0;z-index:4}
table.rawtbl td.rh,table.rawtbl th.rh{position:sticky;left:0;background:var(--panel);font-weight:600;text-align:left;z-index:2;box-shadow:1px 0 0 var(--line);max-width:300px;overflow:hidden;text-overflow:ellipsis}
table.rawtbl tr.tot td{font-weight:700;background:color-mix(in srgb,var(--accent) 6%,var(--panel))}
table.rawtbl tbody tr:hover td{background:var(--chip)}
table.rawtbl tr.blank td{height:6px;padding:0;background:var(--bg)}
.cards{display:grid;grid-template-columns:repeat(auto-fill,minmax(235px,1fr));gap:13px}
.card{background:var(--panel);border:1px solid var(--line);border-radius:11px;padding:13px;box-shadow:var(--shadow);cursor:pointer;transition:transform .08s,border-color .08s}
.card:hover{transform:translateY(-2px);border-color:var(--accent)}
.card .cat{font-size:10px;text-transform:uppercase;letter-spacing:.4px;color:var(--muted);font-weight:700}
.card .nm{font-size:13px;font-weight:600;margin:3px 0 6px;line-height:1.25}
.card .big{font-size:20px;font-weight:700;letter-spacing:-.3px}
.card .unit{font-size:11px;color:var(--muted)}
.card .spark{height:38px;margin-top:6px}
.card .delta{font-size:11.5px;font-weight:700;margin-top:4px}
.up{color:var(--accent)} .down{color:var(--warn)}
.profhead{display:flex;flex-wrap:wrap;gap:14px;align-items:flex-end;margin-bottom:16px}
.note{font-size:11.5px;color:var(--muted);margin-top:10px;line-height:1.5}
.hint{color:var(--muted);font-size:12.5px}
.statrow{display:flex;flex-wrap:wrap;gap:10px;margin:4px 0 2px}
.stat{background:var(--chip);border:1px solid var(--line);border-radius:9px;padding:8px 13px;min-width:120px}
.stat .v{font-size:18px;font-weight:700}
.stat .k{font-size:10.5px;text-transform:uppercase;letter-spacing:.3px;color:var(--muted);font-weight:700}
@media(max-width:820px){
  aside{position:fixed;left:0;top:56px;z-index:40;transform:translateX(-100%);transition:transform .2s}
  body.navopen aside{transform:none}
  :root{--sidebar:270px}
  .gsearch input{width:140px}
}
.menutoggle{display:none}
@media(max-width:820px){.menutoggle{display:flex}}
.homehero{margin:6px 0 22px;max-width:900px}
.homehero .eyebrow{font-size:11px;text-transform:uppercase;letter-spacing:.6px;color:var(--accent);font-weight:700}
.homehero h1{margin:4px 0 8px;font-size:30px;letter-spacing:-.4px}
.homehero p{color:var(--muted);font-size:14px;line-height:1.6;margin:0}
.tocgrid{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:16px}
.toccat{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:14px 16px;box-shadow:var(--shadow)}
.tochead{display:flex;align-items:center;gap:8px;font-weight:700;font-size:13px;text-transform:uppercase;letter-spacing:.4px;padding-bottom:8px;margin-bottom:6px;border-bottom:1px solid var(--line)}
.tochead .tccount{margin-left:auto;font-size:11px;color:var(--muted)}
.toclist{display:flex;flex-direction:column}
.toclink{padding:5px 6px;font-size:13px;color:var(--muted);border-radius:6px;cursor:pointer}
.toclink:hover{background:var(--chip);color:var(--ink)}
footer.attrib{padding:16px 22px;border-top:1px solid var(--line);background:var(--panel);
  color:var(--muted);font-size:11.5px;line-height:1.6}
footer.attrib b{color:var(--ink)}
footer.attrib a{color:var(--accent2)}
</style>
</head>
<body>
<header>
  <button class="iconbtn menutoggle" id="menuToggle">☰</button>
  <div class="brand" id="brandHome" title="Back to contents" style="cursor:pointer">
    <b>Statistical Review of World Energy</b>
    <span>Energy Institute · 2026 edition · <span id="scount"></span> tables</span>
  </div>
  <div class="modes">
    <button class="modebtn" data-mode="home">Contents</button>
    <button class="modebtn active" data-mode="table">Tables</button>
    <button class="modebtn" data-mode="profile">Country profile</button>
  </div>
  <div class="grow"></div>
  <div class="gsearch">
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="7"/><path d="M21 21l-4-4"/></svg>
    <input id="globalSearch" placeholder="Find a table…" autocomplete="off">
  </div>
  <button class="iconbtn" id="themeBtn" title="Toggle light/dark">◐</button>
</header>
<div class="layout">
  <aside id="sidebar"></aside>
  <main id="main"></main>
</div>
<footer class="attrib">
  <b>Data source:</b> Energy Institute, <i>Statistical Review of World Energy</i> (2026 edition) —
  <a href="https://www.energyinst.org/statistical-review" target="_blank" rel="noopener">energyinst.org/statistical-review</a>.
  Data &copy; Energy Institute; reproduced here with attribution for research and educational use.
  The Statistical Review is produced by the Energy Institute in partnership with KPMG and Kearney.
  This interactive dashboard is an independent visualization and is not affiliated with or endorsed by the Energy Institute.
</footer>
<script>const RAW = </script>
<script id="data-script">/*__DATA__*/</script>
<script>
/* ====================== EI DASHBOARD APP ====================== */
const DB = window.__EIDATA__;
const SHEETS = DB.sheets, ORDER = DB.order, CATS = DB.categories;
document.getElementById('scount').textContent = DB.meta.sheetCount;

const CATCOLOR = {
  'Derived & ratios':'#6a5acd',
  'Overview':'#1f8a70','Carbon & Emissions':'#b4452f','Oil':'#6b5b3e','Natural Gas':'#0f6e8c',
  'Coal':'#444','Nuclear':'#7a4fb0','Hydro':'#2a7fc0','Renewables':'#2e9e4f',
  'Electricity':'#c46a1b','Storage & Demand':'#c0397d','Critical Minerals':'#8a6d1f','Reference':'#777'
};
const PALETTE = ['#1f8a70','#c46a1b','#0f6e8c','#b4452f','#7a4fb0','#2e9e4f','#c0397d','#8a6d1f',
  '#3aa6c9','#e08a3c','#5a7d2a','#9b3b6a','#2a6f97','#a8521b','#46836b','#704fa0'];

let MODE='home', CUR=null, SUB='compare', RAW_SUB='';
const state = {}; // per-sheet view state

/* ---------- helpers ---------- */
const $=(s,r=document)=>r.querySelector(s);
const el=(t,c,h)=>{const e=document.createElement(t); if(c)e.className=c; if(h!=null)e.innerHTML=h; return e;};
function fmt(v,dec){
  if(v===null||v===undefined||v==='')return '–';
  if(typeof v!=='number') return v;
  const a=Math.abs(v);
  if(dec!==undefined) return v.toLocaleString('en-US',{minimumFractionDigits:dec,maximumFractionDigits:dec});
  if(a>=100) return v.toLocaleString('en-US',{maximumFractionDigits:0});
  if(a>=1)   return v.toLocaleString('en-US',{maximumFractionDigits:2});
  if(a===0)  return '0';
  return v.toLocaleString('en-US',{maximumFractionDigits:3});
}
const isPctCol = n => /share|growth|%|per annum|ratio/i.test(n);
function fmtCell(v,colname){
  if(v===null||v===undefined)return '–';
  if(colname && isPctCol(colname) && typeof v==='number') return (v*100).toFixed(1)+'%';
  return fmt(v);
}
function latestIdx(values){ for(let i=values.length-1;i>=0;i--) if(values[i]!=null) return i; return -1; }
function csvDownload(name, rows){
  const csv=rows.map(r=>r.map(c=>{
    if(c==null)return '';
    const s=String(c);
    return /[",\n]/.test(s)?'"'+s.replace(/"/g,'""')+'"':s;
  }).join(',')).join('\n');
  const blob=new Blob([csv],{type:'text/csv'});
  const a=el('a'); a.href=URL.createObjectURL(blob); a.download=name; a.click();
}

/* ---------- sidebar ---------- */
function buildSidebar(filter){
  const sb=$('#sidebar'); sb.innerHTML='';
  filter=(filter||'').toLowerCase();
  CATS.forEach(cat=>{
    const matches=cat.sheets.filter(s=>!filter||s.toLowerCase().includes(filter)||cat.name.toLowerCase().includes(filter));
    if(!matches.length) return;
    const g=el('div','catgroup'+(filter?'':((state['_open_'+cat.name]===false)?' collapsed':'')));
    const dot=`<span class="catdot" style="background:${CATCOLOR[cat.name]||'#888'}"></span>`;
    const head=el('div','cathead',`${dot}<span>${cat.name}</span><span class="count">${cat.sheets.length}</span><span class="tw">▾</span>`);
    head.onclick=()=>{ g.classList.toggle('collapsed'); state['_open_'+cat.name]=!g.classList.contains('collapsed'); };
    g.appendChild(head);
    const list=el('div','catlist');
    matches.forEach(name=>{
      const a=el('div','tlink'+(name===CUR?' active':''), title_of(name));
      a.onclick=()=>{ MODE='table'; setMode('table'); selectSheet(name); };
      a.dataset.sheet=name;
      list.appendChild(a);
    });
    g.appendChild(list);
    sb.appendChild(g);
  });
}
function title_of(name){
  const s=SHEETS[name];
  // friendlier label = sheet tab name (already descriptive)
  return name;
}

/* ---------- header modes ---------- */
function setMode(m){
  MODE=m;
  document.querySelectorAll('.modebtn').forEach(b=>b.classList.toggle('active',b.dataset.mode===m));
  if(m==='profile') renderProfile();
  else if(m==='home') renderHome();
  else { if(!CUR) renderHome(); else selectSheet(CUR); }
}
function firstTimeseries(){ return ORDER.find(n=>SHEETS[n].type!=='raw') || ORDER[0]; }

/* ---------- HOME / clickable table of contents ---------- */
function renderHome(){
  MODE='home';
  document.querySelectorAll('.tlink').forEach(a=>a.classList.remove('active'));
  document.querySelectorAll('.modebtn').forEach(b=>b.classList.toggle('active',b.dataset.mode==='home'));
  const main=$('#main'); main.innerHTML='';
  const hero=el('div','homehero');
  hero.innerHTML=`<div class="eyebrow">Energy Institute · 2026 edition</div>
    <h1>Statistical Review of World Energy</h1>
    <p>An interactive view of all <b>${DB.meta.sheetCount}</b> data tables — every fuel, emissions, prices, electricity and critical minerals, ${SHEETS['Total Energy Supply (TES) -EJ']?SHEETS['Total Energy Supply (TES) -EJ'].years[0]+'–'+SHEETS['Total Energy Supply (TES) -EJ'].years[SHEETS['Total Energy Supply (TES) -EJ'].years.length-1]:''}. Pick a table below, or use <b>Country profile</b> to see one country across every metric.</p>`;
  main.appendChild(hero);
  const wrap=el('div','tocgrid');
  CATS.forEach(cat=>{
    const box=el('div','toccat');
    box.innerHTML=`<div class="tochead"><span class="catdot" style="background:${CATCOLOR[cat.name]||'#888'}"></span>${cat.name}<span class="tccount">${cat.sheets.length}</span></div>`;
    const ul=el('div','toclist');
    cat.sheets.forEach(name=>{
      const a=el('a','toclink',escapeHtml(name));
      a.onclick=()=>{ setModeButtons('table'); selectSheet(name); };
      ul.appendChild(a);
    });
    box.appendChild(ul); wrap.appendChild(box);
  });
  main.appendChild(wrap);
}

/* ---------- select & render a sheet ---------- */
function selectSheet(name){
  CUR=name; const s=SHEETS[name];
  document.querySelectorAll('.tlink').forEach(a=>a.classList.toggle('active',a.dataset.sheet===name));
  // ensure its category open
  const main=$('#main'); main.innerHTML='';
  const head=el('div','sheethead');
  const span = s.type==='timeseries'||s.type==='yearindexed' ? `${s.years[0]}–${s.years[s.years.length-1]}` : 'custom layout';
  head.innerHTML=`<h1>${name}</h1>
    <div class="meta">${s.title?escapeHtml(s.title)+' · ':''}${s.unit?'<b>'+escapeHtml(s.unit)+'</b> · ':''}${span}</div>
    <div><span class="badge" style="border-color:${CATCOLOR[s.category]}">${s.category}</span>
    <span class="badge">${s.type==='timeseries'?'time series':s.type==='yearindexed'?'price series':'table'}</span></div>`;
  main.appendChild(head);

  if(s.type==='raw'){ renderRaw(s,main); return; }

  // subtabs
  const tabs=el('div','subtabs');
  const defs = s.type==='timeseries'
    ? [['compare','📈 Compare over time'],['rank','📊 Latest-year ranking'],['table','▦ Data table']]
    : [['compare','📈 Compare over time'],['table','▦ Data table']];
  if(!defs.find(d=>d[0]===SUB)) SUB='compare';
  defs.forEach(([k,lab])=>{
    const b=el('button','subtab'+(k===SUB?' active':''),lab);
    b.onclick=()=>{SUB=k; selectSheet(name);};
    tabs.appendChild(b);
  });
  main.appendChild(tabs);
  const body=el('div'); main.appendChild(body);
  if(SUB==='compare') renderCompare(s,body);
  else if(SUB==='rank') renderRanking(s,body);
  else renderTable(s,body);
}
function escapeHtml(s){return String(s).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));}

/* ---------- entities helpers (unify timeseries & yearindexed) ---------- */
function seriesList(s){ return s.type==='yearindexed' ? s.series.map(x=>({name:x.name,values:x.values,agg:false})) : s.entities; }
function defaultSelection(s){
  const items=seriesList(s);
  if(s.type==='yearindexed') return items.slice(0,Math.min(6,items.length)).map(i=>i.name);
  // top countries by latest value, excluding aggregates
  const scored=items.filter(i=>!i.agg).map(i=>{const li=latestIdx(i.values);return {name:i.name,v:li>=0?Math.abs(i.values[li]):-1};});
  scored.sort((a,b)=>b.v-a.v);
  return scored.slice(0,6).map(i=>i.name);
}

/* ---------- COMPARE ---------- */
let CHART=null;
function renderCompare(s,root){
  const key=CUR;
  state[key]=state[key]||{};
  let st=state[key].compare;
  if(!st){ st={sel:defaultSelection(s), y0:s.years[0], y1:s.years[s.years.length-1]}; state[key].compare=st; }

  const wrap=el('div','controls');
  // year range
  const yr=el('div','ctl');
  yr.innerHTML=`<label>Years</label>`;
  const yrow=el('div'); yrow.style.cssText='display:flex;gap:6px;align-items:center';
  const y0=el('input'); y0.type='number'; y0.min=s.years[0]; y0.max=s.years[s.years.length-1]; y0.value=st.y0; y0.style.width='78px';
  const y1=el('input'); y1.type='number'; y1.min=s.years[0]; y1.max=s.years[s.years.length-1]; y1.value=st.y1; y1.style.width='78px';
  y0.onchange=()=>{st.y0=+y0.value; draw();};
  y1.onchange=()=>{st.y1=+y1.value; draw();};
  yrow.append(y0,el('span',null,'→'),y1); yr.appendChild(yrow);
  // log toggle + presets
  const opts=el('div','ctl');
  opts.innerHTML=`<label>Quick picks</label>`;
  const brow=el('div'); brow.style.cssText='display:flex;gap:6px;flex-wrap:wrap';
  const items=seriesList(s);
  function preset(label,fn){const b=el('button','btn',label);b.onclick=()=>{st.sel=fn();syncChecks();draw();};return b;}
  brow.appendChild(preset('Top 8',()=>{
    const sc=items.filter(i=>!i.agg).map(i=>{const li=latestIdx(i.values);return{n:i.name,v:li>=0?Math.abs(i.values[li]):-1};});
    sc.sort((a,b)=>b.v-a.v); return sc.slice(0,8).map(i=>i.n);
  }));
  if(s.type==='timeseries'){
    brow.appendChild(preset('Regions',()=>items.filter(i=>i.agg&&/^total /i.test(i.name)).map(i=>i.name)));
    brow.appendChild(preset('World',()=>items.filter(i=>/world/i.test(i.name)).map(i=>i.name)));
  }
  brow.appendChild(preset('Clear',()=>[]));
  opts.appendChild(brow);

  wrap.append(yr,opts);
  root.appendChild(wrap);

  // layout: picker + chart
  const grid=el('div'); grid.style.cssText='display:flex;gap:16px;flex-wrap:wrap;margin-top:14px;align-items:flex-start';
  const left=el('div','panel'); left.style.cssText='flex:0 0 260px;max-width:280px';
  left.innerHTML=`<div class="pickbar"><input type="text" id="entSearch" placeholder="Filter ${s.type==='yearindexed'?'series':'countries / regions'}…"></div>`;
  const picker=el('div','entpicker'); left.appendChild(picker);
  const right=el('div','panel'); right.style.cssText='flex:1;min-width:340px';
  const cw=el('div','chartwrap'); const cv=el('canvas'); cw.appendChild(cv); right.appendChild(cw);
  const dl=el('div'); dl.style.cssText='margin-top:10px;display:flex;gap:8px';
  const dlb=el('button','btn','⬇ Download CSV (selected)'); dl.appendChild(dlb); right.appendChild(dl);
  grid.append(left,right); root.appendChild(grid);

  function buildPicker(filter){
    picker.innerHTML='';
    filter=(filter||'').toLowerCase();
    items.forEach(i=>{
      if(filter&&!i.name.toLowerCase().includes(filter))return;
      const row=el('div','row'+(i.agg?' agg':''));
      const id='c_'+Math.random().toString(36).slice(2);
      const cb=el('input'); cb.type='checkbox'; cb.id=id; cb.checked=st.sel.includes(i.name);
      cb.onchange=()=>{ if(cb.checked){if(!st.sel.includes(i.name))st.sel.push(i.name);} else {st.sel=st.sel.filter(x=>x!==i.name);} draw(); };
      const lb=el('label',null,i.name); lb.htmlFor=id; lb.style.cursor='pointer';
      row.append(cb,lb); picker.appendChild(row);
    });
  }
  function syncChecks(){ buildPicker($('#entSearch').value); }
  buildPicker('');
  $('#entSearch').oninput=e=>buildPicker(e.target.value);

  function selData(){
    const i0=s.years.indexOf(st.y0), i1=s.years.indexOf(st.y1);
    const lo=Math.max(0,Math.min(i0,i1)), hi=Math.max(i0,i1);
    const yrs=s.years.slice(lo,hi+1);
    const chosen=items.filter(i=>st.sel.includes(i.name));
    return {yrs,lo,hi,chosen};
  }
  function draw(){
    const {yrs,lo,hi,chosen}=selData();
    if(CHART){CHART.destroy();CHART=null;}
    const ds=chosen.map((i,idx)=>({
      label:i.name, data:i.values.slice(lo,hi+1),
      borderColor:PALETTE[idx%PALETTE.length], backgroundColor:PALETTE[idx%PALETTE.length],
      borderWidth:2, pointRadius:yrs.length>40?0:2, pointHoverRadius:4, tension:.18, spanGaps:true
    }));
    const dark=document.documentElement.getAttribute('data-theme')==='dark';
    const grid=dark?'rgba(255,255,255,.07)':'rgba(0,0,0,.06)';
    const tick=dark?'#9bada6':'#5d6b66';
    CHART=new Chart(cv,{type:'line',data:{labels:yrs,datasets:ds},options:{
      responsive:true,maintainAspectRatio:false,interaction:{mode:'index',intersect:false},
      plugins:{legend:{position:'bottom',labels:{color:tick,boxWidth:12,font:{size:11}}},
        tooltip:{callbacks:{label:c=>`${c.dataset.label}: ${fmt(c.parsed.y)} ${s.unit||''}`}}},
      scales:{x:{grid:{color:grid},ticks:{color:tick,maxTicksLimit:14}},
        y:{grid:{color:grid},ticks:{color:tick},title:{display:!!s.unit,text:s.unit,color:tick}}}
    }});
  }
  dlb.onclick=()=>{
    const {yrs,lo,hi,chosen}=selData();
    const rows=[['Entity',...yrs]];
    chosen.forEach(i=>rows.push([i.name,...i.values.slice(lo,hi+1)]));
    csvDownload((CUR.replace(/[^a-z0-9]+/gi,'_'))+'_compare.csv',rows);
  };
  state[key]._redrawCompare=draw;
  draw();
}

/* ---------- RANKING ---------- */
function renderRanking(s,root){
  const key=CUR; state[key]=state[key]||{};
  let st=state[key].rank; if(!st){st={year:s.years[s.years.length-1],metric:'__year',topN:15,incAgg:false}; state[key].rank=st;}
  const wrap=el('div','controls');
  // year
  const yc=el('div','ctl'); yc.innerHTML='<label>Year</label>';
  const ysel=el('select'); s.years.slice().reverse().forEach(y=>{const o=el('option',null,y);o.value=y;ysel.appendChild(o);});
  ysel.value=st.year; ysel.onchange=()=>{st.year=+ysel.value;draw();}; yc.appendChild(ysel);
  // metric
  const mc=el('div','ctl'); mc.innerHTML='<label>Metric</label>';
  const msel=el('select');
  const mo=el('option',null,'Value for year'); mo.value='__year'; msel.appendChild(mo);
  (s.extraCols||[]).forEach(c=>{const o=el('option',null,c);o.value=c;msel.appendChild(o);});
  msel.value=st.metric; msel.onchange=()=>{st.metric=msel.value;draw();}; mc.appendChild(msel);
  // topN
  const tc=el('div','ctl'); tc.innerHTML='<label>Show</label>';
  const tsel=el('select'); [10,15,20,30,9999].forEach(n=>{const o=el('option',null,n>=9999?'All':'Top '+n);o.value=n;tsel.appendChild(o);});
  tsel.value=st.topN; tsel.onchange=()=>{st.topN=+tsel.value;draw();}; tc.appendChild(tsel);
  // agg toggle
  const ac=el('div','ctl'); ac.innerHTML='<label>Aggregates</label>';
  const ab=el('button','btn'+(st.incAgg?' primary':''),st.incAgg?'Including totals/regions':'Countries only');
  ab.onclick=()=>{st.incAgg=!st.incAgg; ab.className='btn'+(st.incAgg?' primary':''); ab.textContent=st.incAgg?'Including totals/regions':'Countries only'; draw();};
  ac.appendChild(ab);
  wrap.append(yc,mc,tc,ac); root.appendChild(wrap);

  const info=el('div','hint'); info.style.margin='10px 0'; root.appendChild(info);
  const p=el('div','panel'); const cw=el('div','rankwrap'); const cv=el('canvas'); cw.appendChild(cv); p.appendChild(cw); root.appendChild(p);
  let RCHART=null;
  function draw(){
    const yi=s.years.indexOf(st.year);
    let rows=s.entities.map(e=>{
      let v;
      if(st.metric==='__year') v=e.values[yi];
      else v=e.extra?e.extra[st.metric]:null;
      return {name:e.name,agg:!!e.agg,v};
    }).filter(r=>r.v!=null && !isNaN(r.v));
    if(!st.incAgg) rows=rows.filter(r=>!r.agg);
    rows.sort((a,b)=>b.v-a.v);
    const world=s.entities.find(e=>/^total world$/i.test(e.name));
    const wv=world?(st.metric==='__year'?world.values[yi]:(world.extra?world.extra[st.metric]:null)):null;
    const shown=rows.slice(0,st.topN);
    const pct = st.metric!=='__year' && isPctCol(st.metric);
    if(RCHART){RCHART.destroy();}
    const dark=document.documentElement.getAttribute('data-theme')==='dark';
    const grid=dark?'rgba(255,255,255,.07)':'rgba(0,0,0,.06)'; const tick=dark?'#9bada6':'#5d6b66';
    cw.style.height=Math.max(280, shown.length*24+60)+'px';
    RCHART=new Chart(cv,{type:'bar',data:{labels:shown.map(r=>r.name),datasets:[{
      data:shown.map(r=>pct?r.v*100:r.v),
      backgroundColor:shown.map((r,i)=>r.agg?'#9aa7a2':PALETTE[i%PALETTE.length]),
      borderRadius:3
    }]},options:{indexAxis:'y',responsive:true,maintainAspectRatio:false,
      plugins:{legend:{display:false},tooltip:{callbacks:{label:c=>{
        const base=pct?c.parsed.x.toFixed(1)+'%':fmt(c.parsed.x)+' '+(s.unit||'');
        if(!pct && wv) return base+'  ('+((c.parsed.x/wv)*100).toFixed(1)+'% of world)';
        return base;
      }}}},
      scales:{x:{grid:{color:grid},ticks:{color:tick,callback:v=>pct?v+'%':fmt(v)}},
        y:{grid:{display:false},ticks:{color:tick,font:{size:11},autoSkip:false}}}
    }});
    const mlabel = st.metric==='__year'?`${s.title||CUR} (${st.year})`:st.metric;
    let txt=`<b>${shown.length}</b> shown · metric: <b>${escapeHtml(st.metric==='__year'?(s.unit||'value')+' in '+st.year:st.metric)}</b>`;
    if(!pct && wv) txt+=` · World total: <b>${fmt(wv)} ${escapeHtml(s.unit||'')}</b>`;
    info.innerHTML=txt;
  }
  draw();
}

/* ---------- DATA TABLE (timeseries / yearindexed) ---------- */
function renderTable(s,root){
  const isTS=s.type==='timeseries';
  const items=seriesList(s);
  const bar=el('div'); bar.style.cssText='display:flex;gap:10px;flex-wrap:wrap;margin-bottom:10px;align-items:center';
  bar.innerHTML=`<input type="text" id="tfilter" placeholder="Filter rows…" style="padding:7px 10px;border:1px solid var(--line);border-radius:7px;background:var(--bg);color:var(--ink);min-width:200px">`;
  const dlb=el('button','btn','⬇ Download full CSV'); bar.appendChild(dlb);
  const hint=el('span','hint','Click a year column header to sort. Totals/regions in bold.');
  bar.appendChild(hint);
  root.appendChild(bar);

  let sortCol=null, sortDir=-1;
  const scroll=el('div','tablescroll'); root.appendChild(scroll);
  function render(filter){
    filter=(filter||'').toLowerCase();
    const tbl=el('table','data');
    const thead=el('thead'); const htr=el('tr');
    htr.appendChild(el('th','rowhead', isTS?'Country / region':'Year'));
    s.years.forEach((y,ci)=>{const th=el('th',null,y);th.onclick=()=>{sortCol=ci;sortDir=(sortCol===ci?-sortDir:-1);render($('#tfilter').value);};htr.appendChild(th);});
    (s.extraCols||[]).forEach((c,ci)=>{const th=el('th',null,c.replace('per annum ','').replace('Growth rate ','Δ '));th.onclick=()=>{sortCol='x'+ci;sortDir=(sortCol==='x'+ci?-sortDir:-1);render($('#tfilter').value);};htr.appendChild(th);});
    thead.appendChild(htr); tbl.appendChild(thead);
    const tb=el('tbody');
    let list=items.map((it,idx)=>({it,idx}));
    if(filter) list=list.filter(o=>o.it.name.toLowerCase().includes(filter));
    if(sortCol!==null){
      list.sort((a,b)=>{
        let va,vb;
        if(typeof sortCol==='string'){const xi=+sortCol.slice(1);const cn=s.extraCols[xi];
          va=a.it.extra?a.it.extra[cn]:null; vb=b.it.extra?b.it.extra[cn]:null;}
        else {va=a.it.values[sortCol]; vb=b.it.values[sortCol];}
        if(va==null)return 1; if(vb==null)return -1; return (va-vb)*sortDir;
      });
    }
    list.forEach(({it})=>{
      const tr=el('tr',it.agg?'agg':'');
      tr.appendChild(el('td',null,escapeHtml(it.name)));
      it.values.forEach(v=>{const td=el('td',v==null?'na':null,v==null?'–':fmt(v));tr.appendChild(td);});
      if(isTS)(s.extraCols||[]).forEach(cn=>{const v=it.extra?it.extra[cn]:null;tr.appendChild(el('td',v==null?'na':null,fmtCell(v,cn)));});
      tb.appendChild(tr);
      if(isTS && it.gapAfter && !filter && sortCol===null){const sp=el('tr','spacer');const td=el('td');td.colSpan=1+s.years.length+(s.extraCols||[]).length;sp.appendChild(td);tb.appendChild(sp);}
    });
    tbl.appendChild(tb);
    scroll.innerHTML=''; scroll.appendChild(tbl);
  }
  render('');
  $('#tfilter').oninput=e=>render(e.target.value);
  dlb.onclick=()=>{
    const head=['Entity',...s.years,...(s.extraCols||[])];
    const rows=[head];
    items.forEach(it=>rows.push([it.name,...it.values,...((s.extraCols||[]).map(cn=>it.extra?it.extra[cn]:null))]));
    csvDownload((CUR.replace(/[^a-z0-9]+/gi,'_'))+'.csv',rows);
  };
  if(s.notes&&s.notes.length){const n=el('div','note','<b>Notes:</b> '+s.notes.map(escapeHtml).join(' · '));root.appendChild(n);}
}

/* ---------- RAW grid ---------- */
function isNum(c){ return c!==''&&c!=null&&/^-?[\d,]*\.?\d+$/.test(String(c).trim()); }
function toNum(c){ return isNum(c)? parseFloat(String(c).replace(/,/g,'')) : null; }
function isTotalRow(lbl){ return /^(total|of which|oecd|non-oecd|world|other |rest of)/i.test(lbl||''); }

/* Interpret a custom grid as label-column + numeric columns so we can chart it. */
function parseRaw(grid){
  if(!grid||!grid.length) return null;
  const maxc=Math.max(...grid.map(r=>r.length));
  // first data row: col0 is non-numeric text and the row has >=1 numeric cell
  let firstData=-1;
  for(let r=1;r<grid.length;r++){
    const l=String(grid[r][0]||'').trim();
    const hasNum=grid[r].slice(1).some(isNum);
    if(l && !isNum(l) && hasNum){ firstData=r; break; }
  }
  if(firstData<0) return null;
  // header row = the row above firstData with the most non-empty cells
  let hdr=firstData-1, best=-1;
  for(let r=Math.max(0,firstData-4);r<firstData;r++){
    const cnt=(grid[r]||[]).filter(c=>String(c||'').trim()).length;
    if(cnt>best){best=cnt;hdr=r;}
  }
  // column labels (carry a block marker from rows above to disambiguate repeats, e.g. 2024/2025)
  const cols=[];
  for(let c=1;c<maxc;c++){
    let lab=String((grid[hdr]||[])[c]||'').trim();
    let marker='';
    for(let r=0;r<hdr;r++){ const up=String((grid[r]||[])[c]||'').trim(); if(up) marker=up; }
    const full=(marker && marker!==lab ? marker+' · ' : '')+ (lab||('Col '+c));
    // numeric coverage
    let n=0; for(let r=firstData;r<grid.length;r++){ if(isNum((grid[r]||[])[c])) n++; }
    cols.push({c, label:full, numeric:n>=2});
  }
  const rows=[];
  for(let r=firstData;r<grid.length;r++){
    const lbl=String(grid[r][0]||'').trim();
    if(!lbl && !grid[r].slice(1).some(x=>String(x||'').trim())) continue; // blank
    rows.push({label:lbl, cells:grid[r], tot:isTotalRow(lbl)});
  }
  const numCols=cols.filter(c=>c.numeric);
  return {hdr, firstData, cols, numCols, rows};
}

let RAWCHART=null;
function renderRaw(s,main){
  const P=parseRaw(s.grid);
  const chartable = P && P.numCols.length>=1 && P.rows.length>=2;
  // sub-tabs
  let sub = RAW_SUB || (chartable?'chart':'table');
  if(!chartable) sub='table';
  const tabs=el('div','subtabs');
  const defs = chartable ? [['chart','📊 Chart'],['table','▦ Table']] : [['table','▦ Table']];
  defs.forEach(([k,lab])=>{
    const b=el('button','subtab'+(k===sub?' active':''),lab);
    b.onclick=()=>{RAW_SUB=k; selectSheet(CUR);}; tabs.appendChild(b);
  });
  main.appendChild(tabs);
  const body=el('div'); main.appendChild(body);

  if(sub==='chart' && chartable){
    const st=(state['_raw_'+CUR]=state['_raw_'+CUR]||{});
    // default column: prefer one containing "Total" then latest year, else last numeric
    if(st.col===undefined){
      const tcol=P.numCols.find(c=>/total/i.test(c.label));
      st.col = (tcol?tcol.c:P.numCols[P.numCols.length-1].c);
      st.topN=15; st.incTot=false;
    }
    const ctr=el('div','controls');
    const cc=el('div','ctl'); cc.innerHTML='<label>Column</label>';
    const csel=el('select'); P.numCols.forEach(c=>{const o=el('option',null,escapeHtml(c.label));o.value=c.c;csel.appendChild(o);});
    csel.value=st.col; csel.onchange=()=>{st.col=+csel.value;draw();}; cc.appendChild(csel);
    const tc=el('div','ctl'); tc.innerHTML='<label>Show</label>';
    const tsel=el('select'); [10,15,20,30,9999].forEach(n=>{const o=el('option',null,n>=9999?'All':'Top '+n);o.value=n;tsel.appendChild(o);}); tsel.value=st.topN;
    tsel.onchange=()=>{st.topN=+tsel.value;draw();}; tc.appendChild(tsel);
    const ac=el('div','ctl'); ac.innerHTML='<label>Totals / regions</label>';
    const ab=el('button','btn'+(st.incTot?' primary':''),st.incTot?'Included':'Excluded');
    ab.onclick=()=>{st.incTot=!st.incTot;ab.className='btn'+(st.incTot?' primary':'');ab.textContent=st.incTot?'Included':'Excluded';draw();}; ac.appendChild(ab);
    ctr.append(cc,tc,ac); body.appendChild(ctr);
    const info=el('div','hint'); info.style.margin='10px 0'; body.appendChild(info);
    const p=el('div','panel'); const cw=el('div','rankwrap'); const cv=el('canvas'); cw.appendChild(cv); p.appendChild(cw); body.appendChild(p);
    function draw(){
      let rows=P.rows.map(r=>({label:r.label, v:toNum(r.cells[st.col]), tot:r.tot})).filter(r=>r.v!=null);
      if(!st.incTot) rows=rows.filter(r=>!r.tot);
      rows.sort((a,b)=>b.v-a.v);
      const shown=rows.slice(0,st.topN);
      if(RAWCHART) RAWCHART.destroy();
      const dark=document.documentElement.getAttribute('data-theme')==='dark';
      const grid=dark?'rgba(255,255,255,.07)':'rgba(0,0,0,.06)'; const tick=dark?'#9bada6':'#5d6b66';
      cw.style.height=Math.max(260, shown.length*24+50)+'px';
      const colLabel=(P.numCols.find(c=>c.c===st.col)||{}).label||'';
      RAWCHART=new Chart(cv,{type:'bar',data:{labels:shown.map(r=>r.label),datasets:[{
        data:shown.map(r=>r.v), backgroundColor:shown.map((r,i)=>r.tot?'#9aa7a2':PALETTE[i%PALETTE.length]), borderRadius:3}]},
        options:{indexAxis:'y',responsive:true,maintainAspectRatio:false,plugins:{legend:{display:false},
          tooltip:{callbacks:{label:c=>`${fmt(c.parsed.x)} ${s.unit||''}`}}},
          scales:{x:{grid:{color:grid},ticks:{color:tick,callback:v=>fmt(v)}},y:{grid:{display:false},ticks:{color:tick,font:{size:11},autoSkip:false}}}}});
      info.innerHTML=`Charting column <b>${escapeHtml(colLabel)}</b>${s.unit?' ('+escapeHtml(s.unit)+')':''} · ${shown.length} rows`;
    }
    draw();
  } else {
    const note=el('div','hint'); note.style.margin='2px 0 10px';
    note.innerHTML='Custom layout (trade matrix, fuel breakdown, or reference table) shown faithfully as in the workbook.';
    body.appendChild(note);
    const dlb=el('button','btn','⬇ Download CSV'); dlb.style.marginBottom='10px'; body.appendChild(dlb);
    const scroll=el('div','tablescroll'); const tbl=el('table','rawtbl');
    const hdrIdx = P ? P.hdr : 0;
    (s.grid||[]).forEach((row,ri)=>{
      const isBlank=!row.some(c=>String(c||'').trim());
      const isHead = ri===hdrIdx;
      const tr=el('tr', isBlank?'blank':((P&&ri>hdrIdx&&isTotalRow(String(row[0]||'')))?'tot':null));
      row.forEach((c,ci)=>{
        const tag = isHead?'th':'td';
        const cls=[]; if(ci===0)cls.push('rh'); if(isNum(c)&&!isHead)cls.push('num');
        const cell=el(tag,cls.join(' ')||null,escapeHtml(c==null?'':c));
        if(ci===0 && c && String(c).length>36) cell.title=String(c);
        tr.appendChild(cell);
      });
      tbl.appendChild(tr);
    });
    scroll.appendChild(tbl); body.appendChild(scroll);
    dlb.onclick=()=>csvDownload((CUR.replace(/[^a-z0-9]+/gi,'_'))+'.csv', s.grid);
  }
  if(s.notes&&s.notes.length){const n=el('div','note','<b>Notes:</b> '+s.notes.map(escapeHtml).join(' · '));main.appendChild(n);}
}

/* ---------- COUNTRY PROFILE ---------- */
const PROFILE = DB.profile || {regions:[],countries:[]};
const PROF_LABEL = {};
PROFILE.countries.concat(PROFILE.regions).forEach(it=>PROF_LABEL[it.value]=it.label);
let PROF={ent:null};
function renderProfile(){
  const main=$('#main'); main.innerHTML='';
  if(!PROF.ent) PROF.ent = PROF_LABEL['US'] ? 'US' : (PROFILE.countries[0]||PROFILE.regions[0]||{}).value;
  const head=el('div','profhead');
  const c=el('div','ctl'); c.innerHTML='<label>Country / region</label>';
  const sel=el('select'); sel.style.minWidth='260px';
  function addGroup(label,items){
    if(!items||!items.length)return;
    const og=document.createElement('optgroup'); og.label=label;
    items.forEach(it=>{const o=el('option',null,escapeHtml(it.label)); o.value=it.value; og.appendChild(o);});
    sel.appendChild(og);
  }
  addGroup('Countries', PROFILE.countries);
  addGroup('Regions & groups', PROFILE.regions);
  sel.value=PROF.ent; sel.onchange=()=>{PROF.ent=sel.value;renderProfile();}; c.appendChild(sel);
  head.appendChild(c);
  const disp=PROF_LABEL[PROF.ent]||PROF.ent;
  const h=el('div'); h.innerHTML=`<h1 style="margin:0">${escapeHtml(disp)}</h1><div class="hint">Latest available value across every time-series table that includes this entity. Click any card to open its full chart.</div>`;
  head.appendChild(h);
  main.appendChild(head);

  CATS.forEach(cat=>{
    const cards=[];
    cat.sheets.forEach(name=>{
      const s=SHEETS[name]; if(s.type!=='timeseries')return;
      const e=s.entities.find(x=>x.name===PROF.ent); if(!e)return;
      const li=latestIdx(e.values); if(li<0)return;
      cards.push({name,s,e,li});
    });
    if(!cards.length)return;
    const sec=el('div'); sec.style.margin='6px 0 4px';
    sec.innerHTML=`<div class="cathead" style="padding:10px 0 6px"><span class="catdot" style="background:${CATCOLOR[cat.name]}"></span><span>${cat.name}</span></div>`;
    main.appendChild(sec);
    const grid=el('div','cards');
    cards.forEach(({name,s,e,li})=>{
      const card=el('div','card');
      const val=e.values[li]; const yr=s.years[li];
      // delta vs prior available
      let prev=null; for(let i=li-1;i>=0;i--){if(e.values[i]!=null){prev=e.values[i];break;}}
      let deltaHtml='';
      if(prev!=null && prev!==0){const d=(val-prev)/Math.abs(prev)*100; deltaHtml=`<div class="delta ${d>=0?'up':'down'}">${d>=0?'▲':'▼'} ${Math.abs(d).toFixed(1)}% vs prior yr</div>`;}
      card.innerHTML=`<div class="cat">${escapeHtml(name)}</div>
        <div class="nm">${escapeHtml(s.unit||'')}</div>
        <div class="big">${fmt(val)}</div><div class="unit">${yr}</div>
        ${deltaHtml}<div class="spark"><canvas></canvas></div>`;
      card.onclick=()=>{ MODE='table'; setModeButtons('table'); SUB='compare';
        selectSheet(name);
        // preselect this entity
        state[name]=state[name]||{}; state[name].compare={sel:[PROF.ent], y0:s.years[0], y1:s.years[s.years.length-1]};
        selectSheet(name);
      };
      grid.appendChild(card);
      setTimeout(()=>{ // sparkline
        const cv=card.querySelector('canvas');
        const vals=e.values, yrs=s.years;
        new Chart(cv,{type:'line',data:{labels:yrs,datasets:[{data:vals,borderColor:CATCOLOR[cat.name]||PALETTE[0],borderWidth:1.6,pointRadius:0,tension:.2,spanGaps:true,fill:false}]},
          options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{display:false},tooltip:{enabled:false}},scales:{x:{display:false},y:{display:false}},elements:{line:{borderCapStyle:'round'}}}});
      },0);
    });
    main.appendChild(grid);
  });
}
function setModeButtons(m){document.querySelectorAll('.modebtn').forEach(b=>b.classList.toggle('active',b.dataset.mode===m));MODE=m;}

/* ---------- theme ---------- */
function applyTheme(t){document.documentElement.setAttribute('data-theme',t); try{localStorage.setItem('ei-theme',t);}catch(e){}
  if(CUR && MODE==='table') { if(SUB==='compare' && state[CUR]&&state[CUR]._redrawCompare) state[CUR]._redrawCompare(); }
}
$('#themeBtn').onclick=()=>applyTheme(document.documentElement.getAttribute('data-theme')==='dark'?'light':'dark');
(function(){let t='light';try{t=localStorage.getItem('ei-theme')||'light';}catch(e){} applyTheme(t);})();

/* ---------- wire up ---------- */
document.querySelectorAll('.modebtn').forEach(b=>b.onclick=()=>setMode(b.dataset.mode));
$('#brandHome').onclick=()=>renderHome();
$('#globalSearch').oninput=e=>buildSidebar(e.target.value);
$('#menuToggle').onclick=()=>document.body.classList.toggle('navopen');
$('#sidebar').addEventListener('click',()=>{if(window.innerWidth<=820)document.body.classList.remove('navopen');});

buildSidebar('');
renderHome();
</script>
</body>
</html>
"""

# inject data: replace the placeholder script content
inject = "window.__EIDATA__ = " + data_str + ";"
HTML = HTML.replace("/*__DATA__*/", inject)
# remove the stray placeholder line "const RAW =" (artifact) -> keep harmless? Replace it.
HTML = HTML.replace("<script>const RAW = </script>\n", "")

with open(OUT, "w") as f:
    f.write(HTML)

import os
print("Wrote", OUT, f"({os.path.getsize(OUT)/1e6:.2f} MB)")
