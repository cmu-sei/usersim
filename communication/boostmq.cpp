// Copyright 2017 Carnegie Mellon University. See LICENSE.md file for terms.

#define BUFFSIZE 50010
#define BOOST_DATE_TIME_NO_LIB

#include <boost/python.hpp>
#include <boost/python/module.hpp>
#include <boost/python/def.hpp>
#include <iostream>
#include <string>
#include <boost/interprocess/ipc/message_queue.hpp>

using namespace boost::interprocess;

class MQ
{
	public:
	MQ(const char* name, unsigned int max_msg_num, size_t max_msg_size)
	{
		mq = new message_queue(open_or_create, name, max_msg_num, max_msg_size);
		queue_name = name;
        //msg_size = max_msg_size;
        msg_size = mq->get_max_msg_size();
	}
	
	~MQ()
	{
		delete mq;
	}
	
	std::string receivequeue_noblock()
	{
		char buff[BUFFSIZE];
		unsigned int priority;
		size_t rec_size;
		if (mq->try_receive(buff, sizeof(char) * BUFFSIZE, rec_size, priority))
			{
				buff[rec_size] = '\0';
			}
		else
			{
				buff[0] = '\0';
			}
		std::string retval(buff);
		return retval;
	}
	
	std::string receivequeue()
	{
		char buff[BUFFSIZE];
		unsigned int priority;
		size_t rec_size;
		mq->receive(buff, sizeof(char) * BUFFSIZE, rec_size, priority);
		buff[rec_size] = '\0';
		std::string retval(buff);
		return retval;
	}
	
	void sendqueue (char* msg, int priority)
	{
        /* Sending a message larger than a queue message can hold breaks the queue so let's make sure that doesn't
         * happen.
         */
        // +1 for terminating null.
        size_t msglen = strlen(msg) + 1;
        if (msglen <= msg_size) {
            mq->send(msg, (sizeof(char) * msglen), priority);
        }
	}
	
	void killqueue()
	{
		message_queue::remove(queue_name);
	}
	
	private:
	message_queue *mq;
	const char* queue_name;
    size_t msg_size;
};


BOOST_PYTHON_MODULE(boostmq)
{
    using namespace boost::python;
    class_<MQ>("MQ", init<const char*, unsigned int, unsigned int>())
        .def("receivequeue_noblock", &MQ::receivequeue_noblock)
		.def("killqueue", &MQ::killqueue)
		.def("receivequeue", &MQ::receivequeue)
		.def("sendqueue", &MQ::sendqueue)
    ;
}
