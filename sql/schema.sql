-- SQLite 3 analytical mart; generated from contracts.py and executed by transform.py.
PRAGMA foreign_keys=ON;

CREATE TABLE "f1_DimCircuit" (
  "CircuitKey" TEXT NOT NULL,
  "Circuit" TEXT NOT NULL,
  "Country" TEXT NOT NULL,
  "Locality" TEXT NOT NULL,
  "Latitude" REAL NOT NULL,
  "Longitude" REAL NOT NULL,
  "DataClass" TEXT NOT NULL,
  PRIMARY KEY ("CircuitKey"),
  CHECK (DataClass IN ('PUBLIC','PUBLIC_DERIVED'))
);

CREATE TABLE "f1_DimConstructor" (
  "ConstructorKey" TEXT NOT NULL,
  "Constructor" TEXT NOT NULL,
  "Nationality" TEXT NOT NULL,
  "DataClass" TEXT NOT NULL,
  PRIMARY KEY ("ConstructorKey"),
  CHECK (DataClass IN ('PUBLIC','PUBLIC_DERIVED'))
);

CREATE TABLE "f1_DimDate" (
  "Date" TEXT NOT NULL,
  "Year" INTEGER NOT NULL,
  "YearMonth" TEXT NOT NULL,
  "MonthNumber" INTEGER NOT NULL,
  "Month" TEXT NOT NULL,
  "Quarter" TEXT NOT NULL,
  "WeekStart" TEXT NOT NULL,
  "DataClass" TEXT NOT NULL,
  PRIMARY KEY ("Date"),
  CHECK (DataClass IN ('PUBLIC','PUBLIC_DERIVED'))
);

CREATE TABLE "f1_DimDriver" (
  "DriverKey" TEXT NOT NULL,
  "Driver" TEXT NOT NULL,
  "Nationality" TEXT NOT NULL,
  "DOB" TEXT NOT NULL,
  "DataClass" TEXT NOT NULL,
  PRIMARY KEY ("DriverKey"),
  CHECK (DataClass IN ('PUBLIC','PUBLIC_DERIVED'))
);

CREATE TABLE "f1_DimSeason" (
  "Season" INTEGER NOT NULL,
  "DataClass" TEXT NOT NULL,
  PRIMARY KEY ("Season"),
  CHECK (DataClass IN ('PUBLIC','PUBLIC_DERIVED'))
);

CREATE TABLE "fmcg_DimCategory" (
  "CategoryKey" INTEGER NOT NULL,
  "Category" TEXT NOT NULL,
  "DataClass" TEXT NOT NULL,
  PRIMARY KEY ("CategoryKey"),
  CHECK (DataClass IN ('SYNTHETIC'))
);

CREATE TABLE "fmcg_DimChannel" (
  "ChannelKey" INTEGER NOT NULL,
  "Channel" TEXT NOT NULL,
  "DataClass" TEXT NOT NULL,
  PRIMARY KEY ("ChannelKey"),
  CHECK (DataClass IN ('SYNTHETIC'))
);

CREATE TABLE "fmcg_DimCustomer" (
  "CustomerKey" INTEGER NOT NULL,
  "Customer" TEXT NOT NULL,
  "ChannelKey" INTEGER NOT NULL,
  "RegionKey" INTEGER NOT NULL,
  "EligibleStores" INTEGER NOT NULL,
  "DataClass" TEXT NOT NULL,
  PRIMARY KEY ("CustomerKey"),
  CHECK (DataClass IN ('SYNTHETIC'))
);

CREATE TABLE "fmcg_DimDate" (
  "Date" TEXT NOT NULL,
  "Year" INTEGER NOT NULL,
  "MonthNumber" INTEGER NOT NULL,
  "Month" TEXT NOT NULL,
  "YearMonth" TEXT NOT NULL,
  "Quarter" TEXT NOT NULL,
  "WeekStart" TEXT NOT NULL,
  "DataClass" TEXT NOT NULL,
  PRIMARY KEY ("Date"),
  CHECK (DataClass IN ('SYNTHETIC'))
);

CREATE TABLE "fmcg_DimProduct" (
  "ProductKey" INTEGER NOT NULL,
  "Product" TEXT NOT NULL,
  "Brand" TEXT NOT NULL,
  "CategoryKey" INTEGER NOT NULL,
  "Category" TEXT NOT NULL,
  "PackMl" INTEGER NOT NULL,
  "Innovation" INTEGER NOT NULL,
  "LaunchDate" TEXT NOT NULL,
  "RegularPrice" REAL NOT NULL,
  "UnitCost" REAL NOT NULL,
  "DataClass" TEXT NOT NULL,
  PRIMARY KEY ("ProductKey"),
  CHECK (DataClass IN ('SYNTHETIC'))
);

