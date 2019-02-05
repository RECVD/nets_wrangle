# nets_wrangle - troubleshooting
Code for the purpose of troubleshooting issues that come up during wrangling, mostly to FIND problems, not fix them

## File Descriptions  
- **Address_mismatch_troubleshooting**: Identifies Location table businesses that have out of sync FirstYear and LastYear values
- **checkfile_tabs**:  Checks the file for missing or extra tabs in any lines
- **geo_quality_comp**: Compares the geocoding quality of Walls & Associates to our geocoding (pre back-filling)
- **misc_masteraddress_comparison**: Quantifies mismatches between actual FirstYear and LastYear and the ones that have appeared in the Location file
- **reclassify_phase1**: Reclassifies records in a classification table to match phase 1 (phase 1 definitions are now built into the wrangle_classify code which is why this script is contained in the troubleshooting folder)
