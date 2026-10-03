/**
 * LoanGuard AI — High-Impact Interactive Frontend Logic
 */

document.addEventListener('DOMContentLoaded', () => {
    initNavigationTabs();
    initSyncedSliders();
    initPresets();
    initFormSubmission();
    initSensitivitySimulator();
    initChartFilters();
    initLightbox();
    initKeyboardShortcuts();
    updateLiveMathBar();
});

// ============================================================
// 1. Navigation Tabs
// ============================================================
function initNavigationTabs() {
    const navButtons = document.querySelectorAll('.nav-btn');
    const tabPanes = document.querySelectorAll('.tab-pane');

    navButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            const targetId = btn.getAttribute('data-tab');

            navButtons.forEach(b => b.classList.remove('active'));
            tabPanes.forEach(p => p.classList.remove('active'));

            btn.classList.add('active');
            const targetPane = document.getElementById(targetId);
            if (targetPane) {
                targetPane.classList.add('active');
            }
        });
    });
}

// ============================================================
// 2. Synced Sliders & Live Math Bar
// ============================================================
function initSyncedSliders() {
    const syncPairs = [
        { inputId: 'loan_amount', rangeId: 'range_loan_amount', hintId: 'hintLoanAmount', prefix: '$', suffix: '' },
        { inputId: 'installment', rangeId: 'range_installment', hintId: 'hintInstallment', prefix: '$', suffix: '/mo' },
        { inputId: 'int_rate', rangeId: 'range_int_rate', hintId: 'hintIntRate', prefix: '', suffix: '% APR' },
        { inputId: 'annual_income', rangeId: 'range_annual_income', hintId: 'hintIncome', prefix: '$', suffix: '/yr' },
        { inputId: 'dti', rangeId: 'range_dti', hintId: 'hintDTI', prefix: '', suffix: '% Ratio' }
    ];

    syncPairs.forEach(pair => {
        const input = document.getElementById(pair.inputId);
        const range = document.getElementById(pair.rangeId);
        const hint = document.getElementById(pair.hintId);

        if (!input || !range) return;

        // When Range Slider moves
        range.addEventListener('input', () => {
            input.value = range.value;
            updateHint(hint, range.value, pair.prefix, pair.suffix);
            updateLiveMathBar();
        });

        // When Number Input changes
        input.addEventListener('input', () => {
            range.value = input.value;
            updateHint(hint, input.value, pair.prefix, pair.suffix);
            updateLiveMathBar();
        });
    });
}

function updateHint(hintEl, val, prefix, suffix) {
    if (!hintEl) return;
    const num = parseFloat(val) || 0;
    const formatted = num >= 1000 ? num.toLocaleString() : num;
    hintEl.textContent = `${prefix}${formatted}${suffix}`;
}

function updateLiveMathBar() {
    const loanAmount = parseFloat(document.getElementById('loan_amount')?.value) || 0;
    const installment = parseFloat(document.getElementById('installment')?.value) || 0;
    const income = parseFloat(document.getElementById('annual_income')?.value) || 1;
    const dti = parseFloat(document.getElementById('dti')?.value) || 0;

    // Monthly Debt Burden %
    const burdenPct = (installment * 12 / income) * 100;
    const burdenEl = document.getElementById('quickBurden');
    if (burdenEl) {
        burdenEl.textContent = `${burdenPct.toFixed(1)}% of income`;
        burdenEl.className = 'math-val ' + (burdenPct < 15 ? 'text-green' : (burdenPct < 25 ? 'text-amber' : 'text-red'));
    }

    // Loan-to-Income Multiple
    const lti = loanAmount / income;
    const ltiEl = document.getElementById('quickLTI');
    if (ltiEl) {
        ltiEl.textContent = `${lti.toFixed(2)}x`;
        ltiEl.className = 'math-val ' + (lti < 0.25 ? 'text-green' : (lti < 0.5 ? 'text-amber' : 'text-red'));
    }

    // DTI Status
    const dtiStatusEl = document.getElementById('quickDTIStatus');
    if (dtiStatusEl) {
        if (dti < 20) {
            dtiStatusEl.textContent = 'Excellent (< 20%)';
            dtiStatusEl.className = 'math-val text-green';
        } else if (dti <= 35) {
            dtiStatusEl.textContent = 'Moderate (20-35%)';
            dtiStatusEl.className = 'math-val text-amber';
        } else {
            dtiStatusEl.textContent = 'Critical (> 35%)';
            dtiStatusEl.className = 'math-val text-red';
        }
    }
}

