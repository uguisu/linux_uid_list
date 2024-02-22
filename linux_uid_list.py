# coding=utf-8
# author xin.he
import subprocess

from config import *


class LinuxUidList:

    def __init__(self):
        pass

    @staticmethod
    def __blacklist__uid__():
        return {
            'root': 'root',
            'daemon': 'daemon',
            'bin': 'bin',
            'sys': 'sys',
            'sync': 'sync',
            'games': 'games',
            'man': 'man',
            'lp': 'lp',
            'mail': 'mail',
            'news': 'news',
            'proxy': 'proxy',
            'www-data': 'www-data',
            'backup': 'backup',
            'irc': 'irc',
            'nobody': 'nobody',
            'systemd-network': 'systemd-network',
            'systemd-resolve': 'systemd-resolve',
            'systemd-timesync': 'systemd-timesync',
            'systemd-coredump': 'systemd-coredump',
            'syslog': 'syslog',
            'uuidd': 'uuidd',
            'tcpdump': 'tcpdump',
            'landscape': 'landscape',
            'sshd': 'sshd',
            'docker': 'docker',
            '_apt': '_apt',
            'tss': 'tss',
            'vbox': 'vbox',
        }

    @staticmethod
    def execute_command(cmd: str = 'ls') -> str:
        """
        execute command
        :param cmd: command as string
        :return: command output values
        """

        # init
        rtn = ''

        try:
            # execute command
            rtn = subprocess.check_output(cmd, shell=True)
            rtn = rtn.decode()

        except subprocess.CalledProcessError as e:
            print(f'Failed with error {str(e)}')

        return rtn

    def fetch_uid_dict(self):

        def _fetch_uname_from_home() -> list:
            """
            fetch username list from HOME folder
            :return: username list
            """

            cmd = f'''
                ssh {ssh_user_name}@{_h} -p {ssh_port} "ls /home"
            '''
            _uname_from_home = self.execute_command(cmd)

            # format result
            _w_lst = []
            for _w in _uname_from_home.split('\n'):
                _w = str.strip(_w)
                if len(_w) > 0 and self.__blacklist__uid__().get(_w) is None:
                    _w_lst.append(_w)

            del _uname_from_home

            # debug
            # for _a in _w_lst:
            #     print(f'{_h} : DEBUG->{_a}')

            return _w_lst

        def _fetch_uname_uid_from_etc_p() -> dict:
            """
            fetch username and id from /etc/passwd
            :return: username dict. key: username; val: uid as a set object
            """

            cmd = f'''
                ssh {ssh_user_name}@{_h} -p {ssh_port} "cat /etc/passwd | cut -d : -f 1,3"
            '''
            return _fetch_xname_xid_from_etc(cmd)

        def _fetch_gname_gid_from_etc_g() -> dict:
            """
            fetch username and id from /etc/group
            :return: username dict. key: group name(the same as username); val: uid as a set object
            """

            cmd = f'''
                ssh {ssh_user_name}@{_h} -p {ssh_port} "cat /etc/group | cut -d : -f 1,3"
            '''
            return _fetch_xname_xid_from_etc(cmd)

        def _fetch_xname_xid_from_etc(cmd) -> dict:
            _uname_from_home = self.execute_command(cmd)

            # format result
            # key: username; val: uid as a set object
            _w_dict = dict()
            for _w in _uname_from_home.split('\n'):
                # example-> root:0
                _w = str.strip(_w)

                if len(_w) > 0:
                    _w = _w.split(':')
                    if 2 == len(_w) and self.__blacklist__uid__().get(_w[0]) is None:
                        _set = _w_dict.get(_w[0], set())
                        _set.add(_w[1])
                        _w_dict[_w[0]] = _set
                        del _set

            del _uname_from_home

            # debug
            # for _k in _w_dict.keys():
            #     print(f'{_h} : DEBUG->{_k} : {_w_dict.get(_k)}')
            # print('-' * 50)

            return _w_dict

        # verify
        if host_list is None or 0 == len(host_list):
            raise AttributeError()

        # A dict object that contain user info without duplicate
        # merged_user_info = {
        #     'root': {
        #         0: ['127.0.0.1', '127.0.0.2'],
        #         1: ['127.0.0.3', '127.0.0.4'],
        #     }
        # }
        merged_user_info = dict()

        for _h in host_list:

            # username list from HOME folder
            uname_from_home = _fetch_uname_from_home()

            # username and uid from system settings
            uname_uid_etc_p = _fetch_uname_uid_from_etc_p()

            # group name and gid from system settings
            # gname_gid_etc_g = _fetch_gname_gid_from_etc_g()

            # merge
            for _stander_user_name in uname_from_home:
                _etc_p_set: set = uname_uid_etc_p.get(_stander_user_name)
                assert 1 == len(_etc_p_set)
                # convert to simple object
                _etc_p_set: str = _etc_p_set.pop()

                # _etc_g_set = gname_gid_etc_g.get(_stander_user_name)
                # assert 1 == len(_etc_g_set)

                # debug
                # print(f'{_h}\tusername = {_stander_user_name}'
                #       f'\n\t_etc_p_set = {_etc_p_set}'
                #       # f'\n\_etc_g_set = {_etc_g_set}'
                #       )

                # edit
                _merged_user_info_uname_dict = merged_user_info.get(_stander_user_name, dict())
                _merged_user_info_uid_lst = _merged_user_info_uname_dict.get(_etc_p_set, [])
                _merged_user_info_uid_lst.append(_h)
                # edit - update
                _merged_user_info_uname_dict[_etc_p_set] = _merged_user_info_uid_lst
                merged_user_info[_stander_user_name] = _merged_user_info_uname_dict

        print(self.__format_result(merged_user_info))

    @staticmethod
    def __format_result(result: dict) -> str:

        rtn = ''
        max_uid = -1

        for _k, _v in result.items():
            # example->  _k = root, _v = {0: ['127.0.0.1', '127.0.0.2'], ...}

            rtn += f'== {_k} =====\n'

            for _uid, _host_list in _v.items():
                # example->  _uid = 0, _host_list = ['127.0.0.1', '127.0.0.2']
                rtn += f'    {_uid}: {_host_list}\n'

                if int(_uid) < 30000:
                    max_uid = max(max_uid, int(_uid))

        rtn += f'@@@@@ Next suggest UID is {max_uid + 1} @@@@@'

        return rtn


if __name__ == '__main__':
    lul = LinuxUidList()
    lul.fetch_uid_dict()
