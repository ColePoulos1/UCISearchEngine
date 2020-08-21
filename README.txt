To start the search, run launch.py. You will then be able to search multiple times by simply inputting your
query and pressing Enter.
To quit, either Ctrl+C or input the search 'DEV:QUIT'.
To run the indexer, input the search 'DEV:INDEX'.

The program relies on launch.py, querizer.py, and indexer.py. It stores a folder of complete indexes and a temporary
folder of partial indexes. Additionally an 'index of the index', a url-to-int map, and a total count of sites are kept on file.
These are all created when running the indexer with 'DEV:INDEX', and accessed when running a search.