// ============================================================
// 3. Preset Test Profiles
// ============================================================
const PROFILES = {
    prime: {
        loan_amount: 10000,
        installment: 308.50,
        int_rate: 6.89,
        annual_income: 95000,
        dti: 11.2,
        home_ownership: 'MORTGAGE',
        verification_status: 'Verified',
        application_type: 'INDIVIDUAL'
    },
    moderate: {
        loan_amount: 14000,
        installment: 465.20,
        int_rate: 13.99,
        annual_income: 48000,
        dti: 22.4,
        home_ownership: 'RENT',
        verification_status: 'Source Verified',
        application_type: 'INDIVIDUAL'
    },
    highRisk: {
        loan_amount: 28000,
        installment: 985.40,
        int_rate: 22.80,
        annual_income: 30000,
        dti: 38.6,
        home_ownership: 'RENT',
        verification_status: 'Not Verified',
        application_type: 'INDIVIDUAL'
    }
};

function fillForm(data) {
    for (const [key, value] of Object.entries(data)) {
        const input = document.getElementById(key);
        const range = document.getElementById(`range_${key}`);
        if (input) {
            input.value = value;
            input.dispatchEvent(new Event('input'));
        }
        if (range) {
            range.value = value;
        }
    }
    updateLiveMathBar();
}

function initPresets() {
    const btnPrime = document.getElementById('presetPrime');
    const btnModerate = document.getElementById('presetModerate');
    const btnHighRisk = document.getElementById('presetHighRisk');
    const btnReset = document.getElementById('btnResetForm');

    if (btnPrime) {
        btnPrime.addEventListener('click', () => {
            fillForm(PROFILES.prime);
            triggerPrediction();
        });
    }

    if (btnModerate) {
        btnModerate.addEventListener('click', () => {
            fillForm(PROFILES.moderate);
            triggerPrediction();
        });
    }

    if (btnHighRisk) {
        btnHighRisk.addEventListener('click', () => {
            fillForm(PROFILES.highRisk);
            triggerPrediction();
        });
    }

    if (btnReset) {
        btnReset.addEventListener('click', () => {
            fillForm({
                loan_amount: 10000,
                installment: 300,
                int_rate: 10.0,
                annual_income: 60000,
                dti: 15.0,
                home_ownership: 'MORTGAGE',
                verification_status: 'Verified',
                application_type: 'INDIVIDUAL'
            });
            const emptyState = document.getElementById('emptyState');
            const resultsContainer = document.getElementById('resultsContainer');
            if (emptyState) emptyState.style.display = 'flex';
            if (resultsContainer) resultsContainer.style.display = 'none';
        });
    }
}

function triggerPrediction() {
    const form = document.getElementById('loanForm');
    if (form) {
        form.dispatchEvent(new Event('submit', { cancelable: true }));
    }
}

// ============================================================
// 4. Form Submission & Real-time Prediction
// ============================================================
function initFormSubmission() {
    const form = document.getElementById('loanForm');
    const btnSubmit = document.getElementById('btnSubmit');

    if (!form) return;

    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        const payload = {
            loan_amount: parseFloat(document.getElementById('loan_amount').value),
            installment: parseFloat(document.getElementById('installment').value),
            int_rate: parseFloat(document.getElementById('int_rate').value),
            annual_income: parseFloat(document.getElementById('annual_income').value),
            dti: parseFloat(document.getElementById('dti').value),
            application_type: document.getElementById('application_type').value,
            verification_status: document.getElementById('verification_status').value,
            home_ownership: document.getElementById('home_ownership').value
        };

        btnSubmit.classList.add('loading');
        btnSubmit.disabled = true;

        try {
            const response = await fetch('/predict', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            const result = await response.json();

            if (response.ok && result.status === 'success') {
                renderResults(result);
            } else {
                alert(`Assessment Error: ${result.message || 'Unable to process applicant credit data.'}`);
            }
        } catch (error) {
            console.error('Fetch error:', error);
            alert('Unable to connect to Flask server. Please verify that app.py is running.');
        } finally {
            btnSubmit.classList.remove('loading');
            btnSubmit.disabled = false;
        }
    });
}

