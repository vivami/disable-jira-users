# Disable inactive Jira users
Automated way to review inactive Jira users and disable them. Uses as input the user export csv file downloaded via the user management page at https://admin.atlassian.com/ and uses Selenium to disable users in Jira.

### Installation

Install Ansible and run the playbook:
```
$ sudo apt install ansible
$ ansible-playbook install_dependencies.yaml
```

### Usage

Download a user export by logging into https://admin.atlassian.com/, Settings, User Management, Export Users.

```
$ export USER="jira-admin@domain.com"
$ export PASS="p@55w0rd"
$ disable_jira_users.py --users /path/to/export-users.csv --days 60
```