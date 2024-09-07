import os
import ast
import inspect
from os import listdir
from os.path import isfile, join

import HW6_CHECKER_Solutions
IMPORT_NAME = HW6_CHECKER_Solutions

"""
    Checker Program

    The Python equivalent of the Java Checker / UnitTester.java programs, for checking student
    code files and running unit tests for student-written functions / programs

    @author Peter Olson
    @version 11.9.23
"""

# ---------------------------------------------------------------------------------------------
# Convert .py to .txt. Collect function names in a list.
# --> Run functions using getattr + parameters. Probably want to decorate correct functions
# --> to run using some identifiable token, e.g. foo_<original_function_name>, search for 'foo'
# Still requires running import file... amend by pushing all code into a block requiring the
# __name__ to be __main__, which would be false when running a script from a different .py file
# ---------------------------------------------------------------------------------------------

# Globals for functions
LIST_DELIMITER = ","  # Used to separate elements of a list
DATA_SEPARATOR = "|"  # Used to separate parameter values
ROW_SEPARATOR = "$"  # Used to separate rows
SET_AND_DICT_START = "{"  # Used to find beginning of set or dictionary
DICT_IDENTIFIER = ":"  # Used to differentiate between sets and dictionaries
SET_AND_DICT_END = "}"  # Used to find end of set or dictionary
TUPLE_START = "("  # Used to find beginning of tuple
TUPLE_END = ")"  # Used to find end of tuple
EXPECTED_IDENTIFIER = "EXPECTED"  # Used for expected output
# All 'foo_' functions are tested...
# Those without are not searched for
FUNCTION_NAME_IDENTIFIER = "foo_"
UNIT_TEST_TEXT_FILE_ROOT = "unit_tests_"


# Classes
class BColors:
    HEADER = '\033[95m'
    OK_BLUE = '\033[94m'
    OK_CYAN = '\033[96m'
    OK_GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    END_C = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


# Functions

# Given a string with elements separated by a delimiter, fill a list with the elements
def fill_list(list_1d, arg_line):
    str_list = arg_line.split(LIST_DELIMITER)
    for token in str_list:
        list_1d.append(token)


# Given a string with rows separated by a delimiter (ROW_SEPARATOR, and elements separated
# by a delimiter (LIST_DELIMITER), fill a 2D list with the elements
def fill_2d_list(list_2d, arg_line):
    row_text_list = arg_line.split(ROW_SEPARATOR)
    for row in row_text_list:
        row_list = []
        fill_list(row_list, row)
        list_2d.append(row_list)


def make_dct_from_text(data, args_obj_list):
    dct = eval(data.replace("'", "\""))
    args_obj_list.append(dct)


def make_tuple_from_text(data, args_obj_list):
    #  Convert text to a tuple using eval
    if LIST_DELIMITER in data:
        a_tuple = eval(data.replace("'", "\""))
        args_obj_list.append(a_tuple)
    #  Tuples of size 1 are auto-converted from being
    #  tuples to just converting to the element inside
    #  so, must manually convert for size 1
    else:
        element = data[1:len(data)-1]
        a_tuple = (eval(element),)
        args_obj_list.append(a_tuple)


def make_set_from_text(data, args_obj_list):
    a_set = eval(data.replace("'", "\""))
    args_obj_list.append(a_set)


def make_1d_list_from_text(data, args_obj_list):
    row_list = []
    fill_list(row_list, data)
    args_obj_list.append(row_list)


def make_2d_list_from_text(data, args_obj_list):
    grid_list = []
    fill_2d_list(grid_list, data)
    args_obj_list.append(grid_list)