function renderResults(data) {
    const emptyState = document.getElementById('emptyState');
    const resultsContainer = document.getElementById('resultsContainer');

    if (emptyState) emptyState.style.display = 'none';
    if (resultsContainer) resultsContainer.style.display = 'flex';

    // 1. Status Banner
    const banner = document.getElementById('decisionBanner');
    const title = document.getElementById('decisionTitle');
    const badge = document.getElementById('riskBadge');
    const icon = document.getElementById('decisionIcon');

    banner.className = `status-banner ${data.decision_badge}`;
    title.textContent = data.decision;
    badge.textContent = `${data.risk_tier} (Default Risk: ${data.default_risk_percentage}%)`;

    if (data.decision_badge === 'success') {
        icon.innerHTML = `<svg width="30" height="30" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg>`;
    } else if (data.decision_badge === 'danger') {
        icon.innerHTML = `<svg width="30" height="30" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>`;
    } else {
        icon.innerHTML = `<svg width="30" height="30" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>`;
    }

    // 2. Circular SVG Progress Gauge
    const riskPercent = Math.min(Math.max(data.default_risk_percentage, 0), 100);
    const circleMeter = document.getElementById('circleMeterProgress');
    const riskValue = document.getElementById('riskPercentValue');
    const spectrumMarker = document.getElementById('spectrumMarker');
    const metaDesc = document.getElementById('gaugeMetaDesc');

    if (riskValue) riskValue.textContent = `${riskPercent.toFixed(1)}%`;
    if (spectrumMarker) spectrumMarker.style.left = `${riskPercent}%`;

    // Circumference = 2 * PI * r = 2 * 3.14159 * 42 ≈ 264
    const totalCircumference = 264;
    const offset = totalCircumference - (totalCircumference * (riskPercent / 100));
    
    if (circleMeter) {
        circleMeter.style.strokeDashoffset = offset;
        if (riskPercent < 25) {
            circleMeter.style.stroke = '#10b981'; // Emerald
        } else if (riskPercent < 40) {
            circleMeter.style.stroke = '#f59e0b'; // Amber
        } else {
            circleMeter.style.stroke = '#f43f5e'; // Crimson
        }
    }

    if (metaDesc) {
        if (riskPercent < 25) {
            metaDesc.innerHTML = `Model estimates a <strong>${riskPercent.toFixed(1)}% chance of default</strong>, comfortably inside the safe prime approval threshold.`;
        } else if (riskPercent < 35) {
            metaDesc.innerHTML = `Model estimates a <strong>${riskPercent.toFixed(1)}% chance of default</strong>. Borderline credit risk requires secondary validation.`;
        } else {
            metaDesc.innerHTML = `Model estimates a severe <strong>${riskPercent.toFixed(1)}% chance of default</strong>, exceeding lender risk limits.`;
        }
    }

    // 3. Multiclass Confidence Bars
    const probs = data.probabilities || {};
    const fpProb = probs['Fully Paid'] || 0;
    const coProb = probs['Charged Off'] || 0;
    const curProb = probs['Current'] || 0;

    document.getElementById('probFullyPaid').textContent = `${fpProb.toFixed(1)}%`;
    document.getElementById('barFullyPaid').style.width = `${fpProb}%`;

    document.getElementById('probChargedOff').textContent = `${coProb.toFixed(1)}%`;
    document.getElementById('barChargedOff').style.width = `${coProb}%`;

    document.getElementById('probCurrent').textContent = `${curProb.toFixed(1)}%`;
    document.getElementById('barCurrent').style.width = `${curProb}%`;

    // 4. Financial Diagnostics
    const fin = data.financial_summary || {};
    document.getElementById('valBurden').textContent = fin.monthly_burden_pct || '0.0%';
    document.getElementById('valLTI').textContent = fin.loan_to_income_pct || '0.0%';
    document.getElementById('valDTI').textContent = fin.dti_ratio || '0.0%';

    // 5. Underwriting Guidance
    document.getElementById('recommendationText').textContent = data.recommendation;
}

