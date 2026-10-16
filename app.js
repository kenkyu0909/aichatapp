"use strict";
/* Windows localhost UI. No private conversation data is kept in browser storage. */
(() => {
const $ = id => document.getElementById(id);
const state = { matches:[],selectedId:null,messages:[],loadingConversation:false,conversationLoadFailed:false,profile:{content:"",avoid:""},status:null,tone:"自動",busy:false };
let timer;
let contactSelectionEpoch=0;
let conversationRevision=0;
const messageDrafts=new Map();
const mutatingContacts=new Set();
const contactMutationCounts=new Map();
const pendingMessageSubmissions=new Set();
const optionalUserQuestionHistory=new Map();
let generationRequestSequence=0;
const generationRequestTokens=new WeakMap();
const generationAreaTokens=new WeakMap();
function node(tag,cls,txt) {
  const e=document.createElement(tag);
  if(cls)e.className=cls;
  if(txt!==undefined)e.textContent=txt;
  return e;
}
function notice(t){
  $("toast").textContent=t;$("toast").hidden=false;
  clearTimeout(timer);timer=setTimeout(()=>{$("toast").hidden=true;},4000);
}
function beginContactMutation(contactId){
  const count=(contactMutationCounts.get(contactId)||0)+1;
  contactMutationCounts.set(contactId,count);mutatingContacts.add(contactId);
}
function endContactMutation(contactId){
  const count=(contactMutationCounts.get(contactId)||1)-1;
  if(count>0)contactMutationCounts.set(contactId,count);
  else{contactMutationCounts.delete(contactId);mutatingContacts.delete(contactId);}
}
function errorText(result){
  const messages={
    invalid_response:"生成した候補が返信ルールに合わなかったため表示できませんでした。もう一度お試しください。",
    request_attempt_limit:"生成の安全試行上限に達したため停止しました。時間をおいて再度お試しください。",
    all_models_rate_limited:"Geminiの利用制限に達しました。時間をおいて再度お試しください。",
    api_permission_denied:"Geminiの認証または利用権限を確認してください。",
    model_unavailable:"指定モデルを利用できません。モデル設定を確認してください。",
    gemini_connection_error:"Geminiとの通信に失敗しました。接続状態を確認して再度お試しください。"
  };
  if(messages[result?.error_code])return messages[result.error_code];
  if(typeof result?.detail==="string")return result.detail;
  return "入力または通信に失敗しました";
}
async function api(path, options={}) {
  let response;
  try {response=await fetch("/api"+path,options);}
  catch {throw Error("ローカルサーバーと通信できません。start.bat が起動中か確認してください。");}
  let body;
  try {body=await response.json();}
  catch {throw Error("サーバーの応答を読み取れませんでした");}
  if(!response.ok)throw Error(errorText(body));
  return body;
}
function json(method,payload){
  return {method,headers:{"Content-Type":"application/json"},body:JSON.stringify(payload)};
}
async function safe(fn) {
  try {await fn();}
  catch(e){notice(e.message || "操作に失敗しました");}
}
function current(){return state.matches.find(c=>c.id===state.selectedId)||null;}
function photoAvatar(c,large=false){
  const av=node("span","avatar"+(large?" big":""));
  if(c.photo){
    const img=node("img");img.src="/api/matches/"+c.id+"/photo";img.alt="";
    av.append(img);
  }else{
    const colors=["#06c59a","#8c99bd","#bb8baf","#e3a18c","#74a8cb"];
    av.style.background=colors[c.id%colors.length];av.textContent=(c.name||"?").charAt(0);
  }
  return av;
}
async function loadMatches(prefer){
  state.matches=await api("/matches");
  let target=prefer!==undefined?prefer:state.selectedId;
  if(!state.matches.some(c=>c.id===target))target=state.matches[0]?.id||null;
  await selectContact(target,false);
  renderContacts();
}
function renderContacts(){
  const list=$("contacts");list.replaceChildren();
  const term=$("search").value.trim().toLocaleLowerCase();
  const filtered=state.matches.filter(c=>c.name.toLocaleLowerCase().includes(term));
  if(!filtered.length)list.append(node("p","empty-chat",state.matches.length?"一致する相手がいません":"左上の＋から相手を登録してください"));
  filtered.forEach(c=>{
    const btn=node("button","contact-item"+(c.id===state.selectedId?" active":""));
    btn.type="button";btn.append(photoAvatar(c));
    const info=node("span","contact-item-details");
    const head=node("span","contact-item-head");
    head.append(node("strong","",c.name));
    head.append(node("span","count-pill",(c.message_count||0)+"通"));
    info.append(head,node("span","contact-preview",c.last_message||c.description||"会話はまだありません"));
    btn.append(info);
    btn.addEventListener("click",()=>safe(()=>selectContact(c.id)));
    list.append(btn);
  });
}
async function selectContact(id,relist=true){
  const previousId=state.selectedId;
  if(previousId!==null&&previousId!==undefined){
    const draft=$("message-input").value;
    if(draft)messageDrafts.set(previousId,draft);
    else messageDrafts.delete(previousId);
  }
  contactSelectionEpoch+=1;
  conversationRevision+=1;
  const selectionEpoch=contactSelectionEpoch;
  state.selectedId=id;
  $("message-input").value=messageDrafts.get(id)||"";
  const generationButtons=[
    [$("first-message"),"🌱 初回メッセージを生成"],
    [$("generate"),$("count").value+"案を生成"],
    [$("follow-up"),"💬 追いメッセージ"],
  ];
  generationButtons.forEach(([button,label])=>{
    generationRequestTokens.set(button,++generationRequestSequence);
    button.disabled=true;
    button.textContent=label;
  });
  const c=current();
  const holder=$("current-avatar");
  const av=c?photoAvatar(c,true):node("span","avatar big","?");
  av.id="current-avatar";holder.replaceWith(av);
  $("current-name").textContent=c?.name||"相手を選択";
  $("current-bio").textContent=c?.description||"プロフィール未登録";
  $("edit-contact").disabled=!c;
  $("messages-count").textContent="▤ "+(c?.message_count||0)+"件の会話";
  $("incoming-count").textContent="💬 相手から："+(c?.incoming_count||0)+"通";
  $("suggestion-list").hidden=true;$("suggestion-list").replaceChildren();
  if(relist)renderContacts();
  state.messages=[];
  state.loadingConversation=!!c;
  state.conversationLoadFailed=false;
  renderMessages();
  if(!c)return;
  const fromId=id;
  let loaded=false;
  try{
    const data=await api("/matches/"+id+"/messages");
    if(fromId!==state.selectedId||selectionEpoch!==contactSelectionEpoch)return;
    state.messages=data;
    loaded=true;
  }finally{
    if(fromId===state.selectedId&&selectionEpoch===contactSelectionEpoch){
      state.loadingConversation=false;state.conversationLoadFailed=!loaded;
      generationButtons.forEach(([button])=>{button.disabled=!loaded;});
      renderMessages();
    }
  }
}
function renderMessages(){
  const holder=$("messages");holder.replaceChildren();
  const hasConversation=state.messages.length>0;
  $("first-message").hidden=state.loadingConversation||state.conversationLoadFailed||!current()||hasConversation;
  $("generate").hidden=state.loadingConversation||state.conversationLoadFailed||!current()||!hasConversation;
  $("follow-up").hidden=state.loadingConversation||state.conversationLoadFailed||!current()||!hasConversation;
  const composerUnavailable=state.loadingConversation||state.conversationLoadFailed||!current()||pendingMessageSubmissions.has(state.selectedId);
  ["message-input","send-them","send-me"].forEach(id=>{$(id).disabled=composerUnavailable;});
  if(state.loadingConversation){holder.append(node("p","empty-chat","会話履歴を読み込み中です"));return;}
  if(state.conversationLoadFailed){holder.append(node("p","empty-chat","会話履歴を読み込めませんでした。通信状態を確認して相手を選び直してください"));return;}
  if(!hasConversation){holder.append(node("p","empty-chat",current()?"まだ会話がありません。初回メッセージを生成するか、下の入力欄から履歴を追加してください。":"左側の＋から相手を登録してください。"));return;}
  state.messages.forEach(m=>{
    const messageContactId=state.selectedId;
    const wrap=node("article","chat-message "+m.role);
    const bubble=node("div","bubble",m.body);
    const stamp=node("span","message-time",(m.role==="me"?"自分":"相手")+" · "+(m.created_at||""));
    const actions=node("span","history-actions");
    const edit=node("button","","編集");edit.type="button";
    edit.onclick=()=>showMessageEditor(m);
    const del=node("button","","削除");del.type="button";
    del.onclick=()=>safe(async()=>{
      if(!confirm("このメッセージを削除しますか？"))return;
      invalidateGenerationResults();
      beginContactMutation(messageContactId);
      try{
        await api("/matches/"+messageContactId+"/messages/"+m.id,{method:"DELETE"});
        if(state.selectedId===messageContactId)await refreshConversation();
        notice("メッセージを削除しました");
      }finally{endContactMutation(messageContactId);}
    });
    actions.append(edit,del);wrap.append(bubble,stamp,actions);holder.append(wrap);
  });
  $("chat-area").scrollTop=$("chat-area").scrollHeight;
}
async function refreshConversation(){
  const id=state.selectedId;
  if(id===null)return;
  let records;
  try{records=await api("/matches/"+id+"/messages");}
  catch(error){
    if(id===state.selectedId){state.loadingConversation=false;state.conversationLoadFailed=true;renderMessages();}
    throw error;
  }
  if(id!==state.selectedId)return;
  state.loadingConversation=false;
  state.conversationLoadFailed=false;
  state.messages=records;
  const c=current();
  if(c){
    c.message_count=records.length;
    c.incoming_count=records.filter(m=>m.role==="them").length;
    c.last_message=records.at(-1)?.body||"";
  }
  renderContacts();
  $("messages-count").textContent="▤ "+records.length+"件の会話";
  $("incoming-count").textContent="💬 相手から："+records.filter(m=>m.role==="them").length+"通";
  $("suggestion-list").hidden=true;$("suggestion-list").replaceChildren();
  renderMessages();
}
function showModal(title,build){
  $("modal-title").textContent=title;
  const body=$("modal-body");body.replaceChildren();
  build(body);
  if(!$("modal").open)$("modal").showModal();
}
function field(body,label,value="",multi=false){
  const caption=node("label","",label);body.append(caption);
  const input=node(multi?"textarea":"input");
  if(multi)input.rows=4;
  input.value=value;body.append(input);return input;
}
function modalFooter(body,label,onSave,includeCancel=true){
  const bar=node("div","modal-actions");
  let cancel=null;
  if(includeCancel){
    cancel=node("button","","キャンセル");cancel.type="button";cancel.onclick=()=>$("modal").close();bar.append(cancel);
  }
  const save=node("button","confirm",label);save.type="button";
  save.onclick=async()=>{
    if(save.disabled)return;
    save.disabled=true;
    if(cancel)cancel.disabled=true;
    try{await safe(onSave);}
    finally{save.disabled=false;if(cancel)cancel.disabled=false;}
  };
  bar.append(save);body.append(bar);
}
function showMessageEditor(m){
  const contactId=state.selectedId;
  showModal("会話履歴を編集",body=>{
    body.append(node("p","modal-description","相手と自分の発言を変更できます。保存後、返信候補はクリアされます。"));
    const role=field(body,"発言者（me=自分、them=相手）",m.role);
    const text=field(body,"本文",m.body,true);
    modalFooter(body,"保存",async()=>{
      if(!["them","me"].includes(role.value))throw Error("発言者は me または them にしてください");
      invalidateGenerationResults();
      beginContactMutation(contactId);
      try{
        await api("/matches/"+contactId+"/messages/"+m.id,json("PUT",{role:role.value,body:text.value}));
        $("modal").close();
        if(state.selectedId===contactId)await refreshConversation();
        notice("履歴を更新しました");
      }finally{endContactMutation(contactId);}
    });
  });
}
async function addMessage(role,override){
  const c=current();if(!c)throw Error("先に相手を登録してください");
  const contactId=c.id;
  if(pendingMessageSubmissions.has(contactId))throw Error("この相手の発言を保存しています。完了後にもう一度お試しください");
  const draftValue=override===undefined?$("message-input").value:null;
  const body=(override===undefined?draftValue:override).trim();
  if(!body)throw Error("メッセージを入力してください");
  invalidateGenerationResults();
  pendingMessageSubmissions.add(contactId);
  beginContactMutation(contactId);
  renderMessages();
  try{
    await api("/matches/"+contactId+"/messages",json("POST",{role,body}));
    if(override===undefined){
      if(messageDrafts.get(contactId)===draftValue)messageDrafts.delete(contactId);
      if(state.selectedId===contactId&&$("message-input").value===draftValue)$("message-input").value="";
    }
    if(state.selectedId===contactId)await refreshConversation();
    notice((role==="me"?"自分":"相手")+"の発言を履歴に登録しました");
  }finally{
    pendingMessageSubmissions.delete(contactId);
    endContactMutation(contactId);
    if(state.selectedId===contactId)renderMessages();
  }
}
async function openContactForm(edit=false){
  const old=edit?current():null;
  let createdId=old?old.id:null;
  showModal(edit?"相手のプロフィールを編集":"相手を追加",body=>{
    body.append(node("p","modal-description","名前・プロフィール・識別用の写真を登録します。写真はGeminiへ送信しません。"));
    const name=field(body,"名前（必須）",old?.name||"");
    const description=field(body,"相手のプロフィール・自由記述",old?.description||"",true);
    body.append(node("label","","識別用写真（任意・JPEG/PNG/WebP、5MB以下）"));
    const file=node("input");file.type="file";file.accept="image/jpeg,image/png,image/webp";body.append(file);
    if(old){
      const remove=node("button","modal-button","この相手と全会話を削除");
      remove.type="button";remove.style.color="#c24b68";remove.onclick=()=>safe(async()=>{
        if(!confirm("相手の情報・写真・会話を完全に削除しますか？"))return;
        await api("/matches/"+old.id,{method:"DELETE"});
        messageDrafts.delete(old.id);
        $("modal").close();await loadMatches();notice("相手を削除しました");
      });body.append(remove);
    }
    modalFooter(body,"保存",async()=>{
      if(!name.value.trim())throw Error("名前を入力してください");
      const upload=file.files?.[0];
      if(upload){
        if(upload.size>5*1024*1024)throw Error("写真は5MB以下にしてください");
        if(!["image/jpeg","image/png","image/webp"].includes(upload.type))throw Error("写真はJPEG/PNG/WebPにしてください");
      }
      const data=await api(createdId?"/matches/"+createdId:"/matches",json(createdId?"PUT":"POST",{name:name.value.trim(),description:description.value}));
      createdId=data.id;
      if(upload){
        const form=new FormData();form.append("file",upload);
        await api("/matches/"+data.id+"/photo",{method:"PUT",body:form});
      }
      $("modal").close();await loadMatches(data.id);notice("相手の情報を保存しました");
    });
  });
}
async function copyText(text){
  try{await navigator.clipboard.writeText(text);notice("文章をコピーしました。送信済み履歴には追加していません。");}
  catch{
    showModal("文章をコピー",body=>{
      body.append(node("p","modal-description","以下を選択してコピーしてください。"));
      const area=field(body,"本文",text,true);area.focus();area.select();
    });
  }
}
function renderCards(container,payload,allowSave,matchId){
  if(payload.demo)container.append(node("p","demo-warning","⚠ APIキー未設定：以下は会話を解析していない固定サンプルです。"));
  if(payload.candidate_notice)container.append(node("p","user-info-terminal",payload.candidate_notice));
  const candidates=[payload.recommended,...(payload.alternatives||[])];
  candidates.forEach((item,i)=>{
    const card=node("article","candidate");
    card.append(node("div","candidate-title",(i===0?"✦ おすすめ · ":"")+item.label));
    card.append(node("div","candidate-text",item.text));
    const actions=node("div","candidate-actions");
    const copy=node("button","","コピー");copy.type="button";copy.onclick=()=>copyText(item.text);actions.append(copy);
    if(allowSave&&!payload.demo){
      const record=node("button","","実際に送った文章を記録");record.type="button";
      record.onclick=()=>showModal("実際に送信した文章を記録",body=>{
        body.append(node("p","modal-description","コピーだけでは送信済みになりません。送信した場合のみ、必要に応じて編集してから保存してください。"));
        const input=field(body,"本文",item.text,true);
        modalFooter(body,"送信済みとして保存",async()=>{
          if(state.selectedId!==matchId)throw Error("相手が変わっています。もう一度確認してください");
          await addMessage("me",input.value);$("modal").close();
        });
      });actions.append(record);
    }
    card.append(actions);container.append(card);
  });
  if(payload.reason)container.append(node("div","result-reason","判断の理由："+payload.reason));
  if($("policy").checked)renderStrategy(container,payload);
}
function renderStrategy(container,payload){
  if(!payload.strategy&&!payload.conversation_stage&&!payload.invite_decision&&!payload.decision_reason&&!payload.next_action)return;
  const stageLabels={
    "Stage 1":"マッチ直後・挨拶と会話開始",
    "Stage 2":"趣味や休日の話題を広げる段階",
    "Stage 3":"食事などへの誘いを検討する段階",
    "Stage 4":"自然な誘いを提案する段階",
    "Stage 5":"日時や場所を相談する段階",
    "Stage 6":"合意・継続・待機・終了を判断する段階"
  };
  const inviteLabels={
    do_not_invite:"まだ誘わない",
    continue_conversation:"自然に会話を続ける",
    consider_invite:"食事などへの誘いを検討",
    invite_gently:"自然に誘ってみる",
    wait:"相手の反応を待つ",
    respect_no:"相手の断りを尊重する",
    ask_user_info:"本人に情報を確認する",
    do_not_repeat_invite:"同じ誘いを繰り返さない",
    schedule_after_acceptance:"日時や場所を相談する",
    continue_or_close:"会話の継続・終了を判断する"
  };
  const rawStage=String(payload.conversation_stage||"");
  const stageMatch=rawStage.match(/^Stage\s*([1-6])(?:\b|$)/i);
  const stage=stageMatch?`Stage ${stageMatch[1]} — ${stageLabels[`Stage ${stageMatch[1]}`]}`:rawStage;
  const invite=inviteLabels[payload.invite_decision]||payload.invite_decision;
  const panel=node("section","policy-suggestion");
  panel.append(node("strong","strategy-heading","会話方針"));
  if(stage)panel.append(node("div","strategy-row","現在の段階："+stage));
  if(invite)panel.append(node("div","strategy-row","誘いの判断："+invite));
  if(payload.decision_reason)panel.append(node("div","strategy-row","判断の根拠："+payload.decision_reason));
  if(payload.next_action)panel.append(node("div","strategy-row","次の行動："+payload.next_action));
  if(payload.strategy)panel.append(node("div","strategy-row",typeof payload.strategy==="string"?payload.strategy:JSON.stringify(payload.strategy)));
  container.append(panel);
}
function mergeUserInfoAnswers(existing,incoming){
  const merged=new Map();
  [...(Array.isArray(existing)?existing:[]),...(Array.isArray(incoming)?incoming:[])].forEach(item=>{
    if(!item||typeof item.question!=="string"||typeof item.answer!=="string")return;
    const question=item.question.trim(),answer=item.answer.trim();
    if(question&&answer){
      const entry={question,answer};
      if(item.confirmed===true)entry.confirmed=true;
      merged.set(question.normalize("NFKC").toLocaleLowerCase(),entry);
    }
  });
  return [...merged.values()];
}
function renderUserInfoQuestions(container,payload,options,matchId,generationTarget,clarificationSession){
  const panel=node("section","user-info-panel");
  panel.append(node("h3","","返信を作る前に確認したいこと"));
  panel.append(node("p","user-info-reason",payload.user_info_reason||"本人情報を確認して、事実を作らずに返信するための質問です。"));
  panel.append(node("p","user-info-privacy","以下の回答はこの生成リクエストに一時的に使います。プロフィールには保存しません。返信候補とも別に表示します。"));
  const questions=(Array.isArray(payload.user_questions)?payload.user_questions:[]).slice(0,3);
  const inputs=[];
  questions.forEach((item,index)=>{
    const row=node("div","user-info-question");
    const label=node("label","","確認 "+(index+1)+": "+(item.question||"必要な情報"));
    const input=node("textarea","user-info-answer");input.id="user-info-answer-"+index;input.rows=2;input.setAttribute("aria-label",item.question||"確認への回答");label.htmlFor=input.id;
    if(item.purpose)row.append(node("small","user-info-purpose","確認する理由："+item.purpose));
    row.append(label,input);panel.append(row);inputs.push({item,input});
  });
  const actions=node("div","user-info-actions");
  const resume=node("button","action-green","回答して再生成");resume.type="button";resume.id="resume-generation";
  resume.onclick=()=>safe(async()=>{
    if(matchId!==null&&matchId!==state.selectedId)throw Error("相手が変わっています。もう一度確認してください");
    const answers=inputs.map(({item,input})=>({question:item.question||"",answer:input.value.trim()})).filter(x=>x.answer);
    resume.disabled=true;skip.disabled=true;
    try{await requestGeneration(options,matchId,answers,generationTarget,false,clarificationSession);}
    finally{resume.disabled=false;skip.disabled=false;}
  });
  const skip=node("button","action-outline","回答をスキップして安全に作成");skip.type="button";skip.id="skip-user-info";
  skip.onclick=()=>safe(async()=>{
    if(matchId!==null&&matchId!==state.selectedId)throw Error("相手が変わっています。もう一度確認してください");
    resume.disabled=true;skip.disabled=true;
    try{await requestGeneration(options,matchId,[],generationTarget,true,clarificationSession);}
    finally{resume.disabled=false;skip.disabled=false;}
  });
  actions.append(resume,skip);panel.append(actions);container.append(panel);
}
function renderOptionalUserQuestion(container,payload,options,matchId,generationTarget){
  const scope=matchId===null?"mode:"+(options.mode||"default"):"match:"+String(matchId);
  const handled=optionalUserQuestionHistory.get(scope)||new Set();
  const question=(Array.isArray(payload.optional_user_questions)?payload.optional_user_questions:[])
    .find(item=>item&&typeof item.question==="string"&&item.question.trim()&&!handled.has(optionalUserQuestionKey(item)));
  if(!question)return;
  const questionKey=optionalUserQuestionKey(question);
  const rememberQuestion=()=>{
    let keys=optionalUserQuestionHistory.get(scope);
    if(!keys){keys=new Set();optionalUserQuestionHistory.set(scope,keys);}
    keys.add(questionKey);
  };
  const forgetQuestion=()=>{
    const keys=optionalUserQuestionHistory.get(scope);
    if(!keys)return;
    keys.delete(questionKey);
    if(!keys.size)optionalUserQuestionHistory.delete(scope);
  };
  const panel=node("section","optional-user-question");
  panel.setAttribute("aria-labelledby","optional-user-question-title");
  panel.append(node("h3","","任意の確認（本人向け）"));
  panel.lastChild.id="optional-user-question-title";
  panel.append(node("p","optional-user-safe","上の候補はこのまま使えます。この質問への回答は任意です。"));
  const label=node("label","",question.question.trim());
  label.htmlFor="optional-user-answer";
  const answer=node("textarea","optional-user-answer");
  answer.id="optional-user-answer";answer.rows=2;answer.setAttribute("aria-label",question.question.trim());
  panel.append(label,answer);
  if(typeof question.purpose==="string"&&question.purpose.trim())panel.append(node("small","optional-user-purpose","確認する理由："+question.purpose.trim()));
  panel.append(node("p","optional-user-privacy","回答はこの生成リクエストの再生成にだけ使います。プロフィールには保存しません。メッセージも自動送信しません。"));
  const actions=node("div","user-info-actions");
  const regenerate=node("button","action-green","回答して再生成");
  regenerate.type="button";regenerate.id="answer-and-regenerate-optional";
  regenerate.onclick=()=>safe(async()=>{
    if(matchId!==null&&matchId!==state.selectedId)throw Error("相手が変わっています。もう一度確認してください");
    const value=answer.value.trim();
    if(!value){notice("回答を入力するか「あとで回答する」を選んでください");answer.focus();return;}
    rememberQuestion();
    regenerate.disabled=true;skip.disabled=true;
    try{
      await requestGeneration(options,matchId,[{question:question.question.trim(),answer:value}],generationTarget);
    }catch(error){
      forgetQuestion();
      throw error;
    }
    finally{regenerate.disabled=false;skip.disabled=false;}
  });
  const skip=node("button","action-outline","あとで回答する");
  skip.type="button";skip.id="skip-optional-user-question";
  skip.onclick=()=>{rememberQuestion();panel.remove();};
  actions.append(regenerate,skip);panel.append(actions);container.append(panel);
}
function normalizeOptionalUserQuestion(question){
  return String(question||"").normalize("NFKC").toLocaleLowerCase().replace(/\s+/g," ").trim();
}
function optionalUserQuestionKey(item){
  const scopeKey=typeof item?.scope_key==="string"?item.scope_key.trim():"";
  return scopeKey?normalizeOptionalUserQuestion(scopeKey):normalizeOptionalUserQuestion(item?.question);
}
function invalidateGenerationResults(){
  conversationRevision+=1;
  const area=$("suggestion-list");
  if(area){area.hidden=true;area.replaceChildren();}
}
async function requestGeneration(options,matchId,userAnswers=[],generationTarget={},skippedUserInfo=false,clarificationSession=null){
  const button=generationTarget.button||$(options.mode==="followup"?"follow-up":options.mode==="first"?"first-message":"generate");
  const area=generationTarget.container||$("suggestion-list");
  const selectionEpoch=contactSelectionEpoch;
  const revision=conversationRevision;
  if(!clarificationSession){
    const sessionId=(typeof crypto!=="undefined"&&typeof crypto.randomUUID==="function")?crypto.randomUUID():("s"+Date.now()+"-"+Math.random().toString(36).slice(2));
    clarificationSession={matchId,selectionEpoch,revision,answers:mergeUserInfoAnswers([],userAnswers),sessionId};
  }else{
    if(clarificationSession.matchId!==matchId||clarificationSession.selectionEpoch!==selectionEpoch||clarificationSession.revision!==revision){
      throw Error("会話が更新されました。最新の内容からもう一度生成してください");
    }
    clarificationSession.answers=mergeUserInfoAnswers(clarificationSession.answers,userAnswers);
  }
  if(matchId!==null&&mutatingContacts.has(matchId))throw Error("会話履歴を保存しています。完了後にもう一度お試しください");
  const requestToken=++generationRequestSequence;
  generationRequestTokens.set(button,requestToken);
  generationAreaTokens.set(area,requestToken);
  const before=button.textContent;button.disabled=true;button.textContent="生成中…";
  try{
    const result=await api("/generate",json("POST",{...options,response_version:2,user_answers:clarificationSession.answers,clarification_session_id:clarificationSession.sessionId,skipped_user_info:skippedUserInfo}));
    if(generationAreaTokens.get(area)!==requestToken||revision!==conversationRevision)return;
    if(matchId!==null&&(matchId!==state.selectedId||selectionEpoch!==contactSelectionEpoch||state.loadingConversation||state.conversationLoadFailed||mutatingContacts.has(matchId)))return;
    area.hidden=false;area.replaceChildren();
    const blocked=result.generation_blocked||(!result.recommended&&(skippedUserInfo||result.skipped_user_info||!result.needs_user_info));
    if(blocked){
      const blockedTitle={
        first:"✦ 初回メッセージは作成できませんでした",
        like:"✦ メッセージ付きいいねは作成できませんでした",
        followup:"✦ 追いメッセージは作成できませんでした"
      }[options.mode]||"✦ 返信候補は作成できませんでした";
      area.append(node("div","suggestion-heading",blockedTitle));
      if(result.candidate_notice)area.append(node("p","user-info-terminal",result.candidate_notice));
      area.append(node("p","user-info-terminal",result.user_info_reason||result.blocking_reason||result.detail||"未確認の本人情報を使わずに返信を作れないため、ここで停止しました。プロフィールを確認してから再度お試しください。"));
    }else if(result.needs_user_info){
      area.append(node("div","suggestion-heading","✦ 本人情報の確認"));
      renderUserInfoQuestions(area,result,options,matchId,generationTarget,clarificationSession);
    }else{
      const title=options.mode==="first"?"✦ 初回メッセージ候補":options.mode==="followup"?"✦ 追いメッセージの提案":options.mode==="like"?"✦ メッセージ付きいいね候補":"✦ 返信候補";
      area.append(node("div","suggestion-heading",title));
      renderCards(area,result,generationTarget.allowSave!==false,matchId);
      renderOptionalUserQuestion(area,result,options,matchId,generationTarget);
      clarificationSession.answers=[];
    }
    if(!generationTarget.container)$("chat-area").scrollTop=$("chat-area").scrollHeight;
  }finally{
    if(generationRequestTokens.get(button)===requestToken){button.disabled=false;button.textContent=before;}
  }
}
async function generate(mode){
  const c=current();if(mode!=="like"&&!c)throw Error("相手を登録してください");
  const count=Number($("count").value);
  const opts={
    response_version:2,mode,match_id:c?.id,count,tone:state.tone,
    direction:$("direction").selectedOptions[0]?.textContent||"",
    extra:$("extra").value,show_policy:$("policy").checked
  };
  await requestGeneration(opts,c.id,[]);
}
function likeModal(){
  showModal("👍 メッセージ付きいいね",body=>{
    body.append(node("p","modal-description","マッチする前の相手のプロフィール文を貼り付けて生成します。相手の登録は不要です。"));
    const name=field(body,"相手の名前（任意）");
    const profile=field(body,"相手のプロフィール文（必須）","",true);
    const feedback=node("div");
    const action=node("button","modal-button confirm","3案を生成");
    action.type="button";
    action.onclick=()=>safe(async()=>{
      if(!profile.value.trim())throw Error("相手のプロフィール文を入力してください");
      action.disabled=true;action.textContent="生成中…";
      try{
        const options={
          response_version:2,mode:"like",name:name.value,description:profile.value,count:3,
          tone:state.tone,show_policy:false
        };
        await requestGeneration(options,null,[],{button:action,container:feedback,allowSave:false});
      }finally{action.disabled=false;action.textContent="3案を生成";}
    });
    action.style.marginTop="12px";body.append(action,feedback);
  });
}
async function profileModal(){
  try{
    state.profile=await api("/profile");
  }catch(error){
    // The startup copy keeps the form available during a temporary outage;
    // failed saves leave the user's edits open for retry after recovery.
    if(!state.profile||typeof state.profile.content!=="string")throw error;
  }
  showModal("📋 自分の情報",body=>{
    body.append(node("p","modal-description","文章生成時に使用するご自身の情報です。後から編集できます。"));
    let fields={};
    try{
      const parsed=JSON.parse(state.profile.content||"{}");
      fields=parsed&&typeof parsed==="object"&&!Array.isArray(parsed)?parsed:{memo:state.profile.content};
    }catch{fields={memo:state.profile.content};}
    const displayProfileValue=value=>{
      if(Array.isArray(value))return value.every(item=>typeof item==="string")?value.join(", "):JSON.stringify(value,null,2);
      if(value&&typeof value==="object")return JSON.stringify(value,null,2);
      return value??"";
    };
    const meta=[
      ["name","名前"],["age","年齢"],["area","居住地域"],["job","学校・仕事"],
      ["hobbies","趣味・好きなこと"],["personality","性格"],["style","話し方の好み"],
      ["goal","どのような関係を望むか"],["memo","その他の情報・自己紹介"]
    ];
    const inputs={};
    meta.forEach(([key,label])=>inputs[key]=field(body,label,displayProfileValue(fields[key]),key==="memo"||key==="goal"||typeof fields[key]==="object"));
    const avoid=field(body,"言ってほしくないこと・避けたい表現",state.profile.avoid,true);
    modalFooter(body,"プロフィールを保存",async()=>{
      const content={...fields};
      for(const [key] of meta){
        const inputValue=inputs[key].value.trim();
        const previous=fields[key];
        const previousDisplay=String(displayProfileValue(previous)).trim();
        if(!Object.prototype.hasOwnProperty.call(fields,key)&&!inputValue)continue;
        if(inputValue===previousDisplay){content[key]=previous;continue;}
        if(Array.isArray(previous)){
          if(previous.every(item=>typeof item==="string"))content[key]=inputValue?inputValue.split(",").map(item=>item.trim()).filter(Boolean):[];
          else{
            let parsed;
            try{parsed=JSON.parse(inputValue||"[]");}catch{throw Error("「"+key+"」はJSON形式で入力してください");}
            if(!Array.isArray(parsed))throw Error("「"+key+"」には配列形式のJSONを入力してください");
            content[key]=parsed;
          }
        }else if(previous&&typeof previous==="object"){
          let parsed;
          try{parsed=JSON.parse(inputValue||"{}");}catch{throw Error("「"+key+"」はJSON形式で入力してください");}
          if(!parsed||typeof parsed!=="object"||Array.isArray(parsed))throw Error("「"+key+"」にはオブジェクト形式のJSONを入力してください");
          content[key]=parsed;
        }else content[key]=inputValue;
      }
      await api("/profile",json("PUT",{content:JSON.stringify(content),avoid:avoid.value}));
      state.profile={content:JSON.stringify(content),avoid:avoid.value};
      $("modal").close();notice("自分のプロフィールを保存しました");
    });
  });
}
function settingsModal(){
  showModal("⚙ ローカルアプリの設定",body=>{
    body.append(node("p","modal-description","データ保存先：PC内の data/ フォルダ（SQLite・写真）。"));
    body.append(node("div","modal-result","Gemini接続："+(state.status?.demo?"未設定（固定サンプル）":"設定あり（"+(state.status?.model||"") +"）")));
    body.append(node("p","modal-description","Gemini APIキーはPC内の .env に設定してください。画面からは設定・表示できません。"));
    body.append(node("p","modal-description","APIキー設定後は start.bat を終了して起動し直してください。Gemini無料枠で送信される文章のデータ取扱条件を確認してください。"));
    const b=node("button","modal-button","架空の相手を2人追加して試す");b.type="button";
    b.onclick=()=>safe(async()=>{
      const tests=[
        {name:"サンプル・さくら",description:"カフェ巡りと旅行が好き。返信は短めです。",msg:"最近新しいカフェに行ってきました！"},
        {name:"サンプル・みお",description:"映画と音楽が好き。",msg:"週末は映画を観て過ごしました"}
      ];
      for(const t of tests){
        const c=await api("/matches",json("POST",{name:t.name,description:t.description}));
        await api("/matches/"+c.id+"/messages",json("POST",{role:"them",body:t.msg}));
      }
      $("modal").close();await loadMatches();notice("架空のサンプル相手を追加しました");
    });
    body.append(b);
    body.append(node("p","modal-description","このサンプルデータも実際のSQLiteに保存されます。不要になったら相手プロフィールから削除してください。"));
  });
}
function guideModal(){
  showModal("🎓 使い方",body=>{
    const steps=[
      "「自分の情報」からプロフィールと話し方を登録します。",
      "左上の＋から相手の名前、プロフィール、識別用写真を登録します。",
      "相手と自分のメッセージを下部のボタンで会話履歴に追加します。",
      "文体・候補数・方向性を設定して返信候補を生成します。",
      "使いたい案をコピーし、実際に送った文章だけ「送信済み」に記録します。"
    ];
    steps.forEach((s,i)=>{const d=node("div","modal-result");d.append(node("strong","",String(i+1)+". "),node("span","",s));body.append(d);});
  });
}
function historyModal(){
  const c=current();if(!c){notice("相手を登録してください");return;}
  showModal(c.name+"との会話履歴",body=>{
    state.messages.forEach(m=>{
      const div=node("div","modal-result");
      div.append(node("strong","",m.role==="me"?"自分":"相手"),node("p","",m.body));body.append(div);
    });
    if(!state.messages.length)body.append(node("p","modal-description","まだメッセージがありません。"));
  });
}
function sentModal(){
  const c=current();if(!c){notice("相手を登録してください");return;}
  showModal(c.name+"へ送った文章",body=>{
    const msgs=state.messages.filter(m=>m.role==="me");
    if(!msgs.length)body.append(node("p","modal-description","まだ自分の送信履歴はありません。"));
    msgs.forEach(m=>{const row=node("div","modal-result");row.append(node("p","",m.body));
      const copy=node("button","modal-button","コピー");copy.type="button";copy.onclick=()=>copyText(m.body);row.append(copy);body.append(row);
    });
  });
}
function exportCurrent(){
  const c=current();if(!c){notice("相手を登録してください");return;}
  const content=JSON.stringify({name:c.name,profile:c.description,messages:state.messages},null,2);
  const url=URL.createObjectURL(new Blob([content],{type:"application/json;charset=utf-8"}));
  const a=node("a");a.href=url;a.download="matching-chat-"+c.id+".json";a.click();
  setTimeout(()=>URL.revokeObjectURL(url),1000);
  notice("会話をJSONとして書き出しました");
}
function attach(){
  $("search").addEventListener("input",renderContacts);
  $("message-input").addEventListener("input",()=>{
    if(state.selectedId===null)return;
    const draft=$("message-input").value;
    if(draft)messageDrafts.set(state.selectedId,draft);
    else messageDrafts.delete(state.selectedId);
  });
  $("new-contact").onclick=()=>safe(()=>openContactForm());
  $("edit-contact").onclick=()=>safe(()=>openContactForm(true));
  $("send-them").onclick=()=>safe(()=>addMessage("them"));
  $("send-me").onclick=()=>safe(()=>addMessage("me"));
  $("message-input").addEventListener("keydown",e=>{
    if(e.ctrlKey&&e.key==="Enter"){e.preventDefault();safe(()=>addMessage("them"));}
  });
  $("generate").onclick=()=>safe(()=>generate("reply"));
  $("first-message").onclick=()=>safe(()=>generate("first"));
  $("follow-up").onclick=()=>safe(()=>generate("followup"));
  $("count").onchange=()=>{$("generate").textContent=$("count").value+"案を生成";};
  $("history-button").onclick=historyModal;
  $("send-content").onclick=sentModal;
  $("export-button").onclick=exportCurrent;
  $("close-modal").onclick=()=>$("modal").close();
  $("modal").addEventListener("click",e=>{if(e.target===$("modal"))$("modal").close();});
  document.querySelectorAll("[data-tone]").forEach(b=>b.onclick=()=>{
    state.tone=b.dataset.tone;
    document.querySelectorAll("[data-tone]").forEach(x=>x.classList.toggle("on",x===b));
  });
  document.querySelectorAll("[data-open]").forEach(b=>b.onclick=()=>safe(()=>( {
    guide:guideModal,like:likeModal,profile:profileModal,settings:settingsModal
  })[b.dataset.open]?.()));
}
async function start(){
  attach();
  await safe(async()=>{
    const [status,profile]=await Promise.all([api("/status"),api("/profile")]);
    state.status=status;state.profile=profile;await loadMatches();
    const pill=document.querySelector(".version");
    if(pill)pill.textContent=status.demo?"LOCAL · DEMO":"LOCAL · "+status.model;
    notice(status.demo?"ローカルアプリを起動しました。AI未接続のデモモードです。":"ローカルアプリを起動しました。Geminiが設定されています。");
  });
}
document.addEventListener("DOMContentLoaded",start);
})();