# From a text file, get unit test input data as a list, as well as the expected value after running
# the given function
#
# @return [] --> list of unit test inputs
# @return _ --> expected output... data type varies
def get_unit_tests(text_file_name):
    # Delimiters / Tokens for scraping data
    function_args = []
    expected_list = []

    text_file = open(text_file_name, "r")
    text_lines = text_file.readlines()

    #  Go through each line
    for text_line in text_lines:
        text_line = text_line.replace("\n", "")
        args_obj_list = []
        args_list = text_line.split(DATA_SEPARATOR)
        #  Go through each parameter
        for arg_num in range(0, len(args_list)):
            line_data = args_list[arg_num]
            #  Dictionaries or Sets
            if line_data.startswith(SET_AND_DICT_START) and \
                    line_data.endswith(SET_AND_DICT_END) and \
                    EXPECTED_IDENTIFIER not in line_data:
                #  Dictionaries
                if DICT_IDENTIFIER in line_data:
                    make_dct_from_text(line_data, args_obj_list)
                #  Sets
                else:
                    make_set_from_text(line_data, args_obj_list)
            # Tuples
            elif line_data.startswith(TUPLE_START) and \
                    line_data.endswith(TUPLE_END) and \
                    EXPECTED_IDENTIFIER not in line_data:
                make_tuple_from_text(line_data, args_obj_list)
            #  2D Lists
            elif ROW_SEPARATOR in line_data and EXPECTED_IDENTIFIER not in line_data:
                make_2d_list_from_text(line_data, args_obj_list)
            #  1D Lists
            elif LIST_DELIMITER in line_data and EXPECTED_IDENTIFIER not in line_data:
                make_1d_list_from_text(line_data, args_obj_list)
            #  Same thing, but for expected values
            elif EXPECTED_IDENTIFIER in line_data:
                expected_data = line_data.replace(EXPECTED_IDENTIFIER + " ", "")
                #  Dictionaries or Sets
                if expected_data.startswith(SET_AND_DICT_START) and \
                        expected_data.endswith(SET_AND_DICT_END):
                    #  Dictionaries
                    if DICT_IDENTIFIER in expected_data:
                        make_dct_from_text(expected_data, expected_list)
                    #  Sets
                    else:
                        make_set_from_text(expected_data, expected_list)
                # Tuples
                elif expected_data.startswith(TUPLE_START) and \
                        expected_data.endswith(TUPLE_END):
                    make_tuple_from_text(expected_data, expected_list)
                #  2D Lists
                elif ROW_SEPARATOR in expected_data:
                    make_2d_list_from_text(expected_data, expected_list)
                #  1D Lists
                elif LIST_DELIMITER in expected_data:
                    make_1d_list_from_text(expected_data, expected_list)
                # Everything else
                else:
                    expected_list.append(expected_data)
            #  Everything else
            else:
                args_obj_list.append(line_data)
        #  Add list of arguments to the function arguments
        if EXPECTED_IDENTIFIER not in text_line:
            function_args.append(args_obj_list)

    return function_args, expected_list


# Round any float values or list of float values to only two decimal places. Leaves any other
# data unchanged
def round_any(value):
    if isinstance(value, float):
        value = round(value, 2)
    elif isinstance(value, list):
        if len(value) <= 0:  # Empty list
            return value
        if isinstance(value[0], list):  # 2D list
            if isinstance(value[0][0], float):  # Round decimals
                for row in range(0, len(value)):
                    for col in range(0, value[row]):
                        value[row][col] = round(value[row][col], 2)
        else:  # 1D list
            if isinstance(value[0], float):  # Round decimals
                for value_index in range(0, len(value)):
                    value[value_index] = round(value[value_index], 2)
    return value


# Convert a list of string literals to their proper data types using ast.literal_eval()
def convert_str_list_to_type(str_list):
    if not isinstance(str_list[0], list):
        for list_index in range(0, len(str_list)):
            if str_list[list_index] == '':  # Empty list
                str_list = []
                return str_list
            str_list[list_index] = ast.literal_eval(str_list[list_index])
    else:
        convert_str_2d_list_to_type(str_list)


