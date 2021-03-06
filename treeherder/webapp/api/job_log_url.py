# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, you can obtain one at http://mozilla.org/MPL/2.0/.

import logging
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.exceptions import ParseError
from rest_framework.decorators import action

from treeherder.webapp.api.utils import with_jobs, oauth_required

logger = logging.getLogger(__name__)


class JobLogUrlViewSet(viewsets.ViewSet):
    """
    A job_log_url object holds a reference to a job log.
    """
    @with_jobs
    def retrieve(self, request, project, jm, pk=None):
        """
        Returns a job_log_url object given its ID
        """
        obj = jm.get_job_log_url_detail(pk)
        return Response(obj)

    @with_jobs
    def list(self, request, project, jm):
        """
        GET method implementation for list view
        job_id -- Mandatory filter indicating which job these log belongs to.
        """

        job_id = request.QUERY_PARAMS.get('job_id')
        if not job_id:
            raise ParseError(
                detail="The job_id parameter is mandatory for this endpoint")
        try:
            job_id = int(job_id)
        except ValueError:
            raise ParseError(detail="The job_id parameter must be an integer")

        # get_job_log_url_list takes a list of job ids
        job_log_url_list = jm.get_job_log_url_list([job_id])

        return Response(job_log_url_list)

    @action()
    @with_jobs
    @oauth_required
    def update_parse_status(self, request, project, jm, pk=None):
        """
        Change the state of a job.
        """
        try:
            parse_status = request.DATA["parse_status"]
            parse_timestamp = request.DATA["parse_timestamp"]
            jm.update_job_log_url_status(pk, parse_status, parse_timestamp)
            obj = jm.get_job_log_url_detail(pk)
            return Response(obj)
        except KeyError:
            raise ParseError(detail=("The parse_status and parse_timestamp"
                                     " parameters are mandatory for this"
                                     " endpoint"))

    @action()
    @with_jobs
    def parse(self, request, project, jm, pk=None):
        """Trigger an async task to parse this log."""
        log_obj = jm.get_job_log_url_detail(pk)
        job = jm.get_job(log_obj["job_id"])[0]

        logger.info("{0} has requested to parse log {1}".format(
                    request.user.username, log_obj))

        #importing here to avoid an import loop
        from treeherder.log_parser.tasks import parse_log
        parse_log.apply_async(
            args=[project, log_obj, job["job_guid"]],
            kwargs={'check_errors': True},
            routing_key='parse_log.high_priority'
        )

        return Response({"message": "Log parsing triggered successfully"})
