(function(){
	$(document).ready(function(){

	});

	var client = new $.RestClient("/branches/api/v1/");
	client.add('project');
	client.project.addVerb('commits', 'GET');
	client.project.addVerb('available-branches', 'GET');
	client.project.addVerb('current-branch', 'GET');
	client.project.addVerb('status', 'GET');

	var branches = {
		"client" : client
	};

	window.branches = branches;
})();