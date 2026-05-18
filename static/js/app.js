// =========================================================================
// 1. CONTROL DEL FORMULARIO Y PETICIÓN A LA API (FLASK + GROQ)
// =========================================================================

document.getElementById('ideaForm').addEventListener('submit', async function(e) {
    e.preventDefault(); // Evita que la página se recargue por completo

    // Referencias a los elementos de la interfaz para los resultados
    const ideaInput = document.getElementById('ideaInput');
    const btnGenerar = document.getElementById('btnGenerar');
    const loadingSection = document.getElementById('loading');
    const resultadosSection = document.getElementById('resultados');

    const idea = ideaInput.value.trim();
    if (!idea) return;

    // Mostrar estado de carga y ocultar resultados previos
    btnGenerar.disabled = true;
    loadingSection.classList.remove('hidden');
    resultadosSection.classList.add('hidden');

    // Limpiar el HTML interno de las tarjetas por seguridad e higiene visual
    document.getElementById('resNegocio').innerHTML = '';
    document.getElementById('resMarketing').innerHTML = '';
    document.getElementById('resFinanzas').innerHTML = '';

    try {
        // Hacer la petición POST al backend (usamos ruta relativa '/api/generar')
        const response = await fetch('/api/generar', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ idea: idea })
        });

        const data = await response.json();

        // Si el backend responde con un error (ej: status 400 o 500)
        if (!response.ok) {
            throw new Error(data.error || 'Ocurrió un error en el servidor al generar el kit.');
        }

        // Renderizar las respuestas transformando el Markdown de la IA a HTML real
        document.getElementById('resNegocio').innerHTML = marked.parse(data.negocio);
        document.getElementById('resMarketing').innerHTML = marked.parse(data.marketing);
        document.getElementById('resFinanzas').innerHTML = marked.parse(data.finanzas);

        // Mostrar la sección de resultados únicamente si la petición fue exitosa
        resultadosSection.classList.remove('hidden');

    } catch (error) {
        console.error('Error detectado en el flujo:', error);
        alert(`⚠️ ¡Vaya! Algo salió mal: ${error.message}`);
    } finally {
        // Restaurar la interfaz: ocultar el spinner de carga y reactivar el botón
        loadingSection.classList.add('hidden');
        btnGenerar.disabled = false;
    }
});


// =========================================================================
// 2. LOGICA PARA EL DICTADO POR VOZ (WEB SPEECH API)
// =========================================================================

const btnVoz = document.getElementById('btnVoz');
const ideaInput = document.getElementById('ideaInput');
const iconoMicro = document.getElementById('iconoMicro');
const textoMicro = document.getElementById('textoMicro');

// Verificar compatibilidad del navegador (funciona nativamente en Chrome, Edge y Safari)
const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

if (SpeechRecognition) {
    const recognition = new SpeechRecognition();
    recognition.lang = 'es-MX'; // Configurado para español de México
    recognition.interimResults = false; // Solo procesa el resultado final cuando el usuario hace una pausa
    recognition.maxAlternatives = 1;

    // Evento de clic en el botón de micrófono
    btnVoz.addEventListener('click', () => {
        // Si ya está activo (icono rojo), lo detenemos manualmente
        if (iconoMicro.classList.contains('text-red-500')) {
            recognition.stop();
        } else {
            // Si está inactivo, comenzamos a escuchar
            recognition.start();
        }
    });

    // Evento: Cuando el navegador abre el micrófono e inicia la escucha
    recognition.onstart = () => {
        iconoMicro.classList.remove('text-indigo-600');
        iconoMicro.classList.add('text-red-500', 'animate-pulse'); // Efecto visual de grabación
        textoMicro.innerText = "Escuchando... Habla ahora";
    };

    // Evento: Cuando el reconocimiento se detiene (ya sea por silencio largo o por stop manual)
    recognition.onend = () => {
        iconoMicro.classList.remove('text-red-500', 'animate-pulse');
        iconoMicro.classList.add('text-indigo-600');
        textoMicro.innerText = "Dictar idea";
    };

    // Evento: Cuando procesa el audio y genera el texto con éxito
    recognition.onresult = (event) => {
        const textoEscuchado = event.results[0][0].transcript;
        
        // Si el usuario ya tenía algo escrito, añade un espacio y concatena el dictado
        if (ideaInput.value.trim()) {
            ideaInput.value = ideaInput.value.trim() + " " + textoEscuchado;
        } else {
            ideaInput.value = textoEscuchado;
        }
        
        // Ajustar el foco al input para comodidad del usuario
        ideaInput.focus();
    };

    // Evento: Manejo de errores del micrófono (bloqueo de permisos, falta de audio, etc.)
    recognition.onerror = (event) => {
        console.error("Error en reconocimiento de voz: ", event.error);
        if (event.error === 'not-allowed') {
            alert("⚠️ Permiso denegado. Por favor, permite el acceso al micrófono en tu navegador.");
        } else if (event.error !== 'no-speech') {
            alert("No se pudo procesar el dictado por voz de forma correcta.");
        }
    };

} else {
    // Si el navegador es antiguo o no soporta la API, ocultamos el botón silenciosamente
    if (btnVoz) {
        btnVoz.style.display = 'none';
    }
    console.warn("El navegador actual no soporta Web Speech API para dictado por voz.");
}