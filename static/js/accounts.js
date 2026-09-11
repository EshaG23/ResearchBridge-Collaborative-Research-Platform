(() => {
  const email = document.querySelector('[data-college-email]');
  const submit = document.querySelector('[data-email-submit]');
  if (email && submit) {
    const validate = () => {
      const value = email.value.trim();
      const valid = /^[^\s@]+@(rbunagpur|rknec)\.in$/i.test(value) && email.validity.typeMismatch === false;
      submit.disabled = !valid;
      document.querySelector('[data-email-feedback]').textContent = value && !valid ? 'Use a valid @rbunagpur.in or @rknec.in college email address.' : '';
    };
    email.addEventListener('input', validate);
    email.addEventListener('blur', () => { email.value = email.value.trim(); validate(); });
    validate();
  }
  const countdown = document.querySelector('[data-countdown]');
  const resend = document.querySelector('[data-resend]');
  const started = Date.now();
  const tick = () => {
    const elapsed = Math.floor((Date.now() - started) / 1000);
    if (countdown) {
      const left = Math.max(0, Number(countdown.dataset.countdown) - elapsed);
      countdown.textContent = left ? `${Math.floor(left/60)}:${String(left%60).padStart(2,'0')}` : 'Expired — request a new code';
      if (!left) document.querySelector('[data-verify-submit]').disabled = true;
    }
    if (resend) {
      const left = Math.max(0, Number(resend.dataset.resend) - elapsed);
      resend.disabled = left > 0;
      resend.textContent = left ? `Request another code in ${left}s` : 'Request another code';
    }
  };
  if (countdown || resend) { tick(); setInterval(tick, 1000); }
  const roleChoices = document.querySelectorAll('[name="role"]');
  const updateRole = () => {
    const role = document.querySelector('[name="role"]:checked')?.value || document.querySelector('input[type=hidden][name=role]')?.value || 'student';
    document.querySelectorAll('[data-role-section]').forEach(section => {
      const show = section.dataset.roleSection === role;
      section.hidden = !show;
      section.querySelectorAll('input, select, textarea').forEach(input => input.disabled = !show);
    });
  };
  roleChoices.forEach(input => input.addEventListener('change', updateRole));
  if (roleChoices.length) updateRole();
})();
