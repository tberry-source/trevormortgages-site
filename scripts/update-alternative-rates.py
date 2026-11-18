from html.parser import HTMLParser
from pathlib import Path
from urllib.request import urlopen
from datetime import datetime
import json
import re
import sys

SOURCE = 'https://www.hometrust.ca/en/mortgages/rates'

class Cards(HTMLParser):
    description = ''

    def handle_starttag(self, tag, attrs):
        if tag != 'hometrust-card':
            return
        card = json.loads(dict(attrs).get('aem-data') or '{}')
        if card.get('headline') == 'Classic Mortgage':
            self.description = card['description']

def parse(html):
    cards = Cards()
    cards.feed(html)
    effective = re.search(r'Posted rates\*?\s*\(effective\s+(\d{2}/\d{2}/\d{4})\)', cards.description, re.I)
    table = re.search(r'<table\b[^>]*>(.*?)</table>', cards.description, re.I | re.S)
    if not effective or not table:
        raise ValueError('Home Trust Classic posted table is missing')
    rows = re.findall(r'<tr\b[^>]*>(.*?)</tr>', table[1], re.I | re.S)
    terms, rates = [
        [re.sub(r'<[^>]+>', '', cell).strip() for cell in re.findall(r'<t[dh]\b[^>]*>(.*?)</t[dh]>', row, re.I | re.S)]
        for row in rows
    ]
    values = rates[1:]
    if len(terms) != 6 or len(values) != 5 or rates[0].lower() != 'posted rates' or not all(
        re.fullmatch(fr'{i}[- ]year fixed', terms[i], re.I) and re.fullmatch(r'\d{1,2}\.\d{2}%', value)
        for i, value in enumerate(values, 1)
    ):
        raise ValueError('Unexpected posted fixed terms or rates')
    date = datetime.strptime(effective[1], '%m/%d/%Y').date().isoformat()
    return {'effective': date, 'rates': values}

if __name__ == '__main__':
    if len(sys.argv) == 2:
        html = Path(sys.argv[1]).read_text()
    else:
        with urlopen(SOURCE, timeout=20) as response:
            html = response.read(1_000_000).decode('utf-8')
    data = parse(html)
    target = Path('business-owner-alternative-rates.json')
    if target.exists() and data['effective'] < json.loads(target.read_text())['effective']:
        raise ValueError('Source effective date moved backwards')
    target.write_text(json.dumps(data, indent=2) + '\n')
