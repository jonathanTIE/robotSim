from ecal.core import core as ecal_core
from ecal.core.service import Server
from time import sleep

class LuaInterpreterService(Server):
    def __init__(self):
        super().__init__("lua_interpreter")
        super().add_method_callback(method_name="lua_test", 
                                    req_type="",
                                    resp_type="",
                                    callback=self.handle_request)

    def handle_request(self, method_name, req_type, resp_type, request):
        # Add your code to handle the request here
        # For example, you can evaluate the Lua code and return the result
        print(request)
        result = ""
        return result

if __name__ == "__main__":
    # Initialize eCAL
    ecal_core.initialize([], "Lua Interpreter Server")

    # Create the LuaInterpreterService instance
    service = LuaInterpreterService()

    # Run the eCAL main loop
    while ecal_core.ok():
        sleep(0.1)

    # Cleanup eCAL
    ecal_core.finalize()
