# Disable inactive Jira users
Automated way to review inactive Jira users and disable them. Uses as input the user export csv file downloaded via the user management page at https://admin.atlassian.com/ and uses Selenium to disable users in Jira.

### Installation

Install Ansible and run the playbook:
```
$ sudo apt install ansible
$ ansible-playbook install_dependencies.yaml
```

### Usage

#### Local

```
$ export JIRA_USER="jira-admin@domain.com"
$ export JIRA_PASS="p@55w0rd"
$ disable_jira_users.py --days 60
```

#### Docker

Running in headless mode, in a Docker container: define `JIRA_USER` and `JIRA_PASS` in `jira_creds` and run the following commands:

```
sudo docker build --build-arg --tag disable-jira-users .
sudo docker run --rm -it --env-file ./jira_creds disable-jira-users --days 90
```
