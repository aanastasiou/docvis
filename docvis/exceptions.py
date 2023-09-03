"""
Hierarhcy of exceptions to specify DocVis' errors.

:author: Athanasios Anastasiou
:date: July 2023
"""

class DocVisError(Exception):
    pass

class TemplatePreprocError(DocVisError):
    """
    Collects a list of errors encountered during template preprocessing.
    """
    def __init__(self, errors):
        self._errors = errors

class VariableNotFoundError(DocVisError):
    pass

class FunDSLSyntaxError(DocVisError):
    pass


