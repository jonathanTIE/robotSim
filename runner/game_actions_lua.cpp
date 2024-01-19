#include "game_actions_lua.h"


uint64_t get_time() {
     using namespace std::chrono;
     return duration_cast<milliseconds>(system_clock::now().time_since_epoch()).count();
}

#define X(action_name, function, ARGUMENTS, OUTPUT) \
        static int game_action_ ## action_name ## _lua(lua_State *L) \
        { \
            int arg_id = 1; \
            (void)arg_id; \
            struct GAME_ACTION_ARGUMENTS_STRUCT_NAME(action_name) args; \
        ARGUMENTS \
            struct GAME_ACTION_OUTPUT_STRUCT_NAME(action_name) output; \
            output = game_action_ ## action_name(args); \
            (void)output; \
            int number_of_return_values = 0; \
        OUTPUT \
            return number_of_return_values; \
        }

#define X_FLOAT_ARGS(parameter_name) \
        if (!lua_isnumber(L, arg_id) && !lua_isnil(L, arg_id)) { \
            lua_pushstring(L, "Invalid argument: not a valid number for " # parameter_name); \
            lua_error(L); \
        } \
        if (lua_isnil(L, arg_id)) { \
            args.parameter_name = NAN; \
            arg_id++; \
        } else { \
            args.parameter_name = lua_tonumber(L, arg_id++); \
        }
#define X_INT_ARGS(parameter_name) \
        if (!lua_isinteger(L, arg_id)) { \
            lua_pushstring(L, "Invalid argument: not a valid integer for " # parameter_name); \
            lua_error(L); \
        } \
        args.parameter_name = lua_tointeger(L, arg_id++);
#define X_BOOL_ARGS(parameter_name) \
        if (!lua_isboolean(L, arg_id)) { \
            lua_pushstring(L, "Invalid argument: not a valid boolean for " # parameter_name); \
            lua_error(L); \
        } \
        args.parameter_name = lua_toboolean(L, arg_id++);
#define X_STR_ARGS(parameter_name) \
        if (!lua_isstring(L, arg_id)) { \
            lua_pushstring(L, "Invalid argument: not a valid string for " # parameter_name); \
            lua_error(L); \
        } \
        args.parameter_name = lua_tostring(L, arg_id++);

#define X_FLOAT_OUTPUT(parameter_name) \
        lua_pushnumber(L, output.parameter_name); \
        number_of_return_values++;
#define X_INT_OUTPUT(parameter_name) \
        lua_pushinteger(L, output.parameter_name); \
        number_of_return_values++;
#define X_BOOL_OUTPUT(parameter_name) \
        lua_pushboolean(L, output.parameter_name); \
        number_of_return_values++;

DEFINE_GAME_ACTION_FUNCTIONS
#undef X

void register_lua_functions(lua_State* L)
{
    #define X(action_name, function, ARGUMENTS, OUTPUT) \
        lua_pushcfunction(L, game_action_ ## action_name ## _lua); \
        lua_setglobal(L, #action_name);


    DEFINE_GAME_ACTION_FUNCTIONS
    #undef X
}