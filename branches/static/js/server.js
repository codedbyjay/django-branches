define(['jquery', 'ko', 'branches'], function($, ko, branches){

    function Server(serverSlug){
        var self = this;
        this.serverSlug = serverSlug;

        /**
         * Keeps track of whether is being processed by the server
         * @type {Boolean}
         */
        self.busy = ko.observable(true);

        /**
         * The branch the server is on
         * @type {[type]}
         */
        self.currentBranch = ko.observable();
        /**
         * The currently selected branch
         * @type {[type]}
         */
        self.selectedBranch = ko.observable();

        self.availableBranches = ko.observableArray();
        /**
         * A list of commits for the current branch
         * @type {[type]}
         */
        self.commits = ko.observableArray();
        /**
         * Keeps track of the whether we've loaded the status information
         * @type {[type]}
         */
        self.dataLoaded = ko.observable(false);

        self.branchSelect = null;

        /**
         * Removes the currently selected branch
         * @return {[type]} [description]
         */
        self.resetSelectedBranch = function(){
            if(self.branchSelect){
                self.branchSelect.setValue(self.currentBranch());
            }
        };

        /**
         * Disables the selectize control for changing branches
         * @return {[type]} [description]
         */
        self.disableBranchSelect = function(){
            if(self.branchSelect){
                self.branchSelect.disable();
            }
        };

        /**
         * Enables the selectize control for changing branches
         * @return {[type]} [description]
         */
        self.enableBranchSelect = function(){
            if(self.branchSelect){
                self.branchSelect.enable();
            }
        };


        /**
         * Changes the branch on the server to the selected branch
         * @return {[type]} [description]
         */
        self.changeBranch = function(){
            var branch = self.selectedBranch();
            if(!branch){
                return;
            }
            var url = "/branches/api/v1/project/" + self.projectId + "/change-branch/";
            var params = {
                "branch" : branch
            };
            $.post(url, params).then(function(data){
                if(data.result){
                    self.changeBranchRequest(data.change_branch_request_pk);
                    self.changingBranches(true);
                }
            }).fail(function(){

            });
        };


        /**
         * Changes the branch on the server to the selected branch
         * @return {[type]} [description]
         */
        self.cancelChangeBranch = function(){
            console.log("Asked to cancel branch change");
            var branch = self.selectedBranch();
            if(!branch){
                console.log("No selected branch, cannot cancel");
                return;
            }
            var url = "/branches/api/v1/project/" + self.projectId + "/cancel-change-branch/";
            var params = {
                "submit" : "submit"
            };
            $.post(url, params).then(function(data){
                if(data.result){
                    self.changeBranchLog("");
                    self.getStatus(); // update everything
                }
            }).fail(function(){

            });
        };

        self.updateBranchList = function(){
            var url = "/branches/api/v1/project/" + self.projectId + "/update-branch-list/";
            var params = {
                "submit" : "submit"
            };
            self.disableBranchSelect();
            self.updatingBranches(true);
            $.post(url, params).then(function(data){
                if(data.result){
                    self.availableBranches(data.branches);
                    self.enableBranchSelect();
                    self.updatingBranches(false);
                }
            }).fail(function(){
                self.updatingBranches(false);
            });

        };

        self.updateBranchSelectOptions = function(){
            if(self.branchSelect){
                var branches = [];
                var availableBranches = self.availableBranches();
                for (var i = availableBranches.length - 1; i >= 0; i--) {
                    var branch = availableBranches[i];
                    branches.push({id: branch, name: branch});
                };
                self.branchSelect.addOption(branches);
                self.branchSelect.refreshOptions();
            }
        };

        /**
         * Sets up selectize for the current branch
         * @return {[type]} [description]
         */
        self.setupBranchSelect = function(){
            var branches = []; 
            var availableBranches = self.availableBranches();
            for (var i = availableBranches.length - 1; i >= 0; i--) {
                var branch = availableBranches[i];
                branches.push({id: branch, name: branch});
            };
            console.log("Current branch is", self.currentBranch());
            console.log("Available options are:", branches);
            $("#id_branch").val(self.currentBranch());
            if($("#id_branch").get().length > 0){
                self.branchSelect = $("#id_branch").selectize({
                    labelField: 'name',
                    valueField: 'id',
                    searchField: 'name',
                    sortField: [{field: "name", direction: "desc"}],
                    options: branches,
                    create: false,
                    maxItems: 1,
                    hideSelected: true,
                    closeAfterSelect: true,
                    openOnFocus: true,
                    render : {
                        item : function(data, escape){
                            return "<span class='branch-item'><i class='fa fa-code-fork'></i>&nbsp;&nbsp;" + escape(data.name) + "</span>";
                        }
                    },
                    onChange: function(value){
                        self.selectedBranch(value);
                    }
                })[0].selectize;
                if(self.changingBranches()){
                    self.disableBranchSelect();
                }
            }
        };

        self.requestStatus = function(){
            branches.send({
                "type" : "request-server-status",
                "server" : self.serverSlug
            });
        }


        /** Gets a status update from the server that tells us the active branch 
            and the available branches
         */
        self.getStatus = function(){
            self.dataLoaded(false);
            branches.client.project.status(self.projectId, {limit: 10}).then(function(data){
                var info = data.info;
                self.currentBranch(info.active_branch);
                self.availableBranches(info.available_branches);
                self.commits(info.commits);
                var lastChangeBranchRequest = info.last_change_branch_request;
                if($.isEmptyObject(lastChangeBranchRequest)){
                    self.changingBranches(false);
                } else {
                    self.changingBranches(!(lastChangeBranchRequest.complete || lastChangeBranchRequest.cancelled));
                }
                self.selectedBranch(info.active_branch);
                // If branchChangeRequest is blank, we can safely set it and 
                // call updateServerLog. If we were on the page when the 
                // change was requested, the changeBranchRequest would have 
                // been set.
                if(!self.changeBranchRequest()){
                    self.changeBranchRequest(lastChangeBranchRequest.id);
                    self.updateServerLog();
                }
                self.setupBranchSelect();
                self.dataLoaded(true);
            });
        };

        self.initialize = function(){
            console.log("Initializing server");
            self.requestStatus();
        };

    };

    branches.servers = {
        "Server" : Server
    };

})();