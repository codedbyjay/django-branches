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


