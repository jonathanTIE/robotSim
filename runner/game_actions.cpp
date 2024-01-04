#include "game_actions.h"
#include "simu_core.h"
#include <stdexcept>
#include <thread>

struct GAME_ACTION_OUTPUT_STRUCT_NAME(set_pose) game_action_set_pose(struct GAME_ACTION_ARGUMENTS_STRUCT_NAME(set_pose) args)
{
    pose_t target{};
    target.x = args.x;
    target.y = args.y;
    target.theta = args.theta;
    nav.set_pose(&target);
    struct GAME_ACTION_OUTPUT_STRUCT_NAME(set_pose) result;
    return result;
}

struct GAME_ACTION_OUTPUT_STRUCT_NAME(get_pose) game_action_get_pose(struct GAME_ACTION_ARGUMENTS_STRUCT_NAME(get_pose) args)
{
    struct GAME_ACTION_OUTPUT_STRUCT_NAME(get_pose) result {};
    pose_t current_pose = nav.get_current_pose();
    result.x = current_pose.x;
    result.y = current_pose.y;
    result.theta = current_pose.theta;
    return result;
}

struct GAME_ACTION_OUTPUT_STRUCT_NAME(overwrite_pose) game_action_overwrite_pose(struct GAME_ACTION_ARGUMENTS_STRUCT_NAME(overwrite_pose) args)
{
    pose_t target{};
    target.x = args.x;
    target.y = args.y;
    target.theta = args.theta;
    nav.overwrite_current_pose(&target);
    struct GAME_ACTION_OUTPUT_STRUCT_NAME(overwrite_pose) result;
    return result;
}

struct GAME_ACTION_OUTPUT_STRUCT_NAME(stop_motion) game_action_stop_motion(struct GAME_ACTION_ARGUMENTS_STRUCT_NAME(stop_motion) args)
{
    nav.stop_motion();
    struct GAME_ACTION_OUTPUT_STRUCT_NAME(stop_motion) result;
    return result;
}

struct GAME_ACTION_OUTPUT_STRUCT_NAME(is_motion_done) game_action_is_motion_done(struct GAME_ACTION_ARGUMENTS_STRUCT_NAME(is_motion_done) args)
{
    struct GAME_ACTION_OUTPUT_STRUCT_NAME(is_motion_done) result;
    result.motion_done = nav.is_motion_done();
    return result;
}

#define PERIPHERAL_CHANNEL_OFFSET 10
struct GAME_ACTION_OUTPUT_STRUCT_NAME(set_pump) game_action_set_pump(struct GAME_ACTION_ARGUMENTS_STRUCT_NAME(set_pump) args)
{
    std::logic_error("Not implemented set_pump for simulation");
    //if (args.channel < PERIPHERAL_CHANNEL_OFFSET) {
    //    set_stepper_board_pump(args.channel, args.value);
    //}
    //else {
    //    set_peripherals_pump(args.channel - PERIPHERAL_CHANNEL_OFFSET, args.value);
    //}
    struct GAME_ACTION_OUTPUT_STRUCT_NAME(set_pump) result;
    return result;
}

struct GAME_ACTION_OUTPUT_STRUCT_NAME(move_stepper) game_action_move_stepper(struct GAME_ACTION_ARGUMENTS_STRUCT_NAME(move_stepper) args)
{
    std::logic_error("Not implemented move_stepper for simulation");
    //move_stepper_board_motor(args.channel, args.target, args.speed);
    struct GAME_ACTION_OUTPUT_STRUCT_NAME(move_stepper) result;
    return result;
}

struct GAME_ACTION_OUTPUT_STRUCT_NAME(move_servo) game_action_move_servo(struct GAME_ACTION_ARGUMENTS_STRUCT_NAME(move_servo) args)
{
    std::logic_error("Not implemented move_servo for simulation");
    //set_peripherals_servo_channel(args.channel, args.value);
    struct GAME_ACTION_OUTPUT_STRUCT_NAME(move_servo) result;
    return result;
}

struct GAME_ACTION_OUTPUT_STRUCT_NAME(reset_stepper) game_action_reset_stepper(struct GAME_ACTION_ARGUMENTS_STRUCT_NAME(reset_stepper) args)
{
    std::logic_error("Not implemented function (actuator) for simulation");

    //define_stepper_board_motor_home(args.channel, args.value);
    struct GAME_ACTION_OUTPUT_STRUCT_NAME(reset_stepper) result;
    return result;
}

struct GAME_ACTION_OUTPUT_STRUCT_NAME(get_button) game_action_get_button(struct GAME_ACTION_ARGUMENTS_STRUCT_NAME(get_button) args)
{
    std::logic_error("Not implemented function (actuator) for simulation");

    struct GAME_ACTION_OUTPUT_STRUCT_NAME(get_button) result;
    //result.status = read_switch(args.channel);
    return result;
}

struct GAME_ACTION_OUTPUT_STRUCT_NAME(sleep) game_action_sleep(struct GAME_ACTION_ARGUMENTS_STRUCT_NAME(sleep) args)
{
    std::this_thread::sleep_for(std::chrono::milliseconds((int)args.delay * 1000));

    struct GAME_ACTION_OUTPUT_STRUCT_NAME(sleep) result;
    return result;
}

struct GAME_ACTION_OUTPUT_STRUCT_NAME(get_time) game_action_get_time(struct GAME_ACTION_ARGUMENTS_STRUCT_NAME(get_time) args)
{
	struct GAME_ACTION_OUTPUT_STRUCT_NAME(get_time) result;
    result.time = 0; // time();
	return result;
}