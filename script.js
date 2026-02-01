// SkillSpeak AI Landing Page JavaScript

// ========== CONFIG ==========
// Only declare API_BASE once at the top
const API_BASE = "http://localhost:5000/api";
let jwtToken, userRole, userId;
function refreshAuthVars() {
  jwtToken = localStorage.getItem("jwtToken") || null;
  userRole = localStorage.getItem("userRole") || null;
  userId = localStorage.getItem("userId") || null;
}
refreshAuthVars();
document.addEventListener('DOMContentLoaded', refreshAuthVars);

// ========== AUTH HELPERS ==========
function setAuth(token, role) {
  jwtToken = token; // Ensure global variable is set
  userRole = role;
  localStorage.setItem("jwtToken", token);
  localStorage.setItem("userRole", role);
}
function clearAuth() {
  jwtToken = null;
  userRole = null;
  localStorage.removeItem("jwtToken");
  localStorage.removeItem("userRole");
}

// ========== GENERIC FETCH ==========
async function apiFetch(endpoint, { method = "GET", body = null, isForm = false } = {}) {
  const headers = {};
  console.log('JWT Token used for fetch:', jwtToken); // Debug: log the token
  if (jwtToken) headers["Authorization"] = "Bearer " + jwtToken;
  if (!isForm) headers["Content-Type"] = "application/json";
  try {
    const res = await fetch(API_BASE + endpoint, {
      method,
      headers,
      body: isForm ? body : body ? JSON.stringify(body) : null,
    });
    if (res.status === 401) {
      clearAuth();
      const isLanding = window.location.pathname.includes("index.html") || window.location.pathname === "/" || window.location.pathname === "/index";
      if (!isLanding) {
        window.location.href = "login.html";
      } else {
        console.warn("Unauthorized on landing page — ignored.");
      }
      return {}; // prevent further error
    }
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || "API error");
    return data;
  } catch (err) {
    showError(err.message);
    throw err;
  }
}

function showError(msg) {
  alert(msg); // Replace with a better UI error display if desired
}

// ========== LOGIN ==========
window.loginHandler = async function (e) {
  e.preventDefault();
  const email = this.email.value, password = this.password.value;
  try {
    const data = await apiFetch("/auth/login", { method: "POST", body: { email, password } });
    setAuth(data.token, data.role);
    if (data.user && data.user.name) {
      localStorage.setItem("userName", data.user.name);
    }
    if (data.user && data.user.email) {
      localStorage.setItem("userEmail", data.user.email);
    }
    if (data.user && data.user.id) {
      localStorage.setItem("userId", data.user.id); // Store userId for session creation
    }
    // Redirect based on user role
    if (data.role === 'admin') {
      window.location.href = "admin.html";
    } else {
      window.location.href = "dashboard.html";
    }
  } catch {}
};

// ========== SIGNUP ==========
window.signupHandler = async function (e) {
  e.preventDefault();
  const name = this.name.value, email = this.email.value, password = this.password.value;
  try {
    await apiFetch("/auth/signup", { method: "POST", body: { name, email, password } });
    localStorage.setItem("userEmail", email);
    window.location.href = "login.html";
  } catch {}
};

// ========== LOGOUT ==========
window.logout = function() {
  clearAuth();
  localStorage.removeItem("userName");
  localStorage.removeItem("userEmail");
  localStorage.removeItem("currentSessionId");
  // You can also clear other keys if needed
  window.location.href = "index.html";
};

// ========== AUDIO RECORDING ==========
let mediaRecorder, audioChunks = [];
let audioBlob = null;
window.startRecording = async function (recordBtn, stopBtn, sendBtn) {
  audioChunks = [];
  const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
  mediaRecorder = new MediaRecorder(stream);
  mediaRecorder.ondataavailable = e => audioChunks.push(e.data);
  mediaRecorder.onstop = () => {
    audioBlob = new Blob(audioChunks, { type: "audio/wav" });
    sendBtn.disabled = false;
  };
  mediaRecorder.start();
  recordBtn.disabled = true;
  stopBtn.disabled = false;
};
window.stopRecording = function (recordBtn, stopBtn) {
  mediaRecorder.stop();
  recordBtn.disabled = false;
  stopBtn.disabled = true;
};
window.sendAudio = async function (sendBtn, chatBox) {
  if (!audioBlob) return;
  const formData = new FormData();
  formData.append("audio", audioBlob, "audio.wav");
  try {
    const data = await apiFetch("/voice/chat", { method: "POST", body: formData, isForm: true });
    addChatBubble("You", "[Voice message sent]", chatBox);
    addChatBubble("AI", data.answer, chatBox);
  } catch {}
  sendBtn.disabled = true;
};
function addChatBubble(sender, text, chatBox) {
  const div = document.createElement("div");
  div.className = "bubble " + (sender === "You" ? "user" : "ai");
  div.innerText = sender + ": " + text;
  if (chatBox) chatBox.appendChild(div);
}

// ========== FEEDBACK ==========
window.feedbackHandler = async function (e, resultElem) {
  e.preventDefault();
  const input = this.input.value;
  try {
    const data = await apiFetch("/feedback/generate", { method: "POST", body: { input } });
    resultElem.innerText =
      `Summary: ${data.feedback.summary}\nScore: ${data.feedback.score}\nSuggestions: ${data.feedback.suggestions}`;
  } catch {}
};

// ========== DASHBOARD ==========
window.loadDashboard = async function (totalElem, avgElem, lastElem) {
  try {
    const stats = await apiFetch("/dashboard/stats");
    totalElem.innerText = stats.total_chats;
    avgElem.innerText = stats.avg_feedback_score.toFixed(2);
    lastElem.innerText = stats.last_activity || "N/A";
  } catch {}
};

