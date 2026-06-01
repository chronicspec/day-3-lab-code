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
        const metricsContainerId = 'metrics-' + Date.now();

        // Gọi khởi tạo khung trống
        appendAgentPlaceholder(agentMessageId, traceContainerId, metricsContainerId);

        try {
            // Gửi yêu cầu phân tích ReAct sang Backend API
            const response = await fetch(API_URL, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: message })
            });
            const data = await response.json();

            if (data.status === 'success') {
                renderAgentTraces(traceContainerId, data.traces);
                renderAgentMetrics(metricsContainerId, data.metrics);
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
    function appendAgentPlaceholder(agentMessageId, traceContainerId, metricsContainerId) {
        const html = `
            <div class="flex gap-4 items-start">
                <div class="h-8 w-8 rounded-full bg-blue-500 flex items-center justify-center text-xs font-bold text-white shrink-0 shadow-md">AI</div>
                <div class="space-y-3 w-full max-w-2xl">
                    
                    <div class="border-l-2 border-gray-700 pl-3 py-1 bg-[#11111e]/40 pr-3 rounded-r-xl">
                        <div class="flex items-center justify-between border-b border-[#1e1e32] pb-1.5 mb-2">
                            <div class="flex gap-3">
                                <button type="button" onclick="switchAgentTab('${traceContainerId}', '${metricsContainerId}', 'thinking')" 
                                        class="text-xs text-blue-400 font-medium focus:outline-none cursor-pointer flex items-center gap-1">
                                    <i class="fa-solid fa-brain text-[10px]"></i> Process Thinking
                                </button>
                                <button type="button" onclick="switchAgentTab('${traceContainerId}', '${metricsContainerId}', 'metrics')" 
                                        class="text-xs text-gray-500 hover:text-gray-400 font-medium focus:outline-none cursor-pointer flex items-center gap-1">
                                    <i class="fa-solid fa-chart-bar text-[10px]"></i> Telemetry Metrics (Lab Eval)
                                </button>
                            </div>
                            <button type="button" onclick="toggleThinkingBlock('${traceContainerId}', '${metricsContainerId}')" class="text-gray-600 hover:text-gray-400">
                                <i id="icon-toggle-${traceContainerId}" class="fa-solid fa-chevron-down text-[10px]"></i>
                            </button>
                        </div>
                        
                        <div id="${traceContainerId}" class="space-y-2 font-mono text-[11px] text-gray-400 bg-[#121222] p-3 rounded-xl border border-[#1e1e35] transition-all">
                            <div class="animate-pulse text-amber-400">&gt; Agent đang kích hoạt chu trình ReAct Loop...</div>
                        </div>
                        
                        <div id="${metricsContainerId}" class="hidden font-mono text-[11px] text-gray-400 bg-[#121222] p-3 rounded-xl border border-[#1e1e35] transition-all">
                            <div class="text-gray-600">Đang tính toán tài nguyên hệ thống...</div>
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

// Hàm chuyển đổi qua lại giữa Tab Suy nghĩ và Tab Thống kê chấm điểm
window.switchAgentTab = function(traceId, metricsId, tabType) {
    const traceBlock = document.getElementById(traceId);
    const metricsBlock = document.getElementById(metricsId);
    
    // Tìm các nút bấm điều hướng để đổi màu active
    const container = traceBlock.parentElement;
    const buttons = container.getElementsByTagName('button');

    if (tabType === 'thinking') {
        traceBlock.classList.remove('hidden');
        metricsBlock.classList.add('hidden');
        buttons[0].className = "text-xs text-blue-400 font-medium focus:outline-none cursor-pointer flex items-center gap-1";
        buttons[1].className = "text-xs text-gray-500 hover:text-gray-400 font-medium focus:outline-none cursor-pointer flex items-center gap-1";
    } else {
        traceBlock.classList.add('hidden');
        metricsBlock.classList.remove('hidden');
        buttons[0].className = "text-xs text-gray-500 hover:text-gray-400 font-medium focus:outline-none cursor-pointer flex items-center gap-1";
        buttons[1].className = "text-xs text-blue-400 font-medium focus:outline-none cursor-pointer flex items-center gap-1";
    }
};

// Hàm ẩn/hiện toàn bộ khu vực giám sát (Cả 2 tab)
window.toggleThinkingBlock = function(traceId, metricsId) {
    const traceBlock = document.getElementById(traceId);
    const metricsBlock = document.getElementById(metricsId);
    const icon = document.getElementById('icon-toggle-' + traceId);
    
    if (traceBlock.classList.contains('hidden') && metricsBlock.classList.contains('hidden')) {
        // Mở lại tab suy nghĩ mặc định
        traceBlock.classList.remove('hidden');
        icon.className = "fa-solid fa-chevron-down text-[10px]";
    } else {
        // Ẩn toàn bộ
        traceBlock.classList.add('hidden');
        metricsBlock.classList.add('hidden');
        icon.className = "fa-solid fa-chevron-right text-[10px]";
    }
};

// Hàm mới: Đổ dữ liệu Metrics chấm điểm từ Backend vào giao diện công cụ
function renderAgentMetrics(metricsId, metrics) {
    const container = document.getElementById(metricsId);
    if (!metrics) {
        container.innerHTML = `<div class="text-red-400">Không có dữ liệu Telemetry thu thập.</div>`;
        return;
    }

    container.innerHTML = `
        <div class="grid grid-cols-2 gap-2 text-[11px] font-mono">
            <div class="bg-[#0b0b14] p-2 rounded border border-[#1e1e32]">
                <span class="text-gray-500">📥 Prompt Tokens:</span> 
                <span class="text-white font-bold">${metrics.prompt_tokens}</span>
            </div>
            <div class="bg-[#0b0b14] p-2 rounded border border-[#1e1e32]">
                <span class="text-gray-500">📤 Completion Tokens:</span> 
                <span class="text-white font-bold">${metrics.completion_tokens}</span>
            </div>
            <div class="bg-[#0b0b14] p-2 rounded border border-[#1e1e32]">
                <span class="text-gray-500">⏱️ Tổng thời gian (Latency):</span> 
                <span class="text-amber-400 font-bold">${metrics.latency}</span>
            </div>
            <div class="bg-[#0b0b14] p-2 rounded border border-[#1e1e32]">
                <span class="text-gray-500">💰 Chi phí ước tính (Cost):</span> 
                <span class="text-emerald-400 font-bold">${metrics.cost}</span>
            </div>
        </div>
        <div class="mt-2 text-[10px] text-gray-500 flex items-center gap-1.5 border-t border-[#1e1e32] pt-1.5">
            <span>Trạng thái đánh giá Lab 3:</span>
            <span class="px-1.5 py-0.5 rounded text-[9px] font-bold ${metrics.status === 'PASSED' ? 'bg-emerald-950 text-emerald-400' : 'bg-red-950 text-red-400'}">${metrics.status}</span>
        </div>
    `;
}