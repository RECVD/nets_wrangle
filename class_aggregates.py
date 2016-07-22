try:
    import pandas as pd
    import json
except ImportError:
    print("Warning: Packages 'Pandas' and 'JSON' must be installed")


def json_load(json_filepath):
    """Loads a JSON configuration file that holds key rankings"""
    with open(json_filepath) as f:
        config = json.load(f)
    return config

def semi_to_list(semi_string_list):
    """Turns a string of items separated by ';'"""
    return [string.strip() for string in semi_string_list.split(';')]

def get_highest_rank(semi_string_list, ranking_config):
    """Returns the highest rank in a list of ranked class separated by semicolons
    ------------------------
    Keyword Arguments:
    semi_string_list = strig of words separated by semicolons
    ranking_config = config file with key ranks
    """
    class_list = semi_to_list(semi_string_list)
    highest_rank = 10**2
    highest_word = ''
    for word in class_list:
        word_rank = ranking_config[word]['ranking']
        if word_rank < highest_rank:
            highest_rank = word_rank
            highest_word = word
        else:
            continue
    return highest_word

if __name__ == "__main__":
    infile = 'C:\Users\jc4673\Documents\Columbia\NETS_Clients2013ASCI\SIC_transformed.txt'
    config_path = r'C:\Users\jc4673\Documents\Columbia\nets_wrangle\ranking_config.json'

    config = json_load(config_path)  # load the configuration file

    sic_df = pd.read_table(infile)   # load the long sic code table into memory by data frame

    # Apply mutually exclusive overall class by rankings
    class_series = sic_df['Overall_Class'].apply(lambda x: get_highest_rank(x, config))
    # Join DunsNumber to overall class and drop duplicate DunsNumber (non longitudinal)
    class_df = pd.concat([sic_df['DunsNumber'],class_series], axis=1).drop_duplicates(subset='DunsNumber')

    counts = class_df.groupby(by='Overall_Class').count()