// ========== PROFILE ==========
window.loadProfile = async function (nameElem, emailElem, bioElem, photoElem) {
  if (!jwtToken) {
    window.location.href = "login.html";
    return;
  }
  try {
    const user = await apiFetch("/profile/me");
    nameElem.value = user.name;
    emailElem.value = user.email;
    bioElem.value = user.bio;
    photoElem.src = user.photo_url;
  } catch {}
};
window.profileUpdateHandler = async function (e, nameElem, bioElem, photoElem) {
  e.preventDefault();
  if (!jwtToken) {
    window.location.href = "login.html";
    return;
  }
  try {
    await apiFetch("/profile/me", { method: "PUT", body: { name: nameElem.value, bio: bioElem.value, photo_url: photoElem.value } });
    alert("Profile updated!");
  } catch {}
};

// ========== CHAT HISTORY STORAGE ==========
// Remove or comment out this function to prevent chat from calling /api/history/add
// async function saveChatSession(messages, summary, session_id = null, chat_id = null) {
//   const jwtToken = localStorage.getItem('jwtToken');
//   if (!jwtToken) return;
//   for (const msg of messages) {
//     await fetch('http://localhost:5000/api/history/add', {
//       method: 'POST',
//       headers: {
//         'Authorization': 'Bearer ' + jwtToken,
//         'Content-Type': 'application/json'
//       },
//       body: JSON.stringify({
//         role: msg.role,
//         message: msg.message,
//         session_id: session_id,
//         chat_id: chat_id
//       })
//     });
//   }
// }
// Example usage: call saveChatSession(messagesArray, summaryText, sessionId) when a chat session ends.

// ========== ADMIN ==========
// ========== ADMIN USER, FEEDBACK, CHAT MANAGEMENT SEARCH & SORT ==========

// Global arrays to store fetched data
window.adminUsers = [];
window.adminFeedback = [];
window.adminChats = [];

// Load users from backend and store in global array
window.loadAdminUsers = async function (tableElem) {
  if (userRole !== "admin") {
    tableElem.innerHTML = "<tr><td colspan='6'>Access denied</td></tr>";
    return;
  }
  try {
    const users = await apiFetch("/admin/users");
    window.adminUsers = users.users || [];
    renderUsersTable(window.adminUsers, tableElem);
  } catch {
    tableElem.innerHTML = "<tr><td colspan='6'>Failed to load users</td></tr>";
  }
};

function renderUsersTable(users, tableElem) {
  const tbody = tableElem.querySelector('tbody') || tableElem;
  tbody.innerHTML = '';
  if (!users.length) {
    tbody.innerHTML = "<tr><td colspan='4' style='text-align:center;opacity:0.7;'>No users found.</td></tr>";
    return;
  }
  let openActionRow = null;
  let openMenuBtn = null;
  users.forEach((u, idx) => {
    const row = tbody.insertRow();
    row.insertCell().innerText = u.name;
    row.insertCell().innerText = u.email;
    row.insertCell().innerText = u.role;
    // Actions cell (three-dot button)
    const actionsCell = row.insertCell();
    actionsCell.style.position = 'relative';
    const menuBtn = document.createElement('button');
    menuBtn.className = 'action-menu-btn';
    menuBtn.innerHTML = '<i class="fas fa-ellipsis-v"></i>';
    if (actionsCell) actionsCell.appendChild(menuBtn);
    menuBtn.onclick = function(e) {
      e.stopPropagation();
      // Remove any open action row
      if (openActionRow) {
        openActionRow.remove();
        openActionRow = null;
        if (openMenuBtn) openMenuBtn.classList.remove('active');
      }
      // Insert action row directly after this row
      openActionRow = tbody.insertRow();
      const cell = openActionRow.insertCell();
      cell.colSpan = 4;
      cell.className = 'user-action-row';
      row.parentNode.insertBefore(openActionRow, row.nextSibling);
      // Block/Unblock button
      const blockBtn = document.createElement('button');
      blockBtn.className = 'btn btn-secondary';
      blockBtn.style.margin = '0 10px';
      blockBtn.innerHTML = u.status === 'blocked' ? '<i class="fas fa-unlock"></i> Unblock' : '<i class="fas fa-ban"></i> Block';
      if (cell) cell.appendChild(blockBtn);
      blockBtn.onclick = async (ev) => {
        ev.stopPropagation();
        await apiFetch(`/admin/${u.status === 'blocked' ? 'unblock_user' : 'block_user'}/${u._id}`, { method: 'POST' });
        await window.loadAdminUsers(tableElem);
      };
      // Delete button
      const deleteBtn = document.createElement('button');
      deleteBtn.className = 'btn btn-danger';
      deleteBtn.style.margin = '0 10px';
      deleteBtn.innerHTML = '<i class="fas fa-trash"></i> Delete';
      if (cell) cell.appendChild(deleteBtn);
      deleteBtn.onclick = async (ev) => {
        ev.stopPropagation();
        if (confirm('Are you sure you want to delete this user?')) {
          await apiFetch(`/admin/delete_user/${u._id}`, { method: 'DELETE' });
          await window.loadAdminUsers(tableElem);
        }
      };
      // Make Admin / Remove Admin button
      if (u.role !== 'admin') {
        const makeAdminBtn = document.createElement('button');
        makeAdminBtn.className = 'btn btn-success';
        makeAdminBtn.style.margin = '0 10px';
        makeAdminBtn.innerHTML = '<i class="fas fa-user-shield"></i> Make Admin';
        if (cell) cell.appendChild(makeAdminBtn);
        makeAdminBtn.onclick = async (ev) => {
          ev.stopPropagation();
          await apiFetch(`/admin/set_admin/${u._id}`, { method: 'POST' });
          await window.loadAdminUsers(tableElem);
        };
      } else {
        const removeAdminBtn = document.createElement('button');
        removeAdminBtn.className = 'btn btn-secondary';
        removeAdminBtn.style.margin = '0 10px';
        removeAdminBtn.innerHTML = '<i class="fas fa-user-slash"></i> Remove Admin';
        if (cell) cell.appendChild(removeAdminBtn);
        removeAdminBtn.onclick = async (ev) => {
          ev.stopPropagation();
          await apiFetch(`/admin/remove_admin/${u._id}`, { method: 'POST' });
          await window.loadAdminUsers(tableElem);
        };
      }
      openMenuBtn = menuBtn;
      menuBtn.classList.add('active');
      // Close action row on click outside
      setTimeout(() => {
        document.addEventListener('click', closeActionRow, { once: true });
      }, 0);
      function closeActionRow(ev) {
        if (!openActionRow.contains(ev.target) && ev.target !== menuBtn) {
          if (openActionRow) openActionRow.remove();
          openActionRow = null;
          menuBtn.classList.remove('active');
        }
      }
    };
  });
}

