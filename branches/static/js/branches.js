define(['jquery', 'knockout', 'ui'], function($, ko, ui){
    var socket;

    /**
     * Connects to the WebSocket
     * @param  {[type]} url [description]
     * @return {[type]}     [description]
     */
    function connect(url){
        if(!url){
            url = 'ws://' + window.location.hostname + ':' + window.location.port + window.location.pathname;
        }

        var deferred = $.Deferred();
        console.log("Connecting to ws on url", url);
        socket = new WebSocket(url);
        socket.onopen = function(){
            deferred.resolve();
        };
        return deferred.promise();
    }

    /**
     * Sends a message over the socket
     */
    function send(obj){
        socket.send(JSON.stringify(obj));
    }

    // Utils
    var reloadIn = function(seconds){
        window.setTimeout(function(){
            window.location.reload();
        }, seconds * 1000)
    };

    var utils = {
        "reloadIn" : reloadIn,
    };

    console.log("Locked and loaded");


    return {
        "utils" : utils,
        "connect" : connect,
        "send" : send,
        "ui" : ui,
    };
});
