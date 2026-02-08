document.addEventListener('DOMContentLoaded', function () {
  const rows = document.querySelectorAll('tbody tr[data-neo-id]');
  const modal = document.getElementById('detail-modal');
  const modalInner = modal.querySelector('.modal-inner');
  const modalTitle = document.getElementById('modal-title');
  const modalBody = document.getElementById('modal-body');
  const modalLink = document.getElementById('modal-link');
  const closeBtn = document.getElementById('modal-close');

  function showModal(data) {
    modalTitle.textContent = data.name || 'Object Details';
    modalBody.innerHTML = `
      <p><strong>ID:</strong> ${data.id || '—'}</p>
      <p><strong>Absolute magnitude (H):</strong> ${data.absolute_magnitude_h || '—'}</p>
      <p><strong>First observation:</strong> ${data.first_observation_date || '—'}</p>
      <p><strong>Last observation:</strong> ${data.last_observation_date || '—'}</p>
      <p><strong>Hazardous:</strong> ${data.is_potentially_hazardous_asteroid ? 'Yes' : 'No'}</p>
      <p><strong>Orbit class:</strong> ${data.orbit_class || '—'}</p>
    `;
    if (data.nasa_jpl_url) {
      modalLink.href = data.nasa_jpl_url;
      modalLink.style.display = 'inline-block';
    } else {
      modalLink.style.display = 'none';
    }
    modal.classList.remove('hidden');
    document.body.style.overflow = 'hidden';
  }

  function hideModal() {
    modal.classList.add('hidden');
    document.body.style.overflow = '';
  }

  rows.forEach(row => {
    const id = row.getAttribute('data-neo-id');
    if (id) {
      row.style.cursor = 'pointer';
      row.addEventListener('click', async () => {
        modalBody.textContent = 'Loading…';
        modalLink.style.display = 'none';
        modal.classList.remove('hidden');
        try {
          const res = await fetch(`/neo/${encodeURIComponent(id)}`);
          if (!res.ok) {
            modalBody.textContent = 'Details not available.';
            return;
          }
          const data = await res.json();
          showModal(data);
        } catch (err) {
          modalBody.textContent = 'Error fetching details: ' + err.message;
          console.error(err);
        }
      });
    }
  });

  closeBtn.addEventListener('click', hideModal);
  modal.addEventListener('click', (e) => {
    if (e.target === modal) hideModal();
  });

});
