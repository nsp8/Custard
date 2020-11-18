from datetime import datetime as dt
import ast
import json
import os
import re
import pandas as pd
from constants import COLUMN_IDENTIFIER


def printf(statement, file_type="CE"):
    """
    A utility function to create custom debug log files, separated by minutes.
    """
    def get_timestamp():
        return f"{dt.now().year}_{dt.now().month}_{dt.now().day}_" \
               f"{dt.now().hour}_{dt.now().minute}"

    def get_file_version(parent_path, file_prefix):
        """
        Facilitates versioning of the files/folders.
        """
        children = os.listdir(parent_path)
        versions = list()
        for file in children:
            if os.path.isfile(os.path.join(parent_path, file)):
                match = re.search(rf"{file_prefix}_(\d+).txt", file)
                if match:
                    current_version = match.groups()[0]
                    versions.append(int(current_version))
        return max(versions) + 1 if versions else 0

    timestamp = str(dt.now().replace(microsecond=0))
    logs_path = os.path.join(os.getcwd(), "Logs")
    # version = get_file_version(logs_path, "print_logs")
    version = f'{file_type}_{get_timestamp()}'
    file_path = os.path.join(logs_path, f"{version}.txt")
    mode = "a" if os.path.lexists(file_path) else "w"
    with open(file_path, mode) as f:
        f.write(f"\n{timestamp}: {statement}")


def is_column_valid(column: str, match_rule: str):
    """
    Validates if the column follows a format according to the series-type.
    See constants.py for the RegExp formats with each series type.

    :column - name of the column
    :match_rule - pattern defined for the series-type.
    """
    pattern = rf"{match_rule}"
    if re.search(pattern, column):
        return True
    return False


def append_blank_rows(data_frame: pd.DataFrame, rows=1):
    """
    Utility function that appends blank rows in the case of shifting rows.
    """
    df_dict = data_frame.to_dict(orient="records")
    for _ in range(rows):
        new_row = {col: "" for col in data_frame.columns}
        df_dict.append(new_row)
    return pd.DataFrame(df_dict)


def append_columns(data_frame: pd.DataFrame, series_type: str, cols=1):
    """
    Utility function that appends blank columns in the case of shifting data.
    """
    data_frame_copy = data_frame.copy()
    last_col = data_frame_copy.columns[-1]
    column_identifier = COLUMN_IDENTIFIER.get(series_type)
    if is_column_valid(last_col, column_identifier):
        if series_type == "Annual":
            if last_col.isdigit():
                for i in range(1, cols + 1):
                    next_column = f"{int(last_col) + i}"
                    data_frame_copy[next_column] = ""
        else:
            def month_format(month):
                return f"0{month}" if month < 10 else f"{month}"
            separator = column_identifier.get("separator")
            year, period = re.split(separator, last_col)
            year, period = int(year), int(period)
            frequency = column_identifier.get("frequency")
            print(f"year = {year} period = {period}")
            for i in range(1, cols + 1):
                print(f"\ti = {i}")
                period_increment = (period + i) % frequency
                print(f"\tperiod_increment = {period_increment}")
                if not period_increment:
                    period_increment = frequency
                year = year + 1 if period_increment == 1 else year
                print(f"\tyear_increment = {year}")
                period_string = str(period_increment)
                if series_type == "Monthly":
                    period_string = month_format(period_increment)
                new_split = (str(year), period_string)
                print(f"\t{new_split}")
                next_column = column_identifier["separator"].join(new_split)
                data_frame_copy[next_column] = ""
    return data_frame_copy


def get_first_column(df, series_type):
    """
    Gets the first column from the DataFrame which follows the rule defined
    in the constants.py file for the series-type.

    :df - DataFrame from where the column is to be fetched.
    :series_type - type of series that the data_frame belongs to. Values
    should be either 'Annual', 'Quarterly' or 'Monthly'.
    """
    pattern = COLUMN_IDENTIFIER.get(series_type).get("pattern")
    _cols = [c for c in map(lambda s: is_column_valid(s, pattern), df.columns)]
    return _cols.index(True)


def assemble(ast_object):
    """
    Assembles the parts of an AST object according to its type, back into a
    string.
    """
    if isinstance(ast_object, ast.Str):
        return f"'{ast_object.s}'"
    if isinstance(ast_object, ast.Num):
        return f"'{ast_object.n}'"
    if isinstance(ast_object, ast.Name):
        return ast_object.id
    if isinstance(ast_object, ast.Call):
        _args = [a for a in map(assemble, ast_object.args)]
        _args = ','.join(_args)
        _func = assemble(ast_object.func)
        _kwds = [f"{k.arg}='{k.value.s}'" for k in ast_object.keywords]
        if _kwds:
            _kwds = ','.join(_kwds)
            return f"{_func}({_args},{_kwds})"
        return f"{_func}({_args})"
    if isinstance(ast_object, ast.And):
        return " and "
    if isinstance(ast_object, ast.Or):
        return " or "
    if isinstance(ast_object, ast.UAdd):
        return "+"
    if isinstance(ast_object, ast.USub):
        return "-"
    if isinstance(ast_object, ast.UnaryOp):
        _op = assemble(ast_object.op)
        _val = re.sub(r"[\'\"]", "", assemble(ast_object.operand))[0]
        return f"'{_op}{_val}'"
    if isinstance(ast_object, ast.Attribute):
        return f"{assemble(ast_object.value)}.{ast_object.attr}"
    if isinstance(ast_object, ast.Subscript):
        _args = [a for a in map(assemble, ast_object.slice.value.elts)]
        _args = ','.join(_args)
        _target = assemble(ast_object.value)
        return f"{_target}[{_args}]"
    if isinstance(ast_object, ast.BoolOp):
        _expr = list()
        for value in ast_object.values:
            _expr.append(assemble(value))
        _join = assemble(ast_object.op).join(_expr)
        return _join


def update_variable(var_value):
    """
    Function to update the current execution string in the JSON file
    ("variable.json").
    :var_value - string of the value to update
    """
    _var = dict()
    _path = os.path.join(os.getcwd(), "variable.json")
    # printf(f"previous_value: {get_variable()}")
    with open(_path, "w") as wf:
        _var.setdefault("current_execution", var_value)
        # printf(f"updated_value: {_var}")
        json.dump(_var, wf)


def get_variable():
    """
    Function to get the current execution string from the JSON file
    ("variable.json").
    """
    _path = os.path.join(os.getcwd(), "variable.json")
    if os.path.lexists(_path):
        with open(_path) as f:
            prev_value = json.load(f)
            return prev_value
    return dict()


def parse_current_variable(var_str):
    """
    Function to parse the current execution string from the JSON file
    ("variable.json").
    """
    # REGEX-extraction implementation
    """
    _pattern = r".at(\[\s*([\'\"]\s*\w+\s*[\'\"])\s*," \
               r"\s*([\'\"]\s*\w+\s*[\'\"])\s*\]\s*)="
    _match = re.search(_pattern, str(var_str))
    if _match:
        _code = _match.groups()[1]
        _code = re.subn(r"[\'\"]", "", _code)[0]
        return _code
    return None
    """
    # AST-extraction implementation
    _module = ast.parse(var_str, "<string>", "exec")
    _target = assemble(_module.body[0].targets[0])
    _match = re.search(r"\[(.*)\]", _target)
    if _match:
        _group = _match.groups()[0]
        _first = _group.split(",")[0]
        _code = re.subn(r"[\'\"]", "", _first)[0]
        return _code
    return None
