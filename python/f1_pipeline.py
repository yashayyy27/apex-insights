"""Cache-first, rate-limited Jolpica ingestion and honest F1 normalization.

No scraped timing telemetry. Final standings include sprints and official
adjustments; grand-prix-only progression is named accordingly.
"""
import argparse
import json
import time
from datetime import datetime, timezone
import requests
import pandas as pd
from common import ROOT, CONFIG, save_csv, write_json, sha256

BASE = 'https://api.jolpi.ca/ergast/f1/'

class Client:
    def __init__(self, offline=False):
        self.offline = offline
        self.last_request = 0.0
        self.session = requests.Session()
        self.session.headers['User-Agent'] = 'ApexInsights/1.0.0 requests/' + requests.__version__
        self.manifest_path = ROOT / 'data/raw/f1/manifest.json'
        self.manifest = json.loads(self.manifest_path.read_text()) if self.manifest_path.exists() else {}

    def page(self, endpoint, offset):
        name = endpoint.replace('/', '_') + '_offset' + str(offset) + '.json'
        path = ROOT / 'data/raw/f1' / name
        if path.exists():
            if name not in self.manifest or sha256(path) != self.manifest[name]['sha256']:
                raise ValueError('Untrusted or modified cache: ' + name)
            return json.loads(path.read_text())['MRData']
        if self.offline:
            raise FileNotFoundError('Offline cache missing: ' + name)
        url = BASE + endpoint + '.json'
        for attempt in range(5):
            delay = max(0, CONFIG['api_request_interval_seconds'] - (time.monotonic() - self.last_request))
            time.sleep(delay)
            self.last_request = time.monotonic()
            response = self.session.get(url, params={'limit': 100, 'offset': offset}, timeout=45)
            if response.status_code == 429 or response.status_code >= 500:
                retry = response.headers.get('Retry-After', '')
                time.sleep(float(retry) if retry.isdigit() else min(60, 2 ** (attempt + 2)))
                continue
            response.raise_for_status()
            raw = response.json()
            write_json(raw, path)
            self.manifest[name] = {'url': response.url, 'retrieved_utc': datetime.now(timezone.utc).isoformat(),
                                   'sha256': sha256(path), 'license': 'CC BY-NC-SA 4.0',
                                   'attribution': 'Jolpica-F1 / Ergast', 'data_class': 'PUBLIC'}
            write_json(self.manifest, self.manifest_path)
            return raw['MRData']
        raise RuntimeError('Exhausted bounded retries: ' + url)

    def get(self, endpoint, table, rows):
        """Pages are flattened downstream because a race can straddle pages."""
        out = []
        offset = 0
        while True:
            data = self.page(endpoint, offset)
            out.extend(data[table].get(rows, []))
            offset += int(data['limit'])
            if offset >= int(data['total']):
                break
        return out

def seconds(value):
    if value is None or value == '':
        return None
    parts = str(value).split(':')
    return sum(float(v) * 60 ** i for i, v in enumerate(reversed(parts)))

def completed_status(status):
    """Current Jolpica uses Lapped; legacy Ergast uses +N Lap(s)."""
    import re
    return status in {'Finished','Lapped'} or re.fullmatch(r'\+\d+ Laps?',status) is not None

