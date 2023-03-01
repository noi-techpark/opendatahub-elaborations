#/bin/bash
# exit if error
set -e
func () {
    # redirect output to entrypoints stdout/stderr (PID 1)
    python /usr/src/app/main.py > /proc/1/fd/1 2>/proc/1/fd/2
}
# Every n seconds run the job (it's duration should be short so we don't need cronlike)
func
while sleep $JOB_SCHEDULE_SEC ; do 
    func 
done
