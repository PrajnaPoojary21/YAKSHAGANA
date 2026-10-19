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
    sessionStorage.setItem("yaksha_padya", data.formatted_padya || data.cleaned_text || data.raw_text || "");
    sessionStorage.setItem("yaksha_story", data.story || "");
    sessionStorage.setItem("yaksha_raw",   data.raw_text || "");

    // ADDED: needed so result.html can tell a confident match apart from a
    // rejected one -- data.story already holds the right message either
    // way, but the status/confidence let the UI style them differently
    // and show a confidence number only when there's an actual match.
    sessionStorage.setItem("yaksha_match_status", data.match_status || "");
    sessionStorage.setItem(
      "yaksha_confidence",
      (data.match_confidence === null || data.match_confidence === undefined)
        ? ""
        : String(data.match_confidence)
    );

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

// ─── RESULT PAGE: POPULATE CARDS + LANGUAGE TOGGLE ──────────

const TRANSLATE_API_URL = "http://localhost:5000/api/translate";

let originalKannadaStory = "";
let englishStory = "";
let currentLanguage = "kn";


// Escape HTML so story text is displayed safely
function escapeHtml(text) {
  return String(text)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}


// Display story text
function displayStory(text) {

  const storyEl = document.getElementById("story-text");

  if (!storyEl) return;

  storyEl.innerHTML =
    `<p style="font-size:15px; line-height:1.8; margin:0;">
      ${escapeHtml(text)}
    </p>`;
}


// Translate Kannada story to English
async function translateStory() {

  const statusEl = document.getElementById("translate-status");
  const englishBtn = document.getElementById("btn-en");

  if (!originalKannadaStory.trim()) {
    if (statusEl) {
      statusEl.textContent = "No narrative available to translate.";
    }
    return;
  }


  // If English translation already exists, reuse it
  if (englishStory) {
    currentLanguage = "en";

    displayStory(englishStory);

    updateLanguageButtons();

    return;
  }


  if (statusEl) {
    statusEl.textContent = "Translating to English...";
  }


  if (englishBtn) {
    englishBtn.disabled = true;
  }


  try {

    const response = await fetch(
      TRANSLATE_API_URL,
      {
        method: "POST",

        headers: {
          "Content-Type": "application/json; charset=UTF-8"
        },

        body: JSON.stringify({
          text: originalKannadaStory
        })
      }
    );


    const data = await response.json();


    if (!response.ok || !data.success) {

      throw new Error(
        data.error || "Translation failed."
      );

    }


    englishStory = data.english || "";


    if (!englishStory.trim()) {

      throw new Error(
        "Translation returned empty text."
      );

    }


    currentLanguage = "en";

    displayStory(englishStory);

    updateLanguageButtons();


    if (statusEl) {
      statusEl.textContent = "";
    }

  }

  catch (error) {

    console.error(
      "Translation error:",
      error
    );


    currentLanguage = "kn";

    displayStory(originalKannadaStory);

    updateLanguageButtons();


    if (statusEl) {

      statusEl.textContent =
        "⚠ " +
        error.message +
        " Showing Kannada instead.";

    }

  }

  finally {

    if (englishBtn) {
      englishBtn.disabled = false;
    }

  }
}


// Update active language button
function updateLanguageButtons() {

  const btnKn = document.getElementById("btn-kn");
  const btnEn = document.getElementById("btn-en");

  if (!btnKn || !btnEn) return;


  btnKn.classList.toggle(
    "active",
    currentLanguage === "kn"
  );


  btnEn.classList.toggle(
    "active",
    currentLanguage === "en"
  );
}


// Initialize result page
window.addEventListener("DOMContentLoaded", () => {

  const padyaEl = document.querySelector(
    ".card-content.yellow"
  );

  const storyEl = document.getElementById(
    "story-text"
  );

  const btnKn = document.getElementById(
    "btn-kn"
  );

  const btnEn = document.getElementById(
    "btn-en"
  );


  // =========================================================
  // READ EXISTING RESULTS
  // =========================================================

  const padya =
    sessionStorage.getItem("yaksha_padya");

  const story =
    sessionStorage.getItem("yaksha_story");

  const matchStatus =
    sessionStorage.getItem("yaksha_match_status");

  const confidenceRaw =
    sessionStorage.getItem("yaksha_confidence");


  // =========================================================
  // RECOGNIZED PADYA
  // =========================================================

  if (padyaEl) {

    if (padya) {

      padyaEl.innerHTML = padya
        .split("\n")
        .map(
          line =>
            `<p style="margin:6px 0; font-size:16px;">
              ${escapeHtml(line)}
            </p>`
        )
        .join("");

    }

    else {

      padyaEl.innerHTML =
        "<p>ಯಾವುದೇ ಪದ್ಯ ಸಿಗಲಿಲ್ಲ.</p>";

    }

  }


  // =========================================================
  // NARRATIVE STORY
  // =========================================================

  if (storyEl) {

    if (
      matchStatus === "matched" &&
      story
    ) {

      // Save the original Kannada story
      originalKannadaStory = story;


      // Confidence
      let confidenceLine = "";


      if (confidenceRaw) {

        const pct =
          Math.round(
            parseFloat(confidenceRaw) * 100
          );


        if (!Number.isNaN(pct)) {

          confidenceLine =
            `<p style="
              font-size:13px;
              color:#16a34a;
              margin:0 0 10px;
            ">
              ✅ Match confidence: ${pct}%
            </p>`;

        }

      }


      // Display Kannada initially
      storyEl.innerHTML =
        confidenceLine +
        `<p style="
          font-size:15px;
          line-height:1.8;
          margin:0;
        ">
          ${escapeHtml(originalKannadaStory)}
        </p>`;


      // =====================================================
      // KANNADA BUTTON
      // =====================================================

      if (btnKn) {

        btnKn.addEventListener(
          "click",
          () => {

            currentLanguage = "kn";

            displayStory(
              originalKannadaStory
            );

            updateLanguageButtons();

            const statusEl =
              document.getElementById(
                "translate-status"
              );

            if (statusEl) {
              statusEl.textContent = "";
            }

          }
        );

      }


      // =====================================================
      // ENGLISH BUTTON
      // =====================================================

      if (btnEn) {

        btnEn.addEventListener(
          "click",
          translateStory
        );

      }


      updateLanguageButtons();

    }

    else if (story) {

      // Rejected / low-confidence match

      storyEl.innerHTML = `
        <p style="
          font-weight:600;
          color:#b91c1c;
          margin:0 0 8px;
        ">
          ⚠️ Padya Could Not Be Identified Reliably
        </p>

        <p style="
          font-size:15px;
          line-height:1.8;
          margin:0;
        ">
          ${escapeHtml(story)}
        </p>
      `;


      // Disable translation because this isn't
      // a confirmed narrative from the dataset.

      if (btnEn) {
        btnEn.disabled = true;
      }

    }

    else {

      storyEl.innerHTML =
        "<p>ಡೇಟಾಸೆಟ್ ತಯಾರಾದ ನಂತರ ಕಥೆ ಇಲ್ಲಿ ತೋರಿಸಲಾಗುತ್ತದೆ.</p>";


      if (btnEn) {
        btnEn.disabled = true;
      }

    }

  }

});