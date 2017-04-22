#!/usr/bin/env python3
import xml.etree.ElementTree as ET
from xml.dom import minidom
import os
import shutil
import glob
import logging
import argparse

CANDIDATE_DIRS = [
    '/etc/X11/xkb',
    '/usr/share/X11/xkb'
]

def get_xkb_dir():
    for d in CANDIDATE_DIRS:
        logging.debug(f"Checking directory '{d}'")
        if os.path.isdir(d):
            return d


def put_symbols(d):
    to_path = os.path.join(d, "symbols/")
    logging.debug(f"Copying symbols file to '{to_path}'")
    shutil.copy("sv_dvorak", to_path)
    if not os.path.isfile(os.path.join(to_path, "sv_dvorak")):
        raise IOError("Symbols file was not successfully copied.")


def variant_exists(tree, name):
    variant = tree.find(f".//layout/configItem[name='se']../variantList/variant/configItem[name='{name}']")
    return (variant is not None)


def add_to_rules(d):
    evdev_file = os.path.join(d, "rules/evdev.xml")
    logging.debug(f"Parsing '{evdev_file}'")
    tree = ET.parse(evdev_file)
    
    svdvorak_variant = ET.parse('variant.xml').getroot()
    variant_name = svdvorak_variant.find(".//name").text

    if variant_exists(tree, variant_name):
        logging.info("Variant exists in rules, doing nothing.")
        return

    variantlist = tree.find(".//layout/configItem[name='se']../variantList")
    variantlist.append(svdvorak_variant)

    if not variant_exists(tree, variant_name):
        raise Exception("Variant could not be added to tree.")
    logging.debug("Variant added to tree. Writing file.")

    tree.write(evdev_file)


def main():
    d = get_xkb_dir()
    logging.info(f"Located xkb directory at '{d}'")
    
    put_symbols(d)
    logging.info(f"Successfully copied symbols to '{d}/symbols/")

    logging.info("Adding rules to '{d}/rules/evdev.xml'")
    add_to_rules(d)

    logging.info("Clearing xkb cache.")
    cache_files = glob.glob("/var/lib/xkb/*.xkm")
    for f in cache_files:
        os.remove(f)
    logging.debug(f"Removed {len(cache_files)} cache files.")

if __name__=="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", help="Show debug messages",
                        action="store_true")
    args = parser.parse_args()
    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)
        
    try:
        main()
    except PermissionError:
        logging.error("You do not have sufficient permissions. Try running with sudo.")
        exit()        




