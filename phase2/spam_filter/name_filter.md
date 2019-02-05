# FFS Bad Match Study
## All FFS Names
Of **1,860,401** businesses in the expanded FFS SIC codes  

|   Match type   | Frequency |
| :------------: | :-------: |
|   TradeName    |  212,196  |
|    Company     |  128,025  |
|     Either     |  243,084  |
|      Both      |  97,137   |
| TradeName Only |  115,059  |
|  Company Only  |  30,888   |

Randomly sampling **1000** Company matches:  
**2** Bad  
Randomly sampling  **1000** TradeName matches:  
**0** Bad

*Note*: If i was ever unsure if something was a bad match or not, I assumed
that it was not.

### Conclusions:

* TradeName is more or less a gold standard:  we can accept a match as true
if it matches with tradename
* We don't have enough mismatches for any type of machine learning model
based on a category in general
* We may have more luck zeroing in on specifically problematic words within
the word match (usually single, common words)

## "Bad" FFS Names
I chose non-specific one-word names and some very non-specific two-word names.  

Of **1,860,401** businesses in the expanded FFS SIC codes :

|   Match type   | Frequency |
| :------------: | :-------: |
|   TradeName    |  57,405   |
|    Company     |  39,581   |
|     Either     |  57,405   |
|      Both      |  30,583   |
|  Company Only  |  39,581   |
| TradeName Only |  26,822   |

Randomly sampling **1000** Company matches:  
**25** Bad  s
Randomly sampling  **1000** TradeName matches:  
**3** Bad,  *Note - Bad Matches were due to issues within Jack's and despite them I still consider TradeName a gold standard*


| Mismatch Name (Company and TradeName) | Frequency |
|---------|-------|
| Wendy's | 5 |
| Subway | 1 |
| Jack's | 19 |

### Conclusions:

We can solve the vast majority of our mismatch problems by focusing on Wendy's and Jack's.



## Zooming in on Jack's

Of **1,860,401** businesses in the expanded FFS SIC codes :

| Match Type             | Frequency |
| ---------------------- | --------- |
| TradeName              | 764       |
| Company                | 1,678     |
| Either (Total Matches) | 2,132     |
| Both                   | 310       |
| TradeName Only         | 454       |
| Company Only           | 1,368     |

Randomly sampling **500** Company matches:  
**442** Bad  (~88%)

Taking the following into account:

1. Jack's is also known as "Jack's Family Restaurant" and "Jack's Hamburgers". 

2. In my sample i saw only 3 examples of a restaurant only called "Jack's" with no other context. 

3. Because Jack's is such a common name, we have no way of knowing for sure if the restaurants referenced in 2. are in fact Jack's Family Restaurant

### Conclusions (Jack's):

The problem can be solved by replacing "JACKS" in the name list with "JACKS FAMILY RESTAURANT" and "JACKS HAMBURGERS"



## Zooming in on Wendy's

Of **1,860,401** businesses in the expanded FFS SIC codes :

|       Match Type       | Frequency |
| :--------------------: | :-------: |
|       TradeName        |  12,366   |
|        Company         |   6,029   |
| Either (Total Matches) |  13,013   |
|          Both          |   5,382   |
|     TradeName Only     |   6,984   |
|      Company Only      |   6,029   |

Randomly sampling **500** Company ONLY matches:  
**73** Bad, or 

- 15% of Company only Wendy's Match (The only place we'd see this issue)

- 1.1% of total Wendy's Matches

- 0.06% of all FFS matches

Taking the following into account:

1.  There is no way to eliminate the "WENDYS" as we can with "JACKS", as many Wendy's restaurants have only "WENDYS" as a Company name.

2. When Company matches and TradeName does not, my sample seems to show that if any of the following are True there is match, if not there is no match:

   - The word "OLD" appears, as in "WENDYS OLD FASHIONED HAMBURGERS" and its numerous misspellings.

   - The text is "WENDYS INTERNATIONAL INC"

   - The only other text is a number (which is sometimes spelled out)

   - The only other text is a person's name

   - The only other text is a town, country, or state.  ("WENDYS BOWLING GREEN INC" or "WENDYS RESTAURANTS OF CANADA")

### Conclusions (Wendy's):

- With only 955 Company Only matches, doing this by hand is completely reasonable and could probably be classified in about 30 minutes or so.  The only slightly ugly part would be patching those modifications back in to the full dataset 
- I only examined FFS.  If there are names with similar outcomes in other categories then the manual method could quickly become infeasible
- It may not be unreasonable to just accept these mismatches as noise, considering they are only 0.06% of all FFS