# https://quantpedia.com/strategies/trading-fomc-announcements-with-summary-of-economic-projections/
#
# An investor buys nearby E-mini S&P 500 index futures contracts five minutes before the FOMC statements including the release of SEP
# and holds the position for 55 minutes after the announcement.

#region imports
from AlgorithmImports import *
#endregion

class TradingFOMCAnnouncementsSummaryEconomicProjections(QCAlgorithm):

    def Initialize(self):
        self.SetStartDate(2007, 1, 1)
        self.SetCash(100000)
        
        self.symbol_2yr = self.AddEquity("SPY", Resolution.Minute).Symbol # TODO work out which symbol should be put here for 2 year treasury  
        self.symbol_1yr = self.AddEquity("SPY", Resolution.Minute).Symbol# TODO work out which symbol should be put here for 1 year treasury

        self.liquidate_at_the_end = True
        
        announcement_time = datetime.strptime("2023-06-14-", "%Y-%m-%d") # TODO work out what should be put here - considering the timezone as well

        self.signal = "" # TODO need to know what signal it is 
        self.signal_threshold = 0 # TODO need to test the signal threshold
        self.percent_1yr = 0 # TODO need to test out what this is 
        self.percent_2yr = - (1 - self.percent_1yr)
        
        self.Schedule.On(self.DateRules.On(announcement_time), self.TimeRules.BeforeMarketClose(self.symbol, 1), self.Trade)
        self.Schedule.On(self.DateRules.EveryDay(self.symbol), self.TimeRules.BeforeMarketClose(self.symbol, 1), self.Rebalance)
    
    def Trade(self):
        self.SetHoldings(self.symbol_1yr, self.percent_1yr)
        self.SetHoldings(self.symbol, - self.percent_2yr)
        self.liquidate_at_the_end = True      

    def Rebalance(self):
        if self.liquidate_next_day:
            self.liquidate_next_day = False
            return
        
        if self.Portfolio[self.symbol].IsLong:
            self.Liquidate(self.symbol)