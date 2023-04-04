(function (){

	function installStatus()
	{
		//~ <div id="status"><span id="status-res"></span><span id="status-cat"></span></div>
		const body = document.getElementsByTagName("body")[0];
		const status = document.createElement("div");
		status.setAttribute("id", "status");
		body.appendChild(status);
		status.innerHTML = '<span id="status-res"></span><span id="status-cat"></span>';
	}

	function updateStatus()
	{
		const html = document.getElementsByTagName("html")[0];
		const style = getComputedStyle(html);
		const resolution = document.getElementById("status-res");
		resolution.innerText = parseInt(style.width) + " ";
	}

	addEventListener("load", () => {
		installStatus();
		setInterval(updateStatus, 250);
	});

})();