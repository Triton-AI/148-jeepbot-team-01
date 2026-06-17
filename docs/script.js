const search = document.querySelector('#search');
const links = [...document.querySelectorAll('.sidebar a')];
search?.addEventListener('input', e => {
  const q = e.target.value.toLowerCase();
  links.forEach(a => {
    a.style.display = a.textContent.toLowerCase().includes(q) ? 'block' : 'none';
  });
});
