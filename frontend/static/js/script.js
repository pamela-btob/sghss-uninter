const API_URL = 'http://127.0.0.1:8000';  // ← SEM /api NO FINAL
let token = localStorage.getItem('token');
let currentUser = null;

// Inicialização
document.addEventListener('DOMContentLoaded', function() {
    if (token) {
        carregarPerfil();
    } else {
        showScreen('login-screen');
    }
});

// Login
document.getElementById('login-form').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;

    try {
        const response = await fetch(`${API_URL}/api/token/`, {  // ← /api/token/
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ username, password })
        });

        const data = await response.json();

        if (response.ok) {
            token = data.access;
            localStorage.setItem('token', token);
            carregarPerfil();
            showMessage('Login realizado com sucesso!', 'success');
        } else {
            showMessage('Erro no login: ' + (data.detail || 'Credenciais inválidas'), 'error');
        }
    } catch (error) {
        showMessage('Erro de conexão: ' + error.message, 'error');
    }
});

// Carregar perfil do usuário
async function carregarPerfil() {
    try {
        const response = await fetch(`${API_URL}/api/usuarios/perfil/`, {  // ← /api/usuarios/perfil/
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (response.ok) {
            currentUser = await response.json();
            document.getElementById('user-name').textContent = currentUser.username;
            showScreen('dashboard');
            showTab('agendamentos');
            carregarAgendamentos();
            carregarProntuarios();
        } else {
            logout();
        }
    } catch (error) {
        showMessage('Erro ao carregar perfil', 'error');
    }
}

// Carregar agendamentos
async function carregarAgendamentos() {
    try {
        const response = await fetch(`${API_URL}/api/agendamentos/`, {  // ← /api/agendamentos/
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (response.ok) {
            const agendamentos = await response.json();
            const lista = document.getElementById('lista-agendamentos');
            
            if (agendamentos.length === 0) {
                lista.innerHTML = '<p>Nenhum agendamento encontrado.</p>';
            } else {
                lista.innerHTML = agendamentos.map(ag => `
                    <div class="agendamento-item">
                        <strong>Com Dr. ${ag.medico_nome}</strong><br>
                        Data: ${new Date(ag.data_agendamento).toLocaleString()}<br>
                        Tipo: ${ag.tipo_consulta} | Status: ${ag.status}
                    </div>
                `).join('');
            }
        }
    } catch (error) {
        console.error('Erro ao carregar agendamentos:', error);
    }
}

// Carregar prontuários
async function carregarProntuarios() {
    try {
        const response = await fetch(`${API_URL}/api/prontuarios/`, {  // ← /api/prontuarios/
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (response.ok) {
            const prontuarios = await response.json();
            const lista = document.getElementById('lista-prontuarios');
            
            if (prontuarios.length === 0) {
                lista.innerHTML = '<p>Nenhum prontuário encontrado.</p>';
            } else {
                lista.innerHTML = prontuarios.map(pr => `
                    <div class="prontuario-item">
                        <strong>${pr.titulo}</strong><br>
                        Médico: Dr. ${pr.medico_nome}<br>
                        Data: ${new Date(pr.criado_em).toLocaleDateString()}<br>
                        Diagnóstico: ${pr.diagnostico || 'Não informado'}
                    </div>
                `).join('');
            }
        }
    } catch (error) {
        console.error('Erro ao carregar prontuários:', error);
    }
}

// Funções de navegação (mantenha as mesmas)
function showScreen(screenId) {
    document.querySelectorAll('.screen').forEach(screen => {
        screen.classList.add('hidden');
    });
    document.getElementById(screenId).classList.remove('hidden');
}

function showTab(tabId) {
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.add('hidden');
    });
    document.getElementById(tabId).classList.remove('hidden');
}

function showMessage(message, type) {
    const messageDiv = document.getElementById('login-message');
    messageDiv.textContent = message;
    messageDiv.className = `message ${type}`;
    messageDiv.classList.remove('hidden');
    
    setTimeout(() => {
        messageDiv.classList.add('hidden');
    }, 5000);
}

function logout() {
    localStorage.removeItem('token');
    token = null;
    currentUser = null;
    showScreen('login-screen');
    document.getElementById('login-form').reset();
}

function criarAgendamento() {
    const data = prompt('Digite a data do agendamento (YYYY-MM-DDTHH:MM:00Z):\nEx: 2025-12-25T14:00:00Z');
    if (data) {
        showMessage('Funcionalidade de criar agendamento em desenvolvimento!', 'success');
    }
}