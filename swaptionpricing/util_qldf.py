# -*- coding: utf-8 -*-
import QuantLib as ql
import pandas as pd

class util_qldf:
    def __init__(self):
        self.dir_name = None
        self.file_name = None

    def set_path(self, dir_name, file_name):
        self.dir_name = dir_name + ('' if dir_name[len(dir_name)-1] == '' else '/')
        self.file_name = file_name
        self.full_name = self.dir_name + self.file_name

    def load_df(self, index_col=None, dc=ql.Actual365Fixed()):
        self.dat_raw = pd.read_csv(self.full_name, index_col=index_col)
        if index_col == None:
            self.dates_ql = [ql.DateParser.parse(i, 'yyyy/mm/dd') for i in self.dat_raw['DATE']]
        else:
            self.dates_ql = [ql.DateParser.parse(i, 'yyyy/mm/dd') for i in self.dat_raw.index]
        self.discount_df = [i / self.dat_raw['discountDF'][0] for i in self.dat_raw['discountDF']]
        self.forecast_df = [i / self.dat_raw['forecastDF'][0] for i in self.dat_raw['forecastDF']]

        self.create_yieldtermstructure(True)
        self.create_yieldtermstructure(False)

    def create_yieldtermstructure(self, isDiscount=True, dc=ql.Actual365Fixed()):
        if isDiscount:
            self.yterm_discount = ql.DiscountCurve(self.dates_ql, self.discount_df, dc)
            self.yterm_discount_handle = ql.YieldTermStructureHandle(self.yterm_discount)
        else:
            self.yterm_forecast = ql.DiscountCurve(self.dates_ql, self.forecast_df, dc)
            self.yterm_forecast_handle = ql.YieldTermStructureHandle(self.yterm_forecast)

    def get_discount_yieldtermstructure_handle(self):
        return self.yterm_discount_handle

    def get_forecast_yieldtermstructure_handle(self):
        return self.yterm_forecast_handle
