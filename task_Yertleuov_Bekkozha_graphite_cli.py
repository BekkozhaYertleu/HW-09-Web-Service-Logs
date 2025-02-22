#!/usr/bin/env python3
import argparse
import re
from datetime import datetime, timedelta
import pytz

def parse_timestamp(timestamp_str):
    """
    Парсинг временной метки из строки лога.
    """
    main_time_str, ms_str = timestamp_str.split(".")
    main_time = datetime.strptime(main_time_str, "%Y%m%d_%H%M%S")
    tz = pytz.timezone('Europe/Moscow')
    main_time = tz.localize(main_time)
    ms = int(ms_str)
    return main_time + timedelta(milliseconds=ms)

def process_log(log_file, host, port):
    """
    Обработка лог-файла и генерация команд для Graphite.
    Функция принимает либо путь к файлу (строку), либо файловый объект.
    """
    query_data = {}
    if isinstance(log_file, str):
        f = open(log_file, 'r')
        close_after = True
    else:
        f = log_file
        close_after = False

    for line in f:
        match = re.match(r"(\d{8}_\d{6}\.\d{3}) (\S+) (\S+) (.*)", line)
        if match:
            timestamp_str, logger_name, level, message = match.groups()
            timestamp = parse_timestamp(timestamp_str)
            if level == "DEBUG" and message.startswith("start processing query: "):
                query = message[len("start processing query: "):]
                query_data[query] = {"start_time": timestamp}
            elif level == "INFO" and message.startswith("found "):
                parts = message.split(" articles for query: ", 1)
                article_count = int(parts[0].split()[1])
                query = parts[1]
                if query in query_data:
                    query_data[query]["article_count"] = article_count
            elif level == "DEBUG" and message.startswith("finish processing query: "):
                query = message[len("finish processing query: "):]
                if query in query_data:
                    start_time = query_data[query]["start_time"]
                    article_count = query_data[query].get("article_count", 0)
                    finish_time = timestamp
                    complexity = (finish_time - start_time).total_seconds()
                    finish_timestamp = int(finish_time.timestamp())
                    print(f'echo "wiki_search.article_found {article_count} {finish_timestamp}" | nc -N {host} {port}')
                    print(f'echo "wiki_search.complexity {complexity:.3f} {finish_timestamp}" | nc -N {host} {port}')
                    del query_data[query]
    if close_after:
        f.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--process', required=True, help='Path to the log file')
    parser.add_argument('--host', default='localhost', help='Graphite host')
    parser.add_argument('--port', default=2003, type=int, help='Graphite port')
    args = parser.parse_args()
    process_log(args.process, args.host, args.port)