CREATE TABLE "fmcg_DimRegion" (
  "RegionKey" INTEGER NOT NULL,
  "Region" TEXT NOT NULL,
  "DataClass" TEXT NOT NULL,
  PRIMARY KEY ("RegionKey"),
  CHECK (DataClass IN ('SYNTHETIC'))
);

CREATE TABLE "f1_DimRace" (
  "RaceKey" INTEGER NOT NULL,
  "Season" INTEGER NOT NULL,
  "Round" INTEGER NOT NULL,
  "Race" TEXT NOT NULL,
  "CircuitKey" TEXT NOT NULL,
  "Date" TEXT NOT NULL,
  "DataClass" TEXT NOT NULL,
  PRIMARY KEY ("RaceKey"),
  FOREIGN KEY ("CircuitKey") REFERENCES "f1_DimCircuit"("CircuitKey"),
  FOREIGN KEY ("Season") REFERENCES "f1_DimSeason"("Season"),
  FOREIGN KEY ("Date") REFERENCES "f1_DimDate"("Date"),
  CHECK (DataClass IN ('PUBLIC','PUBLIC_DERIVED'))
);

CREATE TABLE "f1_FactConstructorStandings" (
  "Season" INTEGER NOT NULL,
  "ConstructorKey" TEXT NOT NULL,
  "Position" INTEGER NOT NULL,
  "Points" REAL NOT NULL,
  "Wins" INTEGER NOT NULL,
  "DataClass" TEXT NOT NULL,
  PRIMARY KEY ("Season", "ConstructorKey"),
  FOREIGN KEY ("Season") REFERENCES "f1_DimSeason"("Season"),
  FOREIGN KEY ("ConstructorKey") REFERENCES "f1_DimConstructor"("ConstructorKey"),
  CHECK (DataClass IN ('PUBLIC','PUBLIC_DERIVED')),
  CHECK ("Points" >= 0)
);

CREATE TABLE "f1_FactDriverStandings" (
  "Season" INTEGER NOT NULL,
  "DriverKey" TEXT NOT NULL,
  "Position" INTEGER NOT NULL,
  "Points" REAL NOT NULL,
  "Wins" INTEGER NOT NULL,
  "DataClass" TEXT NOT NULL,
  PRIMARY KEY ("Season", "DriverKey"),
  FOREIGN KEY ("Season") REFERENCES "f1_DimSeason"("Season"),
  FOREIGN KEY ("DriverKey") REFERENCES "f1_DimDriver"("DriverKey"),
  CHECK (DataClass IN ('PUBLIC','PUBLIC_DERIVED')),
  CHECK ("Points" >= 0)
);

CREATE TABLE "f1_FactLaps" (
  "RaceKey" INTEGER NOT NULL,
  "DriverKey" TEXT NOT NULL,
  "Lap" INTEGER NOT NULL,
  "Position" INTEGER NOT NULL,
  "LapSeconds" REAL NOT NULL,
  "DataClass" TEXT NOT NULL,
  "ConstructorKey" TEXT NOT NULL,
  PRIMARY KEY ("RaceKey", "DriverKey", "Lap"),
  FOREIGN KEY ("RaceKey") REFERENCES "f1_DimRace"("RaceKey"),
  FOREIGN KEY ("DriverKey") REFERENCES "f1_DimDriver"("DriverKey"),
  FOREIGN KEY ("ConstructorKey") REFERENCES "f1_DimConstructor"("ConstructorKey"),
  CHECK (DataClass IN ('PUBLIC','PUBLIC_DERIVED'))
);

CREATE TABLE "f1_FactPitStops" (
  "RaceKey" INTEGER NOT NULL,
  "DriverKey" TEXT NOT NULL,
  "Stop" INTEGER NOT NULL,
  "Lap" INTEGER NOT NULL,
  "DurationSeconds" REAL,
  "TimeOfDay" TEXT NOT NULL,
  "DataClass" TEXT NOT NULL,
  "ConstructorKey" TEXT NOT NULL,
  "Laps" INTEGER NOT NULL,
  "LapFraction" REAL NOT NULL,
  "TimingEligible" INTEGER NOT NULL,
  PRIMARY KEY ("RaceKey", "DriverKey", "Stop"),
  FOREIGN KEY ("RaceKey") REFERENCES "f1_DimRace"("RaceKey"),
  FOREIGN KEY ("DriverKey") REFERENCES "f1_DimDriver"("DriverKey"),
  FOREIGN KEY ("ConstructorKey") REFERENCES "f1_DimConstructor"("ConstructorKey"),
  CHECK (DataClass IN ('PUBLIC','PUBLIC_DERIVED'))
);

