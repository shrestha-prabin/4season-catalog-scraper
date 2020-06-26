from scraper import PartList, PartDetails
import os
from utils import save_json, load_json, make_dir
from multiprocessing import Pool
from collections import Counter

make_dir('output')
make_dir('output/data')
make_dir('output/parts')
make_dir('output/images')
make_dir('output/excel')

year_list = [
    "2020", "2019", "2018", "2017", "2016", "2015", "2014", "2013", "2012", "2011", "2010", "2009", "2008",
    "2007", "2006", "2005", "2004", "2003", "2002", "2001", "2000", "1999", "1998", "1997", "1996", "1995",
    "1994", "1993", "1992", "1991", "1990", "1989", "1988", "1987", "1986", "1985", "1984", "1983", "1982",
    "1981", "1980", "1979", "1978", "1977", "1976", "1975", "1974", "1973", "1972", "1971", "1970", "1969",
    "1968", "1967", "1966", "1965", "1964", "1963", "1962", "1961", "1960", "1959", "1958", "1957", "1956",
    "1955", "1954", "1953", "1952", "1951", "1950", "1949", "1948", "1947", "1946", "1945", "1944", "1943",
    "1942"
]

if __name__ == '__main__':
    scraper = PartList()
    # scraper.extract_part_list('2017')

    """
    1
    """
    pool = Pool(50)
    pool.map(scraper.extract_part_list, year_list)

    """
    2
    """
    details_scraper = PartDetails()
    # details_scraper.extract_part_details()

    """
    3
    """
    # details_scraper.extract_competitor_oe()
