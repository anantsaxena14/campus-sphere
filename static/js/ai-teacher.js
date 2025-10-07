let currentMode = 'normal';
let isListening = false;
let recognition = null;
let synthesis = window.speechSynthesis;

if ('webkitSpeechRecognition' in window) {
    recognition = new webkitSpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.lang = 'en-US';
    
    recognition.onresult = function(event) {
        const transcript = event.results[0][0].transcript;
        document.getElementById('messageInput').value = transcript;
        sendMessage();
    };
    
    recognition.onend = function() {
        isListening = false;
        updateVoiceButton();
    };
}

function switchMode(mode) {
    currentMode = mode;
    const header = document.getElementById('header');
    const modeClasses = {
        'normal': 'mode-normal',
        'practice': 'mode-practice',
        'counseling': 'mode-counseling'
    };
    
    header.className = `text-white py-6 px-8 transition-all duration-500 ${modeClasses[mode]}`;
    
    const messages = {
        'normal': 'Normal Chat Mode: Ask me anything!',
        'practice': 'Practice Mode: Get questions and test your skills!',
        'counseling': 'Counseling Mode: Let\'s talk about your goals and challenges.'
    };
    
    addSystemMessage(messages[mode]);
    updateAvatarStatus(`Switched to ${mode} mode`);
}

function addSystemMessage(text) {
    const chatMessages = document.getElementById('chatMessages');
    
    if (chatMessages.children[0]?.textContent?.includes('Welcome!')) {
        chatMessages.innerHTML = '';
    }
    
    const messageDiv = document.createElement('div');
    messageDiv.className = 'text-center py-2 message-enter';
    messageDiv.innerHTML = `<span class="inline-block bg-gray-200 text-gray-700 px-4 py-2 rounded-full text-sm">${text}</span>`;
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function addMessage(text, isUser = false) {
    const chatMessages = document.getElementById('chatMessages');
    
    if (chatMessages.children[0]?.textContent?.includes('Welcome!')) {
        chatMessages.innerHTML = '';
    }
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `flex ${isUser ? 'justify-end' : 'justify-start'} message-enter`;
    
    const time = new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
    
    messageDiv.innerHTML = `
        <div class="max-w-md">
            <div class="${isUser ? 'bg-purple-600 text-white' : 'bg-gray-100 text-gray-800'} rounded-2xl px-4 py-3">
                <p class="text-sm">${text}</p>
            </div>
            <p class="text-xs text-gray-500 mt-1 ${isUser ? 'text-right' : 'text-left'}">${time}</p>
        </div>
    `;
    
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

async function sendMessage() {
    const input = document.getElementById('messageInput');
    const message = input.value.trim();
    
    if (!message) return;
    
    addMessage(message, true);
    input.value = '';
    
    updateAvatarStatus('Thinking...');
    
    try {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                message: message,
                mode: currentMode
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            addMessage(data.response, false);
            updateAvatarStatus('Ready to help!');
            
            if (document.getElementById('soundToggle').checked) {
                speak(data.response);
            }
        } else {
            addMessage('Sorry, I encountered an error. Please try again.', false);
            updateAvatarStatus('Error occurred');
        }
    } catch (error) {
        console.error('Error:', error);
        addMessage('Sorry, I could not connect. Please try again.', false);
        updateAvatarStatus('Connection error');
    }
}

function toggleVoice() {
    if (!recognition) {
        alert('Voice recognition is not supported in your browser.');
        return;
    }
    
    if (isListening) {
        recognition.stop();
        isListening = false;
    } else {
        recognition.start();
        isListening = true;
        updateAvatarStatus('Listening...');
    }
    
    updateVoiceButton();
}

function updateVoiceButton() {
    const btn = document.getElementById('voiceBtn');
    if (isListening) {
        btn.innerHTML = '🔴';
        btn.classList.add('pulse-ring');
    } else {
        btn.innerHTML = '🎤';
        btn.classList.remove('pulse-ring');
    }
}

function speak(text) {
    if (synthesis.speaking) {
        synthesis.cancel();
    }
    
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.rate = 1.0;
    utterance.pitch = 1.0;
    utterance.volume = 1.0;
    
    synthesis.speak(utterance);
}

function updateAvatarStatus(status) {
    document.getElementById('avatarStatus').textContent = status;
}

async function getPracticeQuestion(type = 'coding') {
    try {
        const response = await fetch('/api/get_questions', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                subject: 'Programming',
                type: type,
                difficulty: 'medium'
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            const question = data.question;
            let questionText = question.question || 'Question not available';
            
            if (type === 'mcq' && question.options) {
                questionText += '\n\nOptions:\n' + question.options.join('\n');
            }
            
            addMessage(questionText, false);
        }
    } catch (error) {
        console.error('Error getting question:', error);
    }
}
