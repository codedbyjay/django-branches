requirejs(['common'], function(common){
    requirejs(['jquery', 'branches'], function($, branches){
        $(document).ready(function(){
            branches.connect().then(function(){
                $(".server").each(function(){
                    // var server = new branches.servers.Server("{{ server.slug }}");
                    // ko.applyBindings(server, this);
                    // server.initialize();
                });
            });

            // Gather a list of project id's covered on the page
            // if($(".commit-list")){
            //  $("div.project").each(function(){
            //      var projectId = this.id.replace("project-", "");
            //      var server = new Server(projectId);
            //      ko.applyBindings(server, this);
            //      server.initialize();
            //  });
            // }
        });
    });
});

