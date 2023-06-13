# Trading strategy for trading around FOMC announcements
# Three scenarios are distinguised: hawkish, medium and dovish
# when hawkish: short 1 year US Treasury bonds, long 2 year US treasury bonds
# 
# The following strategy was used as a starting point:
# https://quantpedia.com/strategies/trading-fomc-announcements-with-summary-of-economic-projections/
# An investor buys nearby E-mini S&P 500 index futures contracts five minutes before the FOMC statements including the release of SEP
# and holds the position for 55 minutes after the announcement.

#region imports
from AlgorithmImports import *
#endregion

class TradingFOMCAnnouncementsSummaryEconomicProjections(QCAlgorithm):

    def Initialize(self):
        self.SetStartDate(2023, 1, 1)
        self.SetCash(100000)
        
        # self.treasury_1yr = self.AddEquity("GBIL", Resolution.Minute).Symbol
        # GBIL: Goldman Sachs Access Treasury 0-1 Year ETF
        # https://www.gsam.com/content/gsam/us/en/individual/products/etf-fund-finder/goldman-sachs-access-treasury-0-1-year-etf.html
        # inception date: 09.06.16
        # self.symbol_1yr = self.AddEquity("IBTU", Resolution.Minute).Symbol# Use IBTU for 1 year treasury?
        # IBTU: The iShares $ Treasury Bond 0-1 yr until maturity UCITS ETF 
        # inception date 20/Feb/2019
        # https://www.ishares.com/uk/individual/en/products/307241/ishares-treasury-bond-0-1yr-ucits-etf?switchLocale=y&siteEntryPassthrough=true
        # self.treasury_2yr = self.AddEquity("SHY", Resolution.Minute).Symbol 
        # SHY: ETF US Treasury maturity date between 1 and 3 years
        # https://www.ishares.com/us/products/239452/ishares-13-year-treasury-bond-etf

        # Other equities / indicators: 
        self.spy = self.AddEquity("SPY", Resolution.Minute) # might be used as indicator
        # self.vix = self.AddData(CBOE, "VIX", Resolution.Minute).Symbol # VIX might be used as indicator
        # self.regional_banks = self.AddEquity("IAT", Resolution.Minute).Symbol # could short when hawkish
        # https://www.ishares.com/us/products/239521/ishares-us-regional-banks-etf
        # self.finance = self.AddEquity("XLF", Resolution.Minute).Symbol # long when hawkish / medium / dovish
        # self.gold = self.AddEquity("GLD", Resolution.Minute).Symbol # long when hawkish
        # self.vix_equity = self.AddEquity("VIIX", Resolution.Minute).Symbol 

        # Maybe change resolution to Second

        self.symbol = self.AddEquity("XLF", Resolution.Minute).Symbol

        self.SetBenchmark("SPY")
        
        csv_string_file = self.Download('https://data.quantpedia.com/backtesting_data/economic/fed_days.csv')
        # contains the dates of the FOMC announcements from 1990 - 2023 (without start time)
        self.dates = csv_string_file.split('\r\n')
        self.announcement_dates = [datetime.strptime(x, "%Y-%m-%d") for x in self.dates] 
        self.start_time_hour = 14 # TODO check timezone. Default time zone quantconnect is NY time zone? FOMC meeting start at 1400 correct?
        self.end_time_hour = 15
        self.end_time_min = 54
        self.time_liquidate_min = 55

        #self.signal =  # TODO need to know what signal it is 
        #self.signal_threshold =  # TODO need to test the signal threshold
        #self.percent_1yr = 0 # TODO need to test out what this is 
        #self.percent_2yr = - (1 - self.percent_1yr)
        
        # self.Schedule.On(self.DateRules.On(self.announcement_date), self.TimeRules.At(start_time_hour,0), self.Trade)
        self.Schedule.On(self.DateRules.On(self.announcement_dates), self.TimeRules.At(self.end_time_hour,self.time_liquidate_min ), self.Rebalance)
    
    def OnSecuritiesChanged(self, changes):
        for security in changes.AddedSecurities:
            security.SetLeverage(10)

    # def OnData(self, data: Slice):
    #     if not self.spy in data:
    #         return
    def OnData(self, data) -> None:
        if self.symbol in data and data[self.symbol]:
            #self.Log(f"data available")
            if self.Time.replace(minute=0, hour=0) in self.announcement_dates:
                self.Log(f"today is {self.Time} is a FED day")
                if self.Time.replace(minute=0, hour=self.start_time_hour) < self.Time < self.Time.replace(minute=self.end_time_min, hour=self.end_time_hour): 
                    if not self.Portfolio[self.symbol].IsShort:
                        self.SetHoldings(self.symbol, 1)
                        
                        #self.SetHoldings(self.symbol, 1)
                        #self.Log(f"the time is {self.Time} BUY")
                        #self.SetHoldings(self.treasury_1yr, self.percent_1yr)
                        #self.SetHoldings(self.treasury_2yr, - self.percent_2yr)  

    def Rebalance(self):
        if self.Portfolio[self.symbol].IsLong:
            self.Liquidate(self.symbol)
            self.Log(f"the time is {self.Time} rebalance liquidate")
