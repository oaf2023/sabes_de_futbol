document.addEventListener('DOMContentLoaded', () => {
    
    // COMPONENTE 1: BOLETA DIGITAL - Generar las 13 filas
    const filasBoletaContainer = document.getElementById('filas-boleta');
    const partidos = [
        "BOCA - RIVER",
        "RACING - INDEPTE",
        "SAN LORENZO - HURACAN",
        "ESTUDIANTES - GIMNASIA",
        "ROSARIO CTRAL - NEWELLS",
        "VELEZ - FERRO",
        "ARGENTINOS - PLATENSE",
        "LANUS - BANFIELD",
        "COLON - UNION",
        "TALLERES - BELGRANO",
        "CHACARITA - ATLANTA",
        "NUEVA CHICAGO - ALL BOYS",
        "DEF. BELGRANO - EXCURSION"
    ];

    partidos.forEach((partido, index) => {
        const row = document.createElement('div');
        row.className = 'row';
        
        row.innerHTML = `
            <span class="partido">${index + 1}. ${partido}</span>
            <span class="opcion"><input type="radio" name="partido_${index}" value="L" class="input-radio"></span>
            <span class="opcion"><input type="radio" name="partido_${index}" value="E" class="input-radio"></span>
            <span class="opcion"><input type="radio" name="partido_${index}" value="V" class="input-radio"></span>
        `;
        
        filasBoletaContainer.appendChild(row);
    });

    // COMPONENTE 2: PANEL DE SORTEO - Lógica de Sorteo
    const btnJugar = document.querySelector('.btn-jugar');
    const ruletaSlot = document.getElementById('slot-1');
    const audioClick = document.getElementById('audio-click');
    const audioGol = document.getElementById('audio-gol');
    const audioFanfarria = document.getElementById('audio-fanfarria');
    const audioDerrota = document.getElementById('audio-derrota');
    
    // Fake audio sources for testing purposes
    audioClick.src = "https://www.soundjay.com/button/button-16.mp3";
    audioGol.src = "https://www.soundjay.com/human/crowd-cheering-1.mp3"; 
    // "Fanfarria"
    audioFanfarria.src = "https://www.soundjay.com/misc/success-trumpet-01.mp3";
    audioDerrota.src = "https://www.soundjay.com/misc/fail-buzzer-01.mp3";

    // Random choice L, E, V
    const resultadosPosibles = ['L', 'E', 'V'];

    btnJugar.addEventListener('click', () => {
        // Play click sound
        audioClick.play().catch(e => console.log('Audio play error:', e));
        
        // Disable button during draw
        btnJugar.disabled = true;
        btnJugar.innerText = "SORTEANDO...";

        let counter = 0;
        const spinInterval = setInterval(() => {
            // Animación ruleta
            ruletaSlot.innerText = resultadosPosibles[Math.floor(Math.random() * resultadosPosibles.length)];
            ruletaSlot.style.color = '#fff'; // Flashing effect
            setTimeout(() => { ruletaSlot.style.color = 'var(--color-acento)'; }, 50);
            
            counter++;
            if (counter > 20) {
                clearInterval(spinInterval);
                finalizarSorteo();
            }
        }, 100);
    });

    function finalizarSorteo() {
        // Resultado final estático para demo
        ruletaSlot.innerText = 'L';
        btnJugar.innerText = "VOLVER A JUGAR";
        btnJugar.disabled = false;
        
        // Randomly Decide Win or Lose for the demo effect
        const isWin = Math.random() > 0.5;
        
        if (isWin) {
            audioGol.play().catch(e => console.log('Audio play error:', e));
            triggerSuccessAnimation();
        } else {
            audioDerrota.play().catch(e => console.log('Audio play error:', e));
            triggerFailAnimation();
        }
    }

    function triggerSuccessAnimation() {
        console.log("VICTORIA - GOL!");
        // Add confeti
        for(let i=0; i<50; i++) {
            const confeti = document.createElement('div');
            confeti.classList.add('confeti');
            if(Math.random() > 0.5) confeti.classList.add('blanco');
            else confeti.classList.add('celeste');
            
            confeti.style.left = Math.random() * 100 + 'vw';
            confeti.style.animationDuration = (Math.random() * 3 + 2) + 's';
            confeti.style.opacity = Math.random();
            document.body.appendChild(confeti);
            
            setTimeout(() => { confeti.remove(); }, 5000);
        }
        
        // Highlight prize
        const premioMayor = document.querySelector('.premio-mayor');
        premioMayor.classList.add('glow');
        audioFanfarria.play().catch(e => console.log('Audio play error:', e));
    }

    function triggerFailAnimation() {
        console.log("DERROTA :(");
        const boleta = document.querySelector('.boleta-digital');
        boleta.classList.add('derrota-anim');
        setTimeout(() => { boleta.classList.remove('derrota-anim'); }, 2000);
    }
});
