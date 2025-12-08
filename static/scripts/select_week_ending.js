const snapBtn = document.getElementById('snap-to-sunday');
const customInput = document.getElementById('custom-date');
if (snapBtn && customInput) {
  snapBtn.addEventListener('click', function() {
    if (!customInput.value) {
      alert('Pick a date first.');
      return;
    }
    const d = new Date(customInput.value);
    // find next (or same) Sunday
    const day = d.getDay(); // 0 = Sunday
    const diff = (7 - day) % 7; // days to add to reach Sunday
    d.setDate(d.getDate() + diff);
    // set the date input value in yyyy-mm-dd
    const y = d.getFullYear();
    const m = String(d.getMonth() + 1).padStart(2, '0');
    const da = String(d.getDate()).padStart(2, '0');
    customInput.value = `${y}-${m}-${da}`;
    // optionally check radio if it matches one of the options
    const radios = document.querySelectorAll('input[name="week_ending"]');
    radios.forEach(r => {
      if (r.value === customInput.value) r.checked = true;
    });
  });
}