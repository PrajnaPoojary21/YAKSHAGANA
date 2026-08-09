// alert("SCRIPT LOADED");


// ─── NAVIGATION ────────────────────────────────────────────
function goToHow()    { window.location.href = "how.html"; }
function goToUpload() { window.location.href = "upload.html"; }
function goToHome()   { window.location.href = "index.html"; }

// ─── AUDIO FILE PREVIEW ────────────────────────────────────
const audioFile = document.getElementById("audioFile");
const player    = document.getElementById("audioPlayer");

if (audioFile) {
  audioFile.addEventListener("change", function () {
    const file = this.files[0];
    if (file) {
      player.src = URL.createObjectURL(file);
      player.style.display = "block";
    }
  });
}

// ─── RESET BUTTON ──────────────────────────────────────────
const resetBtn = document.querySelector(".reset");
if (resetBtn) {
  resetBtn.addEventListener("click", () => {
    if (audioFile) audioFile.value = "";
    if (player) {
      player.src = "";
      player.style.display = "none";
    }
    const statusEl = document.getElementById("upload-status");
    if (statusEl) statusEl.textContent = "";
  });
}

// ─── MAIN: SEND AUDIO TO BACKEND ───────────────────────────
async function recognizeAudio() {
  const fileInput = document.getElementById("audioFile");
  const statusEl  = document.getElementById("upload-status");
  const submitBtn = document.getElementById("submitBtn");

  // Validate file selected
  if (!fileInput || !fileInput.files[0]) {
    alert("ದಯವಿಟ್ಟು ಮೊದಲು ಆಡಿಯೋ ಫೈಲ್ ಆಯ್ಕೆ ಮಾಡಿ.");
    return;
  }

  const file = fileInput.files[0];

  // Show loading state
  if (statusEl) {
    statusEl.innerHTML = "⏳ ಆಡಿಯೋ ಪ್ರಕ್ರಿಯೆ ನಡೆಯುತ್ತಿದೆ... ಸ್ವಲ್ಪ ಕಾಯಿರಿ";
    statusEl.style.color = "#f97316";
  }
  if (submitBtn) {
    submitBtn.disabled = true;
    submitBtn.textContent = "⏳ Processing...";
  }


   try {
    const formData = new FormData();
    formData.append("audio", file);

    const response = await fetch("http://localhost:5000/transcribe", {
        method: "POST",
        body: formData
    });

    if (!response.ok) {
        throw new Error("HTTP Error: " + response.status);
    }

    const data = await response.json();

    console.log("Backend Response:", data);

    // sessionStorage.setItem("yaksha_padya", data.formatted_padya || data.cleaned_text || data.raw_text);
    // sessionStorage.setItem("yaksha_story", data.story || "");
    // sessionStorage.setItem("yaksha_raw", data.raw_text || "");
    
    sessionStorage.clear();

sessionStorage.setItem("yaksha_padya", data.formatted_padya || data.cleaned_text || data.raw_text);
sessionStorage.setItem("yaksha_story", data.story || "");
sessionStorage.setItem("yaksha_raw", data.raw_text || "");

console.log("Saved Padya:", sessionStorage.getItem("yaksha_padya"));
console.log("Saved Story:", sessionStorage.getItem("yaksha_story"));
    
    // console.log("Redirecting...");
    // window.location.href = "result.html";
    setTimeout(() => {
    window.location.href = "result.html";
}, 1000);

} catch (err) {
    console.error(err);

    if (statusEl) {
        statusEl.innerHTML = "❌ " + err.message;
        statusEl.style.color = "#ef4444";
    }

    if (submitBtn) {
        submitBtn.disabled = false;
        submitBtn.textContent = "✨ Recognize & Extract Story";
    }
}

  // try {
  //   // Build form data
  //   const formData = new FormData();
  //   formData.append("audio", file);


// const response = await fetch("http://localhost:5000/transcribe", {
//   method: "POST",
//   body: formData
// });

// alert("Fetch successful");

// const data = await response.json();

// alert("JSON parsed");

// sessionStorage.setItem("yaksha_padya", data.formatted_padya || "");
// sessionStorage.setItem("yaksha_story", data.story || "");

// alert("Session storage saved");

// window.location.href = "result.html";

// alert("Redirect failed");

    // // Call backend
    // const response = await fetch("http://localhost:5000/transcribe", {
    //   method: "POST",
    //   body: formData
    // });

    // const data = await response.json();



    // console.log("Backend Response:", data);

    // if (!response.ok || data.error) {
    //   throw new Error(data.error || "Backend error");
    // }

    // // Save results to sessionStorage
    // console.log("Saving to sessionStorage...");
    // console.log("Padya:", data.formatted_padya);
    // console.log("Story:", data.story);
    // sessionStorage.setItem("yaksha_padya", data.formatted_padya || data.cleaned_text || data.raw_text);
    // sessionStorage.setItem("yaksha_story", data.story || "");
    // sessionStorage.setItem("yaksha_raw",   data.raw_text || "");

    // // Go to result page
    // window.location.href = "result.html";

//   } catch (err) {
//     console.error(err);

//     alert(
//         "Error Name: " + err.name +
//         "\n\nMessage: " + err.message +
//         "\n\nStack:\n" + err.stack
//     );

//     if (statusEl) {
//         statusEl.innerHTML = "❌ " + err.message;
//         statusEl.style.color = "red";
//     }

//     if (submitBtn) {
//         submitBtn.disabled = false;
//         submitBtn.textContent = "✨ Recognize & Extract Story";
//     }
// }
}

// ─── RESULT PAGE: POPULATE CARDS ───────────────────────────
window.addEventListener("DOMContentLoaded", () => {

  console.log("Result page loaded");
  console.log("Padya:", sessionStorage.getItem("yaksha_padya"));
  console.log("Story:", sessionStorage.getItem("yaksha_story"));

  
  const padyaEl = document.querySelector(".card-content.yellow");
  const storyEl = document.querySelector(".card-content.red");

  if (padyaEl && storyEl) {
    const padya = sessionStorage.getItem("yaksha_padya");
    const story = sessionStorage.getItem("yaksha_story");

    if (padya) {
      padyaEl.innerHTML = padya
        .split('\n')
        .map(line => `<p style="margin:6px 0; font-size:16px;">${line}</p>`)
        .join('');
    } else {
      padyaEl.innerHTML = "<p>ಯಾವುದೇ ಪದ್ಯ ಸಿಗಲಿಲ್ಲ.</p>";
    }

    if (story) {
      storyEl.innerHTML = `<p style="font-size:15px; line-height:1.8;">${story}</p>`;
    } else {
      storyEl.innerHTML = "<p>ಡೇಟಾಸೆಟ್ ತಯಾರಾದ ನಂತರ ಕಥೆ ಇಲ್ಲಿ ತೋರಿಸಲಾಗುತ್ತದೆ.</p>";
    }
  }
});