(() => {
  const pad=document.getElementById('signature-pad');
  const review=document.getElementById('signature-review');
  function paint(canvas,strokes) {
    const ctx=canvas.getContext('2d');ctx.clearRect(0,0,canvas.width,canvas.height);
    ctx.strokeStyle='#183e4c';ctx.lineWidth=2.5;ctx.lineCap='round';ctx.lineJoin='round';
    strokes.forEach(stroke=>{ctx.beginPath();stroke.forEach(([x,y],i)=>i?ctx.lineTo(x*canvas.width,y*canvas.height):ctx.moveTo(x*canvas.width,y*canvas.height));ctx.stroke();});
  }
  if(review)paint(review,JSON.parse(document.getElementById('signature-preview').textContent));
  if(!pad)return;
  const hidden=document.getElementById('id_signature');let strokes=[];let active=null;
  try{strokes=JSON.parse(hidden.value||'[]');}catch(e){strokes=[];}
  const save=()=>{hidden.value=JSON.stringify(strokes);paint(pad,strokes);const status=document.getElementById('signature-status');if(status)status.textContent=strokes.flat().length>=5?'Signature captured. Review it before submitting.':'No signature drawn yet.';};
  const point=e=>{const r=pad.getBoundingClientRect();return [Math.max(0,Math.min(1,(e.clientX-r.left)/r.width)),Math.max(0,Math.min(1,(e.clientY-r.top)/r.height))];};
  pad.addEventListener('pointerdown',e=>{e.preventDefault();if(strokes.length>=100)return;pad.setPointerCapture(e.pointerId);active=[point(e)];strokes.push(active);save();});
  pad.addEventListener('pointermove',e=>{if(!active)return;e.preventDefault();if(strokes.reduce((n,s)=>n+s.length,0)>=5000)return;active.push(point(e));save();});
  for(const event of ['pointerup','pointercancel','lostpointercapture'])pad.addEventListener(event,()=>{active=null;save();});
  document.getElementById('clear-signature').addEventListener('click',()=>{strokes=[];active=null;save();});
  const method=document.getElementById('id_method');
  const toggle=()=>{for(const [value,id] of [['drawn','draw-option'],['typed','typed-option'],['physical','physical-option']])document.getElementById(id).hidden=method.value!==value;document.getElementById('sign-submit').textContent=method.value==='physical'?'Submit signed copy for verification':'Review signature';};
  method.addEventListener('change',toggle);toggle();save();
})();
