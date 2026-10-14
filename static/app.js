"use strict";

const $ = (id) => document.getElementById(id);
const state = { matches: [], selectedId: null, messages: [], editingId: null, view: "chat" };
let noticeTimer;

async function api(path, options = {}) {
  const response = await fetch("/api" + path, options);
  let result;
  try { result = await response.json(); }
  catch { throw new Error("サーバーから正しい応答が返りませんでした"); }
  if (!response.ok) {
    const detail = result.detail;
    throw new Error(typeof detail === "string" ? detail : "入力内容を確認してください");
  }
  return result;
}
const jsonOptions = (method, data) => ({
  method, headers: { "Content-Type": "application/json" }, body: JSON.stringify(data)
});
function notify(text) {
  const element = $("notice");
  element.textContent = text;
  element.hidden = false;
  clearTimeout(noticeTimer);
  noticeTimer = setTimeout(() => { element.hidden = true; }, 5000);
}
async function safe(action) {
  try { await action(); }
  catch (error) { notify(error.message || "操作に失敗しました"); }
}
function element(tag, className, text) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text !== undefined) node.textContent = text;
  return node;
}
function avatar(match, large = false) {
  const node = element("span", "avatar" + (large ? " avatar-lg" : ""));
  if (match.photo) {
    const img = document.createElement("img");
    img.src = "/api/matches/" + match.id + "/photo";
    img.alt = "";
    node.append(img);
  } else {
    node.textContent = match.name.slice(0, 1);
  }
  return node;
}
function setView(next) {
  state.view = next;
  for (const view of ["chat", "like", "profile"]) {
    $("view-" + view).hidden = view !== next;
    $("nav-" + view).classList.toggle("selected", view === next);
  }
}
function selectedMatch() {
  return state.matches.find(m => m.id === state.selectedId) || null;
}
async function loadMatches() {
  state.matches = await api("/matches");
  if (state.selectedId !== null && !selectedMatch()) state.selectedId = null;
  renderMatchList();
}
function renderMatchList() {
  const list = $("match-list");
  list.replaceChildren();
  if (!state.matches.length) list.append(element("p", "muted-item", "「＋」から相手を登録してください"));
  for (const match of state.matches) {
    const item = element("button", "match-item" + (state.selectedId === match.id ? " active" : ""));
    item.type = "button";
    item.append(avatar(match));
    const details = element("span", "match-item-text");
    details.append(element("strong", "", match.name), element("small", "", match.description || "プロフィール未登録"));
    item.append(details);
    item.addEventListener("click", () => safe(() => selectMatch(match.id)));
    list.append(item);
  }
}
async function selectMatch(id) {
  state.selectedId = id;
  const match = selectedMatch();
  if (!match) return;
  setView("chat");
  $("current-avatar").replaceWith(Object.assign(avatar(match, true), { id: "current-avatar" }));
  $("current-name").textContent = match.name;
  $("current-subtitle").textContent = match.description ? match.description.slice(0, 70) : "プロフィール未登録";
  $("empty-chat").hidden = true;
  $("chat-content").hidden = false;
  $("edit-match").hidden = false;
  $("generate-reply").disabled = false;
  $("reply-results").replaceChildren();
  renderMatchList();
  await reloadMessages();
}
async function reloadMessages() {
  if (state.selectedId === null) return;
  const expectedId = state.selectedId;
  const messages = await api("/matches/" + expectedId + "/messages");
  if (state.selectedId !== expectedId) return;
  state.messages = messages;
  renderMessages();
}
function renderMessages() {
  const root = $("chat-messages");
  root.replaceChildren();
  if (!state.messages.length) {
    root.append(element("p", "chat-tip", "ここに会話が表示されます。まずは相手からのメッセージを追加してください。"));
    return;
  }
  for (const msg of state.messages) {
    const row = element("div", "message-row " + msg.role);
    const bubble = element("div", "message-bubble", msg.body);
    const actions = element("div", "message-actions");
    const edit = element("button", "", "編集");
    edit.type = "button";
    edit.addEventListener("click", () => safe(async () => {
      const body = prompt("メッセージを編集", msg.body);
      if (body === null || !body.trim()) return;
      await api("/matches/" + state.selectedId + "/messages/" + msg.id,
        jsonOptions("PUT", { role: msg.role, body: body.trim() }));
      await reloadMessages();
      $("reply-results").replaceChildren();
    }));
    const remove = element("button", "", "削除");
    remove.type = "button";
    remove.addEventListener("click", () => safe(async () => {
      if (!confirm("このメッセージを削除しますか？")) return;
      await api("/matches/" + state.selectedId + "/messages/" + msg.id, { method: "DELETE" });
      await reloadMessages();
      $("reply-results").replaceChildren();
    }));
    actions.append(edit, remove);
    row.append(bubble, actions);
    root.append(row);
  }
  root.scrollTop = root.scrollHeight;
}
function openMatchDialog(match = null) {
  state.editingId = match ? match.id : null;
  $("match-dialog-title").textContent = match ? "相手のプロフィールを編集" : "相手を登録";
  $("match-name").value = match?.name || "";
  $("match-description").value = match?.description || "";
  $("match-photo").value = "";
  $("delete-match").hidden = !match;
  $("match-dialog").showModal();
}
function closeMatchDialog() { $("match-dialog").close(); }

