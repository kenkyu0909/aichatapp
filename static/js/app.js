/* ==========================================
   Application State
   ========================================== */
const state = {
    currentMatchId: null,
    myProfile: {},
    matches: [],
    init: async function() {
        await this.loadProfile();
        await this.loadMatches();
        this.setupEventListeners();
        // Set chat tab as default
        document.getElementById('chatTab').classList.add('active');
    },
    
    loadProfile: async function() {
        try {
            const res = await fetch('/api/profile');
            const data = await res.json();
            if (data && data.fields) {
                state.myProfile = data.fields;
                this.updateProfileDisplay();
            }
        } catch (e) {
            console.error('Failed to load profile:', e);
            // Profile will be managed by server, initialize empty
            state.myProfile = {};
        }
    },
    
    saveProfile: async function(fields) {
        try {
            const res = await fetch('/api/profile', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ fields })
            });
            const data = await res.json();
            if (data && data.status === 'ok') {
                state.myProfile = data.fields;
                this.updateProfileDisplay();
                // Switch to chat tab after saving
                this.switchTab('chatTab');
                return true;
            }
        } catch (e) {
            console.error('Failed to save profile:', e);
        }
        return false;
    },
    
    switchTab: function(tabId) {
        // Remove 'active' class from all tabs
        document.querySelectorAll('.tab-panel').forEach(tab => {
            tab.classList.remove('active');
        });
        // Add 'active' class to target tab
        const targetTab = document.getElementById(tabId);
        if (targetTab) {
            targetTab.classList.add('active');
        }
    },
    
    updateProfileDisplay: function() {
        if (!state.myProfile) return;
        document.getElementById('profileName').value = state.myProfile.name || '';
        document.getElementById('profileAge').value = state.myProfile.age || '';
        document.getElementById('profileArea').value = state.myProfile.area || '';
        document.getElementById('profileJob').value = state.myProfile.job || '';
        document.getElementById('profileHobby').value = state.myProfile.hobby || '';
        document.getElementById('profilePersonality').value = state.myProfile.personality || '';
        document.getElementById('profileTalkStyle').value = state.myProfile.talk_style || '';
        document.getElementById('profileDontWant').value = state.myProfile.dont_want || '';
        document.getElementById('profileGoal').value = state.myProfile.goal || '';
    },
    
    loadMatches: async function() {
        try {
            const res = await fetch('/api/matches');
            const data = await res.json();
            if (data.matches) {
                state.matches = data.matches;
                this.renderMatches();
                this.updateMatchSelect();
            }
        } catch (e) {
            console.error('Failed to load matches:', e);
        }
    },
    
    renderMatches: function() {
        const list = document.getElementById('matchesList');
        if (state.matches.length === 0) {
            list.innerHTML = '<p class="empty-state">相手がいません。上記ボタンから追加してください。</p>';
            return;
        }
        
        let html = '';
        state.matches.forEach((match, index) => {
            const lastMsg = match.lastMessage ? 
                `<div class="match-preview">${match.lastMessage.text.substring(0, 20)}${match.lastMessage.text.length > 20 ? '...' : ''}</div>` : '';
            html += `
                <div class="match-item" data-id="${match.id}" ${index === 0 ? 'class="selected"' : ''}>
                    <img src="${match.image_path || '/static/images/default-thumbnail.png'" alt="${match.name}" class="match-thumbnail">
                    <div class="match-info">
                        <div class="match-name">${match.name || '無名'}</div>
                        ${lastMsg}
                    </div>
                    <button class="delete-match-btn" onclick="event.stopPropagation(); deleteMatch(${match.id})">×</button>
                </div>
            `;
        });
        
        list.innerHTML = html;
        
        // Add click handler to all match items
        document.querySelectorAll('.match-item:not(.delete-match-btn)').forEach(item => {
            item.addEventListener('click', () => {
                const id = parseInt(item.dataset.id);
                state.currentMatchId = id;
                this.selectMatch(id);
                this.renderMatches();
            });
        });
    },
    
    updateMatchSelect: function() {
        const select = document.getElementById('matchSelect');
        select.innerHTML = '<option value="">相手を選択してください</option>';
        
        state.matches.forEach(match => {
            const opt = document.createElement('option');
            opt.value = match.id;
            opt.textContent = match.name || '無名';
            select.appendChild(opt);
        });
    },
    
    selectMatch: function(matchId) {
        state.currentMatchId = matchId;
        
        // Update UI
        document.querySelectorAll('.match-item').forEach(item => {
            item.classList.toggle('selected', parseInt(item.dataset.id) === matchId);
        });
        
        // Load conversation history
        this.loadConversationHistory();
    },
    
    loadConversationHistory: async function() {
        if (!state.currentMatchId) {
            document.getElementById('messagesList').innerHTML = '<p class="empty-state">メッセージがありません。</p>';
            return;
        }
        
        try {
            const res = await fetch(`/api/messages/${state.currentMatchId}`);
            const data = await res.json();
            if (data.messages && data.messages.length > 0) {
                this.renderMessages(data.messages);
            } else {
                document.getElementById('messagesList').innerHTML = '<p class="empty-state">メッセージがありません。</p>';
            }
        } catch (e) {
            console.error('Failed to load messages:', e);
        }
    },
    
    renderMessages: function(messages) {
        const list = document.getElementById('messagesList');
        
        if (messages.length === 0) {
            list.innerHTML = '<p class="empty-state">メッセージがありません。</p>';
            return;
        }
        
        let html = '';
        messages.forEach((msg, i) => {
            const senderClass = msg.sender === 'me' ? 'me' : 'them';
            const senderText = msg.sender === 'me' ? '私' : '相手';
            html += `
                <div class="message-item ${senderClass}" style="justify-content: ${msg.sender === 'me' ? 'flex-end' : 'flex-start'}">
                    <span>${senderText}: ${escapeHtml(msg.text)}</span>
                </div>
            `;
        });
        
        list.innerHTML = html;
    },
    
    escapeHtml: function(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    },
    
    addMessage: async function() {
        const input = document.getElementById('newMessageInput');
        const text = input.value.trim();
        if (!text || !state.currentMatchId) return;
        
        try {
            await fetch('/api/messages', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    match_id: state.currentMatchId,
                    sender: 'me',
                    text: text
                })
            });
            
            input.value = '';
            this.loadConversationHistory();
        } catch (e) {
            console.error('Failed to add message:', e);
        }
    },
    
    async generateReply() {
        if (!state.currentMatchId) {
            alert('相手を選択してください');
            return;
        }
        
        // Check if Gemini API is available
        if (!window.geminiAvailable) {
            document.getElementById('apiError').style.display = 'block';
            return;
        }
        
        // Get conversation history
        const messages = this.getMessagesFromUI();
        
        try {
            const res = await fetch('/api/generate/reply', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    mode: 'reply',
                    match_id: state.currentMatchId,
                    conversation_history: messages,
                    my_profile_fields: state.myProfile
                })
            });
            
            const data = await res.json();
            
            if (data.status === 'success') {
                this.displayReplyCandidates(data.data);
            } else {
                alert('返信生成に失敗しました');
            }
        } catch (e) {
            console.error('Failed to generate reply:', e);
            // Fall back to mock
            this.displayMockReply();
        }
    },
    
    getMessagesFromUI: function() {
        const messages = [];
        document.querySelectorAll('.message-item').forEach(item => {
            const sender = item.classList.contains('me') ? 'me' : 'them';
            const text = item.querySelector('span')?.textContent || '';
            messages.push({ sender, text });
        });
        // Reverse so oldest first
        return messages;
    },
    
    displayReplyCandidates: function(data) {
        const container = document.getElementById('replyCandidates');
        
        if (!data || !data.recommended) {
            container.innerHTML = '<p class="empty-state">候補が生成されませんでした。</p>';
            return;
        }
        
        let html = '';
        
        // Recommended candidate
        const recommended = data.recommended;
        html += `
            <div class="candidate-card recommended" id="recommendedCandidate">
                <div class="candidate-label">${recommended.label}</div>
                <div class="candidate-text" id="recommendedText">${recommended.text}</div>
                <div style="margin-top: 12px; display: flex; justify-content: flex-end;">
                    <button class="copy-btn" onclick="copyToClipboard('recommendedText')">コピー</button>
                </div>
            </div>
        `;
        
        // Alternatives
        if (data.alternatives && data.alternatives.length > 0) {
            data.alternatives.forEach((alt, i) => {
                html += `
                    <div class="candidate-card" id="alternative${i}">
                        <div class="candidate-label">${alt.label}</div>
                        <div class="candidate-text" id="alternativeText${i}">${alt.text}</div>
                        <div style="margin-top: 12px; display: flex; justify-content: flex-end;">
                            <button class="copy-btn" onclick="copyToClipboard('alternativeText${i}')">コピー</button>
                        </div>
                    </div>
                `;
            });
        }
        
        // Reason
        if (data.reason) {
            html += `
                <div style="margin-top: 12px; padding-top: 12px; border-top: 1px solid var(--border-color); font-size: 12px; color: var(--text-secondary);">
                    推奨の理由: ${data.reason}
                </div>
            `;
        }
        
        container.innerHTML = html;
    },
    
    displayMockReply: function() {
        const html = `
            <div class="candidate-card recommended">
                <div class="candidate-label">自然体</div>
                <div class="candidate-text">素敵ですね！その話、とても興味深いです。もう少し詳しく教えていただけますか？</div>
                <div style="margin-top: 12px; display: flex; justify-content: flex-end;">
                    <button class="copy-btn" onclick="copyToClipboard('recommendedText')">コピー</button>
                </div>
            </div>
            <div class="candidate-card">
                <div class="candidate-label">少し親しみやすい</div>
                <div class="candidate-text">その経験、とても面白そう！どうやって始めたんですか？</div>
                <div style="margin-top: 12px; display: flex; justify-content: flex-end;">
                    <button class="copy-btn" onclick="copyToClipboard('alternativeText0')">コピー</button>
                </div>
            </div>
            <div class="candidate-card">
                <div class="candidate-label">会話を広げる</div>
                <div class="candidate-text">その分野にはまっているそうですね！何がそこが好きなんですか？</div>
                <div style="margin-top: 12px; display: flex; justify-content: flex-end;">
                    <button class="copy-btn" onclick="copyToClipboard('alternativeText1')">コピー</button>
                </div>
            </div>
            <div style="margin-top: 12px; padding-top: 12px; border-top: 1px solid var(--border-color); font-size: 12px; color: var(--text-secondary);">
                推奨の理由: 相手の話に対する自然な関心から生成しました
            </div>
        `;
        
        document.getElementById('replyCandidates').innerHTML = html;
    },
    
    copyToClipboard: function(elementId) {
        const element = document.getElementById(elementId);
        if (!element) return;
        
        const text = element.textContent || element.innerText;
        navigator.clipboard.writeText(text).then(() => {
            // Visual feedback
            const btn = element.nextElementSibling;
            if (btn && btn.classList.contains('copy-btn')) {
                btn.textContent = 'コピー完了';
                btn.classList.add('copied');
                setTimeout(() => {
                    btn.textContent = 'コピー';
                    btn.classList.remove('copied');
                }, 2000);
            }
        });
    },
    
    async addMessageToUI: function(sender, text) {
        const list = document.getElementById('messagesList');
        const senderClass = sender === 'me' ? 'me' : 'them';
        const senderText = sender === 'me' ? '私' : '相手';
        
        const div = document.createElement('div');
        div.className = `message-item ${senderClass}`;
        div.style.justifyContent = sender === 'me' ? 'flex-end' : 'flex-start';
        div.innerHTML = `<span>${senderText}: ${escapeHtml(text)}</span>`;
        
        list.appendChild(div);
        list.scrollTop = list.scrollHeight;
    },
    
    // Like Generation
    async generateLike: async function() {
        const profileText = document.getElementById('likePartnerProfile').value.trim();
        const partnerName = document.getElementById('likePartnerName').value.trim();
        
        if (!profileText) {
            alert('相手のプロフィールを貼り付けてください');
            return;
        }
        
        // Check if Gemini API is available
        if (!window.geminiAvailable) {
            document.getElementById('likeApiError').style.display = 'block';
            return;
        }
        
        try {
            const res = await fetch('/api/generate/like', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    mode: 'like',
                    partner_profile: profileText,
                    partner_name: partnerName,
                    my_profile_fields: state.myProfile
                })
            });
            
            const data = await res.json();
            
            if (data.status === 'success') {
                this.displayLikeCandidates(data.data);
            } else {
                alert('メッセージ生成に失敗しました');
            }
        } catch (e) {
            console.error('Failed to generate like message:', e);
            this.displayMockLike();
        }
    },
    
    displayLikeCandidates: function(data) {
        const container = document.getElementById('likeCandidates');
        
        if (!data || !data.recommended) {
            container.innerHTML = '<p class="empty-state">候補が生成されませんでした。</p>';
            return;
        }
        
        let html = '';
        
        // Recommended
        const recommended = data.recommended;
        html += `
            <div class="candidate-card recommended">
                <div class="candidate-label">${recommended.label}</div>
                <div class="candidate-text" id="likeRecommendedText">${recommended.text}</div>
                <div style="margin-top: 12px; display: flex; justify-content: flex-end;">
                    <button class="copy-btn" onclick="copyLikeToClipboard('likeRecommendedText')">コピー</button>
                </div>
            </div>
        `;
        
        // Alternatives
        if (data.alternatives && data.alternatives.length > 0) {
            data.alternatives.forEach((alt, i) => {
                html += `
                    <div class="candidate-card">
                        <div class="candidate-label">${alt.label}</div>
                        <div class="candidate-text" id="likeAlternativeText${i}">${alt.text}</div>
                        <div style="margin-top: 12px; display: flex; justify-content: flex-end;">
                            <button class="copy-btn" onclick="copyLikeToClipboard('likeAlternativeText${i}')">コピー</button>
                        </div>
                    </div>
                `;
            });
        }
        
        // Reason
        if (data.reason) {
            html += `
                <div style="margin-top: 12px; padding-top: 12px; border-top: 1px solid var(--border-color); font-size: 12px; color: var(--text-secondary);">
                    推奨の理由: ${data.reason}
                </div>
            `;
        }
        
        container.innerHTML = html;
    },
    
    displayMockLike: function() {
        const namePart = document.getElementById('likePartnerName').value.trim() ? 
            document.getElementById('likePartnerName').value.trim() + 'さん、' : '';
        
        const html = `
            <div class="candidate-card recommended">
                <div class="candidate-label">自然体</div>
                <div class="candidate-text">${namePart}素敵なプロフィールですね！興味を持ちました。</div>
                <div style="margin-top: 12px; display: flex; justify-content: flex-end;">
                    <button class="copy-btn" onclick="copyLikeToClipboard('likeRecommendedText')">コピー</button>
                </div>
            </div>
            <div class="candidate-card">
                <div class="candidate-label">少し親しみやすい</div>
                <div class="candidate-text">${namePart}その話、とても気になります！詳しく教えていただけますか？</div>
                <div style="margin-top: 12px; display: flex; justify-content: flex-end;">
                    <button class="copy-btn" onclick="copyLikeToClipboard('likeAlternativeText0')">コピー</button>
                </div>
            </div>
            <div class="candidate-card">
                <div class="candidate-label">会話を広げる</div>
                <div class="candidate-text">${namePart}同じような経験があって驚きました！どういうきっかけで始めたんですか？</div>
                <div style="margin-top: 12px; display: flex; justify-content: flex-end;">
                    <button class="copy-btn" onclick="copyLikeToClipboard('likeAlternativeText1')">コピー</button>
                </div>
            </div>
            <div style="margin-top: 12px; padding-top: 12px; border-top: 1px solid var(--border-color); font-size: 12px; color: var(--text-secondary);">
                推奨の理由: 相手のプロフィールから自然な導入文を作成しました
            </div>
        `;
        
        document.getElementById('likeCandidates').innerHTML = html;
    }
};

