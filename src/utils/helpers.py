# src/utils/helpers.py
import traceback

def handle_error(exception):
    traceback.print_exc()
    # Could add more error handling, like showing a message box