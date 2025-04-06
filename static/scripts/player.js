const tracks = [
	{ id: 1, name: "Song One", link: "/clips/audio/1" },
	{ id: 2, name: "Song Two", link: "/clips/audio/2" },
	{ id: 3, name: "Song Three", link: "/clips/audio/3" },
];

let queue = [];
let currentIndex = -1;
const audio = document.getElementById("audio");
const trackQueueEl = document.getElementById("trackQueue");
const allTracksEl = document.getElementById("allTracksList");
const currentTrackEl = document.getElementById("current-track");
const playPauseBtn = document.getElementById("playPauseBtn");
const loopCheckbox = document.getElementById("loopCheckbox");
const fadeCheckbox = document.getElementById("fadeCheckbox");
const progress = document.getElementById("progress");
const progressContainer = document.querySelector(".progress-container");

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
		playPauseBtn.textContent = "Pause";
	};
	if (fadeCheckbox.checked && !audio.paused) {
		fadeOut(audio, playTrack);
	} else {
		playTrack();
	}
}

function togglePlayPause() {
	if (audio.paused) {
		audio.play();
		playPauseBtn.textContent = "Pause";
	} else {
		audio.pause();
		playPauseBtn.textContent = "Play";
	}
}

function nextTrack() {
	if (currentIndex + 1 < queue.length) {
		loadTrack(currentIndex + 1);
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

audio.addEventListener("timeupdate", () => {
	const percent = (audio.currentTime / audio.duration) * 100;
	progress.style.width = percent + "%";
});

audio.addEventListener("ended", () => {
	if (!audio.loop) {
		nextTrack();
	}
});

// Initial render
renderQueue();
renderAllTracks();
