# Copyright (c) 2021, Totrox Technology and contributors
# For license information, please see license.txt

# import frappe
import frappe
from frappe.model.document import Document


class PermissionAssignment(Document):
    def on_submit(self):
        self.validate_role_detail()
        self.create_permissions()

    def on_cancel(self):
        self.remove_permissions()

    def validate_role_detail(self):
        pass

    def create_permissions(self):
        if self.role:
            self.add_permission_record(role=self.role)
            for row in self.role_permission_profile_detail:
                self.add_permission_record(
                    doctype_name=row.doctype_name, docname=row.docname
                )
            if frappe.db.exists("Role Permission Profile", self.role):
                profile = frappe.get_doc("Role Permission Profile", self.role)
                for row in profile.role_permission_profile_detail:
                    self.add_permission_record(
                        doctype_name=row.doctype_name, docname=row.docname
                    )

    def remove_permissions(self):
        to_remove = frappe.get_all(
            "Permission Record",
            filters={"ref_doctype": "Permission Assignment", "ref_docname": self.name},
        )
        for rec in to_remove:
            frappe.delete_doc(
                "Permission Record", rec.name, force=1, ignore_permissions=True
            )

    def add_permission_record(self, role=None, doctype_name=None, docname=None):
        record_doc = frappe.new_doc("Permission Record")
        record_doc.user = self.user
        record_doc.ref_doctype = self.doctype
        record_doc.ref_docname = self.name
        record_doc.doctype_name = doctype_name
        record_doc.docname = docname
        record_doc.permission = 1 if docname else 0
        record_doc.role = 1 if role else 0
        record_doc.role_name = role
        record_doc.insert(ignore_permissions=True)
