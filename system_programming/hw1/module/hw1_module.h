#ifndef MYMOD_H
#define MYMOD_H

#include <linux/types.h>
#include <uapi/linux/sched.h>

#define HW1_NAME "hw1"
#define TOP_NAME "top"
#define NUMBER_OF_WORKS 10
#define MAX_NUMBER_OF_CPUS 256

#ifndef NS
#define NS 1000000
#endif

#ifndef TASK_COMM_LEN
#define TASK_COMM_LEN 16
#endif

struct recent_task{
	pid_t pid;
	unsigned int policy;
	char comm[TASK_COMM_LEN];
	u64 start_time;
};

struct cpu_recent_tasks{
	struct recent_task rt[NUMBER_OF_WORKS];
};

char RT[3] ="RT",CFS[3] ="CFS";
#endif
