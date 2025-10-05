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
            lineNumbers: true,         // <-- INI UNTUK MENAMPILKAN NOMOR BARIS
            mode: "python",            // Mengaktifkan syntax highlighting untuk Python
            theme: "material-darker",  // Tema warna (bisa diganti)
            indentUnit: 4,             // Atur indentasi 4 spasi
            lineWrapping: true         // Agar baris yang panjang otomatis ke bawah
        });
    }
    if (toggleNavBtn && learningSidebar) {
        toggleNavBtn.addEventListener('click', () => {
            learningSidebar.classList.toggle('open');
        });
    }
    // Auto-scroll chatbox ke bawah jika ada
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

    // Fungsi global untuk tombol 'Lanjut' yang dibuat oleh server
    window.handleNextStep = async (next_url = null) => {
        if (next_url) {
            window.location.href = next_url;
        } else {
            await fetch('/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ action: 'next_step' })
            });
            window.location.reload(); // Selalu reload untuk memuat state baru
        }
    };
    
    function showNextStepButton(next_url = null) {
        const oldButton = document.getElementById('next-step-btn');
        if (oldButton) oldButton.remove();
        
        // Temukan kontainer utama, bukan lagi 'contentArea'
        const mainContent = document.querySelector('.learning-main-content');
        if (!mainContent) return; // Keluar jika kontainer tidak ditemukan

        const nextButton = document.createElement('button');
        nextButton.id = 'next-step-btn';
        nextButton.className = 'button-lanjut'; // Tambahkan class untuk styling
        nextButton.textContent = next_url ? 'Mulai Quiz' : 'Lanjut ke Tahap Berikutnya';
        
        // Panggil fungsi global saat diklik
        nextButton.onclick = () => window.handleNextStep(next_url);
        
        // Tambahkan tombol ke kontainer utama
        mainContent.appendChild(nextButton);
    }

    if (runCodeBtn) {
    runCodeBtn.addEventListener('click', async () => {
        // Ambil kode dari instance CodeMirror, bukan dari textarea
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
    if (chatForm) {
        userInput.addEventListener('keypress', function(event) {
            if (event.key === 'Enter') {
                event.preventDefault();
                chatForm.dispatchEvent(new Event('submit', { cancelable: true }));
            }
        });

        chatForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const message = userInput.value.trim();
            if (!message) return;
            
            addMessage('Anda', message);
            userInput.value = '';

            typingIndicator.style.display = 'flex';
            chatBox.scrollTop = chatBox.scrollHeight; 

            try {
                const response = await fetch('/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message: message, action: 'chat' })
                });

                typingIndicator.style.display = 'none';
                
                const data = await response.json();
                let aiReply = data.reply; // Simpan balasan AI ke variabel

                if (aiReply.includes('[TAMPILKAN_JALANKAN_KODE]')) {
                // Hapus sinyal dari teks yang akan ditampilkan
                aiReply = aiReply.replace('[TAMPILKAN_JALANKAN_KODE]', '').trim();
                
                // Tampilkan tombol "Jalankan Kode"
                const runBtn = document.getElementById('run-code-btn');
                if (runBtn) {
                    runBtn.style.display = 'block'; // atau 'inline-block' sesuai style Anda
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

    // Cek apakah tombol lanjut perlu dibuat saat refresh
    const showNextButtonOnLoad = document.documentElement.getAttribute('data-show-next-button') === 'True';
    if (showNextButtonOnLoad) {
        showNextStepButton();
        if(userInput) userInput.disabled = true;
    }
});