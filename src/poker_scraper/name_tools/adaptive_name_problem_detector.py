import io
from typing import List
from rapidfuzz import fuzz
import datetime
from poker_scraper import persistence
from poker_scraper.datamodel import NameClash
from poker_scraper import email_smtp_service
from poker_scraper.config import config

CLASH_SIMILAR_TO_OTHER_NAME = "SIMILAR_TO_OTHER_NAME"
CLASH_NO_LAST_NAME = "NO_LAST_NAME"
CLASH_SINGLE_TO_FIRST_LAST = "SINGLE_TO_FIRST_LAST"

def adaptive_name_problem_finder_process():
    all_rounds = persistence.get_all_rounds()
    all_names_from_rounds =  [player.player_name for round_obj in all_rounds for player in round_obj.players]
    all_names_from_rounds_unique = list(set(all_names_from_rounds))
    
    #this is super important and brittle
    #we have to update the name clashes database to remove records that no longer clash after they have been fixed
    delete_recently_fixed_name_clashes(all_names_from_rounds_unique)

    current_name_clashes = persistence.get_all_name_clashes()

    if len(current_name_clashes) == 0:
        #then this is the first time this process got called so we check for clashes current data against current data because no name clashes have ever been stored
        new_names_only = all_names_from_rounds_unique
        all_names_ever_processed = all_names_from_rounds_unique.copy()
    else:
        #get the 2 lists all current names and new names that have never been entered before
        #this is the usual case
        new_names_only = [name for name in all_names_from_rounds_unique if name not in {info.name for info in current_name_clashes}]
        all_names_ever_processed = {info.name for info in current_name_clashes}
    
    #the checking for clashes part of the method
    list_new_name_clashes = _characterize_all_new_names(all_names_ever_processed, new_names_only)
    
    #save clashes so they dont trigger next run
    persistence.save_these_name_clashes(list_new_name_clashes)

    #email the new clashes to whoever gets emails
    return _email_new_name_clashes(list_new_name_clashes)

def delete_recently_fixed_name_clashes(all_names_from_rounds_unique: List[str]):
    #run name clashes on all records
    list_of_name_clashes_regenerated = _characterize_all_new_names(all_names_from_rounds_unique, all_names_from_rounds_unique.copy())
    
    #get all name clashes currently existing
    list_of_existing_name_clashes = persistence.get_all_name_clashes()

    #determine which name clashes to remove based on comparing the results of running name clashes on itself and current name clashes
    #first find records in existing name clashes that dont show up in comparison
    names_in_list_of_regenerated_name_clashes = {info.name for info in list_of_name_clashes_regenerated}
    name_clashes_no_longer_relavent = [info for info in list_of_existing_name_clashes if info.name not in names_in_list_of_regenerated_name_clashes]
    
    #delete them
    #i think its ok if we remove them liberaly because they will come back if they still exist later
    persistence.delete_these_name_clashes(name_clashes_no_longer_relavent)
  
    #let people know that these names were fixed  so they can see if they should have been fixed that way
    _email_newly_fixed_name_clashes(name_clashes_no_longer_relavent)

def get_all_name_problems_as_string():
    name_clashes = persistence.get_all_name_clashes()
    return _pretty_print_name_clashes(name_clashes)

def _characterize_all_new_names(all_names, new_names_only) -> List[NameClash]:
    list_new_name_clashes = []
    for cur_new_name in new_names_only:
        #calculate similar name for second case here so can be used inside if
        similar_name = _find_similar_other_name(cur_new_name, all_names)

        if _no_last_name(cur_new_name):
            first_last_matching_new_single_name = _find_a_first_last_matching_this_single(cur_new_name, all_names)
            if first_last_matching_new_single_name not in (None, ""):
                #a new single name was found and matches
                single_to_first_last_clash = NameClash(name=cur_new_name, clash=CLASH_SINGLE_TO_FIRST_LAST, clash_description=first_last_matching_new_single_name)
                list_new_name_clashes.append(single_to_first_last_clash)
            else:
                #a new single name was found but does not have a matching first last combo existing
                no_last_name_clash = NameClash(name=cur_new_name, clash=CLASH_NO_LAST_NAME, clash_description="add a last name")
                list_new_name_clashes.append(no_last_name_clash)
        elif similar_name not in (None, ""):
            similar_name_clash = NameClash(name=cur_new_name, clash=CLASH_SIMILAR_TO_OTHER_NAME, clash_description=similar_name)
            list_new_name_clashes.append(similar_name_clash)
    return list_new_name_clashes

