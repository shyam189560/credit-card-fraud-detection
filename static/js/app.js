document.addEventListener('DOMContentLoaded', () => {
  const cursorGlow = document.getElementById('cursorGlow');

  document.querySelectorAll('.flash').forEach((item) => {
    setTimeout(() => {
      item.style.opacity = '0';
      item.style.transform = 'translateY(-8px)';
    }, 3500);
  });

  if (cursorGlow) {
    window.addEventListener('mousemove', (e) => {
      cursorGlow.style.opacity = '1';
      cursorGlow.style.left = `${e.clientX}px`;
      cursorGlow.style.top = `${e.clientY}px`;
    });

    window.addEventListener('mouseleave', () => {
      cursorGlow.style.opacity = '0';
    });
  }

  document.querySelectorAll('.tilt-card').forEach((card) => {
    card.addEventListener('mousemove', (e) => {
      const rect = card.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;
      const rotateX = ((y / rect.height) - 0.5) * -10;
      const rotateY = ((x / rect.width) - 0.5) * 10;

      card.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) translateY(-4px)`;
      card.style.borderColor = 'rgba(111,124,255,0.28)';
      card.style.boxShadow = '0 32px 80px rgba(0,0,0,0.42), 0 0 0 1px rgba(0,215,198,0.08)';
    });

    card.addEventListener('mouseleave', () => {
      card.style.transform = 'perspective(1000px) rotateX(0deg) rotateY(0deg) translateY(0px)';
      card.style.borderColor = 'rgba(255,255,255,0.10)';
      card.style.boxShadow = '';
    });
  });

  document.querySelectorAll('.magnetic').forEach((btn) => {
    btn.addEventListener('mousemove', (e) => {
      const rect = btn.getBoundingClientRect();
      const x = e.clientX - rect.left - rect.width / 2;
      const y = e.clientY - rect.top - rect.height / 2;
      btn.style.transform = `translate(${x * 0.08}px, ${y * 0.12}px) translateY(-3px)`;
    });

    btn.addEventListener('mouseleave', () => {
      btn.style.transform = 'translate(0, 0)';
    });
  });
});
