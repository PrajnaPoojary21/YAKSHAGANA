// ─── NAVIGATION ────────────────────────────────────────────
// "how" and "home" live INSIDE index.html, so those scroll.
// "upload" and "result" are separate pages, so those still navigate.

function goToHow() {
  const el = document.getElementById("how");
  if (el) {
    el.scrollIntoView({ behavior: "smooth" });
  } else {
    window.location.href = "index.html#how";
  }
}

function goToHome() {
  const el = document.getElementById("home");
  if (el) {
    el.scrollIntoView({ behavior: "smooth" });
  } else {
    window.location.href = "index.html";
  }
}

function goToUpload() { window.location.href = "upload.html"; }
function goToResult() { window.location.href = "result.html"; }

// ─── AUDIO FILE PREVIEW ────────────────────────────────────
const audioFile = document.getElementById("audioFile");
const player    = document.getElementById("audioPlayer");

// ADDED: holds whichever audio the user provided via microphone recording,
// so recognizeAudio() can send it instead of (or alongside) a file upload.
let recordedBlob = null;

if (audioFile) {
  audioFile.addEventListener("change", function () {
    const file = this.files[0];
    if (file) {
      // ADDED: uploading a file cancels out any previous recording,
      // so there's never ambiguity about which audio will be sent.
      recordedBlob = null;
      updateRecordStatus("");

      player.src = URL.createObjectURL(file);
      player.style.display = "block";
    }
  });
}

// ─── ADDED: AUDIO RECORDING (MediaRecorder API) ─────────────
// Same underlying browser API used by most in-browser recording tools.
// Lets the user record live through their microphone as an alternative
// to uploading a file.

const recordBtn = document.getElementById("recordBtn");
const recordStatusEl = document.getElementById("record-status");

let mediaRecorder = null;
let recordedChunks = [];
let recordTimerInterval = null;
let recordSeconds = 0;
let mediaStream = null;

function updateRecordStatus(text, color) {
  if (!recordStatusEl) return;
  recordStatusEl.textContent = text;
  recordStatusEl.style.color = color || "#6b7280";
}

function formatSeconds(totalSeconds) {
  const m = Math.floor(totalSeconds / 60).toString().padStart(2, "0");
  const s = (totalSeconds % 60).toString().padStart(2, "0");
  return `${m}:${s}`;
}

async function toggleRecording() {
  if (!recordBtn) return;

  // Currently recording -> stop it
  if (mediaRecorder && mediaRecorder.state === "recording") {
    mediaRecorder.stop();
    return;
  }

  // Not recording -> start
  if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
    alert("ಈ ಬ್ರೌಸರ್ ಮೈಕ್ರೋಫೋನ್ ರೆಕಾರ್ಡಿಂಗ್ ಬೆಂಬಲಿಸುವುದಿಲ್ಲ.");
    return;
  }

  try {
    mediaStream = await navigator.mediaDevices.getUserMedia({ audio: true });
  } catch (err) {
    updateRecordStatus("❌ ಮೈಕ್ರೋಫೋನ್ ಅನುಮತಿ ನಿರಾಕರಿಸಲಾಗಿದೆ.", "#ef4444");
    return;
  }

  recordedChunks = [];
  mediaRecorder = new MediaRecorder(mediaStream);

  mediaRecorder.addEventListener("dataavailable", (e) => {
    if (e.data.size > 0) recordedChunks.push(e.data);
  });

  mediaRecorder.addEventListener("stop", () => {
    // Stop the mic stream fully (turns off the browser's "recording" indicator)
    if (mediaStream) {
      mediaStream.getTracks().forEach((track) => track.stop());
      mediaStream = null;
    }

    clearInterval(recordTimerInterval);
    recordTimerInterval = null;

    const blob = new Blob(recordedChunks, { type: "audio/webm" });
    recordedBlob = blob;

    // ADDED: recording cancels out any previously selected file upload.
    if (audioFile) audioFile.value = "";

    if (player) {
      player.src = URL.createObjectURL(blob);
      player.style.display = "block";
    }

    updateRecordStatus(`✅ ರೆಕಾರ್ಡ್ ಮಾಡಲಾಗಿದೆ (${formatSeconds(recordSeconds)})`, "#16a34a");

    recordBtn.textContent = "🎙️ Record Again";
    recordBtn.classList.remove("recording-active");
  });

  mediaRecorder.start();
  recordSeconds = 0;
  updateRecordStatus("● Recording... " + formatSeconds(0), "#ef4444");
  recordBtn.textContent = "⏹ Stop Recording";
  recordBtn.classList.add("recording-active");

  recordTimerInterval = setInterval(() => {
    recordSeconds += 1;
    updateRecordStatus("● Recording... " + formatSeconds(recordSeconds), "#ef4444");
  }, 1000);
}

if (recordBtn) {
  recordBtn.addEventListener("click", toggleRecording);
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

    // ADDED: also clear any in-progress/completed recording
    recordedBlob = null;
    if (mediaRecorder && mediaRecorder.state === "recording") {
      mediaRecorder.stop();
    }
    updateRecordStatus("");
    if (recordBtn) {
      recordBtn.textContent = "🎙️ Start Recording";
      recordBtn.classList.remove("recording-active");
    }
  });
}

// ─── MAIN: SEND AUDIO TO BACKEND (runs on upload.html) ─────
async function recognizeAudio() {
  const statusEl  = document.getElementById("upload-status");
  const submitBtn = document.getElementById("submitBtn");

  // CHANGED: accept EITHER an uploaded file OR a microphone recording.
  const hasFile = audioFile && audioFile.files[0];
  const hasRecording = recordedBlob !== null;

  if (!hasFile && !hasRecording) {
    alert("ದಯವಿಟ್ಟು ಮೊದಲು ಆಡಿಯೋ ಫೈಲ್ ಆಯ್ಕೆ ಮಾಡಿ ಅಥವಾ ರೆಕಾರ್ಡ್ ಮಾಡಿ.");
    return;
  }

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

    // CHANGED: prefer the recording if present, otherwise use the uploaded file.
    // Both paths hit the exact same backend endpoint -- no server changes needed.
    if (hasRecording) {
      formData.append("audio", recordedBlob, "recording.webm");
    } else {
      formData.append("audio", audioFile.files[0]);
    }

    const response = await fetch("http://localhost:5000/transcribe", {
      method: "POST",
      body: formData
    });

    const data = await response.json();

    if (!response.ok || data.error) {
      throw new Error(data.error || "Backend error");
    }

    // Save results so result.html can read them after navigation
    sessionStorage.setItem("yaksha_padya", data.formatted_padya || data.cleaned_text || data.raw_text);
    sessionStorage.setItem("yaksha_story", data.story || "");
    sessionStorage.setItem("yaksha_raw",   data.raw_text || "");

    // Go to the result page
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

// ─── RESULT PAGE: POPULATE CARDS (runs on result.html) ─────
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