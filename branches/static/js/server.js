(function(){
	function ServerViewModel(projectId){
		var self = this;
		self.projectId = projectId;
		self.currentBranch = ko.observable();
		self.availableBranches = ko.observableArray();
		self.commits = ko.observableArray();
		self.statusLoaded = ko.observable(false);

		self.getStatus = function(){
			branches.client.project.status(self.projectId, {limit: 3}).then(function(data){
				var info = data.info;
				self.currentBranch(info.active_branch);
				self.availableBranches(info.available_branches);
				self.commits(info.commits);
				self.statusLoaded(true);
			});
		};

		self.initialize = function(){
			self.getStatus();
		};

	};

	$(document).ready(function(){
		// Gather a list of project id's covered on the page
		$("div.project").each(function(){
			var projectId = this.id.replace("project-", "");
			var serverViewModel = new ServerViewModel(projectId);
			ko.applyBindings(serverViewModel, this);
			serverViewModel.initialize();
		});
	});
})();