Because the conditionals are different to check for different business type,
conditional_type is the code that corresponds to how we will check these conditionals.

Code Keys:
----------
1. name
2. sic\_exclusive OR (sic_range AND name)
3. sic_range
4. sic\_exclusive OR sic\_range
5. sic_range AND emp
6. sic_range AND (sales OR emp)
7. sic\_range OR (sic\_range_2 AND name)
8. sic_exclusive
9. sic_exclusive OR name
10. sic_range AND emp AND (sales OR NOT sales_present)


####These values in this list correspond to:

- **name**	 -> Key word or list of key words corresponding to a given business category.  True if the any of the key words can be found in the business name by using Python's `business_name.find('keyword')`
- **sic\_exclusive** -> A list of unique SIC codes.  True if the business SIC code is located in the sic\_exclusive 
- **sic\_range** -> An inclusive range of SIC codes, or list of ranges.  True if the business SIC code is within any of the sic\_ranges
- **emp** -> Number of business employees.  True if the number of business employees is within the range explicitly specified by the category. Able to handle less than ('l' before number), greater than ('g' before number) or a range (number1,number2)
- **sales** -> Dollar amount of annual sales.  True if the sales of the business is within the range explicitly specified by the category. Able to handle less than ('l' before number), greater than ('g' before number) or a range (number1,number2)
- **sales\_present** -> True if there is a value present for sales
- **sic\_range2** -> same as sic\_range, used if separate ranges apply to different parts of the conditional, as in **Code Key #9**

