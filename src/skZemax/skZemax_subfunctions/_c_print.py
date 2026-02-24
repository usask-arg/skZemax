# https://misc.flogisoft.com/bash/tip_colors_and_formatting <-- Documentation on what COMMAND_CONVERSIONS means.
#                                                               (ANSI/VT100 Control sequences)
# Note that most but not all of these options will work. It depends on terminal is being used.
from __future__ import annotations

CPRINT_COMMAND_CONVERSIONS = {
    "bold": 1,
    "dim": 2,
    "underl": 4,
    "blink": 5,
    "invert": 7,
    "hide": 8,
    "clear": 0,
    "clear_bold": 21,
    "clear_dim": 22,
    "clear_underline": 24,
    "clear_blink": 25,
    "clear_invert": 27,
    "clear_hide": 28,
    "de": 39,
    "w": 97,
    "k": 30,
    "r": 31,
    "g": 32,
    "y": 33,
    "b": 34,
    "m": 35,
    "c": 36,
    "lgr": 37,
    "dgr": 90,
    "lr": 91,
    "lg": 92,
    "ly": 93,
    "lb": 94,
    "lm": 95,
    "lc": 96,
    "bkde": 49,
    "bkw": 107,
    "bkk": 40,
    "bkr": 41,
    "bkg": 42,
    "bky": 43,
    "bkb": 44,
    "bkm": 45,
    "bkc": 46,
    "bklgr": 47,
    "bkdgr": 100,
    "bklr": 101,
    "bklg": 102,
    "bkly": 103,
    "bklb": 104,
    "bklm": 105,
    "bklc": 106,
}


def c_print(
    text: str,
    end: str = "\n",
    flush: bool = False,
    command_marker: str = "!@",
    verbose: bool = True,
) -> str:
    """
    Convenient function to print colored text to console.
    Colors for printed text are set by commands between the command markers ('!@' by default)

    Example:

    >>> from c_print import c_print as cp
    >>> cp('!@g!@Hello, !@b!@how are you today?')

    This will output to console text with "Hello," in green and "how are you today?" in blue.

    Written by Daniel Letros

    :param text: Text to print to screen including color/formatting commands.
    :type text: str
    :param end: What to end the string with. Defaults to newline, defaults to newline
    :type end: str, optional
    :param flush: Should force flush or not, Defaults to False.
    :type flush: bool, optional
    :param command_marker:  The bit of chars which surround a chunk of commands, Defaults to '!@'.
    :type command_marker: str, optional
    :param verbose: Allows passage of a 'verbose' bool, Defaults to True.
    :type verbose: bool, optional
    :return: Formatted text string for colored printing
    :rtype: str
    """

    if not verbose:
        return ""

    split_text = text.split(
        command_marker
    )  # Split will always put commands on odd index as long as
    # they are surrounded by the command_marker.
    found_keep = False  # If !@keep!@ is found at end of string DON'T reset the current formatting back to default.

    for idx in range(1, len(split_text), 2):  # Loop through all command markers.
        if (
            idx == len(split_text) - 2
        ):  # Check only the last set of commands for the !@keep!@ command.
            for split_text_item in split_text:
                if split_text_item.lower() == "keep":
                    found_keep = True
                    break
        split_text[idx] = __get_sequence__(
            split_text[idx].split(" ")
        )  # Replace all written commands within
        # command_marker with their properly formatted
        # command sequence string.

    if found_keep:  # Do not reset current formatting.
        print("".join(split_text), end=end, flush=flush)
    else:  # Ensure the reset of current formatiing.
        print("".join([*split_text, __get_sequence__(["clear"])]), end=end, flush=flush)

    return ""  # Return blank string to prevent some applications from printing a 'None' when this function ends


def __get_sequence__(options: list | None = None) -> str:
    """
    Worker function for c_print().

    :param options: A list of all written commands within one command sequence to be parsed, Defaults to [].
    :type options: list, optional
    :return: Formatted command sequences.
    :rtype: str
    """

    if options is None:
        options = []
    start_of_seq = "\033["
    end_of_seq = "m"
    add_seq = ";"

    command_sequence = start_of_seq

    for idx in range(len(options)):
        command_sequence += str(
            CPRINT_COMMAND_CONVERSIONS.get(options[idx].lower(), "")
        )
        if idx != len(options) - 1:
            command_sequence += add_seq
        else:
            command_sequence += end_of_seq

    return command_sequence