// FEEDBACK MANAGEMENT
window.loadAdminFeedback = async function(tableElem) {
  try {
    const res = await apiFetch('/admin/feedback');
    window.adminFeedback = res.feedback || [];
    renderFeedbackTable(window.adminFeedback, tableElem);
  } catch {
    tableElem.innerHTML = "<tr><td colspan='6'>Failed to load feedback</td></tr>";
  }
};
function renderFeedbackTable(feedback, tableElem) {
  const tbody = tableElem.querySelector('tbody') || tableElem;
  tbody.innerHTML = '';
  if (!feedback.length) {
    tbody.innerHTML = "<tr><td colspan='6' style='text-align:center;opacity:0.7;'>No feedback found.</td></tr>";
    return;
  }
  feedback.forEach(fb => {
    const row = tbody.insertRow();
    row.insertCell().innerText = fb.user_name || '';
    row.insertCell().innerText = fb.content || '';
    row.insertCell().innerText = fb.type || '';
    row.insertCell().innerText = fb.status || '';
    row.insertCell().innerText = fb.date || '';
    const delBtn = document.createElement("button");
    delBtn.innerText = "Delete";
    if (row) row.insertCell().appendChild(delBtn);
    delBtn.onclick = async () => {
      await apiFetch(`/admin/delete_feedback/${fb._id}`, { method: "DELETE" });
      row.remove();
    };
  });
}

// CHAT MANAGEMENT
window.loadAdminChats = async function(tableElem) {
  try {
    const chats = await apiFetch('/admin/chats');
    window.adminChats = Array.isArray(chats) ? chats : (chats.chats || []);
    displayChats(window.adminChats);
  } catch {
    tableElem.innerHTML = "<tr><td colspan='5'>Failed to load chats</td></tr>";
  }
};

