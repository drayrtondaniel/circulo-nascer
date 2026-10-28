/* =========================================================
   CÍRCULO NASCER — script.js
   Lógica: LGPD → Quiz (2 etapas) → Lead capture → Recomendação
   ========================================================= */

document.addEventListener('DOMContentLoaded', function () {

    /* ---------- ANALYTICS (dataLayer / GTM) ---------- */
    function trackEvent(eventName, eventData = {}) {
        if (typeof dataLayer !== 'undefined') {
            dataLayer.push({
                event: eventName,
                ...eventData,
                timestamp: new Date().toISOString()
            });
        }
        console.log(`[Analytics] ${eventName}`, eventData);
    }

    /* ---------- LGPD ---------- */
    const lgpdModal = document.getElementById('lgpdModal');
    const lgpdAccept = document.getElementById('lgpdAccept');

    document.querySelector('.btn-next')?.addEventListener('click', function () {
        if (!window.lgpdConsent.accepted) {
            lgpdModal.classList.add('active');
            trackEvent('lgpd_modal_displayed');
        }
    });

    lgpdAccept.addEventListener('click', function () {
        window.lgpdConsent.accepted = true;
        window.lgpdConsent.categories.analytics = document.getElementById('consentAnalytics').checked;
        window.lgpdConsent.categories.marketing = document.getElementById('consentMarketing').checked;
        localStorage.setItem('lgpd_accepted', 'true');
        lgpdModal.classList.remove('active');

        trackEvent('lgpd_consent_given', {
            analytics: window.lgpdConsent.categories.analytics,
            marketing: window.lgpdConsent.categories.marketing
        });
    });

    /* ---------- QUIZ ---------- */
    const answers = {};
    let currentStep = 1;

    // Seleção de opção
    document.querySelectorAll('.option-card').forEach(card => {
        card.addEventListener('click', function () {
            const step = this.closest('.question-step');
            step.querySelectorAll('.option-card').forEach(c => c.classList.remove('selected'));
            this.classList.add('selected');

            answers[`q${step.dataset.step}`] = this.dataset.value;

            const nextBtn = step.querySelector('.btn-next, .btn-submit');
            if (nextBtn) nextBtn.disabled = false;

            trackEvent('quiz_option_selected', {
                step: step.dataset.step,
                value: this.dataset.value
            });
        });
    });

    // Avançar etapa
    document.querySelectorAll('.btn-next').forEach(btn => {
        btn.addEventListener('click', function () {
            if (this.disabled) return;

            trackEvent('quiz_step_completed', { step: currentStep });

            document.querySelector(`.question-step[data-step="${currentStep}"]`).classList.remove('active');
            document.querySelector(`.progress-step[data-step="${currentStep}"]`).classList.remove('active');
            document.querySelector(`.progress-step[data-step="${currentStep}"]`).classList.add('completed');

            currentStep++;

            document.querySelector(`.question-step[data-step="${currentStep}"]`).classList.add('active');
            document.querySelector(`.progress-step[data-step="${currentStep}"]`).classList.add('active');

            trackEvent('quiz_step_started', { step: currentStep });

            if (currentStep === 2) {
                this.style.display = 'none';
            }
        });
    });

    // Voltar etapa
    document.querySelectorAll('.btn-prev').forEach(btn => {
        btn.addEventListener('click', function () {
            document.querySelector(`.question-step[data-step="${currentStep}"]`).classList.remove('active');
            document.querySelector(`.progress-step[data-step="${currentStep}"]`).classList.remove('active');
            document.querySelector(`.progress-step[data-step="${currentStep}"]`).classList.remove('completed');

            currentStep--;

            document.querySelector(`.question-step[data-step="${currentStep}"]`).classList.add('active');
            document.querySelector(`.progress-step[data-step="${currentStep}"]`).classList.add('active');

            if (currentStep < 2) {
                const nextBtn = document.querySelector(`.question-step[data-step="${currentStep}"] .btn-next`);
                if (nextBtn) {
                    nextBtn.style.display = 'block';
                    nextBtn.disabled = !document.querySelector(`.question-step[data-step="${currentStep}"] .option-card.selected`);
                }
            }
        });
    });

    /* ---------- ENVIO DO QUIZ → LEAD CAPTURE ---------- */
    document.querySelector('.btn-submit').addEventListener('click', function () {
        if (this.disabled) return;

        trackEvent('quiz_completed', { answers });

        document.getElementById('leadCapture').classList.add('active');
        trackEvent('lead_capture_displayed');
    });

    // Envio do formulário de lead
    document.getElementById('leadForm').addEventListener('submit', function (e) {
        e.preventDefault();

        if (!document.getElementById('leadConsent').checked) {
            alert('Para receber materiais, é necessário concordar com nossa Política de Privacidade.');
            return;
        }

        const formData = {
            name: this.name.value,
            email: this.email.value,
            whatsapp: this.whatsapp.value,
            quiz_answers: { ...answers },
            timestamp: new Date().toISOString()
        };

        trackEvent('lead_captured', {
            email: formData.email,
            has_whatsapp: !!formData.whatsapp,
            quiz_profile: `${answers.q1 || 'nao-sei'}_${answers.q2 || 'geral'}`
        });

        // Ponto de integração: enviar para CRM/webhook aqui (futuro)

        document.getElementById('leadCapture').classList.remove('active');
        showRecommendation();
    });

    // Pular lead capture
    document.getElementById('leadSkip').addEventListener('click', function () {
        trackEvent('lead_capture_skipped');
        document.getElementById('leadCapture').classList.remove('active');
        showRecommendation();
    });

    /* ---------- RECOMENDAÇÃO ---------- */
    function showRecommendation() {
        const planoRecomendado = calcularPlanoRecomendado(answers);
        atualizarRecomendacao(planoRecomendado);

        document.getElementById('recommendation').classList.add('active');
        document.getElementById('recommendation').scrollIntoView({ behavior: 'smooth', block: 'start' });

        trackEvent('recommendation_viewed', { plano: planoRecomendado });

        document.querySelectorAll('.plan-card').forEach(card => card.classList.remove('recommended'));
        document.getElementById(`plan-${planoRecomendado}`).classList.add('recommended');
    }

    function calcularPlanoRecomendado(answers) {
        const trimestre = answers.q1;
        const expectativa = answers.q2;

        if (trimestre === 'nao-sei' || expectativa === 'geral') {
            return 'acompanhamento'; // padrão equilibrado
        }
        if (trimestre === 'terceiro' || expectativa === 'planejamento') {
            return 'integral';
        }
        if (expectativa === 'suporte' || trimestre === 'primeiro') {
            return 'acompanhamento';
        }
        return 'essential';
    }

    function atualizarRecomendacao(plano) {
        const planos = {
            essential: {
                titulo: 'Plano Essencial — Orientação',
                subtitle: 'Base sólida para uma gestação tranquila e informada',
                reason: 'Para quem busca organização e segurança técnica, este plano oferece revisão periódica do pré-natal e orientação fundamentada sobre exames, garantindo clareza em cada decisão.',
                features: [
                    'Revisão do pré-natal por trimestre',
                    'Sugestão e orientação personalizada sobre exames',
                    'Suporte via WhatsApp (resposta em até 72h)',
                    'Encontro em grupo (videochamada, 90 min)'
                ],
                preco: 'R$ 247,00'
            },
            acompanhamento: {
                titulo: 'Plano Acompanhamento — Presença',
                subtitle: 'Equilíbrio entre suporte personalizado e autonomia na jornada',
                reason: 'Considerando seu perfil, este plano oferece acompanhamento contínuo com reavaliações regulares e canal dedicado para dúvidas, apoiando segurança clínica e emocional em cada etapa.',
                features: [
                    'Reavaliações bimestrais aprofundadas',
                    'Suporte para dúvidas com resposta em até 72h',
                    'Atendimento de urgência por ligação (horário comercial)',
                    'Encontro mensal (individual ou casal)'
                ],
                preco: 'R$ 490,00'
            },
            integral: {
                titulo: 'Plano Integral — Vínculo',
                subtitle: 'Cuidado profundo e contínuo para momentos que exigem atenção especial',
                reason: 'Para gestações que demandam acompanhamento redobrado ou para quem deseja o máximo de suporte personalizado, este plano oferece acompanhamento mensal, urgência 24h e construção conjunta do seu Plano de Parto fundamentado.',
                features: [
                    'Reavaliações mensais (quinzenais no 9º mês)',
                    'Atendimento de urgência por ligação 24 horas',
                    'Construção conjunta do Plano de Parto baseado em evidências',
                    'Canal prioritário e foco total no vínculo emocional e clínico'
                ],
                preco: 'R$ 890,00'
            }
        };

        const planoData = planos[plano];

        document.getElementById('rec-title').textContent = planoData.titulo;
        document.getElementById('rec-subtitle').textContent = planoData.subtitle;
        document.getElementById('rec-reason').textContent = planoData.reason;
        document.querySelector('.recommendation-price').innerHTML =
            `${planoData.preco} <span>/mês — plano trimestral</span>`;

        const featuresList = document.getElementById('rec-features');
        featuresList.innerHTML = '';
        planoData.features.forEach(feature => {
            const li = document.createElement('li');
            li.textContent = feature;
            featuresList.appendChild(li);
        });

        const ctaBtn = document.getElementById('rec-cta');
        ctaBtn.href = `https://wa.me/5519992199683?text=Ol%C3%A1%2C%20vim%20pelo%20site%20do%20C%C3%ADrculo%20Nascer%20e%20gostaria%20de%20saber%20mais%20sobre%20os%20planos.`;
    }

    /* ---------- NAVEGAÇÃO (planos) ---------- */
    document.getElementById('show-all-plans').addEventListener('click', function () {
        trackEvent('browse_all_plans_clicked');
        document.getElementById('plans-section').scrollIntoView({ behavior: 'smooth', block: 'start' });
    });

    document.getElementById('browse-plans').addEventListener('click', function (e) {
        e.preventDefault();
        trackEvent('browse_plans_link_clicked');
        document.getElementById('plans-section').scrollIntoView({ behavior: 'smooth', block: 'start' });
    });

    /* ---------- EVENTOS INICIAIS ---------- */
    trackEvent('quiz_started', { page: 'landing_otimizada' });
    trackEvent('quiz_step_started', { step: 1 });

    /* ---------- TOUCH (mobile) ---------- */
    document.querySelectorAll('.option-card, .btn-plan, .btn-nav, .btn-submit, .btn-primary, .btn-secondary').forEach(el => {
        el.addEventListener('touchstart', function () {
            this.style.transform = 'translateY(-2px)';
        });
        el.addEventListener('touchend', function () {
            this.style.transform = '';
        });
    });

    /* ---------- SMOOTH SCROLL (links internos #) ---------- */
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            const href = this.getAttribute('href');
            if (href === '#') return;

            e.preventDefault();
            const target = document.querySelector(href);
            if (target) {
                trackEvent('internal_link_clicked', { target: href });
                window.scrollTo({
                    top: target.offsetTop - 100,
                    behavior: 'smooth'
                });
            }
        });
    });

});