CREATE TABLE "f1_FactQualifying" (
  "RaceKey" INTEGER NOT NULL,
  "DriverKey" TEXT NOT NULL,
  "ConstructorKey" TEXT NOT NULL,
  "DataClass" TEXT NOT NULL,
  "QualifyingPosition" INTEGER NOT NULL,
  "Q1Seconds" REAL,
  "Q2Seconds" REAL,
  "Q3Seconds" REAL,
  PRIMARY KEY ("RaceKey", "DriverKey"),
  FOREIGN KEY ("RaceKey") REFERENCES "f1_DimRace"("RaceKey"),
  FOREIGN KEY ("DriverKey") REFERENCES "f1_DimDriver"("DriverKey"),
  FOREIGN KEY ("ConstructorKey") REFERENCES "f1_DimConstructor"("ConstructorKey"),
  CHECK (DataClass IN ('PUBLIC','PUBLIC_DERIVED'))
);

CREATE TABLE "f1_FactRaceResults" (
  "RaceKey" INTEGER NOT NULL,
  "DriverKey" TEXT NOT NULL,
  "ConstructorKey" TEXT NOT NULL,
  "DataClass" TEXT NOT NULL,
  "Grid" INTEGER NOT NULL,
  "FinishPosition" INTEGER NOT NULL,
  "Points" REAL NOT NULL,
  "Laps" INTEGER NOT NULL,
  "Status" TEXT NOT NULL,
  "ClassifiedFinish" INTEGER NOT NULL,
  "PositionGain" REAL,
  PRIMARY KEY ("RaceKey", "DriverKey"),
  FOREIGN KEY ("RaceKey") REFERENCES "f1_DimRace"("RaceKey"),
  FOREIGN KEY ("DriverKey") REFERENCES "f1_DimDriver"("DriverKey"),
  FOREIGN KEY ("ConstructorKey") REFERENCES "f1_DimConstructor"("ConstructorKey"),
  CHECK (DataClass IN ('PUBLIC','PUBLIC_DERIVED')),
  CHECK ("Points" >= 0)
);

CREATE TABLE "f1_FactSprintResults" (
  "RaceKey" INTEGER NOT NULL,
  "DriverKey" TEXT NOT NULL,
  "ConstructorKey" TEXT NOT NULL,
  "DataClass" TEXT NOT NULL,
  "Grid" INTEGER NOT NULL,
  "FinishPosition" INTEGER NOT NULL,
  "Points" REAL NOT NULL,
  "Laps" INTEGER NOT NULL,
  "Status" TEXT NOT NULL,
  "ClassifiedFinish" INTEGER NOT NULL,
  "PositionGain" REAL,
  PRIMARY KEY ("RaceKey", "DriverKey"),
  FOREIGN KEY ("RaceKey") REFERENCES "f1_DimRace"("RaceKey"),
  FOREIGN KEY ("DriverKey") REFERENCES "f1_DimDriver"("DriverKey"),
  FOREIGN KEY ("ConstructorKey") REFERENCES "f1_DimConstructor"("ConstructorKey"),
  CHECK (DataClass IN ('PUBLIC','PUBLIC_DERIVED')),
  CHECK ("Points" >= 0)
);

CREATE TABLE "fmcg_FactDistribution" (
  "Date" TEXT NOT NULL,
  "ProductKey" INTEGER NOT NULL,
  "CategoryKey" INTEGER NOT NULL,
  "CustomerKey" INTEGER NOT NULL,
  "ChannelKey" INTEGER NOT NULL,
  "RegionKey" INTEGER NOT NULL,
  "DataClass" TEXT NOT NULL,
  "ActiveStoreDays" INTEGER NOT NULL,
  "EligibleStoreDays" INTEGER NOT NULL,
  PRIMARY KEY ("Date", "ProductKey", "CustomerKey"),
  FOREIGN KEY ("Date") REFERENCES "fmcg_DimDate"("Date"),
  FOREIGN KEY ("CategoryKey") REFERENCES "fmcg_DimCategory"("CategoryKey"),
  FOREIGN KEY ("ChannelKey") REFERENCES "fmcg_DimChannel"("ChannelKey"),
  FOREIGN KEY ("RegionKey") REFERENCES "fmcg_DimRegion"("RegionKey"),
  FOREIGN KEY ("ProductKey") REFERENCES "fmcg_DimProduct"("ProductKey"),
  FOREIGN KEY ("CustomerKey") REFERENCES "fmcg_DimCustomer"("CustomerKey"),
  CHECK (DataClass IN ('SYNTHETIC'))
);

