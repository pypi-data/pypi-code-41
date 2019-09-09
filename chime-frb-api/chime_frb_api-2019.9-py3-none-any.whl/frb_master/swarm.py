#!/usr/bin/env python
# -*- coding: utf-8 -*-

from chime_frb_api.core import API
import typing as t
import uuid

JSON = t.Union[str, int, float, bool, None, t.Mapping[str, "JSON"], t.List["JSON"]]
JOBS = t.List[str]


class Swarm(API):
    """
    CHIME/FRB Swarm API

    Attributes
    ----------
    base_url : str
        Base URL at which the is accessible.
    """

    def __init__(self, base_url: str = "http://frb-vsop.chime:8001"):
        API.__init__(self, base_url=base_url)

    def get_jobs(self) -> JSON:
        """
        Returns the name of all jobs on the analysis cluster.
        """
        return self._get("/v1/swarm/jobs")

    def get_job_status(self, job_name: str) -> JSON:
        """
        Get status of all jobs matching job name

        Parameters
        ----------
        job_name : str
            Name of the job

        Returns
        -------
            { job_name : STATUS } : dict

            Where STATUS can be,
            NEW         The job was initialized.
            PENDING     Resources for the job were allocated.
            ASSIGNED    Docker assigned the job to nodes.
            ACCEPTED    The job was accepted by a worker node.
            PREPARING   Docker is preparing the job.
            STARTING    Docker is starting the job.
            RUNNING     The job is executing.
            COMPLETE    The job exited without an error code.
            FAILED      The job exited with an error code.
            SHUTDOWN    Docker requested the job to shut down.
            REJECTED    The worker node rejected the job.
            ORPHANED    The node was down for too long.
            REMOVE      The job is not terminal but the associated job was removed
        """
        return self._get("/v1/swarm/job-status/{}".format(job_name))

    def spawn_job(
        self,
        image_name: str,
        command: list,
        arguments: list,
        job_name: str,
        mount_archiver: bool = True,
        swarm_network: bool = True,
        job_mem_limit: int = None,
        job_mem_reservation: int = None,
    ) -> JSON:
        """
        Spawn a job on the CHIME/FRB Analysis Cluster

        Parameters
        ----------

        image_name : str
            Name of the container image to spawn the job with
            e.g. chimefrb/iautils:latest

        command : list
            The command to be run in the container

        arguments : list
            Arguments to the command

        job_name : string
            Unique name for the cluster job

        mount_archiver : bool
            Mount Site Data Archivers

        swarm_network : bool
            Mount Cluster Network

        job_mem_limit : int
            Represents the memory limit of the created container in bytes

        job_mem_reservation : int
            Represents the minimum memory reserved of the created container in bytes
        """
        payload = {
            "image_name": image_name,
            "command": command,
            "arguments": arguments,
            "job_name": job_name,
            "mount_archiver": mount_archiver,
            "swarm_network": swarm_network,
            "job_mem_reservation": job_mem_reservation,
            "job_mem_limit": job_mem_limit,
        }
        return self._post("/v1/swarm/spawn-job", payload)

    def get_logs(self, job_name: str) -> JSON:
        """
        Return logs from a CHIME/FRB Job

        Parameters
        ----------
        job_name : string
            Unique name for the cluster job

        Returns
        -------
            dict
        """
        return self._get("/v1/swarm/logs/{}".format(job_name))

    def prune_jobs(self, job_name: str) -> JSON:
        """
        Prune jobs with COMPLETED status and regex match to job_name

        Parameters
        ----------
        job_name : string
            Unique name for the cluster job

        Returns
        -------
            dict: {job_name : boolean}
        """
        return self._get("/v1/swarm/prune-job/{}".format(job_name))

    def kill_job(self, job_name: str) -> JSON:
        """
        Kill a job with ANY status and exact match to job_name

        Parameters
        ----------
        job_name : string
            Unique name for the cluster job

        Returns
        -------
            dict: {job_name : boolean}
        """
        return self._get("/v1/swarm/kill-job/{}".format(job_name))

    def kill_failed_jobs(self, job_name: str = None) -> JSON:
        """
        Prune jobs with FAILED status and regex match to job_name

        Parameters
        ----------
        job_name : string
            Unique name for the cluster job

        Returns
        -------
            dict: {job_name : boolean}
        """
        assert isinstance(job_name, str), "job_name <str> is required"
        status = {}
        for job in self.get_jobs():
            if job_name in job:
                if self.get_job_status(job)[job] == "failed":
                    status[job] = self.kill_job(job)[job]
        return status

    def jobs_running(self, job_names: t.List[str]) -> bool:
        """
        Monitors job[s] on the CHIME/FRB Analysis Cluster untill they are either
        COMPLETE, FAILED or SHUTDOWN

        Parameters
        ----------
        job_names : list
            A list of string job_name paramerters to monitor
        """
        running_statuses = [
            "new",
            "pending",
            "assigned",
            "accepted",
            "preparing",
            "starting",
            "running",
        ]
        if isinstance(job_names, str):
            job_names = [job_names]
        jobs_status = {}
        for job in job_names:
            status = self.get_job_status(job)
            jobs_status[job] = status
            for running in running_statuses:
                if running in status.values():
                    return True
        return False

    def run_fitburst(self, event_number: int, arguments: t.List[str]) -> dict:
        """
        Spawn a fitburst job for a given event number with any arguments that
        Fitburst takes in using command line interface. 

        Parameters
        ----------
        event_number : int
            Event number to run fitburst one
        arguments : list
            List of command line arguments
            eg. cli command --> fitburst eventid 9386707 will become
                cluser command --> ["eventid", "9386707"]

        Returns
        -------
        dictionary of the service id spawned.
        """
        service = self.spawn_job(
            image_name="chimefrb/iautils:latest",
            command=["fitburst"],
            arguments=arguments,
            job_name="fitburst-{0}-{1}".format(
                event_number, str(uuid.uuid4()).split("-")[0]
            ),
            mount_archiver=True,
            swarm_network=True,
            job_mem_reservation=4 * (1024 ** 3),
        )

        return {event_number: service["ID"]}
