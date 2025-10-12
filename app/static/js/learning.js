// static/js/learning.js

document.addEventListener('DOMContentLoaded', () => {
    const chatForm = document.getElementById('chat-form');
    const userInput = document.getElementById('user-input');
    const chatBox = document.getElementById('chat-box');
    const contentArea = document.getElementById('content-area');
    const stepDataContainer = document.getElementById('step-data-container');
    const stepData = JSON.parse(stepDataContainer.dataset.step);

    const codeEditorContainer = document.getElementById('code-editor-container');
    const codeEditor = document.getElementById('code-editor');
    const codeOutput = document.getElementById('code-output');
    const runCodeBtn = document.getElementById('run-code-btn');
    const toggleNavBtn = document.getElementById('toggle-nav-btn');
    const learningSidebar = document.querySelector('.learning-sidebar');
    const typingIndicator = document.getElementById('typing-indicator');
    let editor;
    if (codeEditor) {
        editor = CodeMirror.fromTextArea(codeEditor, {
            lineNumbers: true,         
            mode: "python",            
            theme: "material-darker",  
            indentUnit: 4,             
            lineWrapping: true         
        });
    }
    if (toggleNavBtn && learningSidebar) {
        toggleNavBtn.addEventListener('click', () => {
            learningSidebar.classList.toggle('open');
        });
    }
    // Auto-scroll chatbox
    if (chatBox) {
        chatBox.scrollTop = chatBox.scrollHeight;
    }

    function addMessage(sender, message) {
        const messageDiv = document.createElement('div');
        const roleClass = (sender === 'Anda') ? 'user-message' : 'assistant-message';
        messageDiv.className = `message ${roleClass}`;

        messageDiv.innerHTML = `<p><strong>${sender}:</strong></p><p>${message.replace(/\n/g, '<br>')}</p>`;
        
        chatBox.appendChild(messageDiv);
        chatBox.scrollTop = chatBox.scrollHeight;
    }


    window.handleNextStep = async (next_url = null) => {
        const stepDataContainer = document.getElementById('step-data-container');
        const stepData = JSON.parse(stepDataContainer.dataset.step);
        const moduleName = window.location.pathname.split('/')[2];
        const currentStep = stepData.step;

        await fetch('/clear_step_history', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                module_name: moduleName,
                step_index: currentStep
            })
        });

        if (next_url) {
            window.location.href = next_url;
        } else {
            await fetch('/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ action: 'next_step' })
            });
            
            const nextStepIndex = currentStep + 1;
            window.location.href = `/goto/${moduleName}/${nextStepIndex}`;
        }
    };
    
    function showNextStepButton(next_url = null) {
        const oldButton = document.getElementById('next-step-btn');
        if (oldButton) oldButton.remove();
        
        const mainContent = document.querySelector('.learning-main-content');
        if (!mainContent) return; // Keluar jika kontainer tidak ditemukan

        const nextButton = document.createElement('button');
        nextButton.id = 'next-step-btn';
        nextButton.className = 'button-lanjut'; // Tambahkan class untuk styling
        nextButton.textContent = next_url ? 'Mulai Quiz' : 'Lanjut ke Tahap Berikutnya';
        
        nextButton.onclick = () => window.handleNextStep(next_url);
        
        mainContent.appendChild(nextButton);
    }

    if (runCodeBtn) {
    runCodeBtn.addEventListener('click', async () => {
        const modifiedCode = editor.getValue(); 
        
        codeOutput.textContent = 'Menjalankan...';
        const response = await fetch('/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: modifiedCode, action: 'run_code' })
        });
        const data = await response.json();
        codeOutput.textContent = data.reply;
    });
}
// static/js/learning.js

    if (chatForm) {
        userInput.addEventListener('keypress', function(event) {
            if (event.key === 'Enter' && !event.shiftKey) { // Ditambah !event.shiftKey agar Shift+Enter bisa untuk baris baru
                event.preventDefault();
                chatForm.dispatchEvent(new Event('submit', { cancelable: true }));
            }
        });

        chatForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const chatMessage = userInput.value.trim();
            const codeContent = (typeof editor !== 'undefined' && editor) ? editor.getValue() : '';

            if (!chatMessage && !codeContent) return;

            let finalMessage = chatMessage;
            if (codeContent) {
                finalMessage = `Pesan saya: "${chatMessage}"\n\nBerikut adalah kode yang saya buat:\n\`\`\`python\n${codeContent}\n\`\`\``;
            }
            
            addMessage('Anda', chatMessage || "(mengirimkan kode)");
            userInput.value = '';

            typingIndicator.style.display = 'flex';
            chatBox.scrollTop = chatBox.scrollHeight;

            try {
                const response = await fetch('/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message: finalMessage, action: 'chat' })
                });

                typingIndicator.style.display = 'none';
                
                const data = await response.json();
                let aiReply = data.reply;

                if (aiReply.includes('[TAMPILKAN_JALANKAN_KODE]')) {
                    aiReply = aiReply.replace('[TAMPILKAN_JALANKAN_KODE]', '').trim();
                    const runBtn = document.getElementById('run-code-btn');
                    if (runBtn) {
                        runBtn.style.display = 'block';
                    }
                }

                addMessage('SocraMind', aiReply);
                
                if (data.show_next_button) {
                    userInput.disabled = true;
                    showNextStepButton(data.next_action_url);
                }
            } catch (error) {
                typingIndicator.style.display = 'none';
                console.error("Error saat fetch:", error);
                addMessage('Error', 'Gagal terhubung ke server.');
            }
        });
    }

    const showNextButtonOnLoad = document.documentElement.getAttribute('data-show-next-button') === 'True';
    if (showNextButtonOnLoad) {
        showNextStepButton();
        if(userInput) userInput.disabled = true;
    }
});