# AlgoTrading

## Requirements

Running this project requires following modules:
- numpy==1.18.2
- pandas==1.0.3
- statsmodles==0.13.5
- matplotlib==3.2.1

## Directories
If needed, change paths in MyDirectories.py to correctly access files. 
| Variable Name | Info Stores   | 
| ------------- |:-------------:| 
| TEMP_DIR      |temproray files|
| DATA_PATH     |original TAQ data files|
| DATA_PATH_ADJ |adjusted TAQ files|
| DATA_PATH_CLEAN|cleaned TAQ files|
| BASE_DIR       |base directory where all subdirectories locate|
| SRC_DIR |directory to where our source codes locate|
| BinRTTradesDir |original binary trades files|
| BinRQQuotesDir |original binary quotes files|
| BinRTTradesAdjDir |adjust binary trades files|
| BinRQQuotesAdjDir |original binary quotes files|
| BinRTTradesClDir |cleaned binary trades files|
| BinRQQuotesClDir = |cleaned binary quotes files|
| TEST_PLOT |test plots generated from test|
| RESULT_PLOT |plots generated for final result|
| RECORD|records generated from running codes|

## Files
### codes
TAQAdjust.py and TAQCleaner.py are used to adjust and clean the data. TAQStats.py is used to calculate the statistic summaries as stated in problem 2. TAQAutocorrelation.py include codes to find optimal window that eliminates the bid-ask bounces. TAQCAMP perform mean-variance analysis in problem 4. BaseUtils.py includes some utility functions for the project. For each file, unittest tests would be named as Test_moduleName.py. 
### results
Throughout the projects, we used plots,csv, and text files to record the results. Plots are stored under TEST_PLOT directory and results are under RECORD directory. corrFreq.txt in record directory is used to store results generated from TAQAutocorrelation.py.

