(function(){
    /**
     * An observable activity is an encapsulation of some activity we need to 
     * do ever so often where we are interested in tracking the 'loading' 
     * status.
     * @param  {[type]} options [description]
     * @return {[type]}         [description]
     */
    function observableActivity(options){
        var self = this;
        var defaultOptions = {
            "dataType" : "array",
            "load" : function(){
                // A simple function that supports promises
                var deferred = $.Deferred();
                deferred.resolve();
                return deferred.promise();
            }
        };
        self.options = $.extend(options || {}, defaultOptions);
        self.loadFunction = self.options.load;
        self.loading = ko.observable(false);
        if(self.options.dataType == "array"){
            self.data = ko.observableArray();
        } else {
            self.data = ko.observable({});
        }

        /**
         * This load function calls the "load" function supplied
         * @return {[type]} [description]
         */
        self.load = function(){
            var deferred = $.Deferred();
            self.loadFunction().then(function(data){
                deferred.resolve(data);
            }).fail(function(data){
                deferred.reject(data);
            });
            return deferred.promise();
        };
    };
})();