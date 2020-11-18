import ast
import util

EXPRESSION = None
VALUE = None
VARIABLE = None


def process_statement(variable_string):
    """
    Processes the current statement being executed and checks for the
    presence of if-else conditionals, returns base string accordingly.
    :variable_string - String value of the current statement being executed
    """
    global EXPRESSION
    global VALUE
    global VARIABLE

    def parse_if_expression(exp):
        """
        Parses an AST expression recursively to reduce the if-else statements.
        :exp - an AST object from a string of Python expression.
        """
        if isinstance(exp, ast.IfExp):
            _cond = util.assemble(exp.test)
            _test = f"VARIABLE = {_cond}"
            exec(compile(_test, "<string>", "exec"), globals())
            if VARIABLE:
                VALUE = util.assemble(exp.body)
            else:
                VALUE = parse_if_expression(exp.orelse)
        else:
            VALUE = util.assemble(exp)
        return VALUE

    def get_output(exp):
        """
        Adds the output property to the parameters of the type Function,
        to get the executed value, otherwise the object itself.
        :exp - rvalue of the expression.
        """
        _mod = ast.parse(exp, "<string>", "exec")
        if isinstance(_mod.body[0].value, ast.Call):
            if util.assemble(_mod.body[0].value.func) in dir(cf):
                return f"{exp}.output"
        return util.assemble(exp)

    module_object = ast.parse(variable_string, "<string>", "exec")
    _root = module_object.body[0]
    final_result = parse_if_expression(_root.value)
    assign_part = ""
    if hasattr(_root, "targets"):
        assign_part = f"{util.assemble(_root.targets[0])}="
    util.update_variable(f"{assign_part}{final_result}")
    _expression = f"EXPRESSION = {get_output(final_result)}"
    exec(compile(_expression, "<string>", "exec"), globals())
    final_result = f"{assign_part}{EXPRESSION}"
    return final_result
