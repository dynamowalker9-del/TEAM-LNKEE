// Navigation Menu Functionality

document.addEventListener('DOMContentLoaded', function() {
  const navLinks = document.querySelectorAll('.nav-link');
  
  // Handle navigation link clicks
  navLinks.forEach(link => {
    link.addEventListener('click', function(e) {
      const href = this.getAttribute('href') || '';

      // If it's an intra-page anchor, prevent default and smooth-scroll
      if (href.startsWith('#')) {
        e.preventDefault();
        navLinks.forEach(l => l.classList.remove('active'));
        this.classList.add('active');
        const targetSection = document.querySelector(href);
        if (targetSection) {
          targetSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
        return;
      }

      // External/internal page navigation: allow browser navigation
      navLinks.forEach(l => l.classList.remove('active'));
      this.classList.add('active');
      // letting the browser follow the link (no preventDefault)
    });
  });
  
  // Update active link on scroll
  window.addEventListener('scroll', function() {
    let current = '';
    
    const sections = [
      { id: 'planets-section', link: '[data-section="planets"]' },
      { id: 'asteroid-table', link: '[data-section="asteroids"]' },
      { id: 'dashboard', link: '[data-section="dashboard"]' },
      { id: 'stats', link: '[data-section="stats"]' }
    ];
    
    sections.forEach(section => {
      const element = document.getElementById(section.id);
      if (element) {
        const rect = element.getBoundingClientRect();
        if (rect.top <= 200) {
          current = section.id;
        }
      }
    });
    
    // Update active state based on scroll position
    navLinks.forEach(link => {
      link.classList.remove('active');
      const href = link.getAttribute('href').substring(1);
      if (href === current) {
        link.classList.add('active');
      }
    });
  });
  
  // Set initial active state
  navLinks[0].classList.add('active');
});
