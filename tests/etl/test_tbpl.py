# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, you can obtain one at http://mozilla.org/MPL/2.0/.

from treeherder.etl.tbpl import OrangeFactorBugRequest, BugzillaBugRequest
import json
from time import time
from datadiff import diff


def test_tbpl_bug_request_body(jm, eleven_jobs_processed):
    """
    Test the request body is created correctly
    """

    bug_id = 12345678
    job = jm.get_job_list(0, 1)[0]
    sample_artifact = {
        "build_id": 39953854,
        "buildername": "b2g_emulator_vm mozilla-inbound opt test crashtest-2"
    }
    placeholders = [
        [job["id"], "buildapi", "json",
         json.dumps(sample_artifact), job["id"], "buildapi"]
    ]
    jm.store_job_artifact(placeholders)

    submit_timestamp = int(time())
    who = "user@mozilla.com"

    req = OrangeFactorBugRequest(jm.project, job["id"],
                                 bug_id, submit_timestamp, who)
    req.generate_request_body()

    expected = {
        "buildname": "b2g_emulator_vm mozilla-inbound opt test crashtest-2",
        "machinename": "bld-linux64-ec2-132",
        "os": "b2g-emu-jb",
        # I'm using the request time date here, as start time is not
        # available for pending jobs
        "date": "2013-11-13",
        "type": "B2G Emulator Image Build",
        "buildtype": "debug",
        "starttime": "1384353553",
        "logfile": "00000000",
        "tree": "test_treeherder",
        "rev": "cdfe03e77e66",
        "bug": str(bug_id),
        "who": who,
        "timestamp": str(submit_timestamp)
    }

    assert req.body == expected, diff(expected, req.body)


def test_tbpl_bugzilla_request_body(jm, eleven_jobs_processed):
    """
    Test the request body is created correctly
    """

    bug_id = 12345678
    job = jm.get_job_list(0, 1)[0]

    submit_timestamp = int(time())
    who = "user@mozilla.com"
    jm.insert_bug_job_map(job['id'], bug_id, "manual", submit_timestamp, who)

    bug_suggestions = []
    bug_suggestions.append({"search": "First error line", "bugs": []})
    bug_suggestions.append({"search": "Second error line", "bugs": []})

    bug_suggestions_placeholders = [
        job['id'], 'Bug suggestions',
        'json', json.dumps(bug_suggestions),
        job['id'], 'Bug suggestions',
    ]

    jm.store_job_artifact([bug_suggestions_placeholders])
    req = BugzillaBugRequest(jm.project, job["id"], bug_id)
    req.generate_request_body()

    expected = {
        'comment': (u'log: http://local.treeherder.mozilla.org/'
                    u'logviewer.html#?repo=test_treeherder&job_id=1\n'
                    u'repository: test_treeherder\n'
                    u'start_time: 2013-11-13T06:39:13\n'
                    u'who: user[at]mozilla[dot]com\n'
                    u'machine: bld-linux64-ec2-132\n'
                    u'revision: cdfe03e77e66\n\n'
                    u'First error line\n'
                    u'Second error line')
    }

    assert req.body == expected
