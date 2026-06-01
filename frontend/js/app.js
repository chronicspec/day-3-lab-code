document.addEventListener('DOMContentLoaded', () => {
    const chatForm = document.getElementById('chat-form');
    const userInput = document.getElementById('user-input');
    const chatBox = document.getElementById('chat-box');
    const chatMessages = document.getElementById('chat-messages');
    const suggestionContainer = document.getElementById('suggestion-container');
    const btnSubmit = document.getElementById('btn-submit');

    // API Endpoint kết nối Backend
    const API_URL = 'http://127.0.0.1:8000/api/chat';

    // 1. Lắng nghe sự kiện gửi câu hỏi từ Form
    chatForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const message = userInput.value.trim();
        if (!message) return;

        // Ẩn các thẻ gợi ý kiểu ChatGPT khi bắt đầu chat
        if (suggestionContainer) {
            suggestionContainer.style.display = 'none';
        }

        // Đẩy tin nhắn của User lên màn hình
        appendUserMessage(message);
        userInput.value = '';

        // Đóng băng trạng thái nút bấm và hiển thị icon loading
        btnSubmit.disabled = true;
        btnSubmit.innerHTML = `<i class="fa-solid fa-spinner animate-spin text-sm"></i>`;
        
        const agentMessageId = 'agent-' + Date.now();
        const traceContainerId = 'trace-' + Date.now();
        
        // Tạo khung giữ chỗ tạm thời cho AI (Placeholder)
        appendAgentPlaceholder(agentMessageId, traceContainerId);

        try {
            // Gửi yêu cầu phân tích ReAct sang Backend API
            const response = await fetch(API_URL, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: message })
            });
            const data = await response.json();

            if (data.status === 'success') {
                // Đổ danh sách suy nghĩ (Traces log) vào khối Accordion
                renderAgentTraces(traceContainerId, data.traces);
                // Hiển thị câu trả lời cuối cùng sạch sẽ sau khi định dạng
                renderAgentFinalAnswer(agentMessageId, data.response);
            } else {
                throw new Error(data.detail || 'Lỗi hệ thống nội bộ.');
            }
        } catch (error) {
            document.getElementById(agentMessageId).innerHTML = `<span class="text-red-400">❌ Lỗi kết nối: ${error.message}</span>`;
        } finally {
            // Giải phóng trạng thái nút bấm
            btnSubmit.disabled = false;
            btnSubmit.innerHTML = `<i class="fa-solid fa-arrow-up text-sm"></i>`;
            chatBox.scrollTop = chatBox.scrollHeight;
        }
    });

    // 2. Hàm xử lý khi chọn Thẻ gợi ý mẫu (Prompt Card)
    window.selectSuggestion = function(text) {
        userInput.value = text;
        // Kích hoạt giả lập submit form tự động
        chatForm.dispatchEvent(new Event('submit'));
    };

    // 3. Hàm ẩn/hiện khối suy nghĩ (Toggle Accordion) kiểu DeepSeek
    window.toggleThinking = function(elementId) {
        const block = document.getElementById(elementId);
        const icon = document.getElementById('icon-' + elementId);
        if (block.classList.contains('hidden')) {
            block.classList.remove('hidden');
            icon.className = "fa-solid fa-chevron-down text-[10px]";
        } else {
            block.classList.add('hidden');
            icon.className = "fa-solid fa-chevron-right text-[10px]";
        }
    };

    // 4. Hàm render Tin nhắn Người dùng
    function appendUserMessage(text) {
        const html = `
            <div class="flex gap-4 items-start flex-row-reverse">
                <div class="h-8 w-8 rounded-full bg-emerald-600 flex items-center justify-center text-xs font-bold text-white shrink-0 shadow-sm">ME</div>
                <div class="bg-blue-600/10 text-blue-200 p-3.5 rounded-2xl rounded-tr-none border border-blue-500/20 text-sm whitespace-pre-wrap max-w-2xl leading-relaxed">
                    ${text.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")}
                </div>
            </div>`;
        chatMessages.insertAdjacentHTML('beforeend', html);
        chatBox.scrollTop = chatBox.scrollHeight;
    }

    // 5. Hàm tạo khung chờ cho Agent
    function appendAgentPlaceholder(agentMessageId, traceContainerId) {
        const html = `
            <div class="flex gap-4 items-start">
                <div class="h-8 w-8 rounded-full bg-blue-500 flex items-center justify-center text-xs font-bold text-white shrink-0 shadow-md">AI</div>
                <div class="space-y-3 w-full max-w-2xl">
                    <div class="border-l-2 border-gray-700 pl-3 py-1">
                        <button type="button" onclick="toggleThinking('${traceContainerId}')" class="text-xs text-gray-500 hover:text-gray-400 flex items-center gap-2 focus:outline-none cursor-pointer">
                            <i id="icon-${traceContainerId}" class="fa-solid fa-chevron-down text-[10px]"></i>
                            <span class="font-medium tracking-wide">Process Thinking (Xử lý tác tử)...</span>
                        </button>
                        <div id="${traceContainerId}" class="mt-2 space-y-2 font-mono text-[11px] text-gray-400 bg-[#121222] p-3 rounded-xl border border-[#1e1e35] transition-all">
                            <div class="animate-pulse text-amber-400">&gt; Agent đang kích hoạt chu trình ReAct Loop...</div>
                        </div>
                    </div>
                    <div id="${agentMessageId}" class="text-sm text-gray-200 leading-relaxed whitespace-pre-wrap py-1">
                        <i class="fa-solid fa-circle-notch animate-spin text-blue-400 text-xs"></i> <span class="text-xs text-gray-500 italic">Đang xuất kết quả lịch trình...</span>
                    </div>
                </div>
            </div>`;
        chatMessages.insertAdjacentHTML('beforeend', html);
        chatBox.scrollTop = chatBox.scrollHeight;
    }

    // 6. Điền thông tin chuỗi suy nghĩ trung gian của Agent
    function renderAgentTraces(containerId, traces) {
        const container = document.getElementById(containerId);
        if (!traces || traces.length === 0) {
            container.innerHTML = `<div class="text-gray-600">Không có dữ liệu công cụ trung gian.</div>`;
            return;
        }

        let html = '';
        traces.forEach(t => {
            html += `
                <div class="border-b border-[#1e1e32] pb-2 mb-2 last:border-none last:pb-0 last:mb-0">
                    <div class="text-blue-400 font-bold">[Vòng lập luận #${t.step}]</div>
                    <div class="text-gray-400 mt-0.5"><span class="text-purple-400">🧠 Thought:</span> ${t.thought}</div>
                    <div class="text-amber-400 mt-0.5"><span class="text-amber-500">🛠️ Action (Tool):</span> ${t.action}</div>
                    <div class="text-emerald-400 mt-0.5 max-h-24 overflow-y-auto bg-[#0b0b14] p-1.5 rounded mt-1 border border-[#1a1a2e]"><span class="text-emerald-500">📥 Observation:</span> ${t.observation}</div>
                </div>`;
        });
        container.innerHTML = html;
    }

    // 7. Định dạng văn bản Markdown thô sang HTML sạch sẽ đẹp mắt
    function renderAgentFinalAnswer(messageId, responseText) {
        const messageDiv = document.getElementById(messageId);
        
        let cleanHtml = responseText.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
        // Convert **bold text**
        cleanHtml = cleanHtml.replace(/\*\*(.*?)\*\*/g, '<strong class="text-blue-400 font-bold">$1</strong>');
        // Convert gạch đầu dòng bullet-point
        cleanHtml = cleanHtml.replace(/^\s*-\s*(.*)/gm, '<div class="flex items-start gap-2 my-1"><span class="text-blue-500">•</span><span>$1</span></div>');
        // Giữ nguyên ký tự xuống dòng
        cleanHtml = cleanHtml.replace(/\n/g, '<br>');

        messageDiv.innerHTML = cleanHtml;
    }
});