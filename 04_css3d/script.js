const planetData = {
    mercurio: { nombre: 'Mercurio', diametro: '4.879 km', distancia: '57.9 millones km', periodo: '88 días', dato: 'Es el planeta más cercano al Sol y el más pequeño. Su superficie está llena de cráteres.' },
    venus: { nombre: 'Venus', diametro: '12.104 km', distancia: '108.2 millones km', periodo: '225 días', dato: 'Es el planeta más caliente del sistema solar debido a su densa atmósfera de gases de efecto invernadero.' },
    tierra: { nombre: 'La Tierra', diametro: '12.742 km', distancia: '149.6 millones km', periodo: '365 días', dato: 'El único planeta conocido que alberga vida, con un 71% de su superficie cubierta por agua líquida.' },
    marte: { nombre: 'Marte', diametro: '6.779 km', distancia: '227.9 millones km', periodo: '687 días', dato: 'Alberga el volcán más grande del sistema solar, Olympus Mons, que tiene 21 km de altura.' },
    jupiter: { nombre: 'Júpiter', diametro: '139.820 km', distancia: '778.5 millones km', periodo: '12 años', dato: 'Es un gigante gaseoso tan masivo que contiene más del doble de material que todos los demás cuerpos juntos.' },
    saturno: { nombre: 'Saturno', diametro: '116.460 km', distancia: '1.434 millones km', periodo: '29 años', dato: 'Famoso por su espectacular sistema de anillos, que están compuestos principalmente de hielo y polvo.' },
    urano: { nombre: 'Urano', diametro: '50.724 km', distancia: '2.871 millones km', periodo: '84 años', dato: 'Tiene una inclinación axial extrema de 98°, por lo que parece rotar "de lado" en su órbita.' },
    neptuno: { nombre: 'Neptuno', diametro: '49.244 km', distancia: '4.495 millones km', periodo: '165 años', dato: 'Es el planeta más ventoso del sistema solar, con ráfagas que alcanzan los 2.100 km/h.' }
};

document.addEventListener('DOMContentLoaded', () => {
    generateStars(300);
    init3DControls();
    initPlanetClicks();
});

// Generar fondo de estrellas
function generateStars(count) {
    const universe = document.getElementById('universe');
    for (let i = 0; i < count; i++) {
        const star = document.createElement('div');
        star.classList.add('star');
        
        // Random position, size, opacity and animation timing
        const x = Math.random() * 100;
        const y = Math.random() * 100;
        const size = Math.random() * 2 + 1; // 1px to 3px
        const opacity = Math.random() * 0.5 + 0.3;
        const animDuration = Math.random() * 3 + 2; // 2s to 5s
        const animDelay = Math.random() * 5;
        
        star.style.left = `${x}vw`;
        star.style.top = `${y}vh`;
        star.style.width = `${size}px`;
        star.style.height = `${size}px`;
        star.style.opacity = opacity;
        star.style.animationDuration = `${animDuration}s`;
        star.style.animationDelay = `-${animDelay}s`;
        
        universe.appendChild(star);
    }
}

// Interacciones 3D: Rotación y Zoom
function init3DControls() {
    const universe = document.getElementById('universe');
    const solarSystem = document.getElementById('solar-system');
    
    let isDragging = false;
    let previousX = 0;
    let previousY = 0;
    
    // Valores iniciales (mismos que en el CSS)
    let rotateX = 65; 
    let rotateZ = 0;
    let scale = 1;

    const updateTransform = () => {
        solarSystem.style.transform = `scale(${scale}) rotateX(${rotateX}deg) rotateZ(${rotateZ}deg)`;
    };

    // Control de ratón para rotar
    universe.addEventListener('mousedown', (e) => {
        isDragging = true;
        previousX = e.clientX;
        previousY = e.clientY;
    });

    window.addEventListener('mouseup', () => {
        isDragging = false;
    });

    window.addEventListener('mousemove', (e) => {
        if (!isDragging) return;
        
        const deltaX = e.clientX - previousX;
        const deltaY = e.clientY - previousY;
        
        // Ajustamos la rotación
        rotateZ -= deltaX * 0.3; // Rotar alrededor del eje Z (girar el disco)
        rotateX += deltaY * 0.3; // Rotar alrededor del eje X (inclinar)
        
        // Limitar la inclinación para no dar la vuelta completa (0 a 90 grados es ideal)
        if (rotateX < 0) rotateX = 0;
        if (rotateX > 90) rotateX = 90;
        
        updateTransform();
        
        previousX = e.clientX;
        previousY = e.clientY;
    });

    // Control de scroll para zoom
    universe.addEventListener('wheel', (e) => {
        e.preventDefault(); // Prevenir el scroll de la página
        
        if (e.deltaY < 0) {
            scale += 0.05; // Zoom in
        } else {
            scale -= 0.05; // Zoom out
        }
        
        // Límites de escala
        if (scale < 0.3) scale = 0.3;
        if (scale > 2.5) scale = 2.5;
        
        updateTransform();
    }, { passive: false });
}

// Clics en los planetas para mostrar información
function initPlanetClicks() {
    const planets = document.querySelectorAll('.planet');
    const panel = document.getElementById('info-panel');
    const closeBtn = document.getElementById('close-panel');
    
    // Nodos del DOM para inyectar datos
    const title = document.getElementById('planet-name');
    const diameter = document.getElementById('planet-diameter');
    const distance = document.getElementById('planet-distance');
    const period = document.getElementById('planet-period');
    const fact = document.getElementById('planet-fact');

    planets.forEach(planet => {
        planet.addEventListener('click', (e) => {
            // Evitar que el clic se propague al universo y cause conflictos
            e.stopPropagation();
            
            const planetId = planet.getAttribute('data-planet');
            const data = planetData[planetId];
            
            if (data) {
                title.textContent = data.nombre;
                diameter.textContent = data.diametro;
                distance.textContent = data.distancia;
                period.textContent = data.periodo;
                fact.textContent = data.dato;
                
                panel.classList.add('active');
            }
        });
    });

    closeBtn.addEventListener('click', () => {
        panel.classList.remove('active');
    });

    // Cerrar el panel al hacer clic en cualquier lugar del espacio
    document.getElementById('universe').addEventListener('click', () => {
        panel.classList.remove('active');
    });
    
    // Opcional: Cerrar con la tecla Escape
    window.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            panel.classList.remove('active');
        }
    });
}
