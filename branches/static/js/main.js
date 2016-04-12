(function(){
	$(document).ready(function(){

	});

	var client = new $.RestClient("/branches/api/v1/");
	client.add('project', {
		stripTrailingSlash : false,
	});
	client.project.addVerb('commits', 'GET');
	client.project.addVerb('available-branches', 'GET');
	client.project.addVerb('current-branch', 'GET');
	client.project.addVerb('status', 'GET');
	client.project.addVerb('changebranch', 'POST', {
		stripTrailingSlash: false
	});

	// Utils
	var reloadIn = function(seconds){
		window.setTimeout(function(){
			window.location.reload();
		}, seconds * 1000)
	};

	var utils = {
		"reloadIn" : reloadIn,
	};


	var branches = {
		"client" : client,
		"utils" : utils,
	};


	window.branches = branches;
})();