function displayChats(chats) {
    const tbody = document.getElementById('chatsTableBody');
    tbody.innerHTML = '';
    if (chats.length === 0) {
        tbody.innerHTML = '<tr><td colspan="5" style="text-align: center; opacity: 0.7;">No chats found</td></tr>';
        return;
    }
    chats.forEach(chat => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${chat.session_name || 'Session'}</td>
            <td>${chat.user_name || 'Unknown'}</td>
            <td>${chat.date ? new Date(chat.date).toLocaleString() : ''}</td>
            <td>${chat.chat_count || 0}</td>
            <td style="position:relative;">
                <button class="btn btn-secondary btn-action-menu" data-session-id="${chat._id}" style="padding:6px 12px; font-size:1.2rem;"><i class="fas fa-ellipsis-v"></i></button>
            </td>
        `;
        tbody.appendChild(row);
    });
    // Dropdown logic
    let openDropdown = null;
    tbody.querySelectorAll('.btn-action-menu').forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.stopPropagation();
            // Close any open dropdown
            if (openDropdown) openDropdown.remove();
            // Clone dropdown template
            const template = document.getElementById('chatActionsDropdownTemplate');
            if (!template) return;
            const dropdown = template.firstElementChild.cloneNode(true);
            dropdown.style.display = 'block';
            // Position dropdown
            const rect = btn.getBoundingClientRect();
            dropdown.style.position = 'absolute';
            dropdown.style.top = (btn.offsetTop + btn.offsetHeight + 2) + 'px';
            dropdown.style.left = (btn.offsetLeft - 40) + 'px';
            // Attach handlers
            dropdown.querySelector('.view-btn').onclick = () => {
                viewChatSession(btn.getAttribute('data-session-id'));
                dropdown.remove();
            };
            dropdown.querySelector('.delete-btn').onclick = () => {
                deleteChatSession(btn.getAttribute('data-session-id'));
                dropdown.remove();
            };
            dropdown.querySelector('.export-btn').onclick = () => {
                exportChatSession(btn.getAttribute('data-session-id'));
                dropdown.remove();
            };
            // Remove any existing dropdown in this cell
            btn.parentElement.querySelectorAll('.chat-actions-dropdown').forEach(d => d.remove());
            btn.parentElement.appendChild(dropdown);
            openDropdown = dropdown;
        });
    });
    // Close dropdown on outside click
    document.addEventListener('click', function closeDropdown(e) {
        if (openDropdown && !openDropdown.contains(e.target)) {
            openDropdown.remove();
            openDropdown = null;
        }
    }, { once: true });
}

async function viewChatSession(sessionId) {
    try {
        const session = await apiFetch(`/admin/chats?session_id=${sessionId}`);
        // Fill modal fields
        document.getElementById('modalSessionName').textContent = session.session_name || '';
        document.getElementById('modalUserName').textContent = session.user_name || '';
        document.getElementById('modalSessionDate').textContent = session.start_time || session.created_at || '';
        const messagesDiv = document.getElementById('modalChatMessages');
        messagesDiv.innerHTML = '';
        if (session.chats && session.chats.length) {
            session.chats.forEach((msg, idx) => {
                const msgDiv = document.createElement('div');
                msgDiv.style.marginBottom = '12px';
                msgDiv.innerHTML = `<div style='color:#8f3fe6;'><b>Q${idx + 1}:</b> ${msg.question}</div><div style='color:#3ffed2;'><b>A:</b> ${msg.answer}</div>`;
                messagesDiv.appendChild(msgDiv);
            });
        } else {
            messagesDiv.innerHTML = '<em>No messages.</em>';
        }
        // Show modal
        document.getElementById('chatSessionModal').style.display = 'flex';
    } catch (err) {
        alert('Failed to load chat details.');
    }
}
// Modal close logic
if (document.getElementById('closeChatSessionModal')) {
    document.getElementById('closeChatSessionModal').onclick = function() {
        document.getElementById('chatSessionModal').style.display = 'none';
    };
}

async function deleteChatSession(sessionId) {
    if (!confirm('Are you sure you want to delete this chat session?')) return;
    try {
        // You need to implement a DELETE endpoint in the backend for /admin/chats/<session_id>
        await apiFetch(`/admin/chats/${sessionId}`, { method: 'DELETE' });
        alert('Chat session deleted.');
        window.loadAdminChats(document.getElementById('chatsTable'));
    } catch (err) {
        alert('Failed to delete chat session.');
    }
}

// Export chat session handler (stub)
function exportChatSession(sessionId) {
    // You can implement actual export logic here (e.g., download as JSON)
    alert('Export functionality coming soon for session: ' + sessionId);
}

// ========== ADMIN SETTINGS (AI & FEATURE TOGGLES) ==========

window.saveAISettings = async function() {
  const aiModel = document.getElementById('aiModelSelect').value;
  try {
    await apiFetch('/admin/settings/ai', {
      method: 'POST',
      body: { aiModel }
    });
    alert('AI settings saved successfully!');
  } catch (err) {
    alert('Failed to save AI settings: ' + err.message);
  }
};

document.getElementById('temperatureRange')?.addEventListener('input', function() {
  document.getElementById('temperatureValue').innerText = this.value;
});

window.saveFeatureSettings = async function() {
  const speechToSpeech = document.getElementById('speechToSpeechToggle').checked;
  const textChat = document.getElementById('textChatToggle').checked;
  const feedback = document.getElementById('feedbackToggle').checked;
  const analytics = document.getElementById('analyticsToggle').checked;
  const autoRefresh = document.getElementById('autoRefreshToggle').checked;
  try {
    await apiFetch('/admin/settings/features', {
      method: 'POST',
      body: { speechToSpeech, textChat, feedback, analytics, autoRefresh }
    });
    alert('Feature settings saved successfully!');
  } catch (err) {
    alert('Failed to save feature settings: ' + err.message);
  }
};

// Optionally, add logic to load current settings from backend if GET endpoints are available

// Navbar scroll effect
function handleScroll() {
    const navbar = document.getElementById('navbar');
    if (navbar) {
        if (window.scrollY > 50) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }
    }
    // Fade in animation for elements
    const fadeElements = document.querySelectorAll('.fade-in');
    fadeElements.forEach(element => {
        const elementTop = element.getBoundingClientRect().top;
        const elementVisible = 150;
        if (elementTop < window.innerHeight - elementVisible) {
            element.classList.add('visible');
        }
    });
}

// Smooth scrolling for navigation links
function smoothScroll(e) {
    e.preventDefault();
    const targetId = this.getAttribute('href');
    const targetSection = document.querySelector(targetId);
    
    if (targetSection) {
        targetSection.scrollIntoView({
            behavior: 'smooth'
        });
    }
}

// AI Chat Demo Animation
function animateChat() {
    const chatMessages = document.getElementById('chatMessages');
    const messages = [
        { text: "Tell me about your experience with JavaScript.", type: "ai" },
        { text: "I've been working with JavaScript for 2 years...", type: "user" },
        { text: "That's great! Can you explain closures?", type: "ai" },
        { text: "Closures are functions that have access to variables...", type: "user" },
        { text: "Excellent explanation! How about async/await?", type: "ai" }
    ];

    let messageIndex = 0;
    
    setInterval(() => {
        if (messageIndex < messages.length) {
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${messages[messageIndex].type}`;
            messageDiv.textContent = messages[messageIndex].text;
            if (chatMessages) chatMessages.appendChild(messageDiv);
            
            // Remove old messages to keep chat clean
            if (chatMessages && chatMessages.children.length > 6) {
                chatMessages.removeChild(chatMessages.firstChild);
            }
            
            messageIndex++;
        } else {
            messageIndex = 0;
            if (chatMessages) chatMessages.innerHTML = '<div class="message ai">Hello! I\'m your AI mentor. Ready to practice?</div>';
        }
    }, 3000);
}

// Typing animation for hero text
function typeWriter(element, text, speed = 100) {
    let i = 0;
    element.innerHTML = '';
    
    function type() {
        if (i < text.length) {
            element.innerHTML += text.charAt(i);
            i++;
            setTimeout(type, speed);
        }
    }
    type();
}

// Parallax effect for particles
function handleMouseMove(e) {
    const particles = document.querySelectorAll('.particle');
    const mouseX = e.clientX / window.innerWidth;
    const mouseY = e.clientY / window.innerHeight;

    particles.forEach((particle, index) => {
        const speed = (index % 3 + 1) * 0.5;
        const x = (mouseX - 0.5) * speed;
        const y = (mouseY - 0.5) * speed;
        particle.style.transform = `translate(${x}px, ${y}px)`;
    });
}

// Counter animation for statistics
function animateCounters() {
    const counters = document.querySelectorAll('.counter');
    
    counters.forEach(counter => {
        const target = parseInt(counter.getAttribute('data-target'));
        const duration = 2000; // 2 seconds
        const increment = target / (duration / 16); // 60fps
        let current = 0;
        
        const updateCounter = () => {
            current += increment;
            if (current < target) {
                counter.textContent = Math.floor(current);
                requestAnimationFrame(updateCounter);
            } else {
                counter.textContent = target;
            }
        };
        
        updateCounter();
    });
}