def _email_newly_fixed_name_clashes(fixed_name_clashes: List[NameClash]):
    if fixed_name_clashes is None or len(fixed_name_clashes) == 0:
        return
    
    list_of_recipient_email_addresses = config.LIST_OF_EMAIL_RECIPIENTS_NAME_CLASH
    subject = "New Name Clash Fix Detected - No Action Required - AUTOMATED"
    body = "go to \n" + config.NAME_TOOL_1_LINK + "\nand\n" + config.NAME_TOOL_2_LINK + "\nfor more detailed info on the clashes and to double check they are gone."
   
    file_name = datetime.datetime.now().strftime("%Y%m%d") + "fixedNameClashes.txt"
    for recipient_email_address in list_of_recipient_email_addresses:
        file_object = _name_clashes_to_file_obj(fixed_name_clashes)
        email_smtp_service.send_email(recipient_email_address, subject, body, file_object, file_name)

def _email_new_name_clashes(name_clashes: List[NameClash]):
    if name_clashes is None:
        return

     #dont send an email if there are no clashes to report
    if len(name_clashes) == 0:
        return "No new name clashes found"
    
    list_of_recipient_email_addresses = config.LIST_OF_EMAIL_RECIPIENTS_NAME_CLASH
    subject = "New Name Clashes Detected - Action Required - AUTOMATED"
    body = "The latest name check process found some new name clashes that require your attention. Attached is the names that are clashing now. Fixing them before the end of the league month will make things simple.\n"
    body += "go to \n" + config.NAME_TOOL_1_LINK + "\nand\n" + config.NAME_TOOL_2_LINK + "\nfor more detailed info on the clashes and info on how to fix them."
   
    file_name = datetime.datetime.now().strftime("%Y%m%d") + "newNameClashes.txt"
    for recipient_email_address in list_of_recipient_email_addresses:
        file_object = _name_clashes_to_file_obj(name_clashes)
        email_smtp_service.send_email(recipient_email_address, subject, body, file_object, file_name)

    return _pretty_print_name_clashes(name_clashes)
    

def _pretty_print_name_clashes(name_clashes: List[NameClash]) -> str:
    """Return a pretty one-line string for each NameClash in the list."""
    #sort the name clashes first by the clash type then by name alphabetically
    if not name_clashes:
        return "(no name clashes)"
    sorted_clashes = sorted(name_clashes, key=lambda info: (info.clash, info.name))
    lines = [
        f"{info.name:25} | {info.clash:20} | {info.clash_description}" for info in sorted_clashes
    ]
    return "\n".join(lines)

def _name_clashes_to_file_obj(name_clashes: List[NameClash]) -> io.StringIO:
    """Return an in-memory text file object with pretty-printed NameClash lines."""
    fileobj = io.StringIO()
    fileobj.write(_pretty_print_name_clashes(name_clashes))
    fileobj.seek(0)
    return fileobj

def _no_last_name(name: str) -> bool:
    normalized = name.strip()
    return len(normalized.split(" ")) < 2

def _find_a_first_last_matching_this_single(single_name: str, all_other_names: List[str]) -> str:
    for cur_other_name in all_other_names:
        if _with_and_without_last_name(single_name, cur_other_name):
            return cur_other_name
            
    return None

def _with_and_without_last_name(single_name: str, other_name: str) -> bool:
    # If other_name does not have 2 parts, return False
    parts = other_name.strip().split()
    if len(parts) != 2:
        return False
    # Compare single_name (stripped) to first part of other_name (stripped)
    elif single_name.strip() == parts[0]:
        return True
    else:
        return False 

def _find_similar_other_name(input_name: str, all_other_names: List[str]) -> str:
    for cur_other_name in all_other_names:
        if _are_names_similar(input_name, cur_other_name):
            return cur_other_name
            
    return None

def _are_names_similar(name1: str, name2: str) -> bool:
    # Split names into first and last, or set last to empty string if not present
    if name1 == name2:
        #exact duplicate names are not a problem for us they will get combined somewhere in the application
        return False
    def split_name(name):
        parts = name.strip().split()
        if len(parts) == 1:
            return parts[0], ""
        else:
            return parts[0], parts[-1]

    first1, last1 = split_name(name1)
    first2, last2 = split_name(name2)
   
    first_name_similarity_score = fuzz.ratio(first1, first2)
    last_name_similarity_score = 0
    if last1 in (None, "") and last2 in (None, ""):
        #last names are both missing
        last_name_similarity_score = 100
    elif last1 in (None, "") or last2 in (None, ""):
        #exactly one last name is missing
        #we say this is similar because a first name that has no last name 
        #should be compared to similar first names that do have a last
        last_name_similarity_score = 100
    else:
        #both have last name
        last_name_similarity_score = _last_name_similarity_score(last1, last2)
    return first_name_similarity_score > config.NAME_SIMILARITY_THRESHOLD and last_name_similarity_score >= config.NAME_SIMILARITY_THRESHOLD

def _last_name_similarity_score(last1: str, last2: str) -> float:
    if len(last1) == 1 and last2 and last2[0] == last1[0]:
        #last 1 is a single initial and other name has same first letter
        return 100
    elif len(last2) == 1 and last1 and last1[0] == last2[0]:
        #last 2 is a single initial and other name has same first letter
        return 100
    else:
        #both are multi letter last names fuzzy compare them
        return fuzz.ratio(last1, last2)
