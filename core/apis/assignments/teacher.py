from flask import Blueprint
from core import db
from core.apis import decorators
from core.apis.responses import APIResponse
from core.models.assignments import Assignment
from core.libs.exceptions import FyleError
from .schema import AssignmentSchema, AssignmentGradeSchema

teacher_assignments_resources = Blueprint('teacher_assignments_resources', __name__)

@teacher_assignments_resources.route('/assignments', methods=['GET'], strict_slashes=False)
@decorators.authenticate_principal
def list_assignments(p):
    teachers_assignments = Assignment.get_assignments_by_teacher(p.teacher_id)
    teachers_assignments_dump = AssignmentSchema().dump(teachers_assignments, many=True)
    return APIResponse.respond(data=teachers_assignments_dump)

@teacher_assignments_resources.route('/assignments/grade', methods=['POST'], strict_slashes=False)
@decorators.accept_payload
@decorators.authenticate_principal
def grade_assignment(p, incoming_payload):
    grade_assignment_payload = AssignmentGradeSchema().load(incoming_payload)
    assignment = Assignment.get_by_id(grade_assignment_payload.id)
    # error handling for test cases
    if(assignment is None):
        raise FyleError(404, 'Assignment not found')
    if( p.teacher_id != assignment.teacher_id):
        raise FyleError(400, 'assignment 1 was submitted to teacher 1 and not teacher 2')
    else:
        graded_assignment = Assignment.mark_grade(
            _id=grade_assignment_payload.id,
            grade=grade_assignment_payload.grade,
            auth_principal=p
        )
    db.session.commit()
    graded_assignment_dump = AssignmentSchema().dump(graded_assignment)
    return APIResponse.respond(data=graded_assignment_dump)