// ========== PARTICLE ANIMATION FOR DOTS ========== 
function createParticles() {
    const particlesContainer = document.getElementById('particles');
    if (!particlesContainer) return;
    // Prevent duplicate particles
    if (particlesContainer.childElementCount > 0) return;
    const particleCount = 105; // Increased from 25 to 45
    for (let i = 0; i < particleCount; i++) {
        const particle = document.createElement('div');
        particle.className = 'particle';
        particle.style.left = Math.random() * 100 + '%';
        particle.style.top = Math.random() * 100 + '%';
        particle.style.animationDelay = Math.random() * 6 + 's';
        particle.style.animationDuration = (Math.random() * 3 + 3) + 's';
        particlesContainer.appendChild(particle);
    }
}

// Initialize everything when page loads
document.addEventListener('DOMContentLoaded', function() {
    // Initialize core features
    createParticles();
    animateChat();
    
    // Add scroll event listener
    window.addEventListener('scroll', handleScroll);
    
    // Add smooth scrolling to navigation links
    const navLinks = document.querySelectorAll('.nav-links a');
    navLinks.forEach(link => {
        link.addEventListener('click', smoothScroll);
    });

    // Fix button redirect logic to check login status
    const buttons = document.querySelectorAll('.btn-primary, .btn-secondary, .cta-button');
    buttons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const token = localStorage.getItem("jwtToken");
            if (!token) {
                // Not logged in → go to signup
                window.location.href = 'signup.html';
            } else {
                // Logged in → allow normal behavior
                if (this.id === "startInterviewBtn") {
                    console.log("User is logged in. Starting interview...");
                    // Optionally, trigger start interview logic here if needed
                    // If your logic is already attached elsewhere, you can leave this empty
                } else {
                    // For other buttons, allow default or custom behavior
                }
            }
        });
    });

    // Add mouse move effect for particles
    document.addEventListener('mousemove', handleMouseMove);

    // Add typing animation to hero title (optional)
    const heroTitle = document.querySelector('.hero h1');
    if (heroTitle) {
        const originalText = heroTitle.textContent;
        setTimeout(() => {
            typeWriter(heroTitle, originalText, 50);
        }, 500);
    }

    // Add counter animation when in view
    const observerOptions = {
        threshold: 0.5,
        rootMargin: '0px 0px -100px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                animateCounters();
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);

    // Observe elements that need counter animation
    const counterSection = document.querySelector('.stats');
    if (counterSection) {
        observer.observe(counterSection);
    }

    // Add hover effects for feature cards
    const featureCards = document.querySelectorAll('.feature-card');
    featureCards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-15px) scale(1.02)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0) scale(1)';
        });
    });

    // Add loading animation
    window.addEventListener('load', function() {
        document.body.classList.add('loaded');
    });

    // Update admin dashboard stats for chats and users
    async function loadAdminDashboardStats() {
      try {
        const data = await apiFetch('/admin/dashboard_stats');
        if (typeof debugSetTotalUsers === 'function') {
          debugSetTotalUsers(data.total_users || 0);
        } else {
          const totalUsersElem = document.getElementById('totalUsers');
          if (totalUsersElem) totalUsersElem.innerText = data.total_users || 0;
        }
        const totalChatsElem = document.getElementById('totalChats');
        if (totalChatsElem) totalChatsElem.innerText = data.total_chats || 0;
        const todayChatsElem = document.getElementById('todayChats');
        if (todayChatsElem) todayChatsElem.innerText = data.today_chats || 0;
        const todayUsersElem = document.getElementById('todayUsers');
        if (todayUsersElem) todayUsersElem.innerText = data.today_users || 0;
        const adminUsersElem = document.getElementById('adminUsers');
        if (adminUsersElem) adminUsersElem.innerText = data.admin_users || 0;
        const todayAdminsElem = document.getElementById('todayAdmins');
        if (todayAdminsElem) todayAdminsElem.innerText = data.today_admins || 0;
        const totalSuggestFeedbackElem = document.getElementById('totalSuggestFeedback');
        if (totalSuggestFeedbackElem) totalSuggestFeedbackElem.innerText = data.total_suggest_feedback || 0;
        const totalSuggestFeedbackTodayElem = document.getElementById('totalSuggestFeedbackToday');
        if (totalSuggestFeedbackTodayElem) totalSuggestFeedbackTodayElem.innerText = data.total_suggest_feedback_today || 0;
      } catch (err) {
        const totalChatsElem = document.getElementById('totalChats');
        if (totalChatsElem) totalChatsElem.innerText = '0';
        const todayChatsElem = document.getElementById('todayChats');
        if (todayChatsElem) todayChatsElem.innerText = '0';
        if (typeof debugSetTotalUsers === 'function') {
          debugSetTotalUsers(0);
        } else {
          const totalUsersElem = document.getElementById('totalUsers');
          if (totalUsersElem) totalUsersElem.innerText = '0';
        }
        const todayUsersElem = document.getElementById('todayUsers');
        if (todayUsersElem) todayUsersElem.innerText = '0';
        const adminUsersElem = document.getElementById('adminUsers');
        if (adminUsersElem) adminUsersElem.innerText = '0';
        const todayAdminsElem = document.getElementById('todayAdmins');
        if (todayAdminsElem) todayAdminsElem.innerText = '0';
        const totalSuggestFeedbackElem = document.getElementById('totalSuggestFeedback');
        if (totalSuggestFeedbackElem) totalSuggestFeedbackElem.innerText = '0';
        const totalSuggestFeedbackTodayElem = document.getElementById('totalSuggestFeedbackToday');
        if (totalSuggestFeedbackTodayElem) totalSuggestFeedbackTodayElem.innerText = '0';
      }
    }
    loadAdminDashboardStats();
});

