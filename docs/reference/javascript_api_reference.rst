
==============
Javascript API
==============

The Javascript API allows real time interaction with servers. KnockoutJS and jQuery are the libraries used to update the UI. We use Javascript "classes" to represent projects and servers. The servers and project are aware of the WebSocket and use it primarily for sending and receiving messages. A fallback, HTTP based implementation will be developed later as a fallback for earlier browsers.

Business Layer
==============

..  class:: branches.servers.Server

    ..  attribute:: busy 

        An observable that tells us whether the server is busy or not.

    ..  attribute:: branch

        An observable that keeps track of the current branch.

    ..  attribute:: branches

        An observable array that keeps track of the branches available on the server.

    ..  attribute:: commits

        An observable array giving a list of commits for the currently selected branch.

    ..  attribute:: request

        An observable object that keeps track of the details of the current request that is being executed on the server.

    ..  attribute:: requests

        Keeps track of the history of requests that have been executed on the server.


Presentation Layer
==================
The presentation layer implements the ``ViewModel`` objects necessary for managing the UI on the pages.

