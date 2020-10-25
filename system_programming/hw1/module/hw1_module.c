#include "hw1_module.h"
#include <linux/module.h>
#include <linux/proc_fs.h>
#include <linux/seq_file.h>
#include <linux/cpumask.h>
#include <linux/jiffies.h>
#include <linux/sched/signal.h>
#include <linux/sched.h>
#include <linux/kernel.h>
#include <linux/string.h>
#include <linux/pid.h>
MODULE_AUTHOR("PAK, HyungChul");
MODULE_LICENSE("GPL");
extern struct cpu_recent_tasks crts[MAX_NUMBER_OF_CPUS];
static void print_bar(struct seq_file *s);
/**
 * This function is called at the beginning of a sequence.
 * ie, when:
 * − the /proc file is read (first time)
 * − after the function stop (end of sequence)
 *
 */
static void *seq_start(struct seq_file *s, loff_t *pos)
{
    static unsigned long counter = 0;
    /* beginning a new sequence ? */
    if (*pos == 0)
    {
        /* yes => return a non null value to begin the sequence */
        return &counter;
    }
    else
    {
        /* no => it's the end of the sequence, return end to stop reading */
        *pos = 0;
        return NULL;
    }
}

/**
 * This function is called after the beginning of a sequence.
 * It's called untill the return is NULL (this ends the sequence).
 *
 */
static void *seq_next(struct seq_file *s, void *v, loff_t *pos)
{
    unsigned long *tmp_v = (unsigned long *)v;
    (*tmp_v)++;

    (*pos)++;
    return NULL;
}

/**
 * This function is called at the end of a sequence
 *
 */
static void seq_stop(struct seq_file *s, void *v)
{
    /* nothing to do, we use a static value in start() */
}

static void print_bar(struct seq_file *s){
	int i;
	for(i = 0 ; i< 40; ++i) seq_printf(s, "-");
	seq_printf(s,"\n");
}
/**
 * This function is called for each "step" of a sequence
 *
 */
static int top_seq_show(struct seq_file *s, void *v)
{
    loff_t *spos = (loff_t *) v;
	int total_task_num=0;
	{
		struct task_struct *task;
		for_each_process(task){
			total_task_num++;
		}
	}
	print_bar(s);
	seq_printf(s, "[System Programming Assignment 1]\n");
	seq_printf(s, "ID: 2015147514, Name: Pak, HyungChul\n");
	seq_printf(s, "Total %d tasks, %dHz\n", total_task_num, HZ);
	print_bar(s);
	{
		int cpu_num = num_online_cpus();
		int cpu_id;
		for(cpu_id=0; cpu_id<cpu_num; cpu_id++){
			seq_printf(s, "CPU %d\n", cpu_id);
			print_bar(s);
			{
				int task_order;
				for(task_order=0; task_order<NUMBER_OF_WORKS; task_order++){
					struct recent_task *cur_task = &crts[cpu_id].rt[task_order];
					char sched_type[3];
					if(cur_task->policy ==  SCHED_NORMAL|| cur_task->policy == SCHED_BATCH){
						int i;
						for(i=0; i<3;i++){
							sched_type[i] = CFS[i];
						}
					}else{
						int i;
						for(i=0 ; i<3; i++){
							sched_type[i] = RT[i];
						}
					}

					seq_printf(s, "%16s %6d %12lld %3s\n", cur_task->comm, cur_task->pid, cur_task->start_time/NS,sched_type); 
				}
				print_bar(s);
			}
		}
	}
    return 0;
}

static struct seq_operations top_seq_ops = {
    .start = seq_start,
    .next = seq_next,
    .stop = seq_stop,
    .show = top_seq_show
};


static int top_proc_open(struct inode *inode, struct file *file) {
	return seq_open(file, &top_seq_ops);
}

static const struct file_operations top_file_ops = {
    .owner = THIS_MODULE,
    .open = top_proc_open,
    .read = seq_read,
    .llseek = seq_lseek,
    .release = seq_release
};

static int pid_seq_show(struct seq_file *s, void *unused){
	print_bar(s);
	seq_printf(s, "[System Programming Assignment 1]\n");
	seq_printf(s, "ID: 2015147514, Name: Pak, HyungChul\n");
	print_bar(s);
	{
		char * file_name = s->file->f_path.dentry->d_name.name;
		pid_t find_pid;
		sscanf(file_name, "%d", &find_pid);
		struct task_struct *task;
		for_each_process(task){
			if(task->pid == find_pid){
				char sched_type[3];
				if(task->policy ==  SCHED_NORMAL|| task->policy == SCHED_BATCH){
					int i;
					for(i=0; i<3;i++){
						sched_type[i] = CFS[i];
					}
				}else{
					int i;
					for(i=0 ; i<3; i++){
						sched_type[i] = RT[i];
					}
				}
				seq_printf(s, "Command: %s\nType: %s\nPID: %d\n", task->comm, sched_type,task->pid);
				seq_printf(s, "Start Time: %lld (ms)\n", task->start_time/NS);
				seq_printf(s, "Last Scheduled Time: %lld (ms) \n", task->se.exec_start/NS);
				seq_printf(s, "Last CPU #: %d\nPriority: %d\n",task->recent_used_cpu,task->static_prio);
				seq_printf(s, "Total Execution Time: %d (ms)\n", task->total_cpu_sum_exec_time/NS);
				{
					const unsigned int cpu_count = num_online_cpus();
					int i;
					for(i=0;i<cpu_count;i++){
						seq_printf(s, "- CPU %d: %d (ms)\n",i, task->cpu_exec_time[i]/NS);
					}
				}
				if(task->policy == SCHED_NORMAL||task->policy == SCHED_BATCH){
					seq_printf(s, "Weight: %d\n", task->se.load.weight);
					seq_printf(s, "Virtual Runtime: %d\n", task->se.vruntime);
				}
				break;
			}
		}
		
	}
	return 0;
}

static struct seq_operations pid_seq_ops = {
	.start = seq_start,
	.next = seq_next,
	.stop = seq_stop,
	.show = pid_seq_show
};

static int pid_proc_open(struct inode *inode, struct file *file){
	return seq_open(file, &pid_seq_ops);
}

static const struct file_operations pid_file_ops ={
	.owner = THIS_MODULE,
	.open = pid_proc_open,
	.read = seq_read,
	.llseek = seq_lseek,
	.release = seq_release
};

static int __init hw1_init(void) {
    struct proc_dir_entry *hw1_dir_entry, *top_file_entry, *pid_file_entry[1000];
	hw1_dir_entry = proc_mkdir(HW1_NAME, NULL);
    top_file_entry = proc_create(TOP_NAME, 0, hw1_dir_entry, &top_file_ops);
	{
		struct task_struct *task;
		int file_id =0;
		char str[10];
		for_each_process(task){
			sprintf(str, "%d" ,task->pid);
			pid_file_entry[file_id] = proc_create(str, 0, hw1_dir_entry, &pid_file_ops);
			file_id++;
		}
	}
    return 0;
}

static void __exit hw1_exit(void) {
    remove_proc_entry(HW1_NAME, NULL);
}

module_init(hw1_init);
module_exit(hw1_exit);
