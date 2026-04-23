// 🔗 NAVIGATION
function goToHow() {
  window.location.href = "how.html";
}

function goToUpload() {
  window.location.href = "upload.html";
}

function goToResult() {
  window.location.href = "result.html";
}

function goToHome() {
  window.location.href = "index.html";
}


// 🎧 AUDIO PREVIEW
const audioFile = document.getElementById("audioFile");
const player = document.getElementById("audioPlayer");

if (audioFile) {
  audioFile.addEventListener("change", function () {
    const file = this.files[0];
    if (file) {
      player.src = URL.createObjectURL(file);
      player.style.display = "block";
    }
  });
}


// 🔄 RESET
const resetBtn = document.querySelector(".reset");

if (resetBtn) {
  resetBtn.addEventListener("click", () => {
    if (audioFile) audioFile.value = "";
    if (player) {
      player.src = "";
      player.style.display = "none";
    }
  });
}


// 🎤 RECORDING
let recorder;
let chunks = [];

const recordBtn = document.querySelector(".record-btn");

if (recordBtn) {
  recordBtn.addEventListener("click", async () => {

    if (!recorder || recorder.state === "inactive") {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      recorder = new MediaRecorder(stream);

      recorder.start();
      recordBtn.innerText = "Stop Recording";

      chunks = [];

      recorder.ondataavailable = e => chunks.push(e.data);

    } else {
      recorder.stop();
      recordBtn.innerText = "Start Recording";

      recorder.onstop = () => {
        const blob = new Blob(chunks);
        const url = URL.createObjectURL(blob);

        player.src = url;
        player.style.display = "block";
      };
    }

  });
}