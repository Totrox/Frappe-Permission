# Copyright (c) 2021, Totrox Technology and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.desk.form.assign_to import add as add_assign_to, remove as remove_todo


# from frappe.share import add as add_share


class PermissionRecord(Document):
    def validate(self):
        self.validate_options()

    def validate_options(self):
        if not self.share and not self.permission and not self.assign and not self.role:
            frappe.throw(_("At least one option must be selected"))

    def after_insert(self):
        if self.assign:
            add_assign_to(
                {
                    "assign_to": [self.user],
                    "doctype": self.doctype_name,
                    "name": self.docname,
                    "description": self.docname,
                    "bulk_assign": False,
                    "re_assign": False,
                    "priority": "Medium",
                }
            )
        elif self.share:
            frappe.share.add(
                self.doctype_name, self.docname, self.user, read=1, write=1, notify=1
            )
        if self.permission:
            duplicate_exists = frappe.db.get_all(
                "User Permission",
                filters={
                    "allow": self.doctype_name,
                    "for_value": self.docname,
                    "user": self.user,
                    "apply_to_all_doctypes": 1,
                },
                limit=1,
            )
            if len(duplicate_exists) == 0:
                user_permission = frappe.new_doc("User Permission")
                user_permission.user = self.user
                user_permission.allow = self.doctype_name
                user_permission.for_value = self.docname
                user_permission.apply_to_all_doctypes = 1
                user_permission.insert(ignore_permissions=True)
        if self.role:
            roles_list = frappe.get_all(
                "Has Role", {"parent": self.user, "role": self.role_name}, limit=1
            )
            if len(roles_list) == 0:
                role_doc = frappe.new_doc("Has Role")
                role_doc.parent = self.user
                role_doc.parentfield = "roles"
                role_doc.parenttype = "User"
                role_doc.role = self.role_name
                role_doc.insert(ignore_permissions=True)

    def on_trash(self):
        if self.assign:
            remove_todo(self.doctype_name, self.docname, self.user)
        if self.assign or self.share:
            share_list = frappe.get_all(
                "DocShare",
                filters={
                    "user": self.user,
                    "share_doctype": self.doctype_name,
                    "share_name": self.docname,
                },
            )
            for share in share_list:
                frappe.delete_doc(
                    "DocShare", share.name, force=1, ignore_permissions=True
                )
        if self.permission:
            user_permissions = frappe.db.get_all(
                "User Permission",
                filters={
                    "allow": self.doctype_name,
                    "for_value": self.docname,
                    "user": self.user,
                    "apply_to_all_doctypes": 1,
                },
            )
            for perm in user_permissions:
                frappe.delete_doc(
                    "User Permission", perm.name, force=1, ignore_permissions=True
                )
        if self.role:
            roles_list = frappe.get_all(
                "Has Role", {"parent": self.user, "role": self.role_name}
            )
            if len(roles_list) > 0:
                for role in roles_list:
                    frappe.delete_doc(
                        "Has Role", role.name, force=1, ignore_permissions=True
                    )