// Add some additional interactive features
function addInteractiveFeatures() {
    // Add ripple effect to buttons
    const buttons = document.querySelectorAll('.btn-primary, .btn-secondary, .cta-button');
    
    buttons.forEach(button => {
        button.addEventListener('click', function(e) {
            const ripple = document.createElement('span');
            const rect = this.getBoundingClientRect();
            const size = Math.max(rect.width, rect.height);
            const x = e.clientX - rect.left - size / 2;
            const y = e.clientY - rect.top - size / 2;
            
            ripple.style.width = ripple.style.height = size + 'px';
            ripple.style.left = x + 'px';
            ripple.style.top = y + 'px';
            ripple.classList.add('ripple');
            
            if (this) this.appendChild(ripple);
            
            setTimeout(() => {
                ripple.remove();
            }, 600);
        });
    });
}

// Call additional features
addInteractiveFeatures(); 

// ========== TEST INTERVIEW SESSION FOR HISTORY ==========
window.addTestInterviewSession = async function() {
  const userId = localStorage.getItem('userName');
  if (!userId) {
    alert('Please log in first.');
    return;
  }
  const session_id = 'test_' + Date.now();
  const jobRole = 'Test Engineer';
  const questions = [
    'Tell me about yourself.',
    'What is your greatest strength?',
    'Why do you want this job?'
  ];
  const answers = [
    'I am a detail-oriented engineer with 3 years of experience.',
    'My greatest strength is problem-solving.',
    'I want this job to grow my skills and contribute to your company.'
  ];
  // Save job role answer (first user message)
  await fetch('http://localhost:5000/api/history/add', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      user_id: userId,
      role: 'user',
      message: jobRole,
      session_id: session_id
    })
  });
  // Save Q&A pairs
  for (let i = 0; i < 3; i++) {
    // Save AI question
    await fetch('http://localhost:5000/api/history/add', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        user_id: userId,
        role: 'ai',
        message: questions[i],
        session_id: session_id
      })
    });
    // Save user answer
    await fetch('http://localhost:5000/api/history/add', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        user_id: userId,
        role: 'user',
        message: answers[i],
        session_id: session_id
      })
    });
  }
  alert('Test interview session added! Refresh the history page to see it.');
} 

// Utility: Extract score from improvement string
function extractScore(improvementText) {
  const match = improvementText.match(/average score is ([0-9.]+)\/10/);
  return match ? parseFloat(match[1]) : null;
}

// Get latest improvement score for the current user
window.getLatestImprovementScore = async function() {
  const jwtToken = localStorage.getItem('jwtToken');
  const userName = localStorage.getItem('userName') || 'anonymous';
  const res = await fetch(`${API_BASE}/feedback/list?user_id=${encodeURIComponent(userName)}`, {
    headers: { 'Authorization': 'Bearer ' + jwtToken }
  });
  const data = await res.json();
  const improvements = (data.feedback || []).filter(fb => fb.type === 'improvement' && fb.improvement);
  if (improvements.length === 0) return null;
  // Use the latest improvement
  const latest = improvements[improvements.length - 1].improvement;
  return extractScore(latest);
} 

// Suggestions Management
window.loadAdminSuggestions = async function() {
    try {
        const res = await fetch(`${API_BASE}/feedback/suggest/all`, {
            headers: { 'Authorization': 'Bearer ' + (localStorage.getItem('jwtToken') || '') }
        });
        const data = await res.json();
        const suggestions = data.suggest_feedback || [];
        window.adminSuggestions = suggestions;
        renderSuggestionTable(suggestions);
    } catch (err) {
        const tbody = document.getElementById('suggestionTableBody');
        if (tbody) tbody.innerHTML = '<tr><td colspan="5">Failed to load suggestions</td></tr>';
    }
}
function renderSuggestionTable(suggestions) {
    const tbody = document.getElementById('suggestionTableBody');
    tbody.innerHTML = '';
    if (!suggestions.length) {
        tbody.innerHTML = '<tr><td colspan="5" style="text-align:center;opacity:0.7;">No suggestions found.</td></tr>';
        return;
    }
    suggestions.forEach(sg => {
        const row = tbody.insertRow();
        row.insertCell().innerText = sg.user_name || sg.user_id || '';
        row.insertCell().innerText = sg.suggestion || '';
        // Status dropdown
        const statusCell = row.insertCell();
        const statusSelect = document.createElement('select');
        ['seen','working in progress','done'].forEach(opt => {
            const option = document.createElement('option');
            option.value = opt;
            option.textContent = opt.charAt(0).toUpperCase() + opt.slice(1);
            if (sg.status === opt) option.selected = true;
            statusSelect.appendChild(option);
        });
        statusSelect.onchange = function() {
            saveBtn.style.display = 'inline-block';
        };
        statusCell.appendChild(statusSelect);
        // Save button for status
        const saveBtn = document.createElement('button');
        saveBtn.innerText = 'Save';
        saveBtn.style.display = 'none';
        saveBtn.onclick = async function() {
            await fetch(`${API_BASE}/feedback/suggest/${sg._id}/status`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ status: statusSelect.value })
            });
            saveBtn.style.display = 'none';
        };
        statusCell.appendChild(saveBtn);
        // Date
        let dateStr = '';
        if (sg.created_at) {
            if (typeof sg.created_at === 'string') {
                dateStr = sg.created_at.slice(0, 10);
            } else if (sg.created_at.$date) {
                dateStr = sg.created_at.$date.slice(0, 10);
            }
        }
        row.insertCell().innerText = dateStr;
        // Actions
        const actionsCell = row.insertCell();
        const delBtn = document.createElement('button');
        delBtn.innerText = 'Delete';
        delBtn.onclick = async () => {
            await fetch(`${API_BASE}/feedback/suggest/${sg._id}`, { method: 'DELETE' });
            row.remove();
        };
        actionsCell.appendChild(delBtn);
    });
}
// Patch feedback sidebar logic to also load suggestions
const sidebarFeedbackElem = document.getElementById('sidebar-feedback');
if (sidebarFeedbackElem) {
    const origFeedbackSidebar = sidebarFeedbackElem.onclick;
    sidebarFeedbackElem.onclick = function() {
        if (origFeedbackSidebar) origFeedbackSidebar();
        window.loadAdminSuggestions();
    };
}

