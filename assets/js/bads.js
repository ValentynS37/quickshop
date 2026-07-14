// BADS TrustOS v1 — static interactions, no dependencies
(function(){
  const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  document.addEventListener('DOMContentLoaded',()=>{
    const items=[...document.querySelectorAll('.reveal')];
    if(!('IntersectionObserver' in window)||reduce){items.forEach(x=>x.classList.add('visible'));}
    else{const io=new IntersectionObserver(es=>es.forEach(e=>{if(e.isIntersecting){e.target.classList.add('visible');io.unobserve(e.target);}}),{threshold:.13});items.forEach(x=>io.observe(x));}
    document.querySelectorAll('a[href^="#"]').forEach(a=>a.addEventListener('click',e=>{const t=document.querySelector(a.getAttribute('href'));if(t){e.preventDefault();t.scrollIntoView({behavior:reduce?'auto':'smooth'});}}));
    document.querySelectorAll('[data-open-demo]').forEach(btn=>btn.addEventListener('click',()=>{location.href='dashboard.html';}));
  });
})();