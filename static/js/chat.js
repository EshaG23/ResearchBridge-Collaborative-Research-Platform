(() => {
 const app=document.getElementById('chat-app');if(!app)return;
 const form=document.getElementById('chat-compose'),timeline=document.getElementById('chat-messages'),scroll=document.getElementById('chat-scroll');
 const text=document.getElementById('chat-text'),files=document.getElementById('chat-files'),key=document.getElementById('send-key'),error=document.getElementById('chat-error'),connection=document.getElementById('chat-connection');
 const older=document.getElementById('load-older'),newButton=document.getElementById('new-messages'),sendButton=document.getElementById('chat-send');
 let cursor=Number(app.dataset.latest),oldest=Number(app.dataset.oldest),stopped=false,sending=false,fetching=false,timer,recording=null,voice=null,stream=null,recordTimer,pending=null;
 let csrf=form.querySelector('[name=csrfmiddlewaretoken]').value;
 const uuid=()=>crypto.randomUUID();key.value=uuid();
 const showError=msg=>{error.textContent=msg;error.hidden=false;};
 let lastRead=0,reading=false;
 const nearBottom=()=>scroll.scrollHeight-scroll.scrollTop-scroll.clientHeight<100;
 const bottom=()=>{scroll.scrollTop=scroll.scrollHeight;newButton.hidden=true;};
 function revoke(message='Your session or community access changed. Reload or sign in again.'){stopped=true;clearTimeout(timer);clearTimeout(recordTimer);if(recording&&recording.state!=='inactive')recording.stop();if(stream)stream.getTracks().forEach(t=>t.stop());timeline.replaceChildren();form.hidden=true;connection.textContent='Access unavailable';showError(message);newButton.hidden=true;older.hidden=true;}
 async function responseJSON(response){
   if(response.redirected||[401,404].includes(response.status)){revoke();throw new Error('Please reload and sign in with an authorised account.');}
   const type=response.headers.get('content-type')||'';
   if(!type.includes('application/json'))throw new Error('The server could not handle this request. Your draft is kept; please retry.');
   const data=await response.json();if(data.code==='account_changed'||(data.user_id&&data.user_id!==app.dataset.user)){const message='The signed-in account changed in another tab. Reload this chat to use the current account. For mentor and student testing together, use separate browser profiles or different browsers.';revoke(message);throw new Error(message);}if(data.csrf_token)csrf=data.csrf_token;if(!response.ok){const failure=new Error(data.error||'Request failed. Please retry.');failure.definite=response.status===400;throw failure;}return data;
 }
 // Recover a rotated CSRF token once; keep the page's original account identity.
 async function timedFetch(url,options={}){
   const controller=new AbortController(),timeout=setTimeout(()=>controller.abort(),20000);
   try{return await fetch(url,{...options,signal:controller.signal});}
   catch(e){if(e.name==='AbortError')throw new Error('The connection timed out. Please retry.');throw e;}
   finally{clearTimeout(timeout);}
 }
 async function postJSON(url,data){
   const submit=()=>{data.set('csrfmiddlewaretoken',csrf);return timedFetch(url,{method:'POST',body:data,headers:{'X-CSRFToken':csrf,'X-Chat-User':app.dataset.user}});};
   let response=await submit();
   if(response.status===403){
     await responseJSON(await timedFetch(app.dataset.feed+'?after='+cursor,{cache:'no-store'}));
     if(stopped)throw new Error('Reload the chat before continuing.');
     response=await submit();
     if(response.status===403)throw new Error('Security check could not refresh. Reload this page and try again.');
   }
   return responseJSON(response);
 }
 function insert(item){
   if(timeline.querySelector(`[data-message="${item.id}"]`))return;
   const t=document.createElement('template');t.innerHTML=item.html;const node=t.content.firstElementChild;
   const next=Array.from(timeline.children).find(el=>Number(el.dataset.message)>item.id);timeline.insertBefore(node,next||null);
   if(!oldest||item.id<oldest)oldest=item.id;document.getElementById('chat-empty').hidden=true;
 }
 async function markRead(){
   if(stopped||reading||document.visibilityState!=='visible'||!nearBottom())return;
   const ids=Array.from(timeline.children).map(e=>Number(e.dataset.message)||0),last=Math.max(0,...ids);
   if(last<=lastRead)return;reading=true;
   try{const data=new FormData();data.set('last',last);await postJSON(app.dataset.read,data);lastRead=last;}catch(e){}finally{reading=false;}
 }
 scroll.addEventListener('scroll',markRead);document.addEventListener('visibilitychange',markRead);
 async function poll(){
   if(stopped||fetching)return;fetching=true;
   try{
     const ids=Array.from(timeline.querySelectorAll('[data-poll]')).slice(-100).map(e=>e.dataset.poll).join(',');
     const data=await responseJSON(await timedFetch(app.dataset.feed+'?after='+cursor+'&polls='+ids,{cache:'no-store'}));const follow=nearBottom();
     data.messages.forEach(m=>{insert(m);cursor=Math.max(cursor,m.id);});
     Object.entries(data.polls).forEach(([id,html])=>{const node=timeline.querySelector(`[data-poll="${id}"]`);if(node&&!node.contains(document.activeElement))node.outerHTML=html;});
     if(data.messages.length){if(follow)bottom();else newButton.hidden=false;}
     connection.textContent='Connected · updates every 3 seconds';markRead();
     timer=setTimeout(poll,data.messages.length===40?100:3000);
   }catch(e){if(!stopped){connection.textContent='Reconnecting…';timer=setTimeout(poll,6000);}}
   finally{fetching=false;}
 }
 older.addEventListener('click',async()=>{older.disabled=true;const height=scroll.scrollHeight;
   try{const data=await responseJSON(await timedFetch(app.dataset.feed+'?before='+oldest,{cache:'no-store'}));data.messages.forEach(insert);older.hidden=!data.older;scroll.scrollTop+=scroll.scrollHeight-height;}
   catch(e){showError(e.message);}finally{older.disabled=false;}
 });
 newButton.addEventListener('click',bottom);
 document.addEventListener('click',e=>{const button=e.target.closest('[data-reply]');if(!button||pending||sending)return;document.getElementById('reply-id').value=button.dataset.reply;document.getElementById('reply-name').textContent=button.dataset.name;document.getElementById('reply-preview').hidden=false;text.focus();});
 document.getElementById('cancel-reply').addEventListener('click',()=>{document.getElementById('reply-id').value='';document.getElementById('reply-preview').hidden=true;});
 document.getElementById('toggle-poll').addEventListener('click',()=>{const panel=document.getElementById('poll-compose');panel.hidden=!panel.hidden;if(panel.hidden){document.getElementById('poll-question').value='';document.getElementById('poll-options').value='';}});
 const removeVoice=document.getElementById('remove-voice');removeVoice.addEventListener('click',()=>{voice=null;document.getElementById('record-status').textContent='';selected();});
 const selected=()=>{removeVoice.hidden=!voice;document.getElementById('file-selection').textContent=[...Array.from(files.files).map(f=>f.name),...(voice?[voice.name]:[])].join(' · ')||'Up to 5 attachments · 25 MB each · 60 MB per message';};files.addEventListener('change',selected);
 form.addEventListener('submit',async e=>{e.preventDefault();if(sending||recording||stopped)return;
   const uploads=[...files.files,...(voice?[voice]:[])];if(uploads.length>5||uploads.some(f=>f.size>25*1024*1024)||uploads.reduce((s,f)=>s+f.size,0)>60*1024*1024){showError('Send up to 5 files, 25 MB each and 60 MB total.');return;}
   if(!text.value.trim()&&!uploads.length&&!document.getElementById('poll-question').value.trim()){showError('Write a message, attach a file or add a poll.');return;}
   sending=true;sendButton.disabled=true;sendButton.textContent='Sending…';error.hidden=true;
   const data=pending||new FormData(form);if(!pending){data.delete('files');uploads.forEach(f=>data.append('files',f));}pending=data;
   // Freeze the composer while its immutable send key is in flight.
   Array.from(form.elements).forEach(el=>el.disabled=true);
   try{const result=await postJSON(form.action,data);insert(result);pending=null;form.reset();key.value=uuid();voice=null;selected();document.getElementById('record-status').textContent='';document.getElementById('reply-preview').hidden=true;document.getElementById('poll-compose').hidden=true;bottom();}
   catch(e){if(e.definite)pending=null;showError(e.message+(pending?' Retry sends the same saved draft safely.':' Correct the draft and send again.'));}
   finally{sending=false;Array.from(form.elements).forEach(el=>el.disabled=!!pending);sendButton.disabled=false;sendButton.textContent=pending?'Retry message':'Send message';if(stopped)form.hidden=true;}
 });
 text.addEventListener('keydown',e=>{if(e.key==='Enter'&&!e.shiftKey&&!e.isComposing){e.preventDefault();form.requestSubmit();}});
 timeline.addEventListener('submit',async e=>{const vote=e.target.closest('.poll-form');if(!vote)return;e.preventDefault();const button=e.submitter;if(!button)return;
   const data=new FormData(vote);data.set(button.name,button.value);vote.querySelectorAll('button').forEach(b=>b.disabled=true);
   try{const result=await postJSON(vote.action,data);vote.closest('[data-poll]').outerHTML=result.poll;}
   catch(e){showError(e.message);vote.querySelectorAll('button').forEach(b=>b.disabled=false);}
 });
 const recordButton=document.getElementById('record-audio'),recordStatus=document.getElementById('record-status');
 if(!navigator.mediaDevices?.getUserMedia||!window.MediaRecorder){recordButton.hidden=true;}
 recordButton.addEventListener('click',async()=>{
   if(recording){recording.stop();return;}
   recordButton.disabled=true;
   try{
     stream=await navigator.mediaDevices.getUserMedia({audio:true});if(stopped){stream.getTracks().forEach(t=>t.stop());stream=null;return;}
     const mime=['audio/webm;codecs=opus','audio/webm','audio/mp4'].find(t=>MediaRecorder.isTypeSupported(t));if(!mime)throw new Error('Voice recording is unsupported here. Attach an audio file instead.');
     const recorder=new MediaRecorder(stream,{mimeType:mime});recording=recorder;const chunks=[];
     recorder.ondataavailable=e=>{if(e.data.size)chunks.push(e.data);};
     recorder.onstop=()=>{clearTimeout(recordTimer);stream.getTracks().forEach(t=>t.stop());stream=null;recording=null;if(stopped)return;voice=new File(chunks,mime.includes('mp4')?'voice-note.m4a':'voice-note.webm',{type:mime.split(';')[0]});recordButton.textContent='Record voice note';recordStatus.textContent='Voice note attached. Click Send to share it, or record again to replace it.';selected();};
     recorder.onerror=()=>{showError('Recording failed. Attach an audio file instead.');if(recorder.state!=='inactive')recorder.stop();};
     recorder.start();recordButton.disabled=false;recordButton.textContent='Stop recording';recordStatus.textContent='Recording… stops automatically after 2 minutes.';recordTimer=setTimeout(()=>{if(recorder.state!=='inactive')recorder.stop();},120000);
   }catch(e){if(stream)stream.getTracks().forEach(t=>t.stop());stream=null;recordButton.disabled=false;showError(e.message||'Microphone permission was denied. You can attach an audio file.');}
 });
 window.addEventListener('beforeunload',()=>{stopped=true;clearTimeout(timer);clearTimeout(recordTimer);if(stream)stream.getTracks().forEach(t=>t.stop());});
 bottom();poll();
})();