async function saveMatch(event) {
  event.preventDefault();
  await safe(async () => {
    const data = { name: $("match-name").value.trim(), description: $("match-description").value.trim() };
    if (!data.name) throw new Error("相手の名前を入力してください");
    const editing = state.editingId;
    const saved = await api(editing ? "/matches/" + editing : "/matches",
      jsonOptions(editing ? "PUT" : "POST", data));
    const photo = $("match-photo").files[0];
    if (photo) {
      if (photo.size > 5 * 1024 * 1024) throw new Error("写真は5MB以下にしてください（プロフィール本文は保存済みです）");
      const form = new FormData();
      form.append("file", photo);
      await api("/matches/" + saved.id + "/photo", { method: "PUT", body: form });
    }
    closeMatchDialog();
    await loadMatches();
    await selectMatch(saved.id);
    notify("相手の情報を保存しました");
  });
}
async function deleteSelectedMatch() {
  await safe(async () => {
    if (state.editingId === null || !confirm("相手の情報・写真・会話履歴をすべて削除しますか？元に戻せません。")) return;
    await api("/matches/" + state.editingId, { method: "DELETE" });
    state.selectedId = null;
    closeMatchDialog();
    await loadMatches();
    $("empty-chat").hidden = false;
    $("chat-content").hidden = true;
    $("edit-match").hidden = true;
    $("generate-reply").disabled = true;
    $("reply-results").replaceChildren();
    $("current-avatar").replaceWith(Object.assign(element("span", "avatar avatar-lg", "?"), { id: "current-avatar" }));
    $("current-name").textContent = "相手を選択";
    $("current-subtitle").textContent = "相手ごとに会話を管理できます";
    notify("削除しました");
  });
}
async function saveMessage(event) {
  event.preventDefault();
  if (state.selectedId === null) return;
  await safe(async () => {
    const body = $("message-body").value.trim();
    if (!body) return;
    const role = document.querySelector("input[name=role]:checked").value;
    await api("/matches/" + state.selectedId + "/messages", jsonOptions("POST", { role, body }));
    $("message-body").value = "";
    $("reply-results").replaceChildren();
    await reloadMessages();
    notify("会話履歴に追加しました");
  });
}
async function copyText(value) {
  try {
    await navigator.clipboard.writeText(value);
    notify("文章をコピーしました（送信済みには記録されません）");
  } catch {
    prompt("以下の文章をコピーしてください", value);
  }
}
function renderSuggestions(targetId, data, allowRecord) {
  const root = $(targetId);
  root.replaceChildren();
  if (data.demo) root.append(element("div", "hint-box", "デモモード：APIキーが未設定です。内容は入力文を解析していない固定サンプルです。"));
  const options = [data.recommended, ...data.alternatives];
  options.forEach((option, index) => {
    const card = element("div", "result-card" + (index === 0 ? " featured" : ""));
    const header = element("div", "result-header");
    header.append(element("strong", "", option.label));
    if (index === 0) header.append(element("span", "tag", "おすすめ"));
    card.append(header, element("p", "result-text", option.text));
    const buttons = element("div", "result-buttons");
    const copy = element("button", "", "コピー");
    copy.type = "button";
    copy.addEventListener("click", () => copyText(option.text));
    buttons.append(copy);
    if (allowRecord && !data.demo) {
      const record = element("button", "", "送信済みに記録");
      record.type = "button";
      const matchId = state.selectedId;
      record.addEventListener("click", () => safe(async () => {
        if (state.selectedId !== matchId) throw new Error("相手を選び直してください");
        const body = prompt("実際に送った文章に編集し、OKで履歴へ記録します。未送信ならキャンセルしてください。", option.text);
        if (body === null) return;
        if (!body.trim()) throw new Error("文章が空です");
        await api("/matches/" + matchId + "/messages", jsonOptions("POST", { role: "me", body: body.trim() }));
        await reloadMessages();
        $("reply-results").replaceChildren();
        notify("送信済みの文章を履歴へ記録しました");
      }));
      buttons.append(record);
    }
    card.append(buttons);
    root.append(card);
  });
  root.append(element("p", "result-reason", data.reason));
}
async function runGeneration(mode) {
  const button = mode === "reply" ? $("generate-reply") : $("like-form").querySelector("button[type=submit]");
  const old = button.textContent;
  button.disabled = true;
  button.textContent = "考えています…";
  try {
    let input;
    if (mode === "reply") {
      input = { mode: "reply", match_id: state.selectedId };
    } else {
      input = { mode: "like", name: $("like-name").value.trim(), description: $("like-description").value.trim() };
    }
    const currentId = state.selectedId;
    const data = await api("/generate", jsonOptions("POST", input));
    if (mode === "reply" && currentId !== state.selectedId) return;
    renderSuggestions(mode === "reply" ? "reply-results" : "like-results", data, mode === "reply");
  } finally {
    button.disabled = mode === "reply" ? state.selectedId === null : false;
    button.textContent = old;
  }
}
async function loadProfile() {
  const profile = await api("/profile");
  $("profile-content").value = profile.content;
  $("profile-avoid").value = profile.avoid;
}
async function saveProfile(event) {
  event.preventDefault();
  await safe(async () => {
    await api("/profile", jsonOptions("PUT", {
      content: $("profile-content").value, avoid: $("profile-avoid").value
    }));
    notify("プロフィールを保存しました");
  });
}
async function bootstrap() {
  ["chat", "like", "profile"].forEach(v => $("nav-" + v).addEventListener("click", () => setView(v)));
  $("add-match").addEventListener("click", () => openMatchDialog());
  $("empty-add").addEventListener("click", () => openMatchDialog());
  $("edit-match").addEventListener("click", () => openMatchDialog(selectedMatch()));
  $("cancel-match").addEventListener("click", closeMatchDialog);
  $("cancel-match-bottom").addEventListener("click", closeMatchDialog);
  $("delete-match").addEventListener("click", deleteSelectedMatch);
  $("match-form").addEventListener("submit", saveMatch);
  $("message-form").addEventListener("submit", saveMessage);
  $("profile-form").addEventListener("submit", saveProfile);
  $("generate-reply").addEventListener("click", () => safe(() => runGeneration("reply")));
  $("like-form").addEventListener("submit", e => {
    e.preventDefault();
    safe(() => runGeneration("like"));
  });
  await safe(async () => {
    const [status] = await Promise.all([api("/status"), loadMatches(), loadProfile()]);
    $("status-dot").classList.toggle("demo", status.demo);
    $("status-text").textContent = status.demo ? "デモモード" : "Gemini: " + status.model;
    if (state.matches.length) await selectMatch(state.matches[0].id);
  });
}
document.addEventListener("DOMContentLoaded", bootstrap);
