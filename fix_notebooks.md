#  Figuring Out What All My Random Jupyter Notebooks do because I'm a Dumbass

**DON'T DELETE ANYTHING UNTIL NEW SOLUTION IS UP AND RUNNING**

## "in_development" Folder

**bfill_check**
Purpose: Self explanatory
Needed?: Yes

**cat_log_join_sample**
Purpose: Organize category AND location by BEH_ID, join and classify 
Needed? Yes

**data_check**
Purpose: Final data check before sending out to the team
Needed? Yes

**fix_backfill**
Purpose: A bunch of location file comparisons and sample creations for testing the backfill patch
Needed?

**fix_crosswalk**
Purpose: BEH_LOC and BEH_ID fixing for the crosswalk file
Needed? Yes for this iteration, but only because they were wrong when sent to James in the first place

**fix_lastyear_patch**
Purpose: more year fixing, reasons unclear
Needed? seems not

**Fix_year_format_category**
Purpose: Adjacent implementation of fixing LastYear to avoid overlap along with fixing category order
Needed?: Yes, but simple

**location_file_write**
Purpose: Putting together pieces to write because the file is too big to fit in memory
Needed? No, it should be formatted to write in chunks anyway so that it isn't dependent on a powerful machine

**untitled**
Purpose: Fixing bad BEH_IDS
Needed?: No, as long as we make sure that they're correct in the first place

**untitled1**
Purpose:  Subtracting 1 from LastYear on all BEH_ID !=0
Needed:  Integrate into earlier classification

**untitled2**
Purpose: Testing for BEH_ID and BEH_LOC fix
Needed: Probably not

**untitled3**
Pupose: Checking that the ActiveYears for each location sum to the ActiveYears
for the business as a whole.
Needed: Good idea to implement, and return an error if it fails to make sure that
we're not providing bad data

**yearfix_2**
Pupose: Fix the year issues that are checked in untitled3.
Needed: Yes.  However as implemented it has year overlap, so we need to be sure that
we avoid that.



## "troubleshooting" folder

**address_mismatch_troubleshooting**
Purpose: No fixes done, but investigating incorrect years and missing SIC codes for later years.  Due to issues disparities between longitudinal address file and FirstYear and LastYear in Misc file.  Solution was just to use dates from the longitudinal address file.
Needed: No action taken but conclusions should be incorporated

**checkfile_tabs**
Purpose: Looking for extra tabs that would screw up file reading within the Location file that I created
Needed: Yes

**geo_quality_comp**
Purpose: Comparing Walls geocoding quality to ours.
Needed: No, backfilling fixes this

**misc_masteraddress_comparison**
Purpose: Examining differences in misc addresses and the addresses supplied by the longitudinal "master" address file.  We see a lot of differences and decided to only use the master address file addresses.
Needed: No, just don't use the address from misc

**namesearch_fix**
Purpose: Fixing namesearch to handle spaces more appropriately, changes made to functions.
Needed: YES, THIS IS VERY IMPORTANT.  All of the most recent classifier information should be taken from here.

**namesearch_fix_file**
Purpose: Write developments from namesearch_fix to the file.
Needed: Yes, goes together with namesearch_fix

**reclassify_phase1**
Purpose: Reclassifying from a long time ago
Needed: No

**untitled**
Purpose: Random stuff
Needed: No

# Mapping out the Plan for nets_clean

1. Write create_samples.py to make smaller samples of all the files that we need.
2. Create normalized location file with BEH_ID and BEH_LOC.
3. Fix bad names/years and do backfilling based on geocoding quality from James
4. Find BEH_SICs, along with other information needed to classify such as employee numbers and sales, Company and TradeName.  Join these to the normalized location file on BEH_ID.
5. Perform final classifications using new (faster) method