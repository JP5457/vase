tracks = alltracks;

console.log(tracks);
let queue = [];
let currentIndex = -1;
const audio = document.getElementById("audio");
const trackQueueEl = document.getElementById("trackQueue");
const allTracksEl = document.getElementById("allTracksList");
const currentTrackEl = document.getElementById("current-track");
const playPauseBtn = document.getElementById("playPauseBtn");
const loopCheckbox = document.getElementById("loopCheckbox");
const fadeCheckbox = document.getElementById("fadeCheckbox");
const autoplayCheckbox = document.getElementById("autoplayCheckbox");
const progress = document.getElementById("progress");
const trackLength = document.getElementById("trackLength");
const progressContainer = document.querySelector(".progress-container");
const libraryPicker = document.getElementById("libraryPicker");
const playicon = document.getElementById("playicon");
const pauseicon = document.getElementById("pauseicon");

function renderQueue() {
	trackQueueEl.innerHTML = "";
	queue.forEach((track, index) => {
		const li = document.createElement("li");
		li.textContent = track.name;
		li.classList.toggle("active-track", index === currentIndex);
		li.draggable = true;
		li.onclick = () => loadTrack(index);

		li.ondragstart = (e) => {
			e.dataTransfer.setData("text/plain", index);
		};

		li.ondragover = (e) => e.preventDefault();

		li.ondrop = (e) => {
			const from = parseInt(e.dataTransfer.getData("text/plain"));
			const to = index;
			const movedTrack = queue.splice(from, 1)[0];
			queue.splice(to, 0, movedTrack);
			renderQueue();
		};

		trackQueueEl.appendChild(li);
	});
}

function renderAllTracks() {
	allTracksEl.innerHTML = "";
	tracks.forEach((track) => {
		const li = document.createElement("li");
		li.textContent = track.name;
		li.onclick = () => {
			queue.push(track);
			renderQueue();
		};
		allTracksEl.appendChild(li);
	});
}

function fadeOut(audioElement, callback) {
	let vol = audioElement.volume;
	const fadeInterval = setInterval(() => {
		if (vol > 0.05) {
			vol -= 0.05;
			audioElement.volume = vol;
		} else {
			clearInterval(fadeInterval);
			audioElement.pause();
			audioElement.volume = 1.0;
			callback();
		}
	}, 50);
}

function fadeIn(audioElement) {
	audioElement.volume = 0;
	audioElement.play();
	let vol = 0;
	const fadeInterval = setInterval(() => {
		if (vol < 1.0) {
			vol += 0.05;
			audioElement.volume = vol;
		} else {
			clearInterval(fadeInterval);
		}
	}, 50);
}

function loadTrack(index) {
	if (index < 0 || index >= queue.length) return;
	const track = queue[index];
	const playTrack = () => {
		currentIndex = index;
		audio.src = track.link;
		currentTrackEl.textContent = `Now Playing: ${track.name}`;
		renderQueue();
		audio.load();
		if (fadeCheckbox.checked) {
			fadeIn(audio);
		} else {
			audio.play();
		}
		setPlayButton("Pause");
	};
	if (fadeCheckbox.checked && !audio.paused) {
		fadeOut(audio, playTrack);
	} else {
		playTrack();
	}
}

function setPlayButton(state) {
	if (state == "Pause") {
		playicon.style.display = "none";
		pauseicon.style.display = "block";
	} else {
		playicon.style.display = "block";
		pauseicon.style.display = "none";
	}
}

function togglePlayPause() {
	if (audio.paused) {
		audio.play();
		setPlayButton("Pause");
	} else {
		audio.pause();
		setPlayButton("Play");
	}
}

function nextTrack() {
	if (currentIndex + 1 < queue.length) {
		loadTrack(currentIndex + 1);
		if (!autoplayCheckbox.checked) {
			audio.currentTime = 0;
			audio.pause();
			setPlayButton("Play");
		}
	} else {
		audio.currentTime = 0;
		audio.pause();
		setPlayButton("Play");
	}
}

function previousTrack() {
	if (currentIndex > 0) {
		loadTrack(currentIndex - 1);
	}
}

function restartTrack() {
	audio.currentTime = 0;
}

function toggleLoop() {
	audio.loop = loopCheckbox.checked;
}

function seekTrack(e) {
	const width = progressContainer.clientWidth;
	const clickX = e.offsetX;
	const duration = audio.duration;
	audio.currentTime = (clickX / width) * duration;
}

function updateLibrary() {
	var library = libraryPicker.value;
	if (library != "All") {
		tracks = alltracks.filter((track) => track["library"] == library);
	} else {
		tracks = alltracks;
	}
	renderAllTracks();
}

function previousButton() {
	console.log(audio.currentTime);
	if (audio.currentTime > 2) {
		restartTrack();
	} else {
		previousTrack();
	}
}

audio.addEventListener("timeupdate", () => {
	const percent = (audio.currentTime / audio.duration) * 100;
	progress.style.width = percent + "%";
	trackLength.textContent = getCurrentTrackDurationFormatted();
});

audio.addEventListener("ended", () => {
	if (!audio.loop) {
		nextTrack();
	}
});

function getCurrentTrackDurationFormatted() {
	if (isNaN(audio.duration)) {
		return "00:00 / 00:00";
	}
	if (isNaN(audio.currentTime)) {
		return "00:00 / 00:00";
	}
	const durationminutes = Math.floor(audio.duration / 60);
	const durationseconds = Math.floor(audio.duration % 60);
	const currentminutes = Math.floor(audio.currentTime / 60);
	const currentseconds = Math.floor(audio.currentTime % 60);
	const durationtime = `${durationminutes
		.toString()
		.padStart(2, "0")}:${durationseconds.toString().padStart(2, "0")}`;
	const currenttime = `${currentminutes
		.toString()
		.padStart(2, "0")}:${currentseconds.toString().padStart(2, "0")}`;
	return currenttime + " / " + durationtime;
}

audio.addEventListener("loadeddata", () => {
	trackLength.textContent = getCurrentTrackDurationFormatted();
});

// Initial render
renderQueue();
renderAllTracks();

allTracksEl.ondragover = (e) => e.preventDefault();
allTracksEl.ondrop = (e) => {
	const from = parseInt(e.dataTransfer.getData("text/plain"));
	if (!isNaN(from)) {
		queue.splice(from, 1);
		renderQueue();
	}
};
