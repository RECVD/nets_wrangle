Because the conditionals are different to check for different business type,
conditional_type is the code that corresponds to how we will check these conditionals.

Code Keys:
----------
1. name
2. unique\_SIC OR (SIC_range AND name)
3. SIC_range
4. unique_SIC OR SIC\_range
5. SIC_range AND emp
6. SIC_range AND (sales OR emp)
7. SIC\_range OR (SIC\_range_2 AND name)
8. unique_SIC
9. unique_SIC OR name


####These values in this list correspond to:

- **name**	 -> Key word or list of key words corresponding to a given business category.  True if the any of the key words can be found in the business name by using Python's `business_name.find('keyword')`
- **unique\_SIC** -> A list of unique SIC codes.  True if the the business SIC code is located in the unique/_SIC 
- **SIC\_range** -> An inclusive range of SIC codes, or list of ranges.  True if the business SIC code is within any of the SIC\_ranges
- **emp** -> Number of business employees.  True if the number of business employees is within the range explicitly specified by the category
- **sales** -> Dollar amount of annual sales.  True if the sales of the business is within the range explicitly specified by the category
- **SIC\_range2** -> same as SIC\_range, used if separate ranges apply to different parts of the conditional, as in **Code Key #9**

