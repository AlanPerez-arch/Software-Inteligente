document.getElementById('ideaForm').addEventListener('submit', async function(e) {
    e.preventDefault(); // Evita que la página se recargue por completo

    // Referencias a los elementos de la interfaz
    const ideaInput = document.getElementById('ideaInput');
    const btnGenerar = document.getElementById('btnGenerar');
    const loadingSection = document.getElementById('loading');
    const resultadosSection = document.getElementById('resultados');

    const idea = ideaInput.value.trim();
    if (!idea) return;

    // 1. Mostrar estado de carga y ocultar resultados previos
    btnGenerar.disabled = true;
    loadingSection.classList.remove('hidden');
    resultadosSection.classList.add('hidden');

    // Limpiar el HTML interno de las tarjetas por seguridad
    document.getElementById('resNegocio').innerHTML = '';
    document.getElementById('resMarketing').innerHTML = '';
    document.getElementById('resFinanzas').innerHTML = '';

    try {
        // 2. Hacer la petición POST al backend (usamos ruta relativa '/api/generar')
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

        // 3. Renderizar las respuestas transformando el Markdown de la IA a HTML real
        document.getElementById('resNegocio').innerHTML = marked.parse(data.negocio);
        document.getElementById('resMarketing').innerHTML = marked.parse(data.marketing);
        document.getElementById('resFinanzas').innerHTML = marked.parse(data.finanzas);

        // Mostrar la sección de resultados únicamente si la petición fue exitosa
        resultadosSection.classList.remove('hidden');

    } catch (error) {
        console.error('Error detectado en el flujo:', error);
        alert(`⚠️ ¡Vaya! Algo salió mal: ${error.message}`);
    } finally {
        // 4. Restaurar la interfaz: ocultar el spinner de carga y reactivar el botón
        loadingSection.classList.add('hidden');
        btnGenerar.disabled = false;
    }
});