def convert_str_2d_list_to_type(str_list):
    for row_index in range(0, len(str_list)):
        for col_index in range(0, len(str_list[row_index])):
            str_list[row_index][col_index] = ast.literal_eval(str_list[row_index][col_index])


# Returns whether a function contains an explicit return statement or not
def contains_explicit_return(f):
    return any(isinstance(node, ast.Return) for node in ast.walk(ast.parse(inspect.getsource(f))))


# Get files in current directory "C:\\Users\\Teacher Loaner\\PycharmProjects\\Checker"
mypath = os.getcwd()
only_files = [f for f in listdir(mypath) if isfile(join(mypath, f))]

# Get correct unit test files
assignment_name = input("Enter the assignment being tested:\n"
                        "(p# for project, h# for homework) - Eg. p2\n")
UNIT_TEST_TEXT_FILE_ROOT += assignment_name.lower() + "_"

# Find correct file (assuming only this file and one other .py file are in the directory),
# along with the unit test files and any other directories, such as venv
py_file_name = None
for file in only_files:
    file_name = os.path.splitext(file)
    if ".py" not in file_name:
        continue
    if "CHECKER" in file_name[0] and ".txt" not in file_name[1] \
            and "Solutions" not in file_name[0]:
        py_file_name = file_name[0] + file_name[1]
        #  print(file_name[0] + file_name[1])  # debug

# Read file and grab correct function names with the specified token
has_correct_char_decode = False
file_reader = None
lines = []
encoding_list = ['mbcs', 'utf8', 'utf_8', 'utf_16', 'cp437', 'utf16',
                 'ascii', 'big5', 'big5hkscs', 'cp037', 'cp273',
                 'cp424', 'cp500', 'cp720', 'cp737', 'cp775', 'cp850',
                 'cp852', 'cp855', 'cp856', 'cp857', 'cp858', 'cp860',
                 'cp861', 'cp862', 'cp863', 'cp864', 'cp865', 'cp866',
                 'cp869', 'cp874', 'cp875', 'cp932', 'cp949', 'cp950',
                 'cp1006', 'cp1026', 'cp1125', 'cp1140', 'cp1250',
                 'cp1251', 'cp1252', 'cp1253', 'cp1254', 'cp1255',
                 'cp1256', 'cp1257', 'cp1258', 'euc_jp', 'euc_jis_2004',
                 'euc_jisx0213', 'euc_kr', 'gb2312', 'gbk', 'gb18030',
                 'hz', 'iso2022_jp', 'iso2022_jp_1', 'iso2022_jp_2',
                 'iso2022_jp_2004', 'iso2022_jp_3', 'iso2022_jp_ext',
                 'iso2022_kr', 'latin_1', 'iso8859_2', 'iso8859_3',
                 'iso8859_4', 'iso8859_5', 'iso8859_6', 'iso8859_7',
                 'iso8859_8', 'iso8859_9', 'iso8859_10', 'iso8859_11',
                 'iso8859_13', 'iso8859_14', 'iso8859_15', 'iso8859_16',
                 'johab', 'koi8_r', 'koi8_t', 'koi8_u', 'kz1048',
                 'mac_cyrillic', 'mac_greek', 'mac_iceland',
                 'mac_latin2', 'mac_roman', 'mac_turkish',
                 'ptcp154', 'shift_jis', 'shift_jis_2004',
                 'shift_jisx0213', 'utf_32', 'utf_32_be', 'utf_32_le',
                 'utf_16_be', 'utf_16_le', 'utf_7', 'utf_8_sig']
encoding_list_index = 0
# Find the correct encoding
try:
    file_reader = open(py_file_name, "r")
    lines = file_reader.readlines()
except UnicodeDecodeError:
    while not has_correct_char_decode:
        try:
            file_reader = open(py_file_name, "r", encoding=encoding_list[encoding_list_index])
            lines = file_reader.readlines()
        except UnicodeDecodeError:
            encoding_list_index += 1
        else:
            has_correct_char_decode = True
            # print("debug: encoding is", encoding_list[encoding_list_index])
