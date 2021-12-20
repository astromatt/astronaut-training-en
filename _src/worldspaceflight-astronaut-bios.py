import datetime
import json
import re
import logging
from bs4 import BeautifulSoup
from gateway import HTTPGateway

YEAR = 365.25
GROUP_REGEX = re.compile(r'(?P<selection>.+)\s\((?P<date>.+)\)')
TABLE_NAMES = {
    "EVA's:": 'eva',
    "FAI Flights:": 'fai_flight',
    "USAF (Non-FAI) Flights:": 'non_fai_flight',
    "\nNon-Qualifying Flights with Significance:\n": 'significant_flight'
}

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)
http = HTTPGateway(cache_directory='tmp')


def get_bio_urls(url):
    html = BeautifulSoup(http.get(url), 'html.parser')

    for a in html.find_all('a'):
        if a['href'].startswith('/bios/') and not a['href'].startswith('/bios/biositemap.php'):
            yield a['href']

def clean_date(string):
    try:
        date = datetime.datetime.strptime(string, '%d %B %Y')
        return f'{date:%Y-%m-%d}'
    except ValueError:
        return string


def clean_duration(string):
    duration = string.strip()
    duration = duration.replace(' days', 'd')
    duration = duration.replace(' hours', 'h')
    duration = duration.replace(' minutes', 'm')
    duration = duration.replace(' seconds', 's')
    duration = duration.replace('\u00a0', '')
    duration = duration.replace(' second', 's')
    duration = duration.replace(' econds', 's')
    duration = duration.replace('On orbit ', '')
    duration = duration.replace('(', '')
    duration = duration.replace(')', '')
    duration = duration.replace(' - not classified as a space flight due to low altitude', '')
    return duration.replace(',', '')


def get_bio_data(url):
    html = BeautifulSoup(http.get(url), 'html.parser')
    html.find(id='menubox').decompose()
    astronaut = {}

    try:
        img = [img['src'] for img in html.find_all('img') if img['src'].startswith('/bios/photos/')]
        astronaut['img'] = f'https://www.worldspaceflight.com{img[0]}'
    except IndexError:
        astronaut['img'] = None

    paragraphs = [p.text
        for p in html.find_all('p')
            if p.text and not p.text.isspace() and not p.text.startswith('\\')]

    astronaut['name'] = paragraphs[0]
    astronaut['first_name'] = ' '.join(paragraphs[0].split()[:-1])
    astronaut['last_name'] = paragraphs[0].split()[-1]
    log.warning('Parsing: %s', astronaut['name'])

    for p in paragraphs[1:]:
        if p.startswith('Page last modified'):
            continue

        if ':' not in p:
            astronaut['notes'] = p.strip()
            continue

        key, value = p.split(':')
        key = key.lower().strip()
        value = value.strip()

        if key == 'died':
            if value:
                day, month, year, *remarks = value.split()
                astronaut['died'] = clean_date(f'{day} {month} {year}')
                if remarks:
                    remarks = ' '.join(remarks).replace('(', '').replace(')', '')
                    astronaut['death_remarks'] = remarks
            else:
                astronaut['died'] = None

        elif key == 'group':
            selection = GROUP_REGEX.findall(value)[0]
            astronaut['selection_group'] = selection[0].strip()
            astronaut['selection_date'] = clean_date(selection[1])

        elif key == 'born':
            date, *place = value.split(',')
            if date == 'United States':
                astronaut['birth_date'] = None
                astronaut['birth_place'] = 'United States'
            else:
                astronaut['birth_date'] = clean_date(date)
                astronaut['birth_place'] = ','.join(place).strip()

        else:
            astronaut[key] = value

    for table in html.find_all('table'):
        rows = table.find_all('tr')
        header, content = rows[0], rows[1:]
        table_name = TABLE_NAMES[header.text]
        table_data = []

        for tr in content:
            data = [td.text for td in tr.find_all('td')]

            try:
                int(data[0])
                mission, date, duration = data[1], data[2], data[3]
            except ValueError:
                mission, date, duration = data[0], data[1], data[2]

            table_data.append({
                'mission': mission.strip(),
                'date': clean_date(date),
                'duration': clean_duration(duration),
            })

        astronaut[f'{table_name}_count'] = len(table_data)
        astronaut[f'{table_name}_list'] = table_data

    # date_selection = datetime.datetime.strptime(astronaut['selection_date'], '%Y-%m-%d')
    # date_birth = datetime.datetime.strptime(astronaut['birth_date'], '%Y-%m-%d')
    # astronaut['selection_age'] = (date_selection - date_birth).days / YEAR
    return astronaut


def save(biography):
    first_name = biography['first_name']
    last_name = biography['last_name']
    slug = ''.join(re.findall('[a-zA-Z-]', f'{last_name}-{first_name}'))
    path = f'data/{slug}.json'

    with open(path, 'w') as file:
        log.warning(f'Writing to file {path}')
        content = json.dumps(biography, indent=4, sort_keys=True)
        file.write(content)


if __name__ == '__main__':
    urls = []
    urls.extend(get_bio_urls('https://www.worldspaceflight.com/bios/alpha_names.php'))
    urls.extend(get_bio_urls('https://www.worldspaceflight.com/bios/unflown.php'))

    for url in urls:
        save(get_bio_data(f'https://www.worldspaceflight.com/{url}'))
