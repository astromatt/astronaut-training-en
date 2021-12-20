import csv
import datetime
import json
import logging
import os
import re


YEAR = 365.25
DAY = 86400
HOUR = 3600
MINUTE = 60
DURATION_REGEXP = re.compile(r'((?P<days>\d+?)d)?((?P<hours>\d+?)h)?((?P<minutes>\d+?)m)?((?P<seconds>\d+?)s)?')

logging.basicConfig(
    level=logging.INFO,
    format='"%(asctime).19s", "%(levelname)s", "%(message)s"')
log = logging.getLogger(__name__)


def as_date(string):
    try:
        return datetime.datetime.strptime(string, '%Y-%m-%d')
    except ValueError:
        try:
            return datetime.datetime.strptime(string, '%Y')
        except ValueError:
            log.error(f'Cannot parse date: {string}')
    return string

def timedelta_human(duration):
    seconds = int(duration.seconds)
    days, seconds = divmod(seconds, DAY)
    days = duration.days
    hours, seconds = divmod(seconds, HOUR)
    minutes, seconds = divmod(seconds, MINUTE)
    output = []

    if days:
        output.append(f'{days}d')
    if hours:
        output.append(f'{hours}h')
    if minutes:
        output.append(f'{minutes}m')
    if seconds:
        output.append(f'{seconds}s')

    return ' '.join(output)


def as_timedelta(string):
    """
    >>> as_timedelta('1d 1h 1m 1s')
    datetime.timedelta(1, 3661)

    >>> as_timedelta('1h 1m 1s')
    datetime.timedelta(0, 3661)

    >>> as_timedelta('1h 1s')
    datetime.timedelta(0, 3601)

    >>> as_timedelta('1s')
    datetime.timedelta(0, 1)
    """
    duration = datetime.timedelta()

    for parts in string.split():
        log.debug(f'Parsing value {parts}')
        num = int(parts[:-1])

        if parts.endswith('s'):
            duration += datetime.timedelta(seconds=num)
        elif parts.endswith('m'):
            duration += datetime.timedelta(minutes=num)
        elif parts.endswith('h'):
            duration += datetime.timedelta(hours=num)
        elif parts.endswith('d'):
            duration += datetime.timedelta(days=num)

    return duration


def analyze_file(path):
    log.warning(f'Analyzing file: {path}')
    with open(path) as file:
        astronaut = json.load(file)
        records = {
            'name': astronaut.get('name'),
            'status': astronaut.get('status'),
            'selection_group': astronaut.get('selection_group'),
            'nationality': astronaut.get('nationality'),
            'birth_date': astronaut.get('birth_date'),
        }

        if astronaut.get('died') and astronaut.get('birth_date'):
            date_birth = as_date(astronaut.get('birth_date'))
            date_death = as_date(astronaut.get('died'))
            records['died'] = astronaut.get('died')
            records['age_at_death'] = round((date_death - date_birth).days / YEAR, 1)

        if astronaut.get('selection_date') and astronaut.get('date_birth'):
            date_birth = as_date(astronaut.get('birth_date'))
            date_selection = as_date(astronaut.get('selection_date'))
            records['age_at_selection'] = round((date_selection - date_birth).days / YEAR, 1)
            records['selection_date'] = astronaut.get('selection_date')

        def summarize_list(name):
            elements = astronaut.get(f'{name}_list', [])
            records[f'{name}_count'] = len(elements)
            records[f'{name}_duration'] = datetime.timedelta()
            for element in elements:
                duration = element.get('duration', datetime.timedelta())
                records[f'{name}_duration'] += as_timedelta(duration)
            records[f'{name}_duration'] = timedelta_human(records[f'{name}_duration'])

        summarize_list('eva')
        summarize_list('fai_flight')
        summarize_list('non_fai_flight')
        summarize_list('significant_flight')

        if records.get('fai_flights_count'):
            records['flown'] = True
        elif records.get('non_fai_flight'):
            records['flown'] = True
        elif records.get('significant_flight'):
            records['flown'] = True
        else:
            records['flown'] = False

        return records


def write_csv(filename, data):
    log.warning(f'Saving file: {filename}')
    with open(filename, 'w', encoding='utf-8') as file:
        fieldnames = set()
        for key in [record.keys() for record in data]:
            fieldnames.update(key)

        writer = csv.DictWriter(file, sorted(fieldnames), quoting=csv.QUOTE_ALL, delimiter=',', quotechar='"', lineterminator='\n')
        writer.writeheader()

        for row in data:
            writer.writerow(row)


if __name__ == '__main__':
    data = []
    path = 'data'

    for file in os.listdir(path):

        results = analyze_file(os.path.join(path, file))
        data.append(results)

    write_csv('summary.csv', data)
