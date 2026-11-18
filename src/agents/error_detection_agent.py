def error_detection_agent(execution_result):
    """
    Checks whether SQL execution was successful.
    """

    if execution_result["success"]:
        return {
            "has_error": False,
            "error": None
        }

    return {
        "has_error": True,
        "error": execution_result["error"]
    }

if __name__ == "__main__":

    # Test 1: Successful SQL execution
    success_result = {
        "success": True
    }

    print("Test 1:", error_detection_agent(success_result))

    # Test 2: Failed SQL execution
    failure_result = {
        "success": False,
        "error": "no such column: customer"
    }

    print("Test 2:", error_detection_agent(failure_result))