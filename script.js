// SkillSpeak AI Landing Page JavaScript

// Create floating particles
function createParticles() {
    const particlesContainer = document.getElementById('particles');
    const particleCount = 50;

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

// Navbar scroll effect
function handleScroll() {
    const navbar = document.getElementById('navbar');
    if (window.scrollY > 50) {
        navbar.classList.add('scrolled');
    } else {
        navbar.classList.remove('scrolled');
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
            chatMessages.appendChild(messageDiv);
            
            // Remove old messages to keep chat clean
            if (chatMessages.children.length > 6) {
                chatMessages.removeChild(chatMessages.firstChild);
            }
            
            messageIndex++;
        } else {
            messageIndex = 0;
            chatMessages.innerHTML = '<div class="message ai">Hello! I\'m your AI mentor. Ready to practice?</div>';
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

    // Add click handlers for buttons
    const buttons = document.querySelectorAll('.btn-primary, .btn-secondary, .cta-button');
    buttons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            // Navigate to signup page instead of showing alerts
            window.location.href = 'signup.html';
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
            
            this.appendChild(ripple);
            
            setTimeout(() => {
                ripple.remove();
            }, 600);
        });
    });
}

// Call additional features
addInteractiveFeatures(); 