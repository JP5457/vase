import WaveSurfer from "https://cdn.jsdelivr.net/npm/wavesurfer.js@7/dist/wavesurfer.esm.js";

let streamid = 0;
let audioid = "";

function timeToString(time) {
	let minutes = Math.floor(time / 60);
	let seconds = Math.floor(time % 60);
	minutes = (minutes < 10 ? "0" : "") + minutes;
	seconds = (seconds < 10 ? "0" : "") + seconds;
	return minutes + ":" + seconds;
}

function stringToTime(time) {
	let times = time.split(":");
	let seconds = Number(times[0]) * 60 + Number(times[1]);
	return seconds;
}

function StartRec() {
	document.getElementById("clipper").style.display = "none";
	document.getElementById("loading").style.display = "none";
	document.getElementById("exporter").style.display = "none";
	document.getElementById("error").style.display = "none";
	document.getElementById("exported").style.display = "none";
	let streamurl = document.getElementById("streamurl").value;
	console.log(streamurl);
	const api_url = "/clipper/startrecording";
	fetch(api_url, {
		method: "POST",
		body: JSON.stringify({
			url: streamurl,
		}),
		headers: {
			"Content-type": "application/json; charset=UTF-8",
		},
	})
		.then((response) => {
			return response.json();
		})
		.then((data) => {
			console.log(data["uid"]);
			streamid = data["uid"];
		});
}

function updateState() {
	if (streamid != 0) {
		const api_url = "/clipper/getstate/" + streamid;
		fetch(api_url)
			.then((response) => {
				return response.json();
			})
			.then((data) => {
				document.getElementById("streamstate").innerText =
					data["state"];
			})
			.catch((error) => {
				console.error("Fetch error:", error);
				document.getElementById("streamstate").innerText =
					"Lost Connection";
			});
	}
}

function makeaudio(time) {
	if (streamid != 0) {
		document.getElementById("clipper").style.display = "none";
		document.getElementById("exporter").style.display = "none";
		document.getElementById("loading").style.display = "block";
		document.getElementById("error").style.display = "none";
		document.getElementById("exported").style.display = "none";
		const api_url = "/clipper/makeaudio/" + streamid + "/" + time;
		fetch(api_url)
			.then((response) => {
				return response.json();
			})
			.then((data) => {
				console.log(data["uid"]);
				audioid = data["uid"];
				wavesurfer.load("/clipper/getaudio/" + audioid);
				document.getElementById("clipper").style.display = "block";
				document.getElementById("exporter").style.display = "none";
				document.getElementById("loading").style.display = "none";
				document.getElementById("error").style.display = "none";
				document.getElementById("exported").style.display = "none";
			})
			.catch((error) => {
				document.getElementById("clipper").style.display = "none";
				document.getElementById("exporter").style.display = "none";
				document.getElementById("loading").style.display = "none";
				document.getElementById("error").style.display = "block";
				document.getElementById("errormsg").textContent =
					"Error creating clip audio";
				document.getElementById("exported").style.display = "none";
			});
	} else {
		document.getElementById("clipper").style.display = "none";
		document.getElementById("exporter").style.display = "none";
		document.getElementById("loading").style.display = "none";
		document.getElementById("error").style.display = "block";
		document.getElementById("errormsg").textContent =
			"No stream has been defined";
		document.getElementById("exported").style.display = "none";
	}
}

function makeclip(start, end) {
	let apiUrl = "/clipper/makeclip/" + audioid + "/" + start + "/" + end;
	fetch(apiUrl)
		.then((response) => {
			return response.json();
		})
		.then((data) => {
			clipsurfer.load("/clipper/getclip/" + audioid);
			wavesurfer.pause();
			document.getElementById("download").href =
				"/clipper/getclip/" + audioid;
			document.getElementById("exporter").style.display = "block";
			document.getElementById("loading").style.display = "none";
			document.getElementById("exported").style.display = "none";
		})
		.catch((error) => {
			document.getElementById("clipper").style.display = "none";
			document.getElementById("loading").style.display = "none";
			document.getElementById("error").style.display = "block";
			document.getElementById("errormsg").textContent =
				"Error trying to make clip";
			document.getElementById("exported").style.display = "none";
		});
}

function StoreClip() {
	document.getElementById("loading").style.display = "block";
	let streamname = document.getElementById("streamname").value;
	let clipname = document.getElementById("clipname").value;
	if (streamname != "" && clipname != "") {
		const regex = /^[a-z\d\s]+$/i;
		if (regex.test(streamname) && regex.test(clipname)) {
			streamname = streamname.replace(" ", "-");
			clipname = clipname.replace(" ", "-");
			let apiUrl =
				"/clipper/saveclip/" +
				audioid +
				"/" +
				clipname +
				"/" +
				streamname;
			fetch(apiUrl)
				.then((response) => {
					if (!response.ok) {
						throw new Error("Network response was not ok");
					}
					return response.json();
				})
				.then((data) => {
					document.getElementById("cliplink").href =
						"/clips/" + data["uid"];
					document.getElementById("loading").style.display = "none";
					document.getElementById("exported").style.display = "block";
				})
				.catch((error) => {
					document.getElementById("loading").style.display = "none";
					document.getElementById("error").style.display = "block";
					document.getElementById("errormsg").textContent =
						"Server error when attempting to save clip";
				});
		} else {
			document.getElementById("error").style.display = "block";
			document.getElementById("errormsg").textContent =
				"Stream name and clip name must be alphanumeric without special characters";
		}
	} else {
		document.getElementById("error").style.display = "block";
		document.getElementById("errormsg").textContent =
			"Stream name and clip name not provided";
	}
}

let wavesurfer = WaveSurfer.create({
	container: "#waveform",
	waveColor: "#449183",
	progressColor: "#17473e",
	mediaControls: true,
});

let clipsurfer = WaveSurfer.create({
	container: "#clipWaveform",
	waveColor: "#449183",
	progressColor: "#17473e",
	mediaControls: true,
});

document.getElementById("startrecbtn").addEventListener("click", StartRec);
document.getElementById("storeclip").addEventListener("click", StoreClip);

document.getElementById("clip1").addEventListener(
	"click",
	function () {
		makeaudio("1");
	},
	false
);
document.getElementById("clip5").addEventListener(
	"click",
	function () {
		makeaudio("5");
	},
	false
);

document.getElementById("setStart").addEventListener("click", async () => {
	document.getElementById("startClip").value = timeToString(
		wavesurfer.getCurrentTime()
	);
});

document.getElementById("setEnd").addEventListener("click", async () => {
	document.getElementById("endClip").value = timeToString(
		wavesurfer.getCurrentTime()
	);
});

document.getElementById("clip").addEventListener("click", async () => {
	document.getElementById("error").style.display = "none";
	document.getElementById("loading").style.display = "block";
	document.getElementById("exporter").style.display = "none";
	document.getElementById("exported").style.display = "none";

	let start = stringToTime(document.getElementById("startClip").value);
	let end = stringToTime(document.getElementById("endClip").value);
	if (start > end) {
		document.getElementById("loading").style.display = "none";
		document.getElementById("exporter").style.display = "none";
		document.getElementById("error").style.display = "block";
		document.getElementById("errormsg").textContent =
			"End time must be after start time";
		document.getElementById("exported").style.display = "none";
	} else {
		makeclip(start, end);
	}
});

//runs every second
function updateloop() {
	updateState();
}

setInterval(updateloop, 1 * 1000);
