import argparse



class Config:
    MODEL_PATH:  str = './model/'
    DB_PATH:     str = ''
    OUT_PATH:    str = ''
    CSV_BUFFER_SIZE: int = 1000000
    CSV_SEPARATOR: str = ''
    MS_SQL_HOST: str = ''
    MS_SQL_USER: str = ''
    MS_SQL_PASS: str = ''
    MS_SQL_TABL: str = ''
    MS_SQL_COL:  str = ''

    def __init__(self, logger):
        self.__logger = logger
        self.__config_path:str = './.env'
        self.APP_ARGS = None

        parser = argparse.ArgumentParser(description='AI address splitter')
        parser.add_argument(
            '-i',
            '--init',
            action="store_true",
            help='download model'
        )
        parser.add_argument(
            '-c',
            '--config-path',
            type=lambda s: unicodedata.name(s),
            help='path of .env file'
        )
        parser.add_argument(
            '-a',
            '--address',
            type=lambda s: str(s),
            help='address to parse'
        )
        parser.add_argument(
            '-db',
            '--database',
            type=lambda s: str(s),
            help='csv filepath or "sql"'
        )
        parser.add_argument(
            '-b',
            '--csv-buffer-size',
            type=int,
            help='buffer size for a csv file'
        )
        parser.add_argument(
            '-s',
            '--separator',
            type=str,
            help='delimiter or separator of csv file'
        )
        self.APP_ARGS = parser.parse_args()
        self.__logger.debug("| CONFIG | app args has been parsed")


        if self.APP_ARGS.config_path:
            self.__config_path = self.APP_ARGS.config_path
        else:
            self.__config_path = './.env'

        try:
            with open(self.__config_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    # Пропускаем пустые строки и комментарии
                    if not line or line.startswith("#"):
                        continue

                    # Разделяем строку на ключ и значение
                    if "=" in line:
                        key, value = line.split("=", 1)  # Разделяем только по первому "="
                        key = key.strip()
                        value = value.strip()

                        # Удаляем кавычки из значения
                        if (value.startswith('"') and value.endswith('"')) or \
                           (value.startswith("'") and value.endswith("'")):
                            value = value[1:-1]

                        # Присваиваем значение полю класса, если ключ совпадает
                        if hasattr(self, key):
                            setattr(self, key, value)
                            self.__logger.debug(f"| CONFIG | key <{key}> added")
                        else:
                            self.__logger.error(f"| CONFIG | key <{key}> NOT FOUND IN Config CLASS!")

        except FileNotFoundError:
            self.__logger.error(f"| CONFIG | FILE {self.__config_path} NOT FOUND!")


        if self.APP_ARGS.database:
            if self.APP_ARGS.database.lower() == 'sql':
                self.DB_PATH = self.APP_ARGS.database.lower()
            else:
                self.DB_PATH = self.APP_ARGS.database
        if self.APP_ARGS.csv_buffer_size:
            self.CSV_BUFFER_SIZE = int(self.APP_ARGS.csv_buffer_size)
        if self.APP_ARGS.separator:
            self.CSV_SEPARATOR = self.APP_ARGS.separator

        self.__logger.debug("| CONFIG | config has been created")
