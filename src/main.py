import MyDirectories
import BaseUtils
from TAQAdjust import TAQAdjust
from OptimalK import OptimalKAll
from TAQCleaner import TAQCleanTrades
from FileManager import FileManager
from TAQAutocorrelation import AutoCorrAll

# get all data adjusted
#obj = TAQAdjust(isquote=False)
#obj.adjustAllTrades(tickers = list(BaseUtils.snp_tickers)[232:])

# all = OptimalKAll(BaseUtils.snp_tickers,None,None)
# all.get_all_optimal_k()

# obj = TAQCleanTrades(k = 20, tau = 0.0005)
# obj.cleanAllTrades(tickers=['JBL','TMO'])
# fm1 = FileManager(MyDirectories.getAdjDir())
# fm2 = FileManager(MyDirectories.getCleanDir())

# reader_before = fm1.getTradesFile( '20070621', 'TMO' )
# reader_after = fm2.getTradesFile('20070621', 'TMO')

# print(reader_after.getN()/reader_before.getN())

all = AutoCorrAll(['JBL','TMO'],None,None)
all.get_all_optimal_freq()


