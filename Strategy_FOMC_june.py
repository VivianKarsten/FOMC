#region imports
from AlgorithmImports import *
#endregion

class TradingFOMCAnnouncementsSummaryEconomicProjections(QCAlgorithm):

    def Initialize(self):
        self.SetStartDate(2023, 1, 1)
        self.SetCash(100000)
        
        
        # Other equities / indicators: 
        self.spy = self.AddEquity("SPY", Resolution.Minute) # might be used as indicator
        self.vix = self.AddIndex("VIX", Resolution.Minute).Symbol # VIX used as indicator
        self.regional_banks = self.AddEquity("KRE", Resolution.Minute).Symbol 
        self.finance = self.AddEquity("XLF", Resolution.Minute).Symbol
        self.gbpusd = self.AddForex("GBPUSD").Symbol
        self.jpm = self.AddEquity("JPM", Resolution.Minute).Symbol

        self.SetBenchmark("SPY")

        
        csv_string_file = self.Download('https://data.quantpedia.com/backtesting_data/economic/fed_days.csv')
        # contains the dates of the FOMC announcements from 1990 - 2023 (without start time)
        self.dates = csv_string_file.split('\r\n')
        self.announcement_dates = [datetime.strptime(x, "%Y-%m-%d") for x in self.dates] 
        self.start_time_hour = 14 # TODO check timezone. Default time zone quantconnect is NY time zone? FOMC meeting start at 1400 correct?
        self.end_time_hour = 15
        self.end_time_min = 54
        self.time_liquidate_min = 55

        self.signalflag = 0

        
        # self.Schedule.On(self.DateRules.On(self.announcement_date), self.TimeRules.At(start_time_hour,0), self.Trade)
        self.Schedule.On(self.DateRules.On(self.announcement_dates), self.TimeRules.At(self.end_time_hour,self.time_liquidate_min ), self.Rebalance)
    
    def OnSecuritiesChanged(self, changes):
        for security in changes.AddedSecurities:
            security.SetLeverage(10)

    def OnData(self, data) -> None:
        if self.vix in data and data[self.vix]:
            #self.Log(f"data available")
            if self.Time.replace(minute=0, hour=0) in self.announcement_dates:
                self.Log(f"today is {self.Time} is a FED day")
                if self.Time.replace(minute=0, hour=self.start_time_hour) < self.Time < self.Time.replace(minute=self.end_time_min, hour=self.end_time_hour): 

                    if data[self.vix].Close > 16:
                        if not self.signalflag == 1:
                            self.signalflag = 1
                            self.Rebalance()

                    elif 14.75 < data[self.vix].Close <= 16:
                        if not self.signalflag == 0:
                            self.signalflag = 0
                            self.Rebalance()

                    elif data[self.vix].Close <= 14.75:
                        if not self.signalflag == -1:
                            self.signalflag = -1
                            self.Rebalance()
                         

    def Rebalance(self):
        order_ids = self.Liquidate()
        if self.signalflag == 1:
            self.SetHoldings(self.finance, -1)
            self.SetHoldings(self.gbpusd, 2)
        elif self.signalflag == 0:
            self.SetHoldings(self.regional_banks, -1.3)
            self.SetHoldings(self.jpm, 1.7)

        elif self.signalflag == -1:
            self.SetHoldings(self.regional_banks, 1)