else:
    # print("debug: no encoding")
    pass
finally:
    if file_reader is None:
        print("No suitable encoding found for this file.")
        exit()

function_list = []
for line in lines:
    function_header_identifier = "def "
    if function_header_identifier in line:
        start_pos = line.find("def ") + len(function_header_identifier)
        end_pos = line.find("(", start_pos)
        function_name = line[start_pos:end_pos].strip()
        if FUNCTION_NAME_IDENTIFIER in function_name:
            function_list.append(function_name)

# Test functions using unit tests that are read from the unit test text files
# Save results of expected return values vs actual result values found when running functions
# debug: print(function_list)
index = 0
has_return_values = []
shallow_copy_problem_set = []  # Holds the final values of the inputs after the function is run
expected_return_values = []
actual_return_values = []
for x in range(0, len(function_list)):
    no_return = False  # Keeps track of whether the function has a return
    function_name_instance = function_list[x]
    unit_test_text_file_name = UNIT_TEST_TEXT_FILE_ROOT + str(index) + ".txt"
    # list_args is a 2D list, expected_value_list is a 1D list
    list_args, expected_value_list = get_unit_tests(unit_test_text_file_name)
    expected_return_values.append(expected_value_list)
    function_obj = getattr(IMPORT_NAME, function_name_instance)
    # If function does not have a return statement, make copy of original arguments and compare to
    # arguments after the function has been run
    if contains_explicit_return(function_obj):
        has_return_values.append(True)
    else:
        has_return_values.append(False)

    # Convert arguments to their proper data type
    # Convert list arguments
    for unit_test_data_list_index in range(0, len(list_args)):
        for unit_test_value_index in range(0, len(list_args[unit_test_data_list_index])):
            unit_test_value = list_args[unit_test_data_list_index][unit_test_value_index]
            if isinstance(unit_test_value, dict) or \
                    isinstance(unit_test_value, set) or \
                    isinstance(unit_test_value, tuple):
                pass  # These are already in their correct format
            elif not isinstance(unit_test_value, list):
                if isinstance(unit_test_value, str) and len(unit_test_value) == 0:
                    continue  # Do not add value. Used for functions with no parameters
                elif isinstance(unit_test_value, str):  # For Strings
                    pass
                else:
                    unit_test_value = ast.literal_eval(unit_test_value)
            else:  # Convert elements inside list to their proper type
                convert_str_list_to_type(unit_test_value)
            list_args[unit_test_data_list_index][unit_test_value_index] = unit_test_value
    # Convert expected values
    for unit_test_value_index in range(0, len(expected_value_list)):
        unit_test_value = expected_value_list[unit_test_value_index]
        if isinstance(unit_test_value, dict) or \
                isinstance(unit_test_value, set) or \
                isinstance(unit_test_value, tuple):
            pass  # These are already in their correct format
        elif isinstance(unit_test_value, str):
            if unit_test_value != 'True' and unit_test_value != 'False':
                unit_test_value = unit_test_value.lower()
        if not isinstance(unit_test_value, list):
            if isinstance(unit_test_value, dict) or \
                    isinstance(unit_test_value, set) or \
                    isinstance(unit_test_value, tuple):
                pass
            elif unit_test_value.lstrip('-').replace('.', '', 1).isdigit():
                unit_test_value = ast.literal_eval(unit_test_value)
            elif unit_test_value == 'True' or unit_test_value == 'False':
                unit_test_value = ast.literal_eval(unit_test_value)
            # else, if we do have a string, do not call ast.literal_eval, which cannot convert
            # strings to strings apparently, which is stupid
        else:  # Convert elements inside list to their proper type
            if len(unit_test_value) == 0:  # Check for empty lists
                unit_test_value = []
            elif len(unit_test_value) == 1 and \
                    (unit_test_value[0] == '' or
                     unit_test_value[0] == ""):
                unit_test_value = []
                convert_str_list_to_type(unit_test_value)
            elif len(unit_test_value) == 2 and \
                    (unit_test_value[1] == '' or
                     unit_test_value[1] == ""):
                unit_test_value.pop(1)
                if unit_test_value[0] == '' or unit_test_value[0] == "":
                    unit_test_value = []
                if len(unit_test_value) > 0:
                    convert_str_list_to_type(unit_test_value)
            else:
                convert_str_list_to_type(unit_test_value)
        expected_value_correct_data_type = round_any(unit_test_value)
        expected_value_list[unit_test_value_index] = expected_value_correct_data_type

    # Run all unit tests
    actual_value_list = []
    shallow_copy = []
    original_input_values = []
    for args in list_args:
        if has_return_values[x]:  # Grab list of non-lists
            shallow_copy.append(args)
        else:  # Grab the first list in the list of arguments
            for arg_list in args:
                if isinstance(arg_list, list):
                    shallow_copy.append(args[0])
                    break
        # Check for one parameter list with only 1 element
        # if len(args) == 2 and isinstance(args[1], str) and args[1] == "":
        #    args.pop(1)
        #    actual_value = function_obj(*args)
        # Check for lists with no elements
        if len(args) == 1 and isinstance(args[0], str) and args[0] == "":
            actual_value = function_obj()  # Functions with no parameters
        else:
            # Remove any empty strings, which come from lists with only one element
            for arg in args:
                if isinstance(arg, list) and len(arg) == 2 and isinstance(arg[1], str) and arg[1] == "":
                    arg.pop(1)
            actual_value = function_obj(*args)  # Run the function with the arguments; * expands into args
        actual_value = round_any(actual_value)  # Round to 2 decimal places, if it is a decimal
        if isinstance(actual_value, str):
            actual_value = actual_value.lower()
        actual_value_list.append(actual_value)
    actual_return_values.append(actual_value_list)
    shallow_copy_problem_set.append(shallow_copy)

    index += 1

