from datetime import date
import os
import sys

def generate_config(config_obj, fname, cli=False):
    """
    Generates a list of strings using the config data then its written to an ini
    file

    Args:
        config: Config file dictionary created by
                 :func:`~inicheck.config.UserConfig'.
        fname: String path to the output location for the new config file.

        cli: Boolean value that adds the line "file generated using
             inicheck.cli", Default = False

    Returns:
        None
    """
    header_len = 80
    pg_sep = '#' * header_len

    # Header surround each commented titles in the ini file
    section_header = pg_sep + '\n' + ('# {0}\n') + pg_sep

    # Construct the section strings
    config_str = ""
    config_str += pg_sep

    # File header with specific package option
    if config_obj.mcfg.header != None:
        header = config_obj.mcfg.header.split('\n')
        for line in header:
            config_str += ('\n# ' + line)
    else:
        config_str += "\n# Configuration File "

    # Add in the date generated
    config_str += "\n#\n# Date generated: {0}".format(date.today())

    # Generated with inicheck
    if cli:
        config_str += "\n#\n# Generated using: inicheck <filename> -w"

    config_str += "\n#\n# For more inicheck help see:" + \
                  "\n# http://inicheck.readthedocs.io/en/latest/\n"

    config = config_obj.cfg
    mcfg = config_obj.mcfg.cfg

    # Check to see if section titles were provided
    has_section_titles = hasattr(config_obj.mcfg,'titles')

    # Generate the string for the file, creating them in order.
    for section in mcfg.keys():
        if section in config.keys():
            config_str += '\n' * 2

            # Add a section header
            s_hdr = pg_sep
            if has_section_titles:
                if section in config_obj.mcfg.titles.keys():
                    # Add the header
                    s_hdr = section_header.format(config_obj.mcfg.titles[section])

            else:
                config_str += s_hdr

            config_str += s_hdr
            config_str += '\n'
            config_str += '\n[{0}]\n'.format(section)

            # Add section items and values
            for k in config[section].keys():
                v = config[section][k]
                if type(v) == list:
                    astr = ", ".join(str(c).strip() for c in v)
                else:
                    astr = str(v)
                config_str += "{0:<30} {1:<10}\n".format((k+':'), astr)

    # Write out the string generated
    with open(os.path.abspath(fname), 'w') as f:
        f.writelines(config_str)
        f.close()


def print_config_report(warnings, errors, logger=None):
    """
    Pass in the list of string messages generated by check_config file.
    print out in a pretty format the issues

    Args:
        warnings - List of non-critical messages returned from
                   :func:`~utilities.check_config'.
        errors - List of critical messages returned from
                 :func:`~utilities.check_config'.
        logger - pass in the logger function being used. If no logger is
                 provided, print is used. Default = None

    Returns:
        None
    """

    msg = "{: <20} {: <25} {: <60}"

    # Check to see if user wants the logger or stdout
    if logger != None:
        out = logger.info
    else:
        out = print_out


    msg_len = 90
    out(" ")
    out(" ")
    out("Configuration File Status Report:")
    header = "="*msg_len
    out(header)
    any_warnings = False
    any_errors = False

    # Output warnings
    if len(warnings) > 0:
        any_warnings = True
        out("WARNINGS:")
        out(" ")
        out(msg.format(" Section", "Item", "Message"))
        out("-"*msg_len)
        for w in warnings:
            out(w)
        out(" ")
        out(" ")

    # Output errors
    if len(errors) > 0:
        any_errors = True
        out("ERRORS:")
        out(" ")
        out(msg.format("Section", "Item", "Message"))
        out("-"*msg_len)
        for e in errors:
            out(e)
        out(" ")
        out(" ")

    if not any_errors and not any_warnings:
        out("No errors or warnings were reported with the config file.\n")


def print_out(out_str):
    """
    wrapper for print so we can use either a logger or a stdout
    """
    print(out_str)


def print_recipe_summary(lst_recipes):
    """
    Prints out the recipes found and how they are interpretted
    """
    # len of recipe separators
    msg_len = 80
    header = "=" * msg_len
    recipe_hdr = "-" * msg_len
    r_msg = "\n{: <20}\n"+recipe_hdr
    cfg_msg = "\t\t{: <20} {: <20} {: <20}"

    msg = "\t\t{: <20} {: <25}"

    print('\n\n')
    print("Below are the recipes applied to the config file:")
    print("Recipes Summary:")
    print(header)

    for r in lst_recipes:
        print(r_msg.format(r.name))
        print("\tConditionals:")
        for n, t in r.triggers.items():
            for i, c in enumerate(t.conditions):
                if i == 0:
                    print(msg.format(n, c))
                else:
                    print(msg.format("", c))

        print_cfg_for_recipe(r.adj_config, cfg_msg, hdr="\n\tEdits:")
        #print('\n')
    print('\n')


def print_cfg_for_recipe(cfg, fmt, hdr=None):
    if hdr != None:
        print(hdr)

    for section in cfg.keys():
        for item, value in cfg[section].items():
            print(fmt.format(section, item, value))


def print_details(details, mcfg):
    """
    Prints out the details for a list of provided options
    """

    msg = "{: <15} {: <15} {: <15} {: <25} {: <60}"
    hdr  = '\n' + msg.format('Section', 'Item', 'Default', 'Options',
                           'Description')
    print(hdr)
    print('='*len(hdr))
    nopts = len(details)
    # At least a section was provided
    if nopts >= 1:
        if details[0] in mcfg.keys():
            # A section and item was provided
            if nopts == 2:
                if details[1] in mcfg[details[0]].keys():
                    print(msg.format(details[0], details[1],
                                    str(mcfg[details[0]][details[1]].default),
                                    str(mcfg[details[0]][details[1]].options),
                                    str(mcfg[details[0]][details[1]].description)))
                else:
                    print("Item {0} in not a registered item."
                          "".format(details[1]))
                    sys.exit()

            # Print the whole section
            else:
                for k, v in mcfg[details[0]].items():

                    print(msg.format(details[0],
                                     k,
                                     str(v.default),
                                     str(v.options),
                                     str(v.description)))

        # Section does not exist
        else:
            print("Section {0} in not a valid section.".format(details[0]))
            sys.exit()

    else:
        print("Please provide at least a section for information")
        sys.exit()
