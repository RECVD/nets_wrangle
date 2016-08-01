Because the conditionals are different to check for different business type,
conditional_type is the code that corresponds to how we will check these conditionals.

Code Keys:
----------
1 -> name
2 -> unique_SIC OR (SIC_range AND name)
3 -> SIC_range
4 -> unique_SIC OR SIC_range
5 -> SIC_range AND emp
6 -> SIC_range AND (sales OR emp)
7 -> SIC_range OR (SIC_range_2 AND name)
8 -> unique_SIC
9 -> unique_SIC OR name
