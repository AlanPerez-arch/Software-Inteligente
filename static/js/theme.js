const toggle = document.getElementById("theme-toggle");

/* ===== LOAD THEME ===== */

if(localStorage.getItem("theme") === "light"){

    document.body.classList.add("light-mode");

    toggle.checked = true;

}

/* ===== SWITCH ===== */

toggle.addEventListener("change", () => {

    if(toggle.checked){

        document.body.classList.add("light-mode");

        localStorage.setItem("theme","light");

    }

    else{

        document.body.classList.remove("light-mode");

        localStorage.setItem("theme","dark");

    }

});