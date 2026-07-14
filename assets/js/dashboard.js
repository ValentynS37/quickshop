// BADS Command View — static demo data only
(function(){
  const events=[
    {id:'BADS-2026-001',title:'Satellite image verification request',source:'Satellite / EO',score:86,risk:'medium',type:'image',time:'2026-07-11 08:15',loc:'Kyiv region',flags:['cloud cover','metadata partial'],summary:'AI analysis found infrastructure change signals. Source is consistent but requires human review due to partial metadata.'},
    {id:'BADS-2026-002',title:'OSINT report duplicate check',source:'OSINT text',score:72,risk:'medium',type:'text',time:'2026-07-11 09:02',loc:'Open source',flags:['possible duplicate','source age'],summary:'Message appears similar to earlier report. System recommends checking original source chain before escalation.'},
    {id:'BADS-2026-003',title:'Critical infrastructure sensor anomaly',source:'Telemetry',score:91,risk:'low',type:'telemetry',time:'2026-07-11 09:48',loc:'Energy asset',flags:['signal spike'],summary:'Sensor event is consistent with normal maintenance pattern. Low anomaly severity after source reliability check.'},
    {id:'BADS-2026-004',title:'Image provenance review',source:'User upload',score:64,risk:'high',type:'image',time:'2026-07-11 10:26',loc:'Unknown',flags:['missing GPS','low source reliability','needs review'],summary:'Uploaded image lacks provenance data. Similar visual pattern found in older public material; human review required.'}
  ];
  const $=s=>document.querySelector(s);
  function render(list=events){
    const box=$('#eventList'); if(!box) return;
    box.innerHTML=list.map(e=>`<article class="event" data-id="${e.id}"><div><b>${e.title}</b><span>${e.id} · ${e.source} · ${e.time}</span></div><strong class="score ${e.risk}">${e.score}</strong></article>`).join('');
    document.querySelectorAll('.event').forEach(el=>el.addEventListener('click',()=>openEvent(events.find(e=>e.id===el.dataset.id))));
  }
  function openEvent(e){
    if(!e) return;
    $('#eTitle').textContent=e.title; $('#eId').textContent=e.id; $('#eScore').textContent=e.score; $('#eSource').textContent=e.source; $('#eTime').textContent=e.time; $('#eLoc').textContent=e.loc; $('#eSummary').textContent=e.summary; $('#eFlags').innerHTML=e.flags.map(f=>`<span>${f}</span>`).join('');
    document.body.classList.add('modal-open');
  }
  document.addEventListener('DOMContentLoaded',()=>{
    render();
    document.querySelectorAll('[data-close]').forEach(x=>x.addEventListener('click',()=>document.body.classList.remove('modal-open')));
    const filter=$('#filter'); if(filter) filter.addEventListener('input',()=>{const q=filter.value.toLowerCase();render(events.filter(e=>JSON.stringify(e).toLowerCase().includes(q)));});
    const print=$('#printReport'); if(print) print.addEventListener('click',()=>window.print());
  });
})();