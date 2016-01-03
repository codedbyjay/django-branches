import hashlib
from StringIO import StringIO

from fabric.api import run

class Repo(object):

    def __init__(self, location):
        self.location = location

    @property
    def active_branch(self):
        return run("git rev-parse --abbrev-ref HEAD")

    def get_branch_list(self, *args):
        """ Runs the git branch command with the given args. Also clean up the
            resulting list. Strips output and removes pointers.
        """
        arguments = " ".join(args) if args else ""
        cmd = "git branch %s" % arguments
        results = run(cmd, quiet=True).splitlines()
        remove_pointers = lambda branch: "->" not in branch
        strip = lambda branch: branch.replace("*","").strip()
        return map(strip, filter(remove_pointers, results))

    def get_branch_merges(self, branch, prefixes=[], branches=[]):
        """ Return a list of branches that ``branch`` was merged into. 
            ``prefixes`` specifies a list of patterns to look for re 
            branches.
            ``branches`` is a list of branches to search. If none is 
            specified, we search ALL branches.
        """
        merged_branches = []
        if not prefixes:
            prefixes = ["master", "release"]
        if not branches:
            branches = self.get_branch_list("-a")
        target_branches = []
        for prefix in prefixes:
            for branch in target_branches:
                if branch.startswith(prefix):
                    target_branch.append(branch)
        for target_branch in target_branches:
            branches_merged_into_target_branch = \
                self.get_branch_list("-a", "--merged", target_branch)
            for branch in branches:
                if branch in branches_merged_into_target_branch:
                    merged_branches.append(target_branch)
        return merged_branches


    @property
    def available_branches(self):
        """ Returns a list of ALL branches (local and remote)
        """
        return self.get_branch_list() + [self.active_branch]

    def get_commits(self, limit=50, branch=None):
        """ Returns a list of commits
        """
        commits = []
        fields = ["sha", "author_name", "author_email", "subject", "body", "gravatar_url"]
        result = run('git --no-pager log -n %s --pretty=format:"%%h|||%%an|||%%ae|||%%s|||%%b"' % limit, quiet=True)
        output = result.splitlines()
        for line in output:
            if not line:
                continue
            pieces = line.split("|||")
            if len(pieces) < 2:
                continue
            email = pieces[2]
            email_md5 = hashlib.md5(email.lower()).hexdigest()
            gravatar_url = "http://www.gravatar.com/avatar/%s?size=32" % email_md5
            pieces.append(gravatar_url)
            commits.append(dict(zip(fields, pieces)))
        return commits

    def get_status(self, limit=10):
        active_branch = self.active_branch
        available_branches = self.available_branches
        commits = self.get_commits(limit=limit)
        return dict(active_branch=active_branch,
            available_branches=available_branches,
            commits=commits)