// ============================================================
// 5. Financial Sensitivity Simulator (Tab 3)
// ============================================================
function initSensitivitySimulator() {
    const dtiSlider = document.getElementById('simDTISlider');
    const rateSlider = document.getElementById('simRateSlider');
    const burdenSlider = document.getElementById('simBurdenSlider');

    if (!dtiSlider || !rateSlider || !burdenSlider) return;

    function recalculateSim() {
        const dti = parseFloat(dtiSlider.value);
        const rate = parseFloat(rateSlider.value);
        const burden = parseFloat(burdenSlider.value);

        document.getElementById('simDTIVal').textContent = `${dti.toFixed(1)}%`;
        document.getElementById('simRateVal').textContent = `${rate.toFixed(2)}% APR`;
        document.getElementById('simBurdenVal').textContent = `${burden.toFixed(1)}%`;

        // Sensitivity formula weighted by ML feature importance
        // Importance: int_rate (~21%), installment/burden (~20%), dti (~18%)
        const simScore = Math.min(Math.max((dti * 0.42) + (rate * 0.75) + (burden * 0.48) - 4.5, 3.0), 96.0);

        const scoreEl = document.getElementById('simScoreNum');
        const badgeEl = document.getElementById('simTierBadge');
        if (scoreEl) scoreEl.textContent = `${simScore.toFixed(1)}%`;

        if (badgeEl) {
            if (simScore < 25) {
                badgeEl.textContent = 'LOW RISK TIER (AUTO-APPROVE)';
                badgeEl.className = 'sim-tier-badge badge-prime';
            } else if (simScore < 40) {
                badgeEl.textContent = 'MODERATE RISK TIER (MANUAL REVIEW)';
                badgeEl.className = 'sim-tier-badge badge-moderate';
            } else {
                badgeEl.textContent = 'HIGH DEFAULT RISK (AUTO-REJECT)';
                badgeEl.className = 'sim-tier-badge badge-subprime';
            }
        }

        // DTI Dot & Text
        const dotDTI = document.getElementById('dotDTI');
        const textDTI = document.getElementById('textDTIImpact');
        if (dotDTI && textDTI) {
            if (dti < 20) {
                dotDTI.className = 'sim-dot dot-green';
                textDTI.textContent = 'Strong debt capacity. Ample margin for debt repayment.';
            } else if (dti < 35) {
                dotDTI.className = 'sim-dot dot-amber';
                textDTI.textContent = 'Elevated debt load. Sensitive to income disruption.';
            } else {
                dotDTI.className = 'sim-dot dot-red';
                textDTI.textContent = 'Critical debt saturation. High statistical correlation with default.';
            }
        }

        // Rate Dot & Text
        const dotRate = document.getElementById('dotRate');
        const textRate = document.getElementById('textRateImpact');
        if (dotRate && textRate) {
            if (rate < 12) {
                dotRate.className = 'sim-dot dot-green';
                textRate.textContent = 'Prime borrower interest tier (Grade A/B). Low interest compounding.';
            } else if (rate < 20) {
                dotRate.className = 'sim-dot dot-amber';
                textRate.textContent = 'Near-prime interest tier (Grade C/D). Moderate carrying cost.';
            } else {
                dotRate.className = 'sim-dot dot-red';
                textRate.textContent = 'Subprime interest hazard (Grade E/F/G). Steep repayment slope.';
            }
        }

        // Burden Dot & Text
        const dotBurden = document.getElementById('dotBurden');
        const textBurden = document.getElementById('textBurdenImpact');
        if (dotBurden && textBurden) {
            if (burden < 10) {
                dotBurden.className = 'sim-dot dot-green';
                textBurden.textContent = 'Comfortable cash flow cushion after monthly installment.';
            } else if (burden < 20) {
                dotBurden.className = 'sim-dot dot-amber';
                textBurden.textContent = 'Moderate cash flow tightening. Limited discretionary margin.';
            } else {
                dotBurden.className = 'sim-dot dot-red';
                textBurden.textContent = 'Heavy monthly strain. High default risk if unexpected expense occurs.';
            }
        }
    }

    dtiSlider.addEventListener('input', recalculateSim);
    rateSlider.addEventListener('input', recalculateSim);
    burdenSlider.addEventListener('input', recalculateSim);
    recalculateSim();
}

// ============================================================
// 6. Chart Filtering
// ============================================================
function initChartFilters() {
    const filterChips = document.querySelectorAll('.filter-chip');
    const visualCards = document.querySelectorAll('.visual-card');

    filterChips.forEach(chip => {
        chip.addEventListener('click', () => {
            filterChips.forEach(c => c.classList.remove('active'));
            chip.classList.add('active');

            const filter = chip.getAttribute('data-filter');

            visualCards.forEach(card => {
                const category = card.getAttribute('data-category');
                if (filter === 'all' || category === filter) {
                    card.style.display = 'flex';
                } else {
                    card.style.display = 'none';
                }
            });
        });
    });
}

// ============================================================
// 7. Lightbox Image Modal
// ============================================================
function initLightbox() {
    const visualBoxes = document.querySelectorAll('.visual-image-box');
    visualBoxes.forEach(box => {
        const triggerOpen = () => {
            const img = box.querySelector('.visual-img');
            const titleElem = box.closest('.visual-card')?.querySelector('.visual-title');
            const title = titleElem ? titleElem.textContent.trim() : (img ? img.alt : 'Diagnostic Plot');
            if (img && img.src) {
                openLightbox(img.src, title);
            }
        };

        box.addEventListener('click', triggerOpen);
        box.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                triggerOpen();
            }
        });
    });
}

window.openLightbox = function(imageSrc, title) {
    const modal = document.getElementById('lightboxModal');
    const modalImg = document.getElementById('lightboxImg');
    const modalTitle = document.getElementById('lightboxTitle');

    if (modal && modalImg && modalTitle) {
        modalImg.src = imageSrc;
        modalTitle.textContent = title;
        modal.classList.add('open');
        document.body.style.overflow = 'hidden';
    }
};

window.closeLightbox = function(e) {
    const modal = document.getElementById('lightboxModal');
    if (e.target.classList.contains('lightbox-modal') || e.target.classList.contains('lightbox-close')) {
        modal.classList.remove('open');
        document.body.style.overflow = '';
    }
};

function initKeyboardShortcuts() {
    window.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            const modal = document.getElementById('lightboxModal');
            if (modal && modal.classList.contains('open')) {
                modal.classList.remove('open');
                document.body.style.overflow = '';
            }
        }
    });
}
