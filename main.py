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
        
        self.symbol = self.AddEquity("SPY", Resolution.Minute).Symbol

        # csv_string_file = self.Download('data.quantpedia.com/backtesting_data/economic/fed_summary_economic_projections.csv')
        # dates = csv_string_file.split('\r\n')
        # dates = [datetime.strptime(x, "%Y-%m-%d") for x in dates]
        
        self.liquidate_next_day = True
        
        self.Schedule.On(self.DateRules.On(dates), self.TimeRules.BeforeMarketClose(self.symbol, 1), self.Trade)
        self.Schedule.On(self.DateRules.EveryDay(self.symbol), self.TimeRules.BeforeMarketClose(self.symbol, 1), self.Rebalance)
    
    def Trade(self):
        if not self.Portfolio[self.symbol].IsLong:
            self.SetHoldings(self.symbol, 1)
            self.liquidate_next_day = True        

    def Rebalance(self):
        if self.liquidate_next_day:
            self.liquidate_next_day = False
            return
        
        if self.Portfolio[self.symbol].IsLong:
            self.Liquidate(self.symbol)