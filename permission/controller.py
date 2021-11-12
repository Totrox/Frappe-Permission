# Copyright (c) 2021, Totrox Technology and contributors
# For license information, please see license.txt

import frappe


def process_permissions(doc, method):
    fields = doc.meta.get(
        "fields", {"fieldtype": "Table MultiSelect", "options": "Permission Detail"}
    )
    if fields:
        existing_permissions_row = []
        permissions_map = {}
        to_remove = []
        for field in fields:
            permissions = doc.get(field.fieldname)
            for perm in permissions:
                existing_permissions_row.append(perm.name)
                permissions_map.setdefault(perm.name, perm.permission)
        if method == "on_trash":
            to_remove = frappe.get_all(
                "Permission Record",
                filters={"doctype_name": doc.doctype, "docname": doc.name},
            )
        else:
            to_remove = frappe.get_all(
                "Permission Record",
                filters={"row_id": ["not in", existing_permissions_row]},
            )

            for row in existing_permissions_row:
                exist_permission_record = frappe.get_all(
                    "Permission Record", filters={"row_id": row}
                )
                if len(exist_permission_record) == 0:
                    add_permission_record(
                        "Permission Rule",
                        permissions_map.get(row),
                        row,
                        doc.doctype,
                        doc.name,
                    )
        for rec in to_remove:
            frappe.delete_doc(
                "Permission Record", rec.name, force=1, ignore_permissions=True
            )


def add_permission_record(
    ref_doctype, ref_docname, row_id, doctype_name, docmame, rule_doc=None
):
    if ref_doctype == "Permission Rule":
        if not rule_doc:
            rule_doc = frappe.get_doc("Permission Rule", ref_docname)
        if rule_doc.disabled:
            return
        doctype_options = next(
            (i for i in rule_doc.doctypes if i.doctype_name == doctype_name), None
        )
        if not doctype_options:
            return
        for user in rule_doc.users:
            record_doc = frappe.new_doc("Permission Record")
            record_doc.user = user.user
            record_doc.row_id = row_id
            record_doc.ref_doctype = ref_doctype
            record_doc.ref_docname = ref_docname
            record_doc.doctype_name = doctype_name
            record_doc.docname = docmame
            record_doc.share = doctype_options.get("share")
            record_doc.permission = doctype_options.get("permission")
            record_doc.assign = doctype_options.get("assign")
            record_doc.role = doctype_options.get("role")
            record_doc.role_name = doctype_options.get("role_name")
            record_doc.insert(ignore_permissions=True)
