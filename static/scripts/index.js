let recordedChunks = [];

function startRecording() {
    recordedChunks = [];

    navigator.mediaDevices.getUserMedia({ audio: true })
        .then(stream => {
            const mediaRecorder = new MediaRecorder(stream);

            mediaRecorder.addEventListener("dataavailable", event => {
                recordedChunks.push(event.data);
            });

            mediaRecorder.addEventListener("stop", () => {
                const recordedBlob = new Blob(recordedChunks, { type: "audio/ogg; codecs=opus" });
                const recordedAudio = document.getElementById("recordedAudio");
                recordedAudio.src = URL.createObjectURL(recordedBlob);
            });

            mediaRecorder.start();
        });
}

function stopRecording() {
    const mediaRecorder = new MediaRecorder(stream);
    mediaRecorder.stop();
}