/* ==========================================
   Event Listeners
   ========================================== */
document.addEventListener('DOMContentLoaded', async function() {
    await state.init();
    
    // Profile save
    document.getElementById('saveProfileBtn').addEventListener('click', async function() {
        const fields = {
            name: document.getElementById('profileName').value.trim(),
            age: document.getElementById('profileAge').value.trim(),
            area: document.getElementById('profileArea').value.trim(),
            job: document.getElementById('profileJob').value.trim(),
            hobby: document.getElementById('profileHobby').value.trim(),
            personality: document.getElementById('profilePersonality').value.trim(),
            talk_style: document.getElementById('profileTalkStyle').value.trim(),
            dont_want: document.getElementById('profileDontWant').value.trim(),
            goal: document.getElementById('profileGoal').value.trim()
        };
        
        await state.saveProfile(fields);
    });
    
    // Add message
    document.getElementById('addMessageBtn').addEventListener('click', state.addMessage);
    
    // New message input Enter key
    document.getElementById('newMessageInput').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            state.addMessage();
        }
    });
    
    // Generate reply
    document.getElementById('generateReplyBtn').addEventListener('click', state.generateReply);
    
    // Like generation
    document.getElementById('generateLikeBtn').addEventListener('click', state.generateLike);
    
    // Match selection
    document.getElementById('matchSelect').addEventListener('change', function() {
        const id = parseInt(this.value);
        state.selectMatch(id);
    });
});

// Initialize on load
document.addEventListener('DOMContentLoaded', () => {
    state.init();
});
