# -*- coding, utf-8 -*-
import QuantLib as ql
from collections import OrderedDict

class MarketDataSample:
    def __init__(self):
        self.dataDepoJPYOIS = OrderedDict(
            [
                ("1W", ql.SimpleQuote(-0.0005000)),
                ("1M", ql.SimpleQuote(-0.0004375)),
                ("2M", ql.SimpleQuote(-0.0004375)),
                ("3M", ql.SimpleQuote(-0.0004375)),
                ("4M", ql.SimpleQuote(-0.0004250)),
                ("5M", ql.SimpleQuote(-0.0004125)),
                ("6M", ql.SimpleQuote(-0.0004125)),
                ("9M", ql.SimpleQuote(-0.0003750))
            ]
        )

        self.dataDepoJPYL6 = OrderedDict(
            [
                ("6M", ql.SimpleQuote(0.0004193))
            ]
        )

        self.dataDepoJPYL3 = OrderedDict(
            [
                ("3M", ql.SimpleQuote(0.0002593))
            ]
        )

        self.dataDepoJPYBasis = OrderedDict(
            [
                ("1W", ql.SimpleQuote(-0.0003130)),
                ("1M", ql.SimpleQuote(-0.0017480)),
                ("2M", ql.SimpleQuote(-0.0019490)),
                ("3M", ql.SimpleQuote(-0.0033010)),
                ("4M", ql.SimpleQuote(-0.0031310)),
                ("5M", ql.SimpleQuote(-0.0030940)),
                ("6M", ql.SimpleQuote(-0.0037550)),
                ("9M", ql.SimpleQuote(-0.0044550))
            ]
        )

        self.dataDepoUSDOIS = OrderedDict(
            [
                ("1W", ql.SimpleQuote(0.0090350)),
                ("1M", ql.SimpleQuote(0.0089700)),
                ("2M", ql.SimpleQuote(0.0090300)),
                ("3M", ql.SimpleQuote(0.0093600)),
                ("4M", ql.SimpleQuote(0.0096700)),
                ("5M", ql.SimpleQuote(0.0098600)),
                ("6M", ql.SimpleQuote(0.0101000)),
                ("9M", ql.SimpleQuote(0.0108300))
            ]
        )

        self.dataDepoUSDL3 = OrderedDict(
            [
                ("3M", ql.SimpleQuote(0.0114956))
            ]
        )

        self.dataFutureUSDL3 = OrderedDict(
            [
                (ql.SimpleQuote(99.975), ql.IMM.nextDate(ql.Date.todaysDate()+0)),
                (ql.SimpleQuote(99.985), ql.IMM.nextDate(ql.Date.todaysDate()+90)),
                (ql.SimpleQuote(99.995), ql.IMM.nextDate(ql.Date.todaysDate()+180)),
                (ql.SimpleQuote(99.995), ql.IMM.nextDate(ql.Date.todaysDate()+270))
            ]
        )

        self.dataFraJPYL6 = OrderedDict(
            [
                ("1M", ql.SimpleQuote(0.0004375)),
                ("2M", ql.SimpleQuote(0.0004500)),
                ("3M", ql.SimpleQuote(0.0004625)),
                ("4M", ql.SimpleQuote(0.0004750)),
                ("5M", ql.SimpleQuote(0.0004875))
            ]
        )

        self.dataFraJPYL3 = OrderedDict(
            [
                ("1M", ql.SimpleQuote(0.0002625)),
                ("2M", ql.SimpleQuote(0.0002625)),
                ("3M", ql.SimpleQuote(0.0002625)),
                ("4M", ql.SimpleQuote(0.0002875)),
                ("5M", ql.SimpleQuote(0.0003000)),
                ("6M", ql.SimpleQuote(0.0003250)),
                ("7M", ql.SimpleQuote(0.0003250)),
                ("8M", ql.SimpleQuote(0.0003250))
            ]
        )

        self.dataFraUSDL3 = OrderedDict(
            [
                ("1M", ql.SimpleQuote(0.0120600)),
                ("2M", ql.SimpleQuote(0.0126600)),
                ("3M", ql.SimpleQuote(0.0131800)),
                ("4M", ql.SimpleQuote(0.0136700)),
                ("5M", ql.SimpleQuote(0.0141100)),
                ("6M", ql.SimpleQuote(0.0143900)),
                ("7M", ql.SimpleQuote(0.0149200)),
                ("8M", ql.SimpleQuote(0.0154000))
            ]
        )

        self.dataSwapJPYOIS = OrderedDict(
            [
                ("1Y", ql.SimpleQuote(-0.0003500)),
                ("2Y", ql.SimpleQuote(-0.0003400)),
                ("3Y", ql.SimpleQuote(-0.0003125)),
                ("4Y", ql.SimpleQuote(-0.0002000)),
                ("5Y", ql.SimpleQuote(-0.0000250)),
                ("6Y", ql.SimpleQuote(0.0001500)),
                ("7Y", ql.SimpleQuote(0.0003250)),
                ("8Y", ql.SimpleQuote(0.0005000)),
                ("9Y", ql.SimpleQuote(0.0006750)),
                ("10Y", ql.SimpleQuote(0.0009125)),
                ("12Y", ql.SimpleQuote(0.0015500)),
                ("15Y", ql.SimpleQuote(0.0027750)),
                ("20Y", ql.SimpleQuote(0.0044625)),
                ("25Y", ql.SimpleQuote(0.0053125)),
                ("30Y", ql.SimpleQuote(0.0056875)),
                ("40Y", ql.SimpleQuote(0.0064375))
            ]
        )

        self.dataSwapJPYL6 = OrderedDict(
            [
                ("1Y", ql.SimpleQuote(0.0004750)),
                ("18M", ql.SimpleQuote(0.0005125)),
                ("2Y", ql.SimpleQuote(0.0005500)),
                ("3Y", ql.SimpleQuote(0.0006500)),
                ("4Y", ql.SimpleQuote(0.0008250)),
                ("5Y", ql.SimpleQuote(0.0016025)),
                ("6Y", ql.SimpleQuote(0.0013250)),
                ("7Y", ql.SimpleQuote(0.0016125)),
                ("8Y", ql.SimpleQuote(0.0019375)),
                ("9Y", ql.SimpleQuote(0.0022750)),
                ("10Y", ql.SimpleQuote(0.0026375)),
                ("12Y", ql.SimpleQuote(0.0034750)),
                ("15Y", ql.SimpleQuote(0.0048625)),
                ("20Y", ql.SimpleQuote(0.0067750)),
                ("30Y", ql.SimpleQuote(0.0082875)),
                ("40Y", ql.SimpleQuote(0.0090250))
            ]
        )

        self.dataSwapUSDOIS = OrderedDict(
            [
                ("1Y", ql.SimpleQuote(0.0114600)),
                ("18M", ql.SimpleQuote(0.0125600)),
                ("2Y", ql.SimpleQuote(0.0136400)),
                ("3Y", ql.SimpleQuote(0.0153800)),
                ("4Y", ql.SimpleQuote(0.0166700)),
                ("5Y", ql.SimpleQuote(0.0176800)),
                ("6Y", ql.SimpleQuote(0.0184700)),
                ("7Y", ql.SimpleQuote(0.0191100)),
                ("8Y", ql.SimpleQuote(0.0196400)),
                ("9Y", ql.SimpleQuote(0.0200900)),
                ("10Y", ql.SimpleQuote(0.0205000)),
                ("12Y", ql.SimpleQuote(0.0211600)),
                ("15Y", ql.SimpleQuote(0.0217800)),
                ("20Y", ql.SimpleQuote(0.0223200)),
                ("25Y", ql.SimpleQuote(0.0224500)),
                ("30Y", ql.SimpleQuote(0.0224500)),
                ("40Y", ql.SimpleQuote(0.0223100))
            ]
        )

        self.dataSwapUSDL3 = OrderedDict(
            [
                ("1Y", ql.SimpleQuote(0.0139400)),
                ("2Y", ql.SimpleQuote(0.0162850)),
                ("3Y", ql.SimpleQuote(0.0181750)),
                ("4Y", ql.SimpleQuote(0.0195850)),
                ("5Y", ql.SimpleQuote(0.0206950)),
                ("6Y", ql.SimpleQuote(0.0215850)),
                ("7Y", ql.SimpleQuote(0.0223350)),
                ("8Y", ql.SimpleQuote(0.0229550)),
                ("9Y", ql.SimpleQuote(0.0235050)),
                ("10Y", ql.SimpleQuote(0.0239850)),
                ("12Y", ql.SimpleQuote(0.0247950)),
                ("15Y", ql.SimpleQuote(0.0255850)),
                ("20Y", ql.SimpleQuote(0.0262950)),
                ("30Y", ql.SimpleQuote(0.0265850)),
                ("40Y", ql.SimpleQuote(0.0264500))
            ]
        )

        self.dataSpreadJPYL3 = OrderedDict(
            [
                ("1Y", ql.SimpleQuote(0.0001750)),
                ("18M", ql.SimpleQuote(0.0001875)),
                ("2Y", ql.SimpleQuote(0.0002000)),
                ("3Y", ql.SimpleQuote(0.0002250)),
                ("4Y", ql.SimpleQuote(0.0002500)),
                ("5Y", ql.SimpleQuote(0.0002875)),
                ("6Y", ql.SimpleQuote(0.0003375)),
                ("7Y", ql.SimpleQuote(0.0004000)),
                ("8Y", ql.SimpleQuote(0.0004625)),
                ("9Y", ql.SimpleQuote(0.0005500)),
                ("10Y", ql.SimpleQuote(0.0006250)),
                ("12Y", ql.SimpleQuote(0.0007250)),
                ("15Y", ql.SimpleQuote(0.0008250)),
                ("20Y", ql.SimpleQuote(0.0009250)),
                ("30Y", ql.SimpleQuote(0.0011375)),
                ("40Y", ql.SimpleQuote(0.0011375))
            ]
        )

        self.dataSpreadJPYBasis = OrderedDict(
            [
                ("1Y", ql.SimpleQuote(-0.0047250)),
                ("18M", ql.SimpleQuote(-0.0051500)),
                ("2Y", ql.SimpleQuote(-0.0056750)),
                ("3Y", ql.SimpleQuote(-0.0063250)),
                ("4Y", ql.SimpleQuote(-0.0067375)),
                ("5Y", ql.SimpleQuote(-0.0069750)),
                ("6Y", ql.SimpleQuote(-0.0071125)),
                ("7Y", ql.SimpleQuote(-0.0071375)),
                ("8Y", ql.SimpleQuote(-0.0070750)),
                ("9Y", ql.SimpleQuote(-0.0069375)),
                ("10Y", ql.SimpleQuote(-0.0067750)),
                ("12Y", ql.SimpleQuote(-0.0064250)),
                ("15Y", ql.SimpleQuote(-0.0059500)),
                ("20Y", ql.SimpleQuote(-0.0052000)),
                ("25Y", ql.SimpleQuote(-0.0043750)),
                ("30Y", ql.SimpleQuote(-0.0043000))
            ]
        )
        
        self.dataSpreadJPYL3_basis = OrderedDict(
            [
                ("1Y", ql.SimpleQuote(-0.0045500)),
                ("18M", ql.SimpleQuote(-0.0049625)),
                ("2Y", ql.SimpleQuote(-0.0054750)),
                ("3Y", ql.SimpleQuote(-0.0061000)),
                ("4Y", ql.SimpleQuote(-0.0064875)),
                ("5Y", ql.SimpleQuote(-0.0066875)),
                ("6Y", ql.SimpleQuote(-0.0067750)),
                ("7Y", ql.SimpleQuote(-0.0067375)),
                ("8Y", ql.SimpleQuote(-0.0066125)),
                ("9Y", ql.SimpleQuote(-0.0063875)),
                ("10Y", ql.SimpleQuote(-0.0061500)),
                ("12Y", ql.SimpleQuote(-0.0057000)),
                ("15Y", ql.SimpleQuote(-0.0051250)),
                ("20Y", ql.SimpleQuote(-0.0042750)),
                ("30Y", ql.SimpleQuote(-0.0042750)),
                ("40Y", ql.SimpleQuote(-0.0042750))
            ]
        )
        