CREATE TABLE "fmcg_FactInnovationPanel" (
  "ProductKey" INTEGER NOT NULL,
  "CategoryKey" INTEGER NOT NULL,
  "CustomerKey" INTEGER NOT NULL,
  "ChannelKey" INTEGER NOT NULL,
  "RegionKey" INTEGER NOT NULL,
  "Trials" INTEGER NOT NULL,
  "RepeatWithin28d" INTEGER NOT NULL,
  "Date" TEXT NOT NULL,
  "DataClass" TEXT NOT NULL,
  PRIMARY KEY ("Date", "ProductKey", "CustomerKey"),
  FOREIGN KEY ("Date") REFERENCES "fmcg_DimDate"("Date"),
  FOREIGN KEY ("CategoryKey") REFERENCES "fmcg_DimCategory"("CategoryKey"),
  FOREIGN KEY ("ChannelKey") REFERENCES "fmcg_DimChannel"("ChannelKey"),
  FOREIGN KEY ("RegionKey") REFERENCES "fmcg_DimRegion"("RegionKey"),
  FOREIGN KEY ("ProductKey") REFERENCES "fmcg_DimProduct"("ProductKey"),
  FOREIGN KEY ("CustomerKey") REFERENCES "fmcg_DimCustomer"("CustomerKey"),
  CHECK (DataClass IN ('SYNTHETIC')),
  CHECK ("Trials" >= 0),
  CHECK ("RepeatWithin28d" >= 0)
);

CREATE TABLE "fmcg_FactMarket" (
  "Date" TEXT NOT NULL,
  "CategoryKey" INTEGER NOT NULL,
  "ChannelKey" INTEGER NOT NULL,
  "RegionKey" INTEGER NOT NULL,
  "PortfolioRevenue" REAL NOT NULL,
  "CompetitorRevenue" REAL NOT NULL,
  "MarketRevenue" REAL NOT NULL,
  "DataClass" TEXT NOT NULL,
  PRIMARY KEY ("Date", "CategoryKey", "ChannelKey", "RegionKey"),
  FOREIGN KEY ("Date") REFERENCES "fmcg_DimDate"("Date"),
  FOREIGN KEY ("CategoryKey") REFERENCES "fmcg_DimCategory"("CategoryKey"),
  FOREIGN KEY ("ChannelKey") REFERENCES "fmcg_DimChannel"("ChannelKey"),
  FOREIGN KEY ("RegionKey") REFERENCES "fmcg_DimRegion"("RegionKey"),
  CHECK (DataClass IN ('SYNTHETIC')),
  CHECK ("MarketRevenue" >= 0)
);

CREATE TABLE "fmcg_FactPromotion" (
  "Date" TEXT NOT NULL,
  "ProductKey" INTEGER NOT NULL,
  "CategoryKey" INTEGER NOT NULL,
  "CustomerKey" INTEGER NOT NULL,
  "ChannelKey" INTEGER NOT NULL,
  "RegionKey" INTEGER NOT NULL,
  "DataClass" TEXT NOT NULL,
  "CampaignKey" TEXT NOT NULL,
  "ActualUnits" INTEGER NOT NULL,
  "BaselineUnits" INTEGER NOT NULL,
  "ActualRevenue" REAL NOT NULL,
  "BaselineRevenue" REAL NOT NULL,
  "ActualGP" REAL NOT NULL,
  "BaselineGP" REAL NOT NULL,
  "TradeSpend" REAL NOT NULL,
  "DiscountDepth" REAL NOT NULL,
  "IncrementalUnits" INTEGER NOT NULL,
  "NetIncrementalProfit" REAL NOT NULL,
  PRIMARY KEY ("Date", "ProductKey", "CustomerKey"),
  FOREIGN KEY ("Date") REFERENCES "fmcg_DimDate"("Date"),
  FOREIGN KEY ("CategoryKey") REFERENCES "fmcg_DimCategory"("CategoryKey"),
  FOREIGN KEY ("ChannelKey") REFERENCES "fmcg_DimChannel"("ChannelKey"),
  FOREIGN KEY ("RegionKey") REFERENCES "fmcg_DimRegion"("RegionKey"),
  FOREIGN KEY ("ProductKey") REFERENCES "fmcg_DimProduct"("ProductKey"),
  FOREIGN KEY ("CustomerKey") REFERENCES "fmcg_DimCustomer"("CustomerKey"),
  CHECK (DataClass IN ('SYNTHETIC'))
);

