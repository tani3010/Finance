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
        self.df_ql = [i / self.dat_raw['DF'][0] for i in self.dat_raw['DF']]
        self.create_yieldtermstructure()

    def create_yieldtermstructure(self, dc=ql.Actual365Fixed()):
        self.yterm = ql.DiscountCurve(self.dates_ql, self.df_ql, dc)
        self.yterm_handle = ql.YieldTermStructureHandle(self.yterm)

    def get_yieldtermstructure_handle(self):
        return self.yterm_handle
