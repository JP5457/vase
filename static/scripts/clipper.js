console.log("clipper");

let streamid = 0;

function StartRec() {
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

document.getElementById("startrecbtn").addEventListener("click", StartRec);

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

//runs every second
function updateloop() {
	updateState();
}

setInterval(updateloop, 1 * 1000);