// ========== ADMIN DASHBOARD: DAILY VS NON-FREQUENT USERS DOUGHNUT CHART ========== 
async function loadUserStreakChart() {
  try {
    const res = await apiFetch('/admin/daily_vs_nonfrequent_users');
    const data = res;
    const ctx = document.getElementById('userStreakChart').getContext('2d');
    if (window.userStreakChartInstance) window.userStreakChartInstance.destroy();
    window.userStreakChartInstance = new Chart(ctx, {
      type: 'doughnut',
      data: {
        labels: ['Daily Users', 'Non-Frequent Users'],
        datasets: [{
          data: [data.daily, data.non_frequent],
          backgroundColor: ['#36A2EB', '#FF6384'], // Blue and Red for strong contrast
          borderColor: ['#1E88E5', '#D32F2F'], // Darker blue and red borders
          borderWidth: 2
        }]
      },
      options: {
        responsive: true,
        plugins: {
          legend: { position: 'bottom' },
          title: { display: false }
        }
      }
    });
  } catch (err) {
    console.error('Failed to load user streak chart:', err);
  }
}

document.addEventListener('DOMContentLoaded', function() {
  if (document.getElementById('userStreakChart')) {
    loadUserStreakChart();
  }
}); 

// Utility function for safe element update
function setIfElem(id, value) {
    const elem = document.getElementById(id);
    if (elem) elem.innerText = value;
}

// Update loadAdminDashboardStats to use null checks
async function loadAdminDashboardStats() {
    try {
        const res = await apiFetch('/admin/stats');
        const data = res;
        if (typeof debugSetTotalUsers === 'function') {
            debugSetTotalUsers(data.total_users || 0);
        } else {
            setIfElem('totalUsers', data.total_users || 0);
        }
        setIfElem('totalChats', data.total_chats || 0);
        setIfElem('todayChats', data.today_chats || 0);
        setIfElem('todayUsers', data.today_users || 0);
        setIfElem('adminUsers', data.admin_users || 0);
        setIfElem('todayAdmins', data.today_admins || 0);
        setIfElem('totalSuggestFeedback', data.total_suggest_feedback || 0);
        setIfElem('totalSuggestFeedbackToday', data.total_suggest_feedback_today || 0);
    } catch (err) {
        setIfElem('totalChats', '0');
        setIfElem('todayChats', '0');
        if (typeof debugSetTotalUsers === 'function') {
            debugSetTotalUsers(0);
        } else {
            setIfElem('totalUsers', '0');
        }
        setIfElem('todayUsers', '0');
        setIfElem('adminUsers', '0');
        setIfElem('todayAdmins', '0');
        setIfElem('totalSuggestFeedback', '0');
        setIfElem('totalSuggestFeedbackToday', '0');
    }
} 

