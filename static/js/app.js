document.getElementById('ideaForm').addEventListener('submit', async function(e) {
    e.preventDefault(); // 💥 DETIENE EL REFRESCO: Mantiene el formulario intacto y permite la navegación SPA

    const btnGenerar = document.querySelector('.generate-button');
    const loadingSection = document.getElementById('loading');
    const resultadosSection = document.getElementById('resultados');

    // 1. Gestionar estados visuales de carga antes de la llamada
    if (loadingSection) loadingSection.classList.remove('hidden');
    if (resultadosSection) resultadosSection.classList.add('hidden');
    btnGenerar.disabled = true;

    // Limpiar respuestas de ejecuciones anteriores
    document.getElementById('resNegocio').innerHTML = '';
    document.getElementById('resMarketing').innerHTML = '';
    document.getElementById('resFinanzas').innerHTML = '';

    // 2. Empaquetar de forma automática todos los campos del formulario (inputs, selects, checkboxes)
    const formData = new FormData(this);

    try {
        // Enviar los datos asíncronamente a Flask usando la ruta relativa del navegador
        const response = await fetch('/formulario', {
            method: 'POST',
            body: formData // Envía el paquete de datos estructurado en formato multipart/form-data
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || 'Ocurrió un contratiempo al procesar la información en Bloom AI.');
        }

        // 3. Renderizar las respuestas de los tres prompts usando Marked para procesar los formatos markdown
        document.getElementById('resNegocio').innerHTML = marked.parse(data.negocio);
        document.getElementById('resMarketing').innerHTML = marked.parse(data.marketing);
        document.getElementById('resFinanzas').innerHTML = marked.parse(data.finanzas);

        // Hacer visible la sección inferior con las tres columnas de resultados
        if (resultadosSection) resultadosSection.classList.remove('hidden');

    } catch (error) {
        console.error('Error detectado en el cliente:', error);
        alert(`⚠️ Bloom AI no pudo procesar tu proyecto: ${error.message}`);
    } finally {
        // 4. Concluir estados de carga: Ocultar spinner y habilitar nuevamente el botón
        if (loadingSection) loadingSection.classList.add('hidden');
        btnGenerar.disabled = false;
    }
});