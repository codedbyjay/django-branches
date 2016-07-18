define(function(){

    function ServerViewModel(params){
        var self = this;
        self.server = params.server;
    }

    return {
        "servers" : {
            "ServerViewModel": ServerViewModel,
        }
    };
});