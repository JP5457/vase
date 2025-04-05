import WaveSurfer from "https://cdn.jsdelivr.net/npm/wavesurfer.js@7/dist/wavesurfer.esm.js";

let wavesurfer = WaveSurfer.create({
	container: "#waveform",
	waveColor: "#a00000",
	progressColor: "#c40000",
	mediaControls: true,
});

wavesurfer.load(url);

document.getElementById("copytext").addEventListener(
	"click",
	function () {
		var copyText = document.getElementById("audiolink");
		copyText.select();
		copyText.setSelectionRange(0, 99999);
		navigator.clipboard.writeText(copyText.value);
	},
	false
);
