import os


class Parameters:
    def __init__(self, filename):
        self.__filename = filename
        self.__params = {'apikey_naver_id': '',
                         'apikey_naver_secret': '',
                         'apikey_seoul': ''}
        self.__load_parameterfile()

    def load(self):
        return self.__params

    def __check_dict_key(self, key):
        status = key in self.__params
        return status

    def __load_parameterfile(self):
        cwd = os.getcwd()
        abs_fname = os.path.join(cwd, self.__filename)

        try:
            fid = open(abs_fname, 'r', encoding='utf8')
        except FileNotFoundError as e:
            print(str(e))
            raise FileNotFoundError
        else:
            lines = fid.readlines()

            for line in lines:
                sub = line.split('=')
                if len(sub) == 2:
                    key = sub[0].strip()
                    value = sub[1].strip()
                    if self.__check_dict_key(key):
                        self.__params[key] = value
                    else:
                        print('"{}" is not an unapproved key. Please check below the key lists.'.format(key))
                        print('Available key lists')
                        for it in self.__params.items():
                            print(' - {}'.format(it[0]))
                        raise SyntaxError

