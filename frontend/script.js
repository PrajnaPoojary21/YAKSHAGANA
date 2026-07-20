// // // 🔗 NAVIGATION
// // function goToHow() {
// //   window.location.href = "how.html";
// // }

// // function goToUpload() {
// //   window.location.href = "upload.html";
// // }

// // function goToResult() {
// //   window.location.href = "result.html";
// // }

// // function goToHome() {
// //   window.location.href = "index.html";
// // }


// // // 🎧 AUDIO PREVIEW
// // const audioFile = document.getElementById("audioFile");
// // const player = document.getElementById("audioPlayer");

// // if (audioFile) {
// //   audioFile.addEventListener("change", function () {
// //     const file = this.files[0];
// //     if (file) {
// //       player.src = URL.createObjectURL(file);
// //       player.style.display = "block";
// //     }
// //   });
// // }


// // // 🔄 RESET
// // const resetBtn = document.querySelector(".reset");

// // if (resetBtn) {
// //   resetBtn.addEventListener("click", () => {
// //     if (audioFile) audioFile.value = "";
// //     if (player) {
// //       player.src = "";
// //       player.style.display = "none";
// //     }
// //   });
// // }


// // // 🎤 RECORDING
// // let recorder;
// // let chunks = [];

// // const recordBtn = document.querySelector(".record-btn");

// // if (recordBtn) {
// //   recordBtn.addEventListener("click", async () => {

// //     if (!recorder || recorder.state === "inactive") {
// //       const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
// //       recorder = new MediaRecorder(stream);

// //       recorder.start();
// //       recordBtn.innerText = "Stop Recording";

// //       chunks = [];

// //       recorder.ondataavailable = e => chunks.push(e.data);

// //     } else {
// //       recorder.stop();
// //       recordBtn.innerText = "Start Recording";

// //       recorder.onstop = () => {
// //         const blob = new Blob(chunks);
// //         const url = URL.createObjectURL(blob);

// //         player.src = url;
// //         player.style.display = "block";
// //       };
// //     }

// //   });
// // }

// // ─── NAVIGATION ────────────────────────────────────────────
// function goToHow()    { window.location.href = "how.html"; }
// function goToUpload() { window.location.href = "upload.html"; }
// function goToResult() { window.location.href = "result.html"; }
// function goToHome()   { window.location.href = "index.html"; }

// // ─── AUDIO FILE PREVIEW ────────────────────────────────────
// const audioFile = document.getElementById("audioFile");
// const player    = document.getElementById("audioPlayer");

// if (audioFile) {
//   audioFile.addEventListener("change", function () {
//     const file = this.files[0];
//     if (file) {
//       player.src = URL.createObjectURL(file);
//       player.style.display = "block";
//     }
//   });
// }

// // ─── RESET BUTTON ──────────────────────────────────────────
// const resetBtn = document.querySelector(".reset");
// if (resetBtn) {
//   resetBtn.addEventListener("click", () => {
//     if (audioFile) audioFile.value = "";
//     if (player)    { player.src = ""; player.style.display = "none"; }
//     const statusEl = document.getElementById("upload-status");
//     if (statusEl) statusEl.textContent = "";
//   });
// }

// // ─── MAIN: SEND AUDIO TO BACKEND ──────────────────────────
// async function recognizeAudio() {
//   const fileInput  = document.getElementById("audioFile");
//   const statusEl   = document.getElementById("upload-status");
//   const submitBtn  = document.querySelector(".primary-btn[onclick]");

//   if (!fileInput || !fileInput.files[0]) {
//     alert("ದಯವಿಟ್ಟು ಮೊದಲು ಆಡಿಯೋ ಫೈಲ್ ಆಯ್ಕೆ ಮಾಡಿ.");  // "Please select an audio file first"
//     return;
//   }

//   const file = fileInput.files[0];

//   // Show loading state
//   if (statusEl) {
//     statusEl.textContent = "⏳ ಆಡಿಯೋ ಪ್ರಕ್ರಿಯೆ ನಡೆಯುತ್ತಿದೆ... ಸ್ವಲ್ಪ ಕಾಯಿರಿ";
//     statusEl.style.color = "#f97316";
//   }
//   if (submitBtn) submitBtn.disabled = true;

//   try {
//     const formData = new FormData();
//     formData.append("audio", file);

//     const response = await fetch("http://localhost:5000/transcribe", {
//       method: "POST",
//       body: formData
//     });

//     const data = await response.json();

//     if (!response.ok || data.error) {
//       throw new Error(data.error || "Backend error");
//     }

//     // Save results to sessionStorage so result.html can read them
//     sessionStorage.setItem("yaksha_padya",   data.formatted_padya || data.cleaned_text);
//     sessionStorage.setItem("yaksha_story",   data.story || "");
//     sessionStorage.setItem("yaksha_raw",     data.raw_text || "");

//     // Navigate to result page
//     window.location.href = "result.html";

//   } catch (err) {
//     if (statusEl) {
//       statusEl.textContent = "❌ ದೋಷ: " + err.message;
//       statusEl.style.color = "#ef4444";
//     }
//     if (submitBtn) submitBtn.disabled = false;
//     console.error("Transcription error:", err);
//   }
// }

// // ─── RESULT PAGE: POPULATE CARDS ──────────────────────────
// window.addEventListener("DOMContentLoaded", () => {
//   const padyaEl = document.querySelector(".card-content.yellow");
//   const storyEl = document.querySelector(".card-content.red");

//   if (padyaEl && storyEl) {
//     const padya = sessionStorage.getItem("yaksha_padya");
//     const story = sessionStorage.getItem("yaksha_story");

//     if (padya) {
//       // Display padya with line breaks preserved
//       padyaEl.innerHTML = padya
//         .split('\n')
//         .map(line => `<p style="margin:4px 0">${line}</p>`)
//         .join('');
//     } else {
//       padyaEl.textContent = "ಯಾವುದೇ ಪದ್ಯ ಸಿಗಲಿಲ್ಲ.";  // "No padya found"
//     }

//     if (story) {
//       storyEl.textContent = story;
//     } else {
//       storyEl.textContent = "ಡೇಟಾಸೆಟ್ ತಯಾರಾದ ನಂತರ ಕಥೆ ಇಲ್ಲಿ ತೋರಿಸಲಾಗುತ್ತದೆ.";
//     }
//   }
// });




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
    // Build form data
    const formData = new FormData();
    formData.append("audio", file);

    // Call backend
    const response = await fetch("http://localhost:5000/transcribe", {
      method: "POST",
      body: formData
    });

    const data = await response.json();

    if (!response.ok || data.error) {
      throw new Error(data.error || "Backend error");
    }

    // Save results to sessionStorage
    sessionStorage.setItem("yaksha_padya", data.formatted_padya || data.cleaned_text || data.raw_text);
    sessionStorage.setItem("yaksha_story", data.story || "");
    sessionStorage.setItem("yaksha_raw",   data.raw_text || "");

    // Go to result page
    window.location.href = "result.html";

  } catch (err) {
    if (statusEl) {
      statusEl.innerHTML = "❌ ದೋಷ: " + err.message;
      statusEl.style.color = "#ef4444";
    }
    if (submitBtn) {
      submitBtn.disabled = false;
      submitBtn.textContent = "✨ Recognize & Extract Story";
    }
    console.error("Error:", err);
  }
}

// ─── RESULT PAGE: POPULATE CARDS ───────────────────────────
window.addEventListener("DOMContentLoaded", () => {
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