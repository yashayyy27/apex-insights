"""Fictional beverage portfolio; never CCEP operational data.

Daily product/customer grain, AUD ex GST. Generator parameters create
plausible business tensions; discoveries are conditional on these assumptions.
Targets are set from an independent pre-period demand expectation. Promotional
baseline is a known simulated counterfactual, not a fitted causal estimate.
"""
import numpy as np
import pandas as pd
from common import ROOT, CONFIG, save_csv, write_json

def main(seed=None, destination=None):
    seed = CONFIG['seed'] if seed is None else seed
    rng = np.random.default_rng(seed)
    out = ROOT / 'data/synthetic/fmcg' if destination is None else destination
    cats = ['Sparkling', 'Energy', 'Water', 'Sports', 'Coffee']
    brands = [['Arc Cola', 'Citrus Lane'], ['Volt Avenue', 'Night Current'], ['Clear Ridge', 'Still Harbour'],
              ['Stride Works', 'Flow Sprint'], ['Dawn Roast', 'Urban Bean']]
    counts, regular, costs, velocity = [6, 6, 4, 4, 4], [3.1, 4.2, 2.3, 3.4, 4.7], [1.7, 2.0, 1.4, 1.9, 3.1], [5.2, 3.8, 6.1, 3.1, 1.9]
    products = []
    for ci, count in enumerate(counts):
        for j in range(count):
            pk = len(products) + 1
            innovation = pk in [12, 24]
            launch = '2024-03-01' if pk == 12 else '2024-07-01' if pk == 24 else '2022-01-01'
            ml = [330, 500, 600, 1000][j % 4]
            products.append(dict(ProductKey=pk, Product=f'{brands[ci][j % 2]} {ml}ml V{j + 1}',
                                 Brand=brands[ci][j % 2], CategoryKey=ci + 1, Category=cats[ci], PackMl=ml,
                                 Innovation=int(innovation), LaunchDate=launch,
                                 RegularPrice=round(regular[ci] * ml / 500 * (1 + 0.04 * j), 2),
                                 UnitCost=round(costs[ci] * ml / 500, 2), BaseVelocity=velocity[ci] * (1 - j * .07),
                                 DataClass='SYNTHETIC'))
    product = pd.DataFrame(products)
    channels = pd.DataFrame({'ChannelKey': range(1, 6), 'Channel': ['Grocery', 'Convenience', 'Petrol', 'Hospitality', 'Independent retail'], 'DataClass': 'SYNTHETIC'})
    regions = pd.DataFrame({'RegionKey': range(1, 4), 'Region': ['NSW', 'VIC', 'QLD'], 'DataClass': 'SYNTHETIC'})
    customer = pd.DataFrame([dict(CustomerKey=(c - 1) * 3 + r, Customer=f'Fictional Account {c:02d}-{r}',
                                   ChannelKey=c, RegionKey=r, EligibleStores=[180, 80, 65, 45, 90][c - 1], DataClass='SYNTHETIC')
                             for c in range(1, 6) for r in range(1, 4)])
    date = pd.DataFrame({'Date': pd.date_range(CONFIG['commercial_start'], CONFIG['commercial_end'], freq='D')})
    date['Year'] = date.Date.dt.year
    date['MonthNumber'] = date.Date.dt.month
    date['Month'] = date.Date.dt.strftime('%b')
    date['YearMonth'] = date.Date.dt.strftime('%Y-%m')
    date['Quarter'] = 'Q' + date.Date.dt.quarter.astype(str)
    date['WeekStart'] = (date.Date - pd.to_timedelta(date.Date.dt.dayofweek, unit='D')).dt.strftime('%Y-%m-%d')
    date['DataClass'] = 'SYNTHETIC'
    fact = date[['Date', 'Year', 'MonthNumber']].merge(product, how='cross').merge(customer.drop(columns='DataClass'), how='cross')
    fact = fact[fact.Date.ge(pd.to_datetime(fact.LaunchDate))].reset_index(drop=True)
    n = len(fact)
    day = fact.Date.dt.dayofyear.to_numpy()
    year2 = (fact.Year == 2024).to_numpy()
    category = fact.CategoryKey.to_numpy() - 1
    seasonal = 1 + 0.16 * np.cos(2 * np.pi * (day - 20) / 365.25)
    growth = np.array([.015, .16, .03, .075, -.10])[category]
    channel_velocity = np.array([1.0, .78, .91, .55, .66])[fact.ChannelKey.to_numpy() - 1]
    regional = np.array([1.04, .97, 1.00])[fact.RegionKey.to_numpy() - 1]
    opportunity = (fact.CategoryKey.eq(2) & fact.ChannelKey.eq(2)).to_numpy()
    launch_age = (fact.Date - pd.to_datetime(fact.LaunchDate)).dt.days.to_numpy()
    base_distribution = .72 - (fact.ProductKey.to_numpy() % 6) * .055
    base_distribution -= opportunity * .20
    base_distribution -= (fact.CategoryKey.eq(5) & year2).to_numpy() * .07
    launch_ramp = np.where(fact.Innovation.eq(1), .15 + .85 * (1 - np.exp(-launch_age / 100)), 1)
    distribution = np.clip(base_distribution * launch_ramp + rng.normal(0, .025, n), .03, .96)
    active = np.maximum(1, np.rint(distribution * fact.EligibleStores)).astype(int)
    expected = fact.BaseVelocity.to_numpy() * channel_velocity * regional * seasonal * (1 + growth * year2) * active
    expected *= np.where(fact.Innovation.eq(1), .72 + .28 * (1 - np.exp(-launch_age / 50)), 1)
    # Every eighth week has a seven-day campaign, staggered by SKU/account.
    week = ((fact.Date - pd.Timestamp(CONFIG['commercial_start'])).dt.days // 7).to_numpy()
    promoted = ((week + fact.ProductKey.to_numpy() + fact.CustomerKey.to_numpy()) % 8 == 0)
    discount = np.where(promoted, .12 + .06 * (fact.ProductKey.to_numpy() % 4), 0)
    inflation = 1 + .035 * year2
    listprice = np.round(fact.RegularPrice.to_numpy() * inflation * np.array([1, 1.16, 1.12, .92, 1.03])[fact.ChannelKey.to_numpy() - 1], 2)
    cost = np.round(fact.UnitCost.to_numpy() * (1 + .055 * year2), 2)
    elasticity = np.array([1.8, 2.4, 1.5, 2.1, .8])[category]
    # A multiplicative noise shock applies to both potential outcomes.
    baseline = np.maximum(1, np.rint(expected * rng.lognormal(-.0128, .16, n))).astype(int)
    units = np.rint(baseline * (1 + elasticity * discount)).astype(int)
    netprice = np.round(listprice * (1 - discount), 2)
    revenue = np.round(units * netprice, 2)
    cogs = np.round(units * cost, 2)
    spend = np.where(promoted, np.round(active * .22 + units * .025, 2), 0)
    common = fact[['Date', 'ProductKey', 'CategoryKey', 'CustomerKey', 'ChannelKey', 'RegionKey']].copy()
    common['Date'] = common.Date.dt.strftime('%Y-%m-%d')
    common['DataClass'] = 'SYNTHETIC'
    sale = common.assign(Units=units, VolumeLitres=units * fact.PackMl / 1000, NetPrice=netprice, UnitCost=cost,
                         Revenue=revenue, COGS=cogs, GrossProfit=np.round(revenue - cogs, 2),
                         PromotionFlag=promoted.astype(int), DiscountDepth=discount, TradeSpend=spend,
                         Innovation=fact.Innovation.to_numpy())
    dist = common.assign(ActiveStoreDays=active, EligibleStoreDays=fact.EligibleStores.to_numpy())
    # Target assumes fixed baseline distribution and +6% planned demand in year 2.
    planned_active = np.rint(np.clip(.72 - (fact.ProductKey.to_numpy() % 6) * .055, .1, .95) * launch_ramp * fact.EligibleStores)
    target_units = np.rint(fact.BaseVelocity * channel_velocity * regional * seasonal * planned_active * (1 + .06 * year2)).astype(int)
    target = common.assign(TargetUnits=target_units, TargetRevenue=np.round(target_units * listprice * .98, 2))
    promo = common.loc[promoted].copy()
    promo['CampaignKey'] = (fact.loc[promoted, 'ProductKey'].astype(str) + '-' + fact.loc[promoted, 'CustomerKey'].astype(str) + '-' + pd.Series(week[promoted], index=promo.index).astype(str))
    for name, values in {'ActualUnits': units, 'BaselineUnits': baseline, 'ActualRevenue': revenue,
                          'BaselineRevenue': np.round(baseline * listprice, 2),
                          'ActualGP': np.round(revenue - cogs, 2), 'BaselineGP': np.round(baseline * (listprice - cost), 2),
                          'TradeSpend': spend, 'DiscountDepth': discount}.items():
        promo[name] = np.asarray(values)[promoted]
    promo['IncrementalUnits'] = promo.ActualUnits - promo.BaselineUnits
    promo['NetIncrementalProfit'] = np.round(promo.ActualGP - promo.BaselineGP - promo.TradeSpend, 2)
    # Synthetic competitor dollars generated separately at category/channel/region/day.
    group = ['Date', 'CategoryKey', 'ChannelKey', 'RegionKey']
    market = sale.groupby(group, as_index=False).agg(PortfolioRevenue=('Revenue', 'sum'))
    competitor_scale = np.array([2.6, 3.8, 5.2, 4.1, 6.8])[market.CategoryKey.to_numpy() - 1]
    market['CompetitorRevenue'] = np.round(market.PortfolioRevenue * competitor_scale * rng.lognormal(0, .045, len(market)), 2)
    market['MarketRevenue'] = np.round(market.PortfolioRevenue + market.CompetitorRevenue, 2)
    market['DataClass'] = 'SYNTHETIC'
    panel = sale[sale.Innovation.eq(1)].merge(product[['ProductKey', 'LaunchDate']], on='ProductKey', validate='many_to_one')
    panel['WeekStart'] = pd.to_datetime(panel.Date) - pd.to_timedelta(pd.to_datetime(panel.Date).dt.dayofweek, unit='D')
    panel = panel.groupby(['WeekStart', 'ProductKey', 'CategoryKey', 'CustomerKey', 'ChannelKey', 'RegionKey'], as_index=False).agg(Units=('Units', 'sum'))
    panel = panel[panel.WeekStart + pd.Timedelta(days=34) <= pd.Timestamp(CONFIG['commercial_end'])].copy()
    panel['Trials'] = np.maximum(1, np.rint(panel.Units * .015)).astype(int)
    repeat_prob = np.where(panel.ProductKey.eq(12), .39, .21)
    panel['RepeatWithin28d'] = rng.binomial(panel.Trials.to_numpy(), repeat_prob)
    panel['Date'] = panel.WeekStart.dt.strftime('%Y-%m-%d')
    panel['DataClass'] = 'SYNTHETIC'
    panel = panel.drop(columns=['WeekStart', 'Units'])
    product = product.drop(columns='BaseVelocity')
    date['Date'] = date.Date.dt.strftime('%Y-%m-%d')
    data = {'DimDate': date, 'DimProduct': product, 'DimCategory': pd.DataFrame({'CategoryKey': range(1, 6), 'Category': cats, 'DataClass': 'SYNTHETIC'}),
            'DimCustomer': customer, 'DimChannel': channels, 'DimRegion': regions, 'FactSales': sale,
            'FactDistribution': dist, 'FactTargets': target, 'FactPromotion': promo, 'FactMarket': market, 'FactInnovationPanel': panel}
    for name, frame in data.items():
        save_csv(frame, out / (name + '.csv'))
    write_json({'seed': seed, 'grain': 'Daily SKU/customer unless documented otherwise', 'currency': 'AUD ex GST',
                'rows': {name: len(frame) for name, frame in data.items()},
                'all_brands': 'FICTIONAL', 'all_rows': 'SYNTHETIC',
                'assumptions': {'category_annual_volume_change': dict(zip(cats, [.015, .16, .03, .075, -.10])),
                                'price_inflation': .035, 'cost_inflation': .055, 'year2_target_growth': .06,
                                'baseline': 'Shared-shock generator counterfactual, excludes promotion lift',
                                'no_causal_inference': True}}, ROOT / 'data/synthetic/generation_manifest.json')
    print('Synthetic generation:', {name: len(frame) for name, frame in data.items()})

if __name__ == '__main__':
    main()
