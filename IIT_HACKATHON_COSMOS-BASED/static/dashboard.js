document.addEventListener('DOMContentLoaded', () => {
  const search = document.getElementById('search');
  const filterHazard = document.getElementById('filter-hazard');
  const sortBy = document.getElementById('sort-by');
  const clearBtn = document.getElementById('clear-filters');
  const tbody = document.querySelector('table tbody');
  const tableWrapper = document.getElementById('asteroid-table');
  const planetsSection = document.getElementById('planets-section');

  // Intersection Observer for planet cards pop-in animation with stagger
  if (planetsSection) {
    const planetCards = planetsSection.querySelectorAll('.planet-card');
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          planetCards.forEach((card, index) => {
            setTimeout(() => {
              card.classList.add('pop-in');
            }, index * 90); // 90ms stagger between each
          });
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.1 });
    observer.observe(planetsSection);
  }

  function getRows() { return Array.from(tbody.querySelectorAll('tr')); }

  function rowData(row) {
    const tds = row.querySelectorAll('td');
    return {
      name: tds[0]?.textContent.trim().toLowerCase() || '',
      diameter: parseFloat(tds[1]?.textContent) || 0,
      velocity: parseFloat(tds[2]?.textContent) || 0,
      distance: parseFloat(tds[3]?.textContent.replace(/,/g, '')) || 0,
      hazard: tds[4]?.textContent.toLowerCase().includes('hazard')
    };
  }

  function applyFilters() {
    const q = search.value.trim().toLowerCase();
    const f = filterHazard.value;
    getRows().forEach(row => {
      const d = rowData(row);
      let visible = true;
      if (q && !d.name.includes(q)) visible = false;
      if (f === 'hazard' && !d.hazard) visible = false;
      if (f === 'safe' && d.hazard) visible = false;
      row.style.display = visible ? '' : 'none';
    });
  }

  function applySort() {
    const key = sortBy.value;
    const rows = getRows().filter(r => r.style.display !== 'none');
    rows.sort((a,b) => {
      const A = rowData(a)[key];
      const B = rowData(b)[key];
      if (typeof A === 'string') return A.localeCompare(B);
      return B - A; // numeric: descending
    });
    rows.forEach(r => tbody.appendChild(r));
  }

  search.addEventListener('input', () => { applyFilters(); applySort(); });
  filterHazard.addEventListener('change', () => { applyFilters(); applySort(); });
  sortBy.addEventListener('change', () => { applySort(); });
  clearBtn.addEventListener('click', () => { search.value=''; filterHazard.value='all'; sortBy.value='name'; applyFilters(); applySort(); });

  // Intersection Observer for asteroid table pop-down animation on scroll
  if (tableWrapper) {
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('pop-down');
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.1 });
    observer.observe(tableWrapper);
  }

  // initial
  applyFilters();
});
