__author__ = 'adam'

from datetime import datetime

import pandas as pd
from ggplot import *


import os.path, sys
# used to set path to be root
parent = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent)


#from pyTradeMonster import log, PyTradeMonster
from pytrademonster.services import AccountServices
from pytrademonster.constants import TradeMonsterConstants
from pytrademonster import PyTradeMonster, log

"""
Methods for plotting useful account information

Right now only plots a view on PNL
"""

#global for testing
MAX_TRANSACTIONS = 5000



def plotAccountPnl(pyTradeMonster, transactionType, accountNumber, start, end, filterTicker = None):
    '''
    Retrieve all live accounts' activity and plot cumulative pnl for a given transaction type and account
    Filter ticker filters out PNL by an individual ticker, i.e. 'GOOG'
    '''
    accountService = AccountServices(pyTradeMonster)
    accounts = accountService.getParsedAccountObjects()
    graphFrame = pd.DataFrame()
    for account in accounts.itervalues():
        if account.accountNumber == accountNumber and account.accountType != TradeMonsterConstants.AccountRequests.ACCOUNT_TYPES.OPTION:
            log.info('Processing account: {0}'.format(account))
            accountHistory = accountService.getParsedAccountHistory(account, MAX_TRANSACTIONS, transactionType, start, end )
            historyList = [{key:value for key, value in x.__dict__.items() if not key.startswith('__') and not callable(key)} for x in accountHistory]
            historyFrame = pd.DataFrame(historyList)
            historyFrame = historyFrame.reindex(index=historyFrame.index[::-1]) #make dataframe sorted in ascending chronological order
            historyFrame.transactionDate = historyFrame.transactionDate.str[:-6]
            if filterTicker:
                historyFrame = historyFrame[historyFrame['symbol'].str.contains(filterTicker)]
            historyFrame['date'] = historyFrame.transactionDate.apply(lambda d : datetime.strptime(d,TradeMonsterConstants.TRANSACTION_TIME))
            historyFrame['cumPnl'] = historyFrame.amount.astype(float).cumsum()
            graphFrame = graphFrame.append(historyFrame)
    plot = ggplot(aes(x='date',y='cumPnl'), data=graphFrame) + geom_line()
    print plot



def main():
    """
    Sample use case
    REPLACE ACCOUNT NUMBER WITH YOUR ACTUAL ACCOUNT NUMBER!
    :return:
    """
    pyTradeMonster = PyTradeMonster()
    accountNumber = 'xxxxxx'
    plotAccountPnl(pyTradeMonster, TradeMonsterConstants.AccountRequests.TRANSACTION_TYPES.TRADE, accountNumber, '20110701T00:00:00', '20150830T00:00:00', 'SPY')


if __name__ == '__main__':
    main()