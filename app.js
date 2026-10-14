/* Matching Reply Assistant - UI-only interactive prototype.
   No network requests, Gemini key, localStorage, database or backend.
   Everything stays in memory and disappears on reload. */
(() => {
"use strict";
const $ = (id) => document.getElementById(id);
const avatars = ["#06c59a","#7992b1","#977ebd","#e79c91","#3a93d5","#f4a25d","#63a892","#807db7","#5093a0","#d091a8","#6791c7","#b68d63","#789d64"];
function createDemoContacts() {
  const records = [
    ["あかり","カフェや散歩が好きです","最近、気になっていたカフェに行ってきました！"],
    ["みな","音楽を聴くことと旅行が好き","映画も好きなんですね！"],
    ["こはる","古本屋と喫茶店を探すのが趣味","おすすめの本ってありますか？"],
    ["なつき","料理とパン作りが好きです","焼きたてのパンっておいしいですよね"],
    ["りん","休日は美術館によく行きます","週末はのんびり過ごしていました"],
    ["さや","海の見える場所が好き","この前、海沿いをドライブしました"],
    ["えま","カフェでのんびりが好き","最近は抹茶ラテにハマっています"],
    ["ひなた","映画と音楽が趣味です","映画はどんなジャンルを観ますか？"],
    ["ゆい","温泉旅行が好きです","日帰り温泉に行ってきました"],
    ["もも","写真を撮るのが好きです","きれいな夕焼けを見つけました"],
    ["あおい","散歩と読書が好き","近くの公園を歩いてきました"],
    ["れい","おいしいごはんを探しがち","好きな料理って何ですか？"]
  ];
  return records.map((row,i) => ({
    id:i+1,name:row[0],bio:row[1],color:avatars[i%avatars.length],photo:null,
    messages:[{role:"them",text:row[2],time:i===0?"10/14 08:15":"10/13 20:4"+(i%9)}],
    created:"10/12",notes:""
  }));
}
const original = createDemoContacts;
let contacts = original();
let nextId = 100;
let selectedId = 1;
let tone = "自動";
let selfProfile = {
  name:"",age:"",area:"",job:"",hobbies:"",personality:"",
  style:"短め・自然な文章",avoid:"",goal:""
};
let toastTimer;
function message(text){
  const el=$("toast");el.textContent=text;el.hidden=false;
  clearTimeout(toastTimer);toastTimer=setTimeout(()=>{el.hidden=true},2800);
}
function create(tag,className,text){
  const el=document.createElement(tag);
  if(className)el.className=className;
  if(text!==undefined)el.textContent=text;
  return el;
}
function active(){return contacts.find(c=>c.id===selectedId)||null}
function avatar(c,large=false){
  const el=create("span","avatar"+(large?" big":""));
  if(c.photo){const img=document.createElement("img");img.src=c.photo;img.alt="";el.append(img);}
  else{el.style.background=c.color;el.textContent=c.name[0]||"?";}
  return el;
}
function lastText(c){return c.messages.at(-1)?.text || c.bio || "メッセージはまだありません";}
function renderContacts(){
  const filter=$("search").value.trim().toLocaleLowerCase();
  const list=$("contacts");list.replaceChildren();
  const shown=contacts.filter(c=>c.name.toLocaleLowerCase().includes(filter));
  for(const c of shown){
    const item=create("button","contact-item"+(c.id===selectedId?" active":""));item.type="button";
    item.append(avatar(c));
    const details=create("span","contact-item-details");
    const head=create("div","contact-item-head");
    head.append(create("strong","",c.name));
    head.append(create("span","count-pill",c.messages.length+"通"));
    head.append(create("span","contact-time",c.messages.at(-1)?.time || "新規"));
    details.append(head,create("div","contact-preview",lastText(c)));
    item.append(details);
    item.addEventListener("click",()=>{selectedId=c.id;renderAll();});
    list.append(item);
  }
  if(!shown.length)list.append(create("div","empty-chat","一致する相手がいません"));
}
function renderHeader(){
  const c=active();
  $("current-avatar").replaceWith(Object.assign(c?avatar(c,true):create("span","avatar big","?"),{id:"current-avatar"}));
  $("current-name").textContent=c?.name||"相手を選択";
  $("current-bio").textContent=c?.bio||"相手を追加してください";
  const incoming=c?.messages.filter(m=>m.role==="them").length||0;
  $("incoming-count").textContent="💬 相手から: "+incoming+"通";
  $("messages-count").textContent="▤ "+(c?.messages.length||0)+"件の会話";
  $("edit-contact").disabled=!c;
}
function renderMessages(){
  const list=$("messages");list.replaceChildren();
  const c=active();
  if(!c||!c.messages.length){list.append(create("p","empty-chat","まだ会話がありません。画面下の欄から追加してください。"));return;}
  for(const m of c.messages){
    const item=create("div","chat-message "+m.role);
    const bubble=create("div","bubble",m.text);
    item.append(bubble,create("span","message-time",m.time));
    list.append(item);
  }
}
function renderAll(){renderContacts();renderHeader();renderMessages();resetSuggestions();}
function resetSuggestions(){const el=$("suggestion-list");el.hidden=true;el.replaceChildren();}
function addMessage(role,text){
  const c=active();if(!c){message("相手を追加してください");return false;}
  const value=text.trim();if(!value){message("メッセージを入力してください");return false;}
  c.messages.push({role,text:value,time:new Date().toLocaleString("ja-JP",{month:"numeric",day:"numeric",hour:"2-digit",minute:"2-digit"})});
  renderAll();$("message-input").value="";
  $("chat-area").scrollTop=$("chat-area").scrollHeight;
  message(role==="them"?"相手のメッセージを記録しました":"自分のメッセージを記録しました");
  return true;
}
function sampleReplies(c,followup=false){
  const last=c.messages.at(-1)?.text||"";
  const light=/カフェ|喫茶|珈琲|コーヒー/.test(last);
  const travel=/旅|温泉|海|ドライブ/.test(last);
  const film=/映画|本|音楽/.test(last);
  let base;
  if(followup) base=[
    "そういえば、前にお話ししていたことがちょっと気になってました！",
    "またお時間があるときに、ゆっくりお話しできたらうれしいです！",
    "こんにちは！最近どう過ごしてますか？"
  ];
  else if(light) base=[
    "いいですね！どんな雰囲気のお店だったんですか？",
    "カフェ巡り楽しそうですね！最近お気に入りのお店ってありますか？",
    "気になってたお店に行けたの、いいですね！"
  ];
  else if(travel) base=[
    "いいですね！どのあたりに行かれたんですか？",
    "それは楽しそうですね！景色もきれいそうです",
    "旅行のお話、もっと聞いてみたいです！"
  ];
  else if(film) base=[
    "気になります！どんな作品がお好きなんですか？",
    "いいですね！最近はどんなものにハマってますか？",
    "そういうお話、聞くの好きです！"
  ];
  else base=[
    "そうなんですね！ちょっと気になります",
    "なるほど！よかったらもう少し聞いてみたいです",
    "それは面白そうですね！"
  ];
  const chosen=$("direction").value;
  if(chosen==="question")base[0]=base[2];
  if(chosen==="invite"&&!followup)base[1]="もう少しお話ししてみたいです！タイミングが合えば、今度一緒にお茶でもいかがですか？";
  if(chosen==="warm")base[0]="それ、いいですね！なんだか楽しそうです☺️";
  if(tone==="敬語")base=base.map(s=>s.replace("どんな雰囲気のお店だったんですか？","どのような雰囲気のお店だったんですか？").replace("いいですね！","素敵ですね！"));
  if(tone==="タメ口")base=base.map(s=>s.replaceAll("ですね！","ね！").replaceAll("ですか？","？").replaceAll("ますか？","？").replaceAll("です！","！"));
  return base;
}
async function copy(text){
  try{await navigator.clipboard.writeText(text);message("コピーしました（送信済みにはなりません）");}
  catch{showModal("文章をコピー",body=>{const ta=create("textarea");ta.value=text;ta.rows=4;body.append(ta);ta.focus();ta.select();});}
}
function renderSuggestions(type="reply"){
  const c=active();if(!c){message("相手を選択してください");return;}
  if(type==="reply"&&!c.messages.length){message("先に会話を登録してください");return;}
  const n=Number($("count").value);
  let texts=sampleReplies(c,type==="followup");
  const extra=$("extra").value.trim();
  if(n>3)texts=[...texts,"そうなんですね！話してくれてありがとうございます","それ、気になります！もう少し教えてください"];
  if(n===1)texts=texts.slice(0,1);
  const results=$("suggestion-list");results.hidden=false;results.replaceChildren();
  results.append(create("div","suggestion-heading",type==="followup"?"✦ 追いメッセージ案（ダミー）":"✦ 返信候補（ダミー）"));
  texts.slice(0,n).forEach((t,i)=>{
    const card=create("article","candidate");
    card.append(create("div","candidate-title",["おすすめ・自然体","会話を広げる","短め","親しみやすく","別の切り口"][i]));
    card.append(create("div","candidate-text",t));
    const actions=create("div","candidate-actions");
    const cp=create("button","", "コピー");cp.type="button";cp.addEventListener("click",()=>copy(t));
    const record=create("button","","実際に送った内容を記録");record.type="button";record.addEventListener("click",()=>{showModal("送信した内容を記録",body=>{
      body.append(create("p","modal-description","実際に送信した場合だけ記録してください。文章は自由に編集できます。"));
      const ta=create("textarea");ta.rows=4;ta.value=t;body.append(ta);
      const footer=create("div","modal-actions");
      const ok=create("button","confirm","送信済みに記録");ok.type="button";
      ok.addEventListener("click",()=>{if(addMessage("me",ta.value))$("modal").close();});
      footer.append(ok);body.append(footer);
    });});
    actions.append(cp,record);card.append(actions);results.append(card);
  });
  if($("policy").checked)results.append(create("div","policy-suggestion",
    "会話方針（デモ）：相手の発言に自然に反応し、話題をひとつずつ広げるのが良さそうです。実際の関係性分析ではありません。"));
  if(extra)results.append(create("div","policy-suggestion","追加指示「"+extra+"」は入力されています。UIプレビューでは内容をAIに解釈させていません。"));
  $("chat-area").scrollTop=$("chat-area").scrollHeight;
}
function showModal(title,fill){
  const dialog=$("modal");
  $("modal-title").textContent=title;
  const body=$("modal-body");body.replaceChildren();
  fill(body);
  if(!dialog.open)dialog.showModal();
}
function field(body,label,value="",multi=false){
  const lbl=create("label","",label);body.append(lbl);
  const inp=create(multi?"textarea":"input");if(multi)inp.rows=4;inp.value=value;body.append(inp);return inp;
}
function footerButton(body,title,callback,danger=false){
  const row=create("div","modal-actions");
  const cancel=create("button","","キャンセル");cancel.type="button";cancel.addEventListener("click",()=>$("modal").close());
  const accept=create("button",danger?"danger":"confirm",title);accept.type="button";accept.addEventListener("click",callback);
  row.append(cancel,accept);body.append(row);
}
function contactModal(edit=false){
  const c=edit?active():null;
  showModal(edit?"相手のプロフィールを編集":"新しい相手を登録",body=>{
    body.append(create("p","modal-description","写真は画面内で相手を識別するためだけに使用します。AIに送信する機能はありません。"));
    const name=field(body,"相手の名前",c?.name||"");
    const bio=field(body,"プロフィール・メモ",c?.bio||"",true);
    body.append(create("label","","識別用の写真（任意）"));
    const file=create("input");file.type="file";file.accept="image/*";body.append(file);
    if(edit){
      const remove=create("button","modal-button","相手と会話履歴を削除");remove.type="button";remove.style.color="#b94d64";remove.style.marginTop="12px";
      remove.addEventListener("click",()=>{
        if(!confirm("この相手とすべての会話履歴をデモ画面から削除しますか？"))return;
        if(c.photo)URL.revokeObjectURL(c.photo);
        contacts=contacts.filter(x=>x.id!==c.id);selectedId=contacts[0]?.id??null;renderAll();$("modal").close();message("相手を削除しました");
      });body.append(remove);
    }
    footerButton(body,"保存",()=>{
      if(!name.value.trim()){message("名前を入力してください");name.focus();return;}
      const target=c||{id:nextId++,messages:[],color:avatars[Math.floor(Math.random()*avatars.length)],photo:null,created:"今日"};
      target.name=name.value.trim();target.bio=bio.value.trim();
      if(file.files[0]){if(target.photo)URL.revokeObjectURL(target.photo);target.photo=URL.createObjectURL(file.files[0]);}
      if(!c)contacts.unshift(target);
      selectedId=target.id;renderAll();$("modal").close();message("デモ画面に保存しました");
    });
  });
}
function likeModal(){
  showModal("👍 メッセージ付きいいね",body=>{
    body.append(create("p","modal-description","マッチ前の相手のプロフィールから、最初のメッセージ候補を確認できます。実際のAIには接続しません。"));
    const name=field(body,"相手の名前（任意）","");
    const profile=field(body,"相手のプロフィール文","",true);
    const action=create("button","modal-button confirm","3案をプレビュー");action.type="button";action.style.marginTop="15px";
    const container=create("div");body.append(action,container);
    action.addEventListener("click",()=>{
      if(!profile.value.trim()){message("プロフィール文を入力してください");return;}
      const prefix=name.value.trim()?name.value.trim()+"さん、":"";
      const topic=/カフェ|喫茶/.test(profile.value)?"カフェ巡り":/旅|旅行/.test(profile.value)?"旅行":/映画/.test(profile.value)?"映画":"プロフィール";
      const texts=[
        prefix+"はじめまして！"+topic+"のお話が気になって、いいねしました。よかったらお話ししたいです！",
        prefix+"こんにちは！"+topic+"がお好きなんですね。最近気になっていることってありますか？",
        prefix+"はじめまして！プロフィールを読んで気になりました。よろしくお願いします！"
      ];
      container.replaceChildren();
      texts.forEach((t,i)=>{const div=create("div","modal-result");div.append(create("strong","",i===0?"おすすめ案":"別の案 "+i),create("p","",t));const btn=create("button","modal-button","コピー");btn.type="button";btn.addEventListener("click",()=>copy(t));div.append(btn);container.append(div)});
    });
  });
}
function profileModal(){
  showModal("📋 自分の情報",body=>{
    body.append(create("p","modal-description","ご自身の情報を入力してください。デモ中の一時的な表示のみで、ファイルや外部サービスに保存しません。"));
    const schema=[["name","名前"],["age","年齢"],["area","住んでいるエリア"],["job","学校・仕事"],["hobbies","趣味・好きなこと"],["personality","性格"],["style","普段の話し方"],["avoid","言ってほしくない表現"],["goal","恋愛での希望"]];
    const controls={};schema.forEach(([key,label])=>controls[key]=field(body,label,selfProfile[key],key==="avoid"||key==="goal"));
    footerButton(body,"プロフィールを反映",()=>{for(const [key]of schema)selfProfile[key]=controls[key].value;$("modal").close();message("デモ用プロフィールを反映しました");});
  });
}
function historyModal(){
  const c=active();
  showModal("◷ "+(c?.name||"相手")+"との履歴",body=>{
    body.append(create("p","modal-description","このプレビューで登録した会話のみを表示します。"));
    for(const item of c?.messages||[]){const p=create("div","modal-result");p.append(create("strong","",item.role==="me"?"自分":"相手"),create("p","",item.text));body.append(p);}
    if(!c?.messages.length)body.append(create("p","modal-description","会話はまだありません。"));
  });
}
function guideModal(){
  showModal("🎓 学習・会話の使い方",body=>{
    const lines=["相手を左の一覧から選びます。＋ボタンで追加もできます。","下の入力欄から「相手として送信」または「自分として送信」で履歴を残します。","文体・返信の方向・候補数を選び、「3案を生成」でダミー候補を表示します。","実際に送信する場合は文章を確認し、自分として履歴に記録します。"];
    lines.forEach((s,i)=>{const d=create("div","modal-result");d.append(create("strong","",String(i+1).padStart(2,"0")),create("p","",s));body.append(d)});
    body.append(create("p","modal-description","これはUIプレビューです。学習機能や外部サービス連携は未実装です。"));
  });
}
function settingsModal(){
  showModal("⚙ 設定",body=>{
    body.append(create("p","modal-description","この画面はPC用UIの確認版です。Gemini APIには接続せず、操作した内容も再読み込み時に消えます。"));
    const label=create("label","","初期状態に戻す");body.append(label);
    const btn=create("button","modal-button","架空データをリセット");btn.type="button";
    btn.addEventListener("click",()=>{if(!confirm("デモ画面を初期化しますか？"))return;contacts.forEach(c=>c.photo&&URL.revokeObjectURL(c.photo));contacts=original();selectedId=1;selfProfile={name:"",age:"",area:"",job:"",hobbies:"",personality:"",style:"短め・自然な文章",avoid:"",goal:""};renderAll();$("modal").close();message("デモ画面を初期化しました");});
    body.append(btn);
  });
}
function sentModal(){
  const c=active();showModal("◉ 送信内容の確認",body=>{
    body.append(create("p","modal-description","会話履歴に記録された自分のメッセージを確認できます。"));
    const mine=c?.messages.filter(m=>m.role==="me")||[];
    if(!mine.length)body.append(create("p","modal-description","まだ自分の送信記録はありません。"));
    mine.forEach(m=>{const d=create("div","modal-result");d.append(create("strong","",m.time),create("p","",m.text));body.append(d)});
  });
}
function exportData(){
  const c=active();if(!c){message("相手を選択してください");return;}
  const output={name:c.name,bio:c.bio,messages:c.messages};
  const blob=new Blob([JSON.stringify(output,null,2)],{type:"application/json"});
  const url=URL.createObjectURL(blob);
  const a=document.createElement("a");a.href=url;a.download="conversation-demo-"+c.id+".json";a.click();
  setTimeout(()=>URL.revokeObjectURL(url),1000);message("架空データをJSONでエクスポートしました");
}
document.querySelectorAll("[data-tone]").forEach(b=>b.addEventListener("click",()=>{
  tone=b.dataset.tone;document.querySelectorAll("[data-tone]").forEach(x=>x.classList.toggle("on",x===b));message("文体を「"+tone+"」に変更");
}));
document.querySelectorAll("[data-open]").forEach(b=>b.addEventListener("click",()=>{
  const type=b.dataset.open;({guide:guideModal,like:likeModal,profile:profileModal,settings:settingsModal})[type]?.();
}));
$("new-contact").addEventListener("click",()=>contactModal(false));
$("edit-contact").addEventListener("click",()=>contactModal(true));
$("history-button").addEventListener("click",historyModal);
$("send-content").addEventListener("click",sentModal);
$("export-button").addEventListener("click",exportData);
$("search").addEventListener("input",renderContacts);
$("send-them").addEventListener("click",()=>addMessage("them",$("message-input").value));
$("send-me").addEventListener("click",()=>addMessage("me",$("message-input").value));
$("message-input").addEventListener("keydown",e=>{if(e.ctrlKey&&e.key==="Enter"){e.preventDefault();addMessage("them",$("message-input").value);}});
$("generate").addEventListener("click",()=>renderSuggestions("reply"));
$("follow-up").addEventListener("click",()=>renderSuggestions("followup"));
$("count").addEventListener("change",()=>{
  const n=$("count").value;$("generate").textContent=n+"案を生成";
});
$("close-modal").addEventListener("click",()=>$("modal").close());
$("modal").addEventListener("click",e=>{if(e.target===$("modal"))$("modal").close();});
renderAll();
})();
