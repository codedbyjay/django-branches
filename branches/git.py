import hashlib
from StringIO import StringIO

from fabric.api import run

class Repo(object):

	def __init__(self, location):
		self.location = location

	@property
	def active_branch(self):
		return run("git rev-parse --abbrev-ref HEAD")

	@property
	def available_branches(self):
		result = run("git branch -a")
		branches = []
		for branch in result.splitlines():
			branch = branch.strip()
			if "*" in branch:
				continue # skip the current branch
			if "/" in branch:
				pieces = branch.split("/")
				branches.append(pieces[-1])
			else:
				branches.append(branch)
		return branches


	def get_commits(self, limit=50):
		commits = []
		fields = ["sha", "author_name", "author_email", "subject", "body", "gravatar_url"]
		result = run('git --no-pager log -n %s --pretty=format:"%%h|||%%an|||%%ae|||%%s|||%%b"' % limit, quiet=True)
		output = result.splitlines()
		for line in output:
			if not line:
				continue
			pieces = line.split("|||")
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

