// Adiciona funcionalidades sem modificar o HTML existente
document.addEventListener('DOMContentLoaded', function() {
    // 1. Suaviza rolagem para links internos (se houver âncoras)
    const links = document.querySelectorAll('a[href^="#"]');
    links.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                window.scrollTo({
                    top: target.offsetTop - 20,
                    behavior: 'smooth'
                });
            }
        });
    });

    // 2. Adiciona tooltips a imagens (gráficos)
    const images = document.querySelectorAll('img');
    images.forEach(img => {
        img.title = "Clique para ampliar";
        img.style.cursor = 'pointer';
        img.addEventListener('click', function() {
            window.open(this.src, '_blank');
        });
    });

    // 3. Destaca tabelas (se existirem)
    const tables = document.querySelectorAll('table');
    tables.forEach(table => {
        table.style.boxShadow = '0 2px 10px rgba(0, 0, 0, 0.1)';
    });

    // 4. Atualiza dinamicamente a data no footer (se houver)
    const footer = document.querySelector('footer');
    if (footer) {
        const dateSpan = document.createElement('span');
        dateSpan.textContent = new Date().getFullYear();
        footer.appendChild(document.createTextNode(' | Atualizado em '));
        footer.appendChild(dateSpan);
    }
});