// ========== PANEL SWITCHING FOR ADMIN ========== 
async function loadRecentActivity() {
    try {
        const res = await apiFetch('/admin/recent_activity');
        const activities = res.activities || [];
        const tbody = document.getElementById('recentActivityTable');
        if (!tbody) return;
        tbody.innerHTML = '';
        if (!activities.length) {
            tbody.innerHTML = '<tr><td colspan="4" style="text-align:center;opacity:0.7;">No recent activity found.</td></tr>';
            return;
        }
        activities.forEach(act => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${act.type}</td>
                <td>${act.user}</td>
                <td>${act.detail}</td>
                <td>${act.time ? new Date(act.time).toLocaleString() : ''}</td>
            `;
            tbody.appendChild(row);
        });
    } catch (err) {
        const tbody = document.getElementById('recentActivityTable');
        if (tbody) tbody.innerHTML = '<tr><td colspan="4">Failed to load activity</td></tr>';
    }
}
// Call on dashboard panel show and on page load if dashboard is active
if (document.getElementById('dashboard-panel')?.classList.contains('active')) {
    loadRecentActivity();
}
window.showAdminPanel = function(panel) {
    // Hide all admin sections
    document.querySelectorAll('.admin-section').forEach(section => {
        section.style.display = 'none';
        section.classList.remove('active');
    });
    // Remove active class from all sidebar items
    document.querySelectorAll('.sidebar-item').forEach(item => {
        item.classList.remove('active');
    });
    // Show the selected panel
    let panelId = '';
    switch(panel) {
        case 'dashboard':
            panelId = 'dashboard-panel';
            break;
        case 'user-monitoring':
            panelId = 'user-monitoring-panel';
            break;
        case 'chat-monitoring':
            panelId = 'chat-monitoring-panel';
            break;
        case 'user-suggestions':
            panelId = 'user-suggestions-panel';
            break;
        case 'admin-profile':
            panelId = 'admin-profile-panel';
            break;
        case 'system-settings':
            panelId = 'system-settings-panel';
            break;
        default:
            panelId = 'dashboard-panel';
    }
    const panelElem = document.getElementById(panelId);
    if (panelElem) {
        panelElem.style.display = '';
        panelElem.classList.add('active');
    }
    // Set active class on sidebar item
    document.querySelectorAll('.sidebar-item').forEach(item => {
        if (item.innerText.replace(/\s+/g, '').toLowerCase().includes(panel.replace(/-/g, ''))) {
            item.classList.add('active');
        }
    });
    // Special: Load users if user monitoring panel
    if (panel === 'user-monitoring') {
        const usersTable = document.getElementById('usersTable');
        if (usersTable) window.loadAdminUsers(usersTable);
    }
    // Special: Load chats if chat monitoring panel
    if (panel === 'chat-monitoring') {
        const chatsTable = document.getElementById('chatsTable');
        if (chatsTable) window.loadAdminChats(chatsTable);
    }
    // Special: Load suggestions if user suggestions panel
    if (panel === 'user-suggestions') {
        window.loadAdminSuggestions && window.loadAdminSuggestions();
    }
    // Set the avatar letter dynamically when showing the admin profile panel
    if (panel === 'admin-profile') {
        let adminName = localStorage.getItem('userName') || 'Admin';
        let initial = adminName.trim().charAt(0).toUpperCase();
        document.getElementById('adminAvatarText').textContent = initial;
    }
    // Load recent activity if dashboard
    if (panel === 'dashboard') {
        loadRecentActivity();
    }
    // Load admin profile details if admin profile panel
    if (panel === 'admin-profile') {
        window.loadAdminProfile();
    }
};

// ========== ADMIN PROFILE TAB SWITCHER ==========
window.showProfileTab = function(tab) {
    const accountTab = document.getElementById('profile-tab-account');
    const passwordTab = document.getElementById('profile-tab-password');
    const tabBtns = document.querySelectorAll('.tab-btn');
    if (tab === 'account') {
        accountTab.style.display = '';
        accountTab.classList.add('active');
        passwordTab.style.display = 'none';
        passwordTab.classList.remove('active');
        tabBtns[0].classList.add('active');
        tabBtns[1].classList.remove('active');
    } else {
        accountTab.style.display = 'none';
        accountTab.classList.remove('active');
        passwordTab.style.display = '';
        passwordTab.classList.add('active');
        tabBtns[0].classList.remove('active');
        tabBtns[1].classList.add('active');
    }
};

// Stub for change password form
window.handleChangePassword = function(event) {
    event.preventDefault();
    // TODO: Implement password change logic (API call)
    alert('Change password functionality coming soon!');
    return false;
}; 

document.addEventListener('DOMContentLoaded', function() {
  const modeSelect = document.getElementById('userGrowthModeSelect');
  if (modeSelect) {
    modeSelect.addEventListener('change', function() {
      loadAdminUserGrowthChart(this.value);
    });
    // Initial load
    loadAdminUserGrowthChart(modeSelect.value);
  }
});

async function loadAdminUserGrowthChart(mode) {
  try {
    const res = await apiFetch(`/admin/chart-data?mode=${mode}`);
    const data = res.user_growth;
    const ctx = document.getElementById('adminUserChart').getContext('2d');
    if (window.adminUserChartInstance) window.adminUserChartInstance.destroy();
    window.adminUserChartInstance = new Chart(ctx, {
      type: 'line',
      data: {
        labels: data.labels,
        datasets: [{
          label: 'User Growth',
          data: data.data,
          borderColor: '#36A2EB',
          backgroundColor: 'rgba(54,162,235,0.2)',
          fill: true,
          tension: 0.3
        }]
      },
      options: {
        responsive: true,
        plugins: {
          legend: { display: false }
        }
      }
    });
  } catch (err) {
    console.error('Failed to load user growth chart:', err);
  }
} 

document.addEventListener('DOMContentLoaded', async function() {
  if (window.location.pathname.endsWith('login.html')) return;
  // Set real admin name and avatar in the topbar
  try {
    const user = await apiFetch('/profile/me');
    // Set name
    const userNameElem = document.getElementById('userName');
    if (userNameElem) userNameElem.textContent = user.name || 'Admin';
    // Set avatar (if photo_url exists, else fallback to initial or icon)
    const avatarContainer = document.getElementById('userAvatarContainer');
    if (avatarContainer) {
      if (user.photo_url) {
        avatarContainer.innerHTML = `<img src="${user.photo_url}" alt="avatar" class="user-avatar" style="width:2.2rem;height:2.2rem;border-radius:50%;object-fit:cover;">`;
      } else if (user.name) {
        const initial = user.name.trim().charAt(0).toUpperCase();
        avatarContainer.innerHTML = `<span style='display:inline-flex;align-items:center;justify-content:center;width:2.2rem;height:2.2rem;border-radius:50%;background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);color:#fff;font-size:1.2rem;font-weight:bold;'>${initial}</span>`;
      } else {
        avatarContainer.innerHTML = `<i class="fas fa-user-circle" style="font-size:2rem;"></i>`;
      }
    }
  } catch (err) {
    // fallback: do nothing, keep default
  }
}); 

window.loadAdminProfile = async function() {
  try {
    const user = await apiFetch('/profile/me');
    // Set name
    const nameElem = document.getElementById('adminProfileName');
    if (nameElem) nameElem.textContent = user.name || 'Admin';
    // Set email
    const emailElem = document.getElementById('adminProfileEmail');
    if (emailElem) emailElem.textContent = user.email || '';
    // Set letter avatar
    const avatarElem = document.getElementById('adminAvatarText');
    if (avatarElem) {
      avatarElem.innerHTML = '';
      if (user.name) {
        avatarElem.textContent = user.name.trim().charAt(0).toUpperCase();
      } else {
        avatarElem.textContent = 'A';
      }
    }
  } catch (err) {
    // fallback: do nothing, keep default
  }
}; 

// ========== CHAT INTERVIEW START BUTTON ==========
document.addEventListener('DOMContentLoaded', function() {
  // Avoid auto-creating sessions on chat page; chat.html handles its own flow
  if (window.location.pathname.endsWith('chat.html')) return;
  refreshAuthVars();
  const startBtn = document.getElementById('startInterviewBtn');
  const micAnim = document.getElementById('micAnimationOverlay');
  if (startBtn && micAnim) {
    startBtn.addEventListener('click', async function() {
      refreshAuthVars();
      startBtn.disabled = true;
      startBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Starting...';
      try {
        const session_id = 'session_' + Date.now();
        const payload = { session_id };
        if (userId) payload.user_id = userId;
        await apiFetch('/session/', { method: 'POST', body: payload });
        localStorage.setItem('currentSessionId', session_id);
        micAnim.style.display = 'flex';
        startBtn.style.display = 'none';
      } catch (err) {
        startBtn.disabled = false;
        startBtn.innerHTML = '<i class="fas fa-microphone"></i> Start Interview';
      }
    });
  }
});
// Helper to stop mic animation if needed
window.stopMicAnimation = function() {
  const micAnim = document.getElementById('micAnimationOverlay');
  if (micAnim) micAnim.style.display = 'none';
}; 