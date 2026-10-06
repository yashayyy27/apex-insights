"""Explicit table grains and conformed relationships; reused by tests and models."""
CONTRACTS = {}
for domain, dimensions in {
    'fmcg': {'DimDate': 'Date', 'DimProduct': 'ProductKey', 'DimCustomer': 'CustomerKey', 'DimCategory': 'CategoryKey', 'DimChannel': 'ChannelKey', 'DimRegion': 'RegionKey'},
    'f1': {'DimDate': 'Date', 'DimRace': 'RaceKey', 'DimCircuit': 'CircuitKey', 'DimDriver': 'DriverKey', 'DimConstructor': 'ConstructorKey', 'DimSeason': 'Season'},
    'public': {'PublicContext': 'Metric'},
}.items():
    for table, key in dimensions.items():
        CONTRACTS[(domain, table)] = {'key': [key], 'nullable': []}
for table in ['FactSales', 'FactDistribution', 'FactTargets', 'FactPromotion']:
    CONTRACTS[('fmcg', table)] = {'key': ['Date', 'ProductKey', 'CustomerKey'], 'nullable': []}
CONTRACTS[('fmcg', 'FactMarket')] = {'key': ['Date', 'CategoryKey', 'ChannelKey', 'RegionKey'], 'nullable': []}
CONTRACTS[('fmcg', 'FactInnovationPanel')] = {'key': ['Date', 'ProductKey', 'CustomerKey'], 'nullable': []}
for table in ['FactRaceResults', 'FactSprintResults', 'FactQualifying']:
    CONTRACTS[('f1', table)] = {'key': ['RaceKey', 'DriverKey'], 'nullable': ['PositionGain'] if table != 'FactQualifying' else ['Q1Seconds', 'Q2Seconds', 'Q3Seconds']}
CONTRACTS[('f1', 'FactPitStops')] = {'key': ['RaceKey', 'DriverKey', 'Stop'], 'nullable': ['DurationSeconds']}
CONTRACTS[('f1', 'FactLaps')] = {'key': ['RaceKey', 'DriverKey', 'Lap'], 'nullable': []}
CONTRACTS[('f1', 'FactDriverStandings')] = {'key': ['Season', 'DriverKey'], 'nullable': []}
CONTRACTS[('f1', 'FactConstructorStandings')] = {'key': ['Season', 'ConstructorKey'], 'nullable': []}

def relationships(domain):
    """Return fromTable, fromColumn, toTable, toColumn. Single direction."""
    links = []
    if domain == 'fmcg':
        for (dom, table), contract in CONTRACTS.items():
            if dom != domain or not table.startswith('Fact'):
                continue
            dims = ['Date', 'Category', 'Channel', 'Region']
            if table != 'FactMarket':
                dims += ['Product', 'Customer']
            for dim in dims:
                key = 'Date' if dim == 'Date' else dim + 'Key'
                links.append((table, key, 'Dim' + dim, key))
    if domain == 'f1':
        links += [('DimRace', 'CircuitKey', 'DimCircuit', 'CircuitKey'), ('DimRace', 'Season', 'DimSeason', 'Season'), ('DimRace', 'Date', 'DimDate', 'Date')]
        for fact in ['FactRaceResults', 'FactQualifying', 'FactSprintResults', 'FactPitStops', 'FactLaps']:
            for dim in ['Race', 'Driver', 'Constructor']:
                links.append((fact, dim + 'Key', 'Dim' + dim, dim + 'Key'))
        links += [('FactDriverStandings', 'Season', 'DimSeason', 'Season'), ('FactDriverStandings', 'DriverKey', 'DimDriver', 'DriverKey'),
                  ('FactConstructorStandings', 'Season', 'DimSeason', 'Season'), ('FactConstructorStandings', 'ConstructorKey', 'DimConstructor', 'ConstructorKey')]
    return links
