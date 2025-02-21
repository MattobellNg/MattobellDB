from datetime import date
from odoo import models, fields, api, _
from odoo.exceptions import AccessError, ValidationError


class EmployeeKRAQuestion(models.Model):
    _inherit = "employee.kra.question"

    atd = fields.Date(string="Date", default=date.today(), tracking=True)

class EmployeeKRAInherit(models.Model):
    _inherit = "employee.kra"

    manager_comment_readonly = fields.Boolean(
        string="Manager Comment Readonly",
        compute="_compute_comment_readonly"
    )
    employee_comment_readonly = fields.Boolean(
        string="Employee Comment Readonly",
        compute="_compute_comment_readonly"
    )

    @api.depends('employee_supervisor.user_id', 'employee_id.user_id')
    def _compute_comment_readonly(self):
        for record in self:
            current_user = self.env.user
            record.manager_comment_readonly = record.employee_supervisor.user_id != current_user
            record.employee_comment_readonly = record.employee_id.user_id != current_user

    def action_cancel(self):
        self.state = "cancel"

    def action_draft(self):
        self.state = "draft"
        self.agree = False
        self.disagree = False


class EmployeeKraQuestionnaireInherit(models.Model):
    _inherit = "employee.kra.questionnaire"

    name = fields.Many2one("kra.questionnaire", string="COMPETENCY", tracking=True, required=True)

    @api.constrains('rating', 'name', 'employee_kra_id')
    def _check_rating_and_name(self):
        for record in self:
            if (
                record.employee_kra_id
                and record.employee_kra_id.state == 'respond'
            ):
                if not record.rating:
                    raise ValidationError(_("The 'Rating' field must not be empty when the state is 'respond'."))
                if record.rating and not record.name:  # Check if rating is being set BUT name is blank.
                     raise ValidationError(_("The 'COMPETENCY' field must not be empty if you set a 'Rating'."))
                

    @api.constrains('response')
    def _check_response_not_blank(self):
        for record in self:
            if record.employee_kra_id.state == 'review':  # Check the state of the related employee.kra
                if not record.response or not record.response.strip():
                    raise ValidationError(_("The 'How I exhibited the core values' field must not be empty."))