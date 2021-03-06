

#include <cinttypes>
#include <memory>

#include "sparta/TreeNode.h"
#include "sparta/ParameterSet.h"
#include "sparta/Resource.h"
#include "sparta/ports/PortSet.h"
#include "sparta/ports/DataPort.h"

// Include Event.h
#include "sparta/events/Event.h"

class MyDeviceParams : public sparta::ParameterSet
{
public:
    MyDeviceParams(sparta::TreeNode* n) :
        sparta::ParameterSet(n)
    {

        auto a_dumb_true_validator = [](bool & val, const sparta::TreeNode*)->bool {
            // Really dumb validator
            if(val == true) {
                return true;
            }
            return false;
        };
        my_device_param.addDependentValidationCallback(a_dumb_true_validator,
                                                       "My device parameter must be true");
    }
    PARAMETER(bool, my_device_param, true, "An example device parameter");
};

class MyDevice : public sparta::Resource
{
public:
    MyDevice(sparta::TreeNode * parent_node,
             const MyDeviceParams * my_params);

    //! \brief Name of this resource. Required by sparta::ResourceFactory
    static const char * name;

private:
    // A port set of my ports
    sparta::PortSet              my_ports_;

    // A data in port that receives uint32_t
    sparta::DataInPort<uint32_t> a_delay_in_;

    // The callback to receive data from a sender
    void myDataReceiver_(const uint32_t & dat);

    // An event to be scheduled in the sparta::SchedulingPhase::Tick
    // phase if data is received
    sparta::EventSet event_set_;
    sparta::Event<> event_do_some_work_{&event_set_, "do_work_event",
            CREATE_SPARTA_HANDLER(MyDevice, doSomeWork_)};

    // Method called by the event 'event_do_some_work_'
    void doSomeWork_();
};

// Source
const char * MyDevice::name = "my_device";

MyDevice::MyDevice(sparta::TreeNode * my_node,
                   const MyDeviceParams * my_params) :
    sparta::Resource(my_node, name),
    my_ports_(my_node, "MyDevice Ports"),
    a_delay_in_(&my_ports_, "a_delay_in", 1), // Receive data one cycle later
    event_set_(my_node)
{
    // Tell SPARTA to ignore this parameter
    my_params->my_device_param.ignore();

    // Register the callback
    a_delay_in_.registerConsumerHandler(CREATE_SPARTA_HANDLER_WITH_DATA(MyDevice, myDataReceiver_, uint32_t));
}

// This function will be called when a sender with a DataOutPort
// sends data on its out port.  An example would look like:
//
//     a_delay_out.send(1234);
//
void MyDevice::myDataReceiver_(const uint32_t & dat)
{
    std::cout << "I got data: " << dat << std::endl;
    std::cout << "Time to do some work this cycle: "
              << getClock()->currentCycle() << std::endl;
    // Schedule doSomeWork_() for THIS cycle -- implicit precedence, BTW!
    event_do_some_work_.schedule();
}

// Called from the scheduler; scheduled by the event_do_some_work_
// event.
void MyDevice::doSomeWork_() {
    std::cout << "Well, it's time to do some work. Cycle:"
              << getClock()->currentCycle() << std::endl;
}
