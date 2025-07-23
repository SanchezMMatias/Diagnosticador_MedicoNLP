document.addEventListener("DOMContentLoaded", () => {
  const startBtn = document.getElementById("startAnalysis");
  const progressContainer = document.getElementById("progressContainer");
  const progressPercentage = document.getElementById("progressPercentage");
  const progressFill = document.getElementById("progressFill");
  const progressStatus = document.getElementById("progressStatus");
  const resultsContainer = document.getElementById("resultsContainer");
  const transcripcionTexto = document.getElementById("transcripcionTexto");
  const saveResultsBtn = document.getElementById("saveResults");
  const actionButtons = document.getElementById("actionButtons");
  const audioId = document.getElementById("audioId").value;

  let transcripcionTextoValue = "";

  // Función para iniciar el análisis (llamada AJAX)
  async function iniciarAnalisis() {
    startBtn.disabled = true;
    progressContainer.style.display = "block";
    progressPercentage.textContent = "0%";
    progressFill.style.width = "0%";
    progressStatus.textContent = "Iniciando análisis...";
    resultsContainer.style.display = "none";
    actionButtons.style.display = "none";
    transcripcionTexto.textContent = "Procesando transcripción...";

    try {
      // Llamada AJAX para procesar audio y obtener transcripción
      const response = await fetch("/diagnosticos_app/procesar_audio_ajax/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": getCookie("csrftoken"),
        },
        body: JSON.stringify({ audio_id: audioId }),
      });

      if (!response.ok) throw new Error("Error en la llamada al servidor");

      // Suponemos que el servidor devuelve { transcripcion: "texto" }
      const data = await response.json();

      transcripcionTextoValue = data.transcripcion || "No se generó transcripción.";

      // Mostrar resultado
      transcripcionTexto.textContent = transcripcionTextoValue;

      progressPercentage.textContent = "100%";
      progressFill.style.width = "100%";
      progressStatus.textContent = "Análisis completado";

      resultsContainer.style.display = "block";
      actionButtons.style.display = "flex";
    } catch (error) {
      transcripcionTexto.textContent = "Error durante el análisis: " + error.message;
      progressStatus.textContent = "Error";
    } finally {
      startBtn.disabled = false;
      progressContainer.style.display = "none";
    }
  }

  // Función para guardar la transcripción (llamada AJAX)
  async function guardarResultados() {
    saveResultsBtn.disabled = true;
    saveResultsBtn.textContent = "Guardando...";

    try {
      const response = await fetch("/diagnosticos_app/guardar_resultados_ajax/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": getCookie("csrftoken"),
        },
        body: JSON.stringify({
          audio_id: audioId,
          transcripcion: transcripcionTextoValue,
        }),
      });

      if (!response.ok) throw new Error("Error guardando resultados");

      const data = await response.json();

      alert("Transcripción guardada correctamente");
    } catch (error) {
      alert("Error al guardar: " + error.message);
    } finally {
      saveResultsBtn.disabled = false;
      saveResultsBtn.textContent = "💾 Guardar Resultados";
    }
  }

  // Función para copiar texto transcripción
  document.getElementById("copyTranscription").addEventListener("click", () => {
    if (!transcripcionTextoValue) return alert("No hay texto para copiar");
    navigator.clipboard.writeText(transcripcionTextoValue);
    alert("Texto copiado al portapapeles");
  });

  // Función para descargar transcripción como TXT
  document.getElementById("downloadTranscription").addEventListener("click", () => {
    if (!transcripcionTextoValue) return alert("No hay texto para descargar");
    const blob = new Blob([transcripcionTextoValue], { type: "text/plain" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `transcripcion_audio_${audioId}.txt`;
    a.click();
    URL.revokeObjectURL(url);
  });

  // Evento botón iniciar análisis
  startBtn.addEventListener("click", iniciarAnalisis);

  // Evento botón guardar resultados
  saveResultsBtn.addEventListener("click", guardarResultados);

  // Función para obtener cookie CSRF (reutilizable)
  function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
      const cookies = document.cookie.split(";");
      for (let cookie of cookies) {
        cookie = cookie.trim();
        if (cookie.startsWith(name + "=")) {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }
});
