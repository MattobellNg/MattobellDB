from odoo import models, fields, api, _
from odoo.exceptions import UserError

STATES = [
    ("draft", "Draft"),
    ("submit", "Employee Manager"),
    ("approved", "Inventory Manager"),
    ("cpo", "CPO"),
    ("done", "Done"),
]

class FiberStoreRequest(models.Model):
    _inherit = 'ng.store.request'

    state = fields.Selection(selection=STATES, default="draft", tracking=True)

    def _current_login_user(self):
        """Return current logined in user."""
        return self.env.uid

    def _current_login_employee(self):
        """Get the employee record related to the current login user."""
        hr_employee = self.env["hr.employee"].search([("user_id", "=", self._current_login_user())], limit=1)
        return hr_employee.id

    # Override the requester field to trigger employee update
    requester = fields.Many2one(
        comodel_name="res.users",
        string="User",
        tracking=True,
        default=_current_login_user
    )
    
    # Override end_user to be computed from requester
    end_user = fields.Many2one(
        comodel_name="hr.employee",
        string="Employee",
        compute='_compute_employee_from_user',
        store=True,
        readonly=True,
        default=_current_login_employee,
    )
    
    # Change hod field to manager
    manager_id = fields.Many2one(
        comodel_name="hr.employee",
        string="Manager",
        related="end_user.parent_id",
        store=True,
        readonly=True
    )
    
    @api.depends('requester')
    def _compute_employee_from_user(self):
        """Automatically set employee based on selected user."""
        for record in self:
            if record.requester:
                employee = self.env['hr.employee'].search(
                    [('user_id', '=', record.requester.id)],
                    limit=1
                )
                record.end_user = employee.id
            else:
                record.end_user = _current_login_employee

    def submit(self):
        """Override submit method to send to manager instead of HOD."""
        if not self.approve_request_ids:
            raise UserError(_("You cannot submit an empty item list for requisition."))
        
        # Schedule activity for manager
        if self.manager_id and self.manager_id.user_id:
            self.activity_schedule(
                'ng_store_requisition.mail_activity_data_sr',
                user_id=self.manager_id.user_id.id,
                note=_('New Store Requisition requires your approval')
            )
        
        self.write({"state": "submit"})
        
    def manager_approve(self):
        """Replace department_manager_approve with manager_approve."""
        context = self.env.context
        if not context.get("approved", False):
            return {
                "type": "ir.actions.act_window",
                "res_model": "ir.request.wizard",
                "views": [[False, "form"]],
                "context": {"request_id": self.id},
                "target": "new",
            }
        
        # Notify inventory managers
        users = self.env.ref('ng_store_requisition.ng_store_requisition_finance').users
        for user in users:
            self.activity_schedule(
                'ng_store_requisition.mail_activity_data_sr',
                user_id=user.id,
                note=_('Store Requisition is Approved By Manager')
            )
            
        self.write({"state": "approved"})