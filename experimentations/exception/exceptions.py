import traceback
from typing import Optional, Dict, Any
import json

def format_exception(e: Exception) -> Dict[str, Any]:
    """
    Extracts the innermost traceback frame from `e` and returns
    a dict containing the error message, file, line number, function name,
    and source code context.
    """
    tb_list = traceback.extract_tb(e.__traceback__ or None)
    if not tb_list:
        return {"error": str(e)}
    filename, lineno, funcname, text = tb_list[-1]
    return {
        "error":str(e),
        "file":filename,
        "line":lineno,
        "function":funcname,
        "code_context": text.strip() if text else None,
    }