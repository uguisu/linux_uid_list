# linux UID list

The UID and GID of Linux are obtained by the system's default method during
allocation. This is impeccable on a single machine. However, as the amount of data
continues to skyrocket, more and more servers are mounting external shared
storage devices, which leads to confusion in access permissions when accessing
these shared storage devices from different servers.

To solve this problem, it is necessary to maintain the same 'UID' and 'GID' on all
servers that can access these shared resources.

This software can organize the 'UID' and 'GID' of users on servers within a
specified range, facilitating unified management.

## Requirement
- python3.8 +
- linux

## How to use
- Set Up Passwordless ssh login
- Update server list, ssh port, ssh login user name
- Execute `python3.8 linux_uid_list.py` in CLI.

## Refer

### Assign UID & GIU with explicit number

Assign an explicit number as `UID` and(or) `GID` can significantly reduce the impact
of the problem.

```shell
# setup user info
export ALL_ID=< Assign an explicit number here >
export TARGET_UID=< Assign an explicit username here >

# create user
cd /home
groupadd --gid $ALL_ID $TARGET_UID
useradd -d /home/$TARGET_UID -m -s "/bin/bash" $TARGET_UID --uid $ALL_ID --gid $ALL_ID
chmod =700 ./$TARGET_UID/

# setup password
passwd $TARGET_UID
```

### Change existing user's id

```shell
# setup user info
export ALL_ID=< Assign an explicit number here >
export TARGET_UID=< Assign an explicit username here >

# make change
groupmod -g $ALL_ID $TARGET_UID
usermod -u $ALL_ID $TARGET_UID

# refresh changes
chown -R $ALL_ID:$ALL_ID /home/$TARGET_UID
# chown -R $ALL_ID:$ALL_ID ......
```
