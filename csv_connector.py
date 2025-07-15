import csv
import os
from tempfile import NamedTemporaryFile



class Csv_processing:
    """
    Read and save csv in batches (via buffer_size)
    keep in mind difference in column variations in each batch
    """
    def __init__(self, config, logger):
        self.__logger = logger
        self.__in_path = config.DB_PATH
        self.__out_path = config.OUT_PATH
        self.__csv_separator = config.CSV_SEPARATOR
        self.__buffer_size = int(config.CSV_BUFFER_SIZE)
        self.__logger.debug("| CSV | Csv_processing initialized")

    def process(self, ai_agent):
        temp_files = []
        cols = ['source']  # 1st col
        buffer = []

        try:
            with open(self.__in_path, 'r', encoding='utf-8') as infile:
                reader = csv.reader(infile, delimiter=self.__csv_separator)

                for row in reader:
                    if not row:
                        continue

                    source = row[0]
                    parsed = ai_agent.run(source)
                    row_data = {'source': source}
                    row_data.update(parsed)
                    buffer.append(row_data)

                    for key in parsed.keys():  # refresh cols
                        if key not in cols:
                            cols.append(key)

                    if len(buffer) >= self.__buffer_size:  # saving buffer
                        self.__save_buffer(buffer, temp_files, cols)
                        buffer = []
        except FileExistsError:
            self.__logger.error(f'| CSV | Cannot open {self.__in_path}')

        if buffer:  # saving rest of buffer
            self.__save_buffer(buffer, temp_files, cols)
            buffer = []

        self.__union_tmps(temp_files, cols)


    def __save_buffer(self, buffer: list, temp_files: list, cols: list):
        temp_file = NamedTemporaryFile(mode='w',
                                       delete=False,
                                       encoding='utf-8',
                                       newline=''
                                       )
        writer = csv.DictWriter(temp_file, fieldnames=cols)
        writer.writeheader()
        writer.writerows(buffer)
        temp_file.close()
        temp_files.append(temp_file.name)
        self.__logger.debug(f"| CSV | {len(buffer)} rows saved to tmp file {temp_file.name}")


    def __union_tmps(self, temp_files: list, cols: list):
        with open(self.__out_path,
                  'w', encoding='utf-8',
                  newline=''
                  ) as outfile:
            writer = csv.DictWriter(outfile, fieldnames=cols)
            writer.writeheader()

            for temp_file in temp_files:
                with open(temp_file, 'r', encoding='utf-8') as tf:
                    reader = csv.DictReader(tf)
                    for row in reader:
                        writer.writerow(row)
                os.unlink(temp_file)
