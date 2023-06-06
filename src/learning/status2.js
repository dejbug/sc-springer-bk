(function (){

	function installStatus()
	{
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

		//~ const screenW = screen.width;
		//~ const screenH = screen.height;
		const layoutVpW = document.documentElement.clientWidth;
		const layoutVpH = document.documentElement.clientHeight;
		const visualVpW = window.innerWidth;
		const visualVpH = window.innerHeight;
		const pageW = document.documentElement.offsetWidth;
		const pageH = document.documentElement.offsetHeight;
		const scrollX = Math.round(window.pageXOffset);
		const scrollY = Math.round(window.pageYOffset);
		
		const diffVpW = visualVpW - layoutVpW;
		const diffVpH = visualVpH - layoutVpH;

		resolution.innerText =
			"(" + layoutVpW + ( diffVpW ? "+" + diffVpW : "" )
				+ " : "
				+ layoutVpH + ( diffVpH ? "+" + diffVpH : "" )
				+ ") "
			+ ( scrollX + scrollY ?	"{" + scrollX + ":" + scrollY + "} " :	"" )
			+ "[" + pageH + "] "
			+ parseInt(style.width) + " "
			;
	}

	addEventListener("load", () => {
		installStatus();
		setInterval(updateStatus, 250);
	});

})();