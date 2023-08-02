from subprocess import call, PIPE, run
import json, time
import matplotlib.pyplot as plt

# write the docker ps metrics into db file
def main() :
    while True :
        result = run(["docker", "ps", "-a"], stdout=PIPE, stderr=PIPE, universal_newlines=True)
        error_msg = ""
        if not str(result.stderr) == "" :
            error_msg += "\nError : \n" + str(result.stderr)
        # std out
        result = str(result.stdout).split("\n")
        now_time = str(time.time())
        content = {now_time : []}
        #print(str(result) + error_msg)
        container_id = []
        # get container id
        for i in range(1, len(result)-1) :
            container_id.append(str(result[i]).split(" ")[0])
        # write docker container info into file
        for container in container_id :
            result = run(["docker", "inspect", container], stdout=PIPE, stderr=PIPE, universal_newlines=True)
            result = json.loads(result.stdout)[0]
            content[now_time].append(str(result["Name"]) + " " + str(result["State"]["Running"]))
        # file of storing the docker container info
        db_file = open("./db/dockerContainer.dat")
        origin_content = json.load(db_file)
        # check whether the number of containers have changed compare to last metrics
        checkContainerNumber(origin_content[len(origin_content)-1:][0], content[now_time])
        origin_content.append(content)
        db_file.close()
        """
        db_file = open("./db/dockerContainer.dat", "w")
        json.dump(origin_content, db_file)
        db_file.close()
        """
        time.sleep(5)

# check whether the number of containers have changed compare to last metrics
def checkContainerNumber(docker_last_history, content) :
    print(docker_last_history)
    # key is the time found this metrics
    for key in docker_last_history.keys() :
        if not len(docker_last_history[key]) == len(content) :
            return False
        # last record
        last_name = []
        last_running = []
        for i in range(len(docker_last_history[key])) :
            last = docker_last_history[key][i].split(" ")
            last_name.append(last[0])
            last_running.append(last[1])
        # current record
        cur_name = []
        cur_running = []
        for i in range(len(content)) :
            cur = content[i].split(" ")
            cur_name.append(cur[0])
            cur_running.append(cur[1])
        for i in range(len(last_name)) :
            container_name = last_name[i]
            # check whether the past container name not exist in new record
            if container_name not in cur_name :
                print("Container not Existed !")
                print(container_name)
            # still existed then check whether it still running
            else :
                # container index in current record
                cur_index = cur_name.index(container_name)
                # 
                if last_running[i] == cur_running[cur_index] :
                    continue
                else :
                    # running convert to not running
                    if last_running[i] == "True" :
                        print("Container not Running !")
                        print(container_name)
                    else :
                        print("Container start Running !")
                        print(container_name)


# get docker info in a range time which are store in the db
def dockerGetInfo(range_time) :
    # now time
    now_time = time.time()
    # range time is based on minute
    range_time = now_time - (range_time * 60)
    db_file = open("./db/dockerContainer.dat", "r")
    docker_info_history = json.load(db_file)
    # count each metrics of the numbers of containers were running and not running
    each_metrics_count_run = []
    each_metrics_time = []
    # each info include multiple containers
    for each_info in docker_info_history :
        # key is the time found this metrics
        for key in each_info.keys() :
            # this container info was found in the requested range time
            if float(key) >= float(range_time) :
                # number of running containers in a metric
                count_run = 0
                # count this metrics
                for each_container in each_info[key] :
                    each_container = each_container.split(" ")
                    # the container name
                    each_container_name = each_container[0]
                    # the container running, true or false
                    each_container_running = each_container[1]
                    # if running, count + 1
                    if each_container_running == "True" :
                        count_run += 1
                # save metrics which are in the range
                each_metrics_count_run.append(count_run)
                each_metrics_time.append(key)
    db_file.close()
    dockerSaveImg(each_metrics_count_run, each_metrics_time)

def dockerSaveImg(each_metrics_count_run, each_metrics_time) :
    plt.xlabel("time")
    plt.ylabel("counts")
    plt.grid(True)
    plt.plot(each_metrics_time, each_metrics_count_run)
    plt.gcf().autofmt_xdate()
    plt.tight_layout()
    plt.savefig('/tmp/containerRunCounts.png')
    plt.close()
#dockerGetInfo(180)
main()
"""
        container = container.split(" ")
        # is normal field format
        if len(container) == 3 :
            it_time = container[0]
            # this container info was found in the requested range time
            #for each_range_time in total_range_time :
            if float(it_time) >= float(range_time) :
                # check whether running or not
                is_running = container[2]
                if is_running :
                    count_run += 1
                else :
                    count_not_run += 1
                """
