/* ================================================= */
/* ============ ACCESSIBILITY VOICE MODE =========== */
/* ================================================= */

const voiceToggle = document.getElementById("voice-toggle");

let voiceMode = false;

/* ===== LOAD STATE ===== */

if(localStorage.getItem("voiceMode") === "enabled"){

    voiceMode = true;

    voiceToggle.checked = true;

}

/* ===== TOGGLE ===== */

voiceToggle.addEventListener("change", () => {

    voiceMode = voiceToggle.checked;

    if(voiceMode){

        localStorage.setItem(
            "voiceMode",
            "enabled"
        );

        speakText(
            "Modo accesibilidad activado"
        );

    }

    else{

        localStorage.setItem(
            "voiceMode",
            "disabled"
        );

        speechSynthesis.cancel();

    }

});

/* ================================================= */
/* ================= SPEAK FUNCTION ================ */
/* ================================================= */

function speakText(text){

    if(!voiceMode) return;

    speechSynthesis.cancel();

    const speech = new SpeechSynthesisUtterance(text);

    speech.lang = "es-MX";

    speech.rate = 1;

    speech.pitch = 1;

    speech.volume = 1;

    speechSynthesis.speak(speech);

}

/* ================================================= */
/* ================ HOVER READER =================== */
/* ================================================= */

const readableElements = document.querySelectorAll(

    "button, a, h1, h2, h3, h4, h5, p, textarea"

);

/* ===== EVENTS ===== */

readableElements.forEach((element) => {

    element.addEventListener("mouseenter", () => {

        const text = element.innerText ||
                     element.placeholder ||
                     element.value;

        if(text){

            speakText(text.trim());

        }

    });

});