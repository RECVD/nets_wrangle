import wrangle as wr

if __name__ == '__main__':
    # Define all Filenames
    company_filename = "C:\Users\jc4673\Documents\Columbia\NETS_Clients2013ASCI\NETS2013_Company.txt"
    address_first_filename = "C:\Users\jc4673\Documents\Columbia\NETS_Clients2013ASCI\NETS2013_AddressFirst.txt"
    misc_filename = "C:\Users\jc4673\Documents\Columbia\NETS_Clients2013ASCI\NETS2013_Misc.txt"
    move_filename = "C:\Users\jc4673\Documents\Columbia\NETS_Clients2013ASCI\NETS2013_Move.txt"
    delim = '\t'

    # Define writer
    loc_filepath = "C:\Users\jc4673\Documents\Columbia\NETS_Clients2013ASCI\location_transformed.txt"

    # initialize readers
    read_company = wr.Reader(company_filename, delim_type=delim, line_limit=20)
    read_address_first = wr.Reader(address_first_filename, delim_type=delim, line_limit=20)
    read_misc = wr.Reader(misc_filename, delim_type=delim, line_limit=20)
    read_move = wr.Reader(move_filename, delim_type=delim, line_limit=20)