def normalize(client):
    races, drivers, constructors, circuits = {}, {}, {}, {}
    results, qualifying, sprints, pits, laps, ds, cs = [], [], [], [], [], [], []

    def context(race):
        season, rnd = int(race['season']), int(race['round'])
        key = season * 100 + rnd
        c = race['Circuit']
        circuits[c['circuitId']] = dict(CircuitKey=c['circuitId'], Circuit=c['circuitName'],
                                       Country=c['Location']['country'], Locality=c['Location']['locality'],
                                       Latitude=float(c['Location']['lat']), Longitude=float(c['Location']['long']), DataClass='PUBLIC')
        races[key] = dict(RaceKey=key, Season=season, Round=rnd, Race=race['raceName'],
                          CircuitKey=c['circuitId'], Date=race['date'], DataClass='PUBLIC')
        return key

    def person(item):
        d = item['Driver']
        drivers[d['driverId']] = dict(DriverKey=d['driverId'], Driver=d['givenName'] + ' ' + d['familyName'],
                                     Nationality=d['nationality'], DOB=d['dateOfBirth'], DataClass='PUBLIC')
        if 'Constructor' in item:
            c = item['Constructor']
            constructors[c['constructorId']] = dict(ConstructorKey=c['constructorId'], Constructor=c['name'],
                                                  Nationality=c['nationality'], DataClass='PUBLIC')
        return d['driverId']

    for season in CONFIG['f1_seasons']:
        print('F1 ingest season', season, flush=True)
        calendar = client.get(str(season), 'RaceTable', 'Races')
        for race in calendar:
            context(race)
        for endpoint, label, target in [('results', 'Results', results), ('qualifying', 'QualifyingResults', qualifying), ('sprint', 'SprintResults', sprints)]:
            for race in client.get(f'{season}/{endpoint}', 'RaceTable', 'Races'):
                rk = context(race)
                for x in race[label]:
                    dk = person(x)
                    base = dict(RaceKey=rk, DriverKey=dk, ConstructorKey=x['Constructor']['constructorId'], DataClass='PUBLIC_DERIVED')
                    if endpoint == 'qualifying':
                        base.update(QualifyingPosition=int(x['position']), Q1Seconds=seconds(x.get('Q1')),
                                    Q2Seconds=seconds(x.get('Q2')), Q3Seconds=seconds(x.get('Q3')))
                    else:
                        grid, finish = int(x['grid']), int(x['position'])
                        status = x['status']
                        completed = completed_status(status)
                        base.update(Grid=grid, FinishPosition=finish, Points=float(x['points']),
                                    Laps=int(x['laps']), Status=status, ClassifiedFinish=int(completed),
                                    PositionGain=grid - finish if grid > 0 and completed else None)
                    target.append(base)
        # Pit stops need a race round; do not presume a season-wide endpoint.
        for race in calendar:
            rnd = int(race['round'])
            rk = season * 100 + rnd
            for page_race in client.get(f'{season}/{rnd}/pitstops', 'RaceTable', 'Races'):
                for x in page_race['PitStops']:
                    # Constructor assignment is joined to the actual race result, not a career team.
                    pits.append(dict(RaceKey=rk, DriverKey=x['driverId'], Stop=int(x['stop']),
                                     Lap=int(x['lap']), DurationSeconds=seconds(x['duration']),
                                     TimeOfDay=x['time'], DataClass='PUBLIC_DERIVED'))
        for kind, label, target in [('driverstandings', 'DriverStandings', ds), ('constructorstandings', 'ConstructorStandings', cs)]:
            for standing in client.get(f'{season}/{kind}', 'StandingsTable', 'StandingsLists'):
                for x in standing[label]:
                    if kind == 'driverstandings':
                        key = person(x)
                        key_name = 'DriverKey'
                    else:
                        c = x['Constructor']
                        key, key_name = c['constructorId'], 'ConstructorKey'
                        constructors[key] = dict(ConstructorKey=key, Constructor=c['name'], Nationality=c['nationality'], DataClass='PUBLIC')
                    target.append(dict(Season=season, **{key_name: key}, Position=int(x['position']),
                                       Points=float(x['points']), Wins=int(x['wins']), DataClass='PUBLIC'))
    for season, rnd in CONFIG['sample_lap_races']:
        print('F1 sample laps', season, rnd, flush=True)
        for race in client.get(f'{season}/{rnd}/laps', 'RaceTable', 'Races'):
            for lap in race['Laps']:
                for x in lap['Timings']:
                    laps.append(dict(RaceKey=season * 100 + rnd, DriverKey=x['driverId'], Lap=int(lap['number']),
                                     Position=int(x['position']), LapSeconds=seconds(x['time']), DataClass='PUBLIC_DERIVED'))
    out = ROOT / 'data/processed/f1'
    result_df = pd.DataFrame(results).drop_duplicates(['RaceKey', 'DriverKey'])
    pit_df = pd.DataFrame(pits).drop_duplicates(['RaceKey', 'DriverKey', 'Stop'])
    pit_df = pit_df.merge(result_df[['RaceKey', 'DriverKey', 'ConstructorKey', 'Laps']], on=['RaceKey', 'DriverKey'], validate='many_to_one')
    pit_df['LapFraction'] = pit_df['Lap'] / pit_df['Laps']
    # This is a transparent analytical exclusion, not a claim about stationary stops.
    pit_df['TimingEligible'] = (pit_df['DurationSeconds'].between(10, 60)).astype(int)
    data = {'DimRace': pd.DataFrame(races.values()).sort_values('RaceKey'),
            'DimDriver': pd.DataFrame(drivers.values()).sort_values('DriverKey'),
            'DimConstructor': pd.DataFrame(constructors.values()).sort_values('ConstructorKey'),
            'DimCircuit': pd.DataFrame(circuits.values()).sort_values('CircuitKey'),
            'DimSeason': pd.DataFrame({'Season': CONFIG['f1_seasons'], 'DataClass': 'PUBLIC'}),
            'FactRaceResults': result_df, 'FactQualifying': pd.DataFrame(qualifying).drop_duplicates(['RaceKey', 'DriverKey']),
            'FactSprintResults': pd.DataFrame(sprints).drop_duplicates(['RaceKey', 'DriverKey']),
            'FactPitStops': pit_df, 'FactLaps': pd.DataFrame(laps).drop_duplicates(['RaceKey', 'DriverKey', 'Lap']),
            'FactDriverStandings': pd.DataFrame(ds), 'FactConstructorStandings': pd.DataFrame(cs)}
    date = pd.DataFrame({'Date': pd.date_range(CONFIG['commercial_start'], CONFIG['commercial_end'])})
    date['Year'] = date.Date.dt.year
    date['YearMonth'] = date.Date.dt.strftime('%Y-%m')
    date['MonthNumber'] = date.Date.dt.month
    date['Month'] = date.Date.dt.strftime('%b')
    date['Quarter'] = 'Q' + date.Date.dt.quarter.astype(str)
    date['WeekStart'] = (date.Date-pd.to_timedelta(date.Date.dt.dayofweek,unit='D')).dt.strftime('%Y-%m-%d')
    date['Date'] = date.Date.dt.strftime('%Y-%m-%d')
    date['DataClass'] = 'PUBLIC_DERIVED'
    data['DimDate'] = date
    lap_df = data['FactLaps'].merge(result_df[['RaceKey', 'DriverKey', 'ConstructorKey']], on=['RaceKey', 'DriverKey'], validate='many_to_one')
    data['FactLaps'] = lap_df
    for name, frame in data.items():
        if frame.empty:
            raise ValueError('Required public table missing: ' + name)
        save_csv(frame, out / (name + '.csv'))
    write_json({name: len(frame) for name, frame in data.items()}, ROOT / 'outputs/f1_counts.json')
    print('F1 normalization complete:', {k: len(v) for k, v in data.items()}, flush=True)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--offline', action='store_true')
    args = parser.parse_args()
    normalize(Client(args.offline))

if __name__ == '__main__':
    main()
