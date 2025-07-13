#! /usr/bin/env python3
# -*- coding: utf-8 -*-


from dart import (
    create_task,
    get_dartboards,
    get_folders,
    is_logged_in,
    replicate_space,
    update_dartboard,
    update_folder,
)

# The DART_TOKEN environment variable must be set to the value from
# https://app.dartai.com/?settings=account at this point
is_logged_in(should_raise=True)


# You can get this ID from the space's three dot menu > 'Copy ID'
TEMPLATE_SPACE_ID = "J3h4WKcqRpnS"
NEW_COLOR_HEX = "#000000"

# Title is optional
new_space_id = replicate_space(
    TEMPLATE_SPACE_ID,
    title="New space title",
    abrev="NST",
    color_hex=NEW_COLOR_HEX,
    accessible_by_team=True,
)

# Because space replication is async, you might need to add a timeout
# or loop until you get the expected number of dartboards here
dartboards = get_dartboards(new_space_id)
main_dartboard = [e for e in dartboards if e.title == "Dartboard title to change"][0]
# Update the relevant dartboard
update_dartboard(main_dartboard.duid, title="New dartboard title", color_hex=NEW_COLOR_HEX)

# Do the same for folders
folders = get_folders(new_space_id)
for folder in folders:
    update_folder(folder.duid, title="New folder title", color_hex=NEW_COLOR_HEX)

# Create and assign tasks to the new dartboard
create_task(
    dartboard_duid=main_dartboard.duid,
    title="New task",
    priority_int=0,
)
