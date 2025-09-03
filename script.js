// Простейшие интерактивности// Простейшие интерактивности
document.querySelectorAll('.faq-item h3').forEach(title => {
    title.addEventListener('click', () => {
        const p = title.nextElementSibling;
        if (p.style.display === 'block') p.style.display = 'none';
        else p.style.display = 'block';
    });
});
