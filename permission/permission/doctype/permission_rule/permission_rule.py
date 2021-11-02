# Copyright (c) 2021, Totrox Technology and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from permission.controller import add_permission_record


class PermissionRule(Document):
    def validate(self):
        self.validate_doctypes()
        self.controle_disabled()

    def on_trash(self):
        self.delete_permissions()

    def validate_doctypes(self):
        for doc in self.doctypes:
            field = frappe.get_meta(doc.doctype_name).get_field(doc.field)
            if not field:
                frappe.throw(
                    _("Field '{0}' not exist in Dcotype '{1}'").format(
                        doc.field, doc.doctype_name
                    )
                )
            else:
                if not field.fieldtype == "Table MultiSelect":
                    frappe.throw(
                        _("Field '{0}' Type should be 'Table MultiSelect'").format(
                            doc.field
                        )
                    )
                if not field.options == "Permission Detail":
                    frappe.throw(
                        _("Field '{0}' Options should be 'Permission Detail'").format(
                            doc.field
                        )
                    )
                if not doc.share and not doc.permission and not doc.assign:
                    frappe.throw(
                        _(
                            "At least one option must be selected in line number {0} in DcoTypes Table"
                        ).format(doc.idx)
                    )

    def controle_disabled(self):
        old_doc = self.get_doc_before_save()
        if self.disabled != old_doc.disabled:
            if self.disabled:
                self.delete_permissions()
            else:
                self.create_permissions()

    def delete_permissions(self):
        to_remove = frappe.get_all(
            "Permission Record",
            filters={"permission_rule": self.name},
        )
        for rec in to_remove:
            frappe.delete_doc(
                "Permission Record", rec.name, force=1, ignore_permissions=True
            )

    def create_permissions(self):
        if self.disabled:
            return
        for doctype in self.doctypes:
            rows = frappe.get_all(
                "Permission Detail",
                filters={
                    "permission": self.name,
                    "parenttype": doctype.doctype_name,
                    "parentfield": doctype.field,
                },
                fields=["parent", "name"],
            )
            for row in rows:
                add_permission_record(
                    self.name, row.name, doctype.doctype_name, row.parent, self
                )