# Check expected unit test results verses actual unit test results
score = 100
max_score_per_function = 100 / len(expected_return_values)
# Missing function
missing_problems_margin = 0
if len(expected_return_values) != len(actual_return_values):
    score -= max_score_per_function
    missing_problems_margin += len(expected_return_values) - len(actual_return_values)

for problem_number in range(0, len(expected_return_values) - missing_problems_margin):
    total_unit_tests = len(expected_return_values[problem_number])
    points_per_unit_test = max_score_per_function / total_unit_tests
    points_per_problem = 0
    for unit_test_number in range(0, total_unit_tests):
        expected_result = expected_return_values[problem_number][unit_test_number]
        actual_result = actual_return_values[problem_number][unit_test_number]
        function_name_sans_foo = function_list[problem_number].replace("foo_", "")
        if not has_return_values[problem_number]:  # Compare expected input and input state instead
            actual_result = shallow_copy_problem_set[problem_number][unit_test_number]
        if actual_result == expected_result:
            print("Unit test #", problem_number, " for ", function_name_sans_foo, " function:\n",
                  f"{BColors.OK_GREEN}Passed!{BColors.END_C}", " Expected: ", expected_result,
                  ", Found: ", actual_result, sep='')
            points_per_problem += points_per_unit_test
        else:
            print("Unit test #", problem_number, " for ", function_name_sans_foo, " function:\n",
                  f"{BColors.FAIL}Fail!{BColors.END_C}", " Expected: ", expected_result, ", Found: ", actual_result,
                  sep='')
            score -= points_per_unit_test
    print("\n#", problem_number, f"{BColors.OK_BLUE} score: {BColors.END_C}", round(points_per_problem, 2),
          "/", round(max_score_per_function, 2), "\n", sep='', end='\n')

# Print final score results
student_name = py_file_name.split(".")[0]
score = round(score, 2)
print(student_name, f"{BColors.OK_BLUE} score: {BColors.END_C}", score, sep='')
