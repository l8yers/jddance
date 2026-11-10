'use strict';

const year = document.getElementById('year');
if (year) year.textContent = new Date().getFullYear();

const toggle = document.getElementById('menuToggle');
const menu = document.getElementById('mobileMenu');
if (toggle && menu && typeof menu.showModal === 'function') {
  document.documentElement.classList.add('has-menu');
  toggle.hidden = false;
  let savedScroll = 0;
  const closeMenu = () => menu.close();
  toggle.addEventListener('click', () => {
    savedScroll = window.scrollY;
    document.body.style.top = `-${savedScroll}px`;
    document.body.classList.add('menu-open');
    toggle.setAttribute('aria-expanded', 'true');
    menu.showModal();
  });
  document.getElementById('closeMenu').addEventListener('click', closeMenu);
  menu.addEventListener('click', event => {
    if (event.target.closest('a')) closeMenu();
    if (event.target === menu) {
      const rect = menu.getBoundingClientRect();
      if (event.clientX < rect.left || event.clientX > rect.right || event.clientY < rect.top || event.clientY > rect.bottom) closeMenu();
    }
  });
  // Keep Tab within the menu; native dialog makes the background inert.
  menu.addEventListener('keydown', event => {
    if (event.key !== 'Tab') return;
    const controls = [...menu.querySelectorAll('button, a[href]')];
    const first = controls[0], last = controls[controls.length - 1];
    if (event.shiftKey && document.activeElement === first) {
      event.preventDefault(); last.focus();
    } else if (!event.shiftKey && document.activeElement === last) {
      event.preventDefault(); first.focus();
    }
  });
  menu.addEventListener('close', () => {
    document.body.classList.remove('menu-open');
    document.body.style.top = '';
    window.scrollTo(0, savedScroll);
    toggle.setAttribute('aria-expanded', 'false');
    if (window.matchMedia('(max-width: 900px)').matches) toggle.focus({preventScroll: true});
  });
  window.matchMedia('(min-width: 901px)').addEventListener('change', event => {
    if (event.matches && menu.open) closeMenu();
  });
}

const video = document.getElementById('hero-video');
const videoButton = document.querySelector('.video-toggle');
if (video && videoButton) {
  const motion = window.matchMedia('(prefers-reduced-motion: reduce)');
  const loadVideo = () => {
    const source = video.querySelector('source');
    if (!source.hasAttribute('src')) {
      source.src = source.dataset.src;
      video.load();
    }
  };
  const play = async () => {
    loadVideo();
    try { await video.play(); } catch { /* Poster and manual play remain available. */ }
  };
  const update = () => { const paused = video.paused;
    const label = paused ? 'Play video' : 'Pause video';
    videoButton.setAttribute('aria-label', label);
    videoButton.title = label;
    videoButton.querySelector('.video-play-icon').toggleAttribute('hidden', !paused);
    videoButton.querySelector('.video-pause-icon').toggleAttribute('hidden', paused); };
  videoButton.hidden = false;
  update();
  videoButton.addEventListener('click', () => video.paused ? play() : video.pause());
  video.addEventListener('play', update);
  video.addEventListener('pause', update);
  motion.addEventListener('change', event => { if (event.matches) video.pause(); });
  // Wait until the video is visible; reduced-motion/data-saving users get the poster.
  if (!motion.matches && !navigator.connection?.saveData) {
    if ('IntersectionObserver' in window) {
      const observer = new IntersectionObserver(entries => {
        if (entries.some(entry => entry.isIntersecting)) { play(); observer.disconnect(); }
      });
      observer.observe(video);
    } else { play(); }
  }
  document.addEventListener('visibilitychange', () => { if (document.hidden) video.pause(); });
}

const form = document.getElementById('enquiry-form');
if (form) {
  const params = new URLSearchParams(window.location.search);
  const interest = params.get('interest');
  if (['Classes', 'Studio Hire', 'Wedding First Dance', 'Hen Party', 'Other'].includes(interest)) form.elements.interest.value = interest;

}

// Netlify Forms remains the only backend. Native POST still works without JS.
if (form) {
  const status = document.getElementById('form-status');
  const submit = form.querySelector('[type="submit"]');
  form.addEventListener('submit', async event => {
    event.preventDefault();
    if (submit.disabled) return;
    submit.disabled = true;
    submit.textContent = 'Sending…';
    form.setAttribute('aria-busy', 'true');
    status.hidden = false;
    status.textContent = 'Sending your message…';
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 20000);
    try {
      const response = await fetch(form.action, {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: new URLSearchParams(new FormData(form)).toString(),
        signal: controller.signal,
      });
      if (!response.ok) throw new Error('Submission was not accepted');
      window.location.assign(form.action);
    } catch {
      status.textContent = 'We couldn’t confirm your message was sent. Your details are still here. Please try again, or email jddanceex@gmail.com.';
      submit.disabled = false;
      submit.textContent = 'Send message';
    } finally {
      clearTimeout(timeout);
      form.removeAttribute('aria-busy');
    }
  });
}
