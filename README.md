# nets_wrangle
Wrangling original NETS files to aid in transformation of the NETS data for the RECVD project. **Note: this code is somewhat convoluted and difficult to follow.  It was intended to be replaced by the `nets_clean` repo, which is unifinished. **

## File Descriptions  

- **create_first_last.py**: Creates a new list of the first and last year that a business was active based on their listed years based on the special longitudinal address files sent to us by Don Walls.
- **functions.py**: - Intended for importing purposes, Contains most of the functions that are used throughout multiple files
- **wrangle_location.py**:  Take in the longitudinal address files created by Don Walls and uses them along with the NETS_FirstLast derived file to create normalized Location file
- **Normal2Long.py**:  Take in a normalized format file and transform into the long format 
- **wrangle_classification.py**: Take in the SIC, Sales, Emp, and Company files along with the json_config file detailing category attributes, and create a normalized file of businesses by SIC codes and business classifications
- **nets_backfill.py**: Backfills the NETS location data to eliminate poor quality older values
- **lastyear_patch.py**: patches incorrect FirstYear and LastYear values from misc based on the values that are contained in master address files
