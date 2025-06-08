// script.js (insere getVoices() e log de erro na saudação)
document.addEventListener('DOMContentLoaded', () => {
  const chatMessages = document.getElementById('chat-messages');
  const userInput    = document.getElementById('user-input');
  const sendBtn      = document.getElementById('send-btn');
  const micBtn       = document.getElementById('mic-btn');
  const muteBtn      = document.getElementById('mute-btn');
  let isMuted = false;

  // força carregamento das vozes
  window.speechSynthesis.getVoices();

  function speak(text) {
    if (isMuted) return;
    const utter = new SpeechSynthesisUtterance(text);
    utter.lang = 'pt-BR';
    utter.rate = 1;
    window.speechSynthesis.speak(utter);
  }

  function addMessage(text, isUser=false, type='texto', dados={}) {
    const msgDiv = document.createElement('div');
    msgDiv.className = `message ${isUser ? 'user' : 'bot'}`;
    const content = document.createElement('div');
    content.className = 'message-content';

    if (type === 'texto') {
      content.innerHTML = `<p>${text}</p>`;
    } else if (type === 'lembretes') {
      content.innerHTML = `<p>${text}</p>`;
      if (dados.lembretes) {
        const ul = document.createElement('ul');
        ul.className = 'lembretes-lista';
        dados.lembretes.forEach(l => {
          const li = document.createElement('li');
          li.textContent = l;
          ul.appendChild(li);
        });
        content.appendChild(ul);
      }
    } else if (type === 'pesquisa') {
      content.innerHTML = `<p>${text}</p>`;
      if (dados.url) {
        const a = document.createElement('a');
        a.href = dados.url;
        a.target = '_blank';
        a.className = 'pesquisa-link';
        a.innerHTML = '<i class="fas fa-external-link-alt"></i> Abrir pesquisa';
        content.appendChild(a);
      }
    }

    msgDiv.appendChild(content);
    chatMessages.appendChild(msgDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
  }

  async function enviarComando(cmd) {
    window.speechSynthesis.cancel();
    try {
      const res = await fetch('/api/comando', {
        method:'POST',
        headers:{'Content-Type':'application/json'},
        body: JSON.stringify({ comando: cmd })
      });
      const data = await res.json();
      addMessage(data.resposta, false, data.tipo, data.dados);
      speak(data.resposta);
      if (data.tipo === 'lembretes' && Array.isArray(data.dados.lembretes)) {
        data.dados.lembretes.forEach(l => speak(l));
      }
    } catch (err) {
      console.error('Erro enviarComando:', err);
      addMessage('Erro ao processar seu comando.', false);
      speak('Desculpe, ocorreu um erro ao processar seu comando.');
    }
  }

  function processarEnvio() {
    window.speechSynthesis.cancel();
    const cmd = userInput.value.trim();
    if (!cmd) return;
    addMessage(cmd, true);
    enviarComando(cmd);
    userInput.value = '';
  }

  ;(async function boasVindas() {
    try {
      window.speechSynthesis.cancel();
      const res = await fetch('/api/boasvindas');
      if (!res.ok) {
        console.error('Saudação falhou, status:', res.status);
        return;
      }
      const data = await res.json();
      addMessage(data.resposta, false);
      speak(data.resposta);
    } catch (err) {
      console.error('Erro na saudação:', err);
    }
  })();

  sendBtn.addEventListener('click', processarEnvio);
  userInput.addEventListener('keypress', e => {
    if (e.key === 'Enter') processarEnvio();
  });

  muteBtn.addEventListener('click', () => {
    isMuted = !isMuted;
    muteBtn.innerHTML = isMuted
      ? '<i class="fas fa-volume-mute"></i>'
      : '<i class="fas fa-volume-up"></i>';
    window.speechSynthesis.cancel();
  });

  if ('SpeechRecognition' in window || 'webkitSpeechRecognition' in window) {
    const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
    const rec = new SR();
    rec.lang = 'pt-BR';
    rec.continuous = false;
    rec.interimResults = false;

    rec.onresult = e => {
      userInput.value = e.results[0][0].transcript;
      processarEnvio();
    };
    rec.onerror = () => {
      addMessage('Não consegui entender. Tente novamente.', false);
    };
    rec.onend = () => micBtn.classList.remove('listening');

    micBtn.addEventListener('click', () => {
      window.speechSynthesis.cancel();
      rec.start();
      micBtn.classList.add('listening');
      addMessage('Estou ouvindo...', false);
    });
  } else {
    micBtn.style.display = 'none';
  }

  userInput.focus();
});
