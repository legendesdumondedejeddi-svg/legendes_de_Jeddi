document.querySelectorAll('.lang-switch .submenu a').forEach(link => {
    link.addEventListener('click', e => {
        e.preventDefault();
        const lang = link.getAttribute('href').split('=')[1];
        alert('Sélection de la langue : ' + lang + '\n(Le chargement des traductions peut être implémenté ici)');
    });
});
