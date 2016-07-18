=============
API Reference
=============


Models
======

..  autoclass:: branches.models.Server
    :members: initialize, execute, get_absolute_url

    ..  attribute:: user

        The owner of the server

    ..  attribute:: name

        A short name for the server

    ..  attribute:: address

        The IP / hostname for the server

    ..  attribute:: username

        The username to use to login to the server

    ..  attribute:: port

        The port to use to connect to the server

    ..  attribute:: repositories

        A list of repositories hosted on the server

    ..  attribute:: initialized

        This is set to true after we have successfully connected to the server


..  autoclass:: branches.models.Repository

    ..  attribute:: name

        The name of the repository

    ..  attribute:: url

        The url for the repository

..  autoclass:: branches.models.Project
    :members: get_log, is_changing_branch, is_change_branch_requested, change_branch_log, cancel_change_branch, repo, current_branch, available_branches, get_status, get_commits, last_change_branch_request, update_branch_list

    ..  attribute:: server

    The server that the project resides on

    ..  attribute:: repository

    The repository that this project is linked to

    ..  attribute:: location

    The location of the repository on the server

    ..  attribute:: change_branch_script

    A script that is run each time the branch changes


Signals
=======
The following signals are used to allow the system to know when to send messages to different channels.

    ..  attribute:: request_created 

        This signal is dispatched whenever a new request is created.

        -   ``server`` - the slug of the server.
        -   ``project`` - the slug of the project.
        -   ``owner`` - the slug for the owner of the server / project.
        -   ``branch`` - the target branch of the request.
        -   ``current_branch`` - the branch the server is currently on (at the time of request creation).

    ..  attribute:: request_started

        This signal is dispatched when a Celery worker has picked up the request and started to action it. 

    ..  attribute:: request_cancel

        This signal is dispatched when someone opts to cancel the request.

    ..  attribute:: request_cancelling

        This signal is dispatched when the request is in the process of being cancelled. This typically involves asking Celery to stop a task which may take a few milliseconds.

    ..  attribute:: request_cancelled

        This signal is dispatched when the request is finally cancelled.

    ..  attribute:: request_completed

        This signal is fired when a request has run to completion.

