// =====================================================================
// SYSTÈME D'ANIMATIONS MODERNE POUR STREAMLIT
// =====================================================================

class ModernAnimations {
    constructor() {
        this.init();
    }
    
    init() {
        // Attendre que le DOM soit chargé
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => {
                this.setupAnimations();
            });
        } else {
            this.setupAnimations();
        }
    }
    
    setupAnimations() {
        this.setupScrollAnimations();
        this.setupInteractions();
        this.setupCounterAnimations();
        console.log('✅ Animations modernes activées');
    }
    
    // Animation au scroll
    setupScrollAnimations() {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('animate-fade-up');
                }
            });
        }, { 
            threshold: 0.1,
            rootMargin: '50px' 
        });
        
        // Observer toutes les cartes modernes
        const observeCards = () => {
            document.querySelectorAll('.modern-card').forEach(card => {
                if (!card.classList.contains('observed')) {
                    observer.observe(card);
                    card.classList.add('observed');
                }
            });
        };
        
        // Observer immédiatement et re-observer quand de nouveaux éléments apparaissent
        observeCards();
        
        // Re-scanner périodiquement pour les nouveaux éléments Streamlit
        setInterval(observeCards, 1000);
    }
    
    // Interactions avec les éléments
    setupInteractions() {
        // Délégation d'événements pour les nouveaux éléments
        document.addEventListener('mouseenter', (e) => {
            if (e.target.matches('.metric-card')) {
                this.animateMetricCard(e.target, true);
            }
        });
        
        document.addEventListener('mouseleave', (e) => {
            if (e.target.matches('.metric-card')) {
                this.animateMetricCard(e.target, false);
            }
        });
        
        // Animation des boutons avec effet ripple
        document.addEventListener('click', (e) => {
            if (e.target.matches('.btn-modern')) {
                this.createRippleEffect(e);
            }
        });
    }
    
    // Animation des cartes métriques
    animateMetricCard(card, isHover) {
        if (isHover) {
            card.style.transform = 'translateY(-8px) scale(1.05)';
            card.style.boxShadow = '0 20px 40px rgba(49, 130, 206, 0.3)';
            card.style.borderColor = 'rgba(49, 130, 206, 0.4)';
        } else {
            card.style.transform = '';
            card.style.boxShadow = '';
            card.style.borderColor = '';
        }
    }
    
    // Effet ripple sur les boutons
    createRippleEffect(e) {
        const button = e.target;
        const ripple = document.createElement('span');
        const rect = button.getBoundingClientRect();
        const size = Math.max(rect.width, rect.height);
        const x = e.clientX - rect.left - size / 2;
        const y = e.clientY - rect.top - size / 2;
        
        ripple.style.cssText = `
            position: absolute;
            width: ${size}px;
            height: ${size}px;
            left: ${x}px;
            top: ${y}px;
            background: rgba(255, 255, 255, 0.3);
            border-radius: 50%;
            transform: scale(0);
            animation: ripple 0.6s ease-out;
            pointer-events: none;
            z-index: 1;
        `;
        
        // Assurer que le bouton a position relative
        if (getComputedStyle(button).position === 'static') {
            button.style.position = 'relative';
        }
        
        button.appendChild(ripple);
        setTimeout(() => ripple.remove(), 600);
    }
    
    // Animation des compteurs
    setupCounterAnimations() {
        const animateValue = (element, start, end, duration) => {
            if (end === 0) return;
            
            const range = end - start;
            const increment = end > start ? 1 : -1;
            const stepTime = Math.abs(Math.floor(duration / range));
            let current = start;
            
            const timer = setInterval(() => {
                current += increment;
                
                // Formatter les nombres avec séparateurs
                if (current >= 1000) {
                    element.textContent = current.toLocaleString();
                } else {
                    element.textContent = current;
                }
                
                if (current === end) {
                    clearInterval(timer);
                }
            }, stepTime);
        };
        
        // Observer pour déclencher les compteurs
        const counterObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const element = entry.target;
                    const text = element.textContent;
                    
                    // Extraire le nombre du texte
                    const number = parseInt(text.replace(/[^0-9]/g, ''));
                    
                    if (number > 0 && number < 10000) {
                        element.textContent = '0';
                        animateValue(element, 0, number, 2000);
                        counterObserver.unobserve(element);
                    }
                }
            });
        });
        
        // Observer les valeurs métriques
        const observeCounters = () => {
            document.querySelectorAll('.metric-value').forEach(el => {
                if (!el.classList.contains('counted')) {
                    counterObserver.observe(el);
                    el.classList.add('counted');
                }
            });
        };
        
        // Observer maintenant et re-scanner
        observeCounters();
        setInterval(observeCounters, 2000);
    }
    
    // Fonction utilitaire pour afficher des notifications
    showToast(message, type = 'info', duration = 5000) {
        const toast = document.createElement('div');
        const icons = {
            success: '✅',
            error: '❌',
            warning: '⚠️',
            info: 'ℹ️'
        };
        
        toast.className = `toast toast-${type}`;
        toast.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: rgba(26, 29, 35, 0.95);
            border: 1px solid rgba(255, 255, 255, 0.12);
            border-radius: 12px;
            padding: 16px 20px;
            color: white;
            z-index: 10000;
            backdrop-filter: blur(20px);
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
            transform: translateX(400px);
            animation: slideInToast 0.4s ease forwards;
            display: flex;
            align-items: center;
            gap: 12px;
            min-width: 300px;
            border-left: 4px solid ${type === 'success' ? '#38a169' : type === 'error' ? '#e53e3e' : type === 'warning' ? '#ed8936' : '#3182ce'};
        `;
        
        toast.innerHTML = `
            <span style="font-size: 1.2rem;">${icons[type]}</span>
            <span style="font-weight: 500; flex: 1;">${message}</span>
            <button onclick="this.parentElement.remove()" style="background: none; border: none; color: rgba(255,255,255,0.7); cursor: pointer; font-size: 1.2rem; padding: 0;">×</button>
        `;
        
        document.body.appendChild(toast);
        
        // Auto-remove
        setTimeout(() => {
            toast.style.animation = 'slideInToast 0.3s ease reverse';
            setTimeout(() => toast.remove(), 300);
        }, duration);
    }
}

// CSS pour les animations (ajouté dynamiquement)
const animationCSS = `
    @keyframes ripple {
        to { transform: scale(2); opacity: 0; }
    }
    
    @keyframes slideInToast {
        to { transform: translateX(0); }
    }
    
    .btn-modern { 
        position: relative; 
        overflow: hidden; 
    }
    
    .animate-fade-up {
        animation: fadeInUp 0.6s ease forwards;
    }
`;

// Ajouter le CSS
const style = document.createElement('style');
style.textContent = animationCSS;
document.head.appendChild(style);

// Initialiser les animations
const animations = new ModernAnimations();

// Exposer globalement pour usage dans Streamlit
window.animations = animations;
window.showToast = (message, type, duration) => animations.showToast(message, type, duration);

// Message de confirmation
console.log('🎉 Système d\'animations moderne chargé avec succès!');
