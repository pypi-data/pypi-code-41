"""
CSV import/export API for grades.
"""
from __future__ import absolute_import, unicode_literals

import datetime
import json
import logging

from django.http import HttpResponse, HttpResponseForbidden, StreamingHttpResponse
from django.views.generic import View

from . import api

log = logging.getLogger(__name__)


class GradeOnlyExport(View):
    """
    CSV Export of grade information only. To be used by both bulk grade export and interventions.
    """

    def __init__(self, **kwargs):
        """
        Configure initial state.
        """
        super(GradeOnlyExport, self).__init__(**kwargs)
        self.processor = None
        self.extra_filename = ''

    def get_export_iterator(self, request):  # pylint: disable=unused-argument
        """
        Return an iterator appropriate for a streaming response.
        """
        return []

    def initialize_processor(self, request, course_id):
        """
        Abstract method to initialize processor particular to the class.
        """
        pass

    def dispatch(self, request, course_id, *args, **kwargs):  # pylint: disable=arguments-differ
        """
        Dispatch django request.
        """
        self.initialize_processor(request, course_id)
        return super(GradeOnlyExport, self).dispatch(request, course_id, *args, **kwargs)

    def get(self, request, course_id, *args, **kwargs):  # pylint: disable=unused-argument
        """
        Export grades in CSV format.

        GET arguments:
        track: name of enrollment mode
        cohort: name of cohort
        subsection: block id of graded subsection
        """
        iterator = self.get_export_iterator(request)
        filename = [course_id]

        if self.extra_filename:
            filename.append(self.extra_filename)
        filename.append(datetime.datetime.utcnow().isoformat())

        response = StreamingHttpResponse(iterator, content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="%s.csv"' % '-'.join(filename)

        log.info('Exporting %s CSV for %s', course_id, self.__class__)
        return response


class GradeImportExport(GradeOnlyExport):
    """
    CSV Grade import/export view.
    """

    def post(self, request, course_id, *args, **kwargs):  # pylint: disable=unused-argument
        """
        Import grades from a CSV file.
        """
        result_id = request.POST.get('result_id', None)
        if result_id:
            results = self.processor.get_deferred_result(result_id)
            if results.ready():
                data = results.get()
                log.info('Got results from celery %r', data)
            else:
                data = {'waiting': True, 'result_id': result_id}
                log.info('Still waiting for %s', result_id)
        else:
            the_file = request.FILES['csv']
            self.processor.process_file(the_file, autocommit=True)
            data = self.processor.status()
            log.info('Processed file %s for %s -> %s saved, %s processed, %s error. (async=%s)',
                     the_file.name,
                     course_id,
                     data.get('saved', 0),
                     data.get('total', 0),
                     len(data.get('error_rows', [])),
                     data.get('waiting', False))
        return HttpResponse(json.dumps(data), content_type='application/json')

    def get_export_iterator(self, request):
        """
        Create an iterator for exporting grade data.
        """
        return self.processor.get_iterator(error_data=bool(request.GET.get('error_id', '')))

    def initialize_processor(self, request, course_id):
        """
        Initialize GradeCSVProcessor.
        """
        operation_id = request.GET.get('error_id', '')
        if operation_id:
            self.processor = api.GradeCSVProcessor.load(operation_id)
            if self.processor.course_id != course_id:
                return HttpResponseForbidden()
            self.extra_filename = 'graded-results'
        else:
            assignment_grade_max = request.GET.get('assignmentGradeMax')
            assignment_grade_min = request.GET.get('assignmentGradeMin')
            course_grade_min = request.GET.get('courseGradeMin')
            course_grade_max = request.GET.get('courseGradeMax')
            self.processor = api.GradeCSVProcessor(
                course_id=course_id,
                _user=request.user,
                track=request.GET.get('track'),
                cohort=request.GET.get('cohort'),
                subsection=request.GET.get('assignment'),
                assignment_type=request.GET.get('assignmentType'),
                subsection_grade_max=(float(assignment_grade_max)
                                      if assignment_grade_max else None),
                subsection_grade_min=(float(assignment_grade_min)
                                      if assignment_grade_min else None),
                course_grade_min=(float(course_grade_min) if course_grade_min else None),
                course_grade_max=(float(course_grade_max) if course_grade_max else None),
            )


class GradeOperationHistoryView(View):
    """
    Collection View for history of grade override file uploads.
    """

    def get(self, request, course_id):
        """
        Get all previous times grades have been overwritten for this course.
        """
        processor = api.GradeCSVProcessor(
            course_id=course_id,
            _user=request.user
        )
        history = processor.get_committed_history()
        return HttpResponse(json.dumps(history), content_type='application/json')


class InterventionsExport(GradeOnlyExport):
    """
    Interventions export view.
    """

    extra_filename = 'intervention'

    def get_export_iterator(self, request):
        """
        Create an iterator for exporting intervention data.
        """
        return self.processor.get_iterator()

    def initialize_processor(self, request, course_id):
        """
        Initialize InterventionCSVProcessor.
        """
        assignment_grade_max = request.GET.get('assignmentGradeMax')
        assignment_grade_min = request.GET.get('assignmentGradeMin')
        course_grade_min = request.GET.get('courseGradeMin')
        course_grade_max = request.GET.get('courseGradeMax')

        self.processor = api.InterventionCSVProcessor(
            course_id=course_id,
            _user=request.user,
            track=request.GET.get('track'),
            cohort=request.GET.get('cohort'),
            subsection=request.GET.get('assignment'),
            assignment_type=request.GET.get('assignmentType'),
            subsection_grade_min=(float(assignment_grade_min)
                                  if assignment_grade_min else None),
            subsection_grade_max=(float(assignment_grade_max)
                                  if assignment_grade_max else None),
            course_grade_min=(float(course_grade_min) if course_grade_min else None),
            course_grade_max=(float(course_grade_max) if course_grade_max else None)
        )
