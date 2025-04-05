document.getElementById("searchbtn").addEventListener(
	"click",
	function () {
		let searchterm = document.getElementById("searchterm").value;
		if (searchterm != "") {
			const regex = /^[a-z\d\s]+$/i;
			if (regex.test(searchterm)) {
				searchterm = searchterm.replace(/\s+/g, "-");
				let url = "/clips/search/" + searchterm;
				window.location.replace(url);
			}
		} else {
			window.location.replace("/clips/all");
		}
	},
	false
);