CREATE TABLE "fmcg_FactSales" (
  "Date" TEXT NOT NULL,
  "ProductKey" INTEGER NOT NULL,
  "CategoryKey" INTEGER NOT NULL,
  "CustomerKey" INTEGER NOT NULL,
  "ChannelKey" INTEGER NOT NULL,
  "RegionKey" INTEGER NOT NULL,
  "DataClass" TEXT NOT NULL,
  "Units" INTEGER NOT NULL,
  "VolumeLitres" REAL NOT NULL,
  "NetPrice" REAL NOT NULL,
  "UnitCost" REAL NOT NULL,
  "Revenue" REAL NOT NULL,
  "COGS" REAL NOT NULL,
  "GrossProfit" REAL NOT NULL,
  "PromotionFlag" INTEGER NOT NULL,
  "DiscountDepth" REAL NOT NULL,
  "TradeSpend" REAL NOT NULL,
  "Innovation" INTEGER NOT NULL,
  PRIMARY KEY ("Date", "ProductKey", "CustomerKey"),
  FOREIGN KEY ("Date") REFERENCES "fmcg_DimDate"("Date"),
  FOREIGN KEY ("CategoryKey") REFERENCES "fmcg_DimCategory"("CategoryKey"),
  FOREIGN KEY ("ChannelKey") REFERENCES "fmcg_DimChannel"("ChannelKey"),
  FOREIGN KEY ("RegionKey") REFERENCES "fmcg_DimRegion"("RegionKey"),
  FOREIGN KEY ("ProductKey") REFERENCES "fmcg_DimProduct"("ProductKey"),
  FOREIGN KEY ("CustomerKey") REFERENCES "fmcg_DimCustomer"("CustomerKey"),
  CHECK (DataClass IN ('SYNTHETIC')),
  CHECK ("Revenue" >= 0),
  CHECK ("COGS" >= 0),
  CHECK ("Units" >= 0)
);

CREATE TABLE "fmcg_FactTargets" (
  "Date" TEXT NOT NULL,
  "ProductKey" INTEGER NOT NULL,
  "CategoryKey" INTEGER NOT NULL,
  "CustomerKey" INTEGER NOT NULL,
  "ChannelKey" INTEGER NOT NULL,
  "RegionKey" INTEGER NOT NULL,
  "DataClass" TEXT NOT NULL,
  "TargetUnits" INTEGER NOT NULL,
  "TargetRevenue" REAL NOT NULL,
  PRIMARY KEY ("Date", "ProductKey", "CustomerKey"),
  FOREIGN KEY ("Date") REFERENCES "fmcg_DimDate"("Date"),
  FOREIGN KEY ("CategoryKey") REFERENCES "fmcg_DimCategory"("CategoryKey"),
  FOREIGN KEY ("ChannelKey") REFERENCES "fmcg_DimChannel"("ChannelKey"),
  FOREIGN KEY ("RegionKey") REFERENCES "fmcg_DimRegion"("RegionKey"),
  FOREIGN KEY ("ProductKey") REFERENCES "fmcg_DimProduct"("ProductKey"),
  FOREIGN KEY ("CustomerKey") REFERENCES "fmcg_DimCustomer"("CustomerKey"),
  CHECK (DataClass IN ('SYNTHETIC')),
  CHECK ("TargetRevenue" >= 0)
);

CREATE TABLE "public_PublicContext" (
  "Metric" TEXT NOT NULL,
  "Value" REAL NOT NULL,
  "Basis" TEXT NOT NULL,
  "Scope" TEXT NOT NULL,
  "SourceURL" TEXT NOT NULL,
  "PublishedDate" TEXT NOT NULL,
  "DataClass" TEXT NOT NULL,
  PRIMARY KEY ("Metric"),
  CHECK (DataClass IN ('PUBLIC','PUBLIC_DERIVED'))
);
