        lab_tech_id = page.session.store.get("lab_tech_id")

            if not lab_tech_id:
                content_controls.append(ft.Text("Lab technician session missing. Please log in again."))
                return

            def fmt_dt(v):
                return str(v)[:16] if v else "N/A"

            def priority_bg(priority_value):
                if priority_value == "STAT":
                    return ft.Colors.RED_500
                if priority_value == "Urgent":
                    return ft.Colors.ORANGE_500
                return ft.Colors.GREEN_500

            def status_bg(status_value):
                if status_value == "Completed":
                    return ft.Colors.GREEN_700
                if status_value == "Processing":
                    return ft.Colors.BLUE_700
                if status_value == "Sample Collected":
                    return ft.Colors.ORANGE_700
                if status_value == "Cancelled":
                    return ft.Colors.RED_700
                return ft.Colors.GREY_700

            def update_order_status(order_id, new_status):
                execute_query(
                    "UPDATE LabOrder SET status=%s WHERE order_id=%s",
                    (new_status, order_id)
                )
                show_snack("Order status updated", ft.Colors.GREEN)
                nav_to("lab_dashboard")

            doctors = get_query_data("""
                SELECT doctor_id, first_name, last_name
                FROM Doctor
                ORDER BY first_name, last_name
            """)

            tests_catalog = get_query_data("""
                SELECT
                    t.test_id,
                    t.test_name,
                    t.test_code,
                    COALESCE(c.category_name, 'Uncategorized') AS category_name,
                    t.description,
                    t.sample_type,
                    t.sample_volume,
                    t.normal_range,
                    t.unit,
                    t.turnaround_hours,
                    t.price,
                    t.equipment_required
                FROM LabTest t
                LEFT JOIN LabTestCategory c ON t.test_cat_id = c.test_cat_id
                ORDER BY category_name, t.test_name
            """)

            lab_orders = get_query_data("""
                SELECT
                    lo.order_id,
                    loi.order_item_id,
                    p.first_name AS patient_first,
                    p.last_name AS patient_last,
                    d.first_name AS doctor_first,
                    d.last_name AS doctor_last,
                    t.test_name,
                    t.test_code,
                    COALESCE(c.category_name, 'Uncategorized') AS category_name,
                    t.sample_type,
                    t.sample_volume,
                    t.normal_range,
                    t.unit,
                    t.turnaround_hours,
                    t.price,
                    t.equipment_required,
                    lo.priority,
                    lo.status,
                    lo.ordered_at,
                    lo.notes
                FROM LabOrder lo
                JOIN LabOrderItem loi ON lo.order_id = loi.order_id
                JOIN LabTest t ON loi.test_id = t.test_id
                LEFT JOIN LabTestCategory c ON t.test_cat_id = c.test_cat_id
                JOIN Patient p ON lo.patient_id = p.patient_id
                JOIN Doctor d ON lo.doctor_id = d.doctor_id
                ORDER BY lo.ordered_at DESC
            """)

            pending_items = get_query_data("""
                SELECT
                    loi.order_item_id,
                    lo.order_id,
                    p.first_name,
                    p.last_name,
                    t.test_name,
                    lo.ordered_at,
                    lo.priority
                FROM LabOrderItem loi
                JOIN LabOrder lo ON loi.order_id = lo.order_id
                JOIN Patient p ON lo.patient_id = p.patient_id
                JOIN LabTest t ON loi.test_id = t.test_id
                WHERE lo.status IN ('Ordered', 'Sample Collected', 'Processing')
                ORDER BY lo.ordered_at DESC
            """)

            results = get_query_data("""
                SELECT
                    lr.result_id,
                    p.first_name AS patient_first,
                    p.last_name AS patient_last,
                    t.test_name,
                    lr.result_value,
                    lr.unit,
                    lr.normal_range,
                    lr.status,
                    lr.remarks,
                    lr.sample_collected_at,
                    lr.reported_at,
                    d1.first_name AS verifier_first,
                    d1.last_name AS verifier_last
                FROM LabResult lr
                JOIN LabOrderItem loi ON lr.order_item_id = loi.order_item_id
                JOIN LabOrder lo ON loi.order_id = lo.order_id
                JOIN Patient p ON lo.patient_id = p.patient_id
                JOIN LabTest t ON loi.test_id = t.test_id
                LEFT JOIN Doctor d1 ON lr.verified_by = d1.doctor_id
                ORDER BY lr.reported_at DESC
            """)

            test_groups = {}
            for t in tests_catalog or []:
                cat = t.get("category_name") or "Uncategorized"
                test_groups.setdefault(cat, []).append(t)

            summary_total_tests = len(tests_catalog or [])
            summary_total_orders = len(lab_orders or [])
            summary_pending = len(pending_items or [])
            summary_results = len(results or [])

            # -------------------- SUMMARY --------------------
            content_controls.append(
                ft.Container(
                    margin=ft.Margin.only(bottom=12),
                    padding=16,
                    border_radius=12,
                    bgcolor=ft.Colors.BLUE_50,
                    content=ft.Column([
                        ft.Text("Lab Technician Dashboard", size=24, weight="bold"),
                        ft.Text("Test catalog, orders, results, and history in one workspace."),
                        ft.Row(
                            controls=[
                                ft.Container(
                                    padding=12,
                                    border_radius=10,
                                    bgcolor=ft.Colors.WHITE,
                                    width=170,
                                    content=ft.Column([
                                        ft.Text("Tests", size=12, color=ft.Colors.GREY_600),
                                        ft.Text(str(summary_total_tests), size=22, weight="bold")
                                    ])
                                ),
                                ft.Container(
                                    padding=12,
                                    border_radius=10,
                                    bgcolor=ft.Colors.WHITE,
                                    width=170,
                                    content=ft.Column([
                                        ft.Text("Orders", size=12, color=ft.Colors.GREY_600),
                                        ft.Text(str(summary_total_orders), size=22, weight="bold")
                                    ])
                                ),
                                ft.Container(
                                    padding=12,
                                    border_radius=10,
                                    bgcolor=ft.Colors.WHITE,
                                    width=170,
                                    content=ft.Column([
                                        ft.Text("Pending", size=12, color=ft.Colors.GREY_600),
                                        ft.Text(str(summary_pending), size=22, weight="bold")
                                    ])
                                ),
                                ft.Container(
                                    padding=12,
                                    border_radius=10,
                                    bgcolor=ft.Colors.WHITE,
                                    width=170,
                                    content=ft.Column([
                                        ft.Text("Results", size=12, color=ft.Colors.GREY_600),
                                        ft.Text(str(summary_results), size=22, weight="bold")
                                    ])
                                ),
                            ],
                            spacing=12,
                        )
                    ])
                )
            )

            # -------------------- TAB 1: CATALOG --------------------
            catalog_sections = []
            if test_groups:
                for cat_name, items in test_groups.items():
                    item_cards = []
                    for t in items:
                        item_cards.append(
                            ft.Container(
                                margin=ft.Margin.only(bottom=8),
                                padding=12,
                                border_radius=10,
                                bgcolor=ft.Colors.GREY_100,
                                content=ft.Column([
                                    ft.Text(f"{t['test_name']} ({t.get('test_code') or 'No code'})", weight="bold"),
                                    ft.Text(f"Sample: {t.get('sample_type') or 'N/A'} | Volume: {t.get('sample_volume') or 'N/A'}"),
                                    ft.Text(f"Range: {t.get('normal_range') or 'N/A'} | Unit: {t.get('unit') or 'N/A'}"),
                                    ft.Text(f"Turnaround: {t.get('turnaround_hours') or 'N/A'} hrs | Price: {t.get('price') or 'N/A'}"),
                                    ft.Text(f"Equipment: {t.get('equipment_required') or 'N/A'}"),
                                    ft.Text(f"Description: {t.get('description') or 'N/A'}"),
                                ])
                            )
                        )

                    catalog_sections.append(
                        ft.Container(
                            margin=ft.Margin.only(bottom=12),
                            padding=14,
                            border_radius=12,
                            bgcolor=ft.Colors.WHITE,
                            content=ft.Column([
                                ft.Text(cat_name, size=16, weight="bold"),
                                *item_cards
                            ])
                        )
                    )
            else:
                catalog_sections.append(ft.Text("No lab tests found"))

            # -------------------- TAB 2: ORDERS --------------------
            order_cards = []
            if lab_orders:
                for o in lab_orders:
                    status_dd = ft.Dropdown(
                        width=220,
                        label="Update Status",
                        value=o["status"],
                        options=[
                            ft.dropdown.Option("Ordered"),
                            ft.dropdown.Option("Sample Collected"),
                            ft.dropdown.Option("Processing"),
                            ft.dropdown.Option("Completed"),
                            ft.dropdown.Option("Cancelled"),
                        ]
                    )

                    order_cards.append(
                        ft.Container(
                            margin=ft.Margin.only(bottom=12),
                            padding=14,
                            border_radius=12,
                            bgcolor=ft.Colors.WHITE,
                            content=ft.Column([
                                ft.Row(
                                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                    controls=[
                                        ft.Text(f"{o['patient_first']} {o['patient_last']}", size=16, weight="bold"),
                                        ft.Container(
                                            padding=6,
                                            border_radius=8,
                                            bgcolor=priority_bg(o["priority"]),
                                            content=ft.Text(o["priority"], color=ft.Colors.WHITE, weight="bold")
                                        )
                                    ]
                                ),
                                ft.Text(f"Order ID: {o['order_id']} | Item ID: {o['order_item_id']}"),
                                ft.Text(f"Doctor: Dr. {o['doctor_first']} {o['doctor_last']}"),
                                ft.Text(f"Test: {o['test_name']} ({o.get('test_code') or 'No code'})"),
                                ft.Text(f"Category: {o.get('category_name') or 'Uncategorized'}"),
                                ft.Text(f"Sample: {o.get('sample_type') or 'N/A'} | Volume: {o.get('sample_volume') or 'N/A'}"),
                                ft.Text(f"Normal Range: {o.get('normal_range') or 'N/A'} | Unit: {o.get('unit') or 'N/A'}"),
                                ft.Text(f"Turnaround: {o.get('turnaround_hours') or 'N/A'} hrs | Price: {o.get('price') or 'N/A'}"),
                                ft.Text(f"Ordered At: {fmt_dt(o.get('ordered_at'))}"),
                                ft.Text(f"Notes: {o.get('notes') or 'N/A'}"),
                                ft.Row(
                                    controls=[
                                        ft.Container(
                                            padding=6,
                                            border_radius=8,
                                            bgcolor=status_bg(o["status"]),
                                            content=ft.Text(o["status"], color=ft.Colors.WHITE, weight="bold")
                                        ),
                                        status_dd,
                                        ft.FilledButton(
                                            "Save Status",
                                            on_click=lambda e, oid=o["order_id"], dd=status_dd: update_order_status(oid, dd.value)
                                        )
                                    ],
                                    spacing=12
                                )
                            ])
                        )
                    )
            else:
                order_cards.append(ft.Text("No lab orders found"))

            # -------------------- TAB 3: ENTER RESULT --------------------
            item_dropdown = ft.Dropdown(
                label="Select Order Item",
                width=420,
                options=[
                    ft.dropdown.Option(
                        key=str(i["order_item_id"]),
                        text=f"#{i['order_item_id']} | {i['first_name']} {i['last_name']} | {i['test_name']} | {fmt_dt(i.get('ordered_at'))}"
                    )
                    for i in (pending_items or [])
                ]
            )

            result_value = ft.TextField(label="Result Value", width=300)
            result_unit = ft.TextField(label="Unit", width=180)
            result_normal_range = ft.TextField(label="Normal Range", width=240)
            result_status = ft.Dropdown(
                label="Result Status",
                width=220,
                options=[
                    ft.dropdown.Option("Normal"),
                    ft.dropdown.Option("Abnormal"),
                    ft.dropdown.Option("Critical"),
                ],
                value="Normal"
            )
            result_remarks = ft.TextField(label="Remarks", multiline=True, min_lines=2, max_lines=4, width=520)

            verified_by = ft.Dropdown(
                label="Verified By Doctor (optional)",
                width=320,
                options=[ft.dropdown.Option("None")] + [
                    ft.dropdown.Option(
                        key=str(d["doctor_id"]),
                        text=f"Dr. {d['first_name']} {d['last_name']}"
                    )
                    for d in (doctors or [])
                ],
                value="None"
            )

            def submit_result(e):
                if not item_dropdown.value:
                    show_snack("Select an order item first.", ft.Colors.RED)
                    return

                conn = get_db_connection()
                if not conn:
                    return

                cursor = conn.cursor()
                try:
                    verified_value = None
                    if verified_by.value and verified_by.value != "None":
                        verified_value = int(verified_by.value)

                    cursor.execute("""
                        INSERT INTO LabResult (
                            order_item_id,
                            lab_tech_id,
                            sample_collected_at,
                            result_value,
                            unit,
                            normal_range,
                            status,
                            remarks,
                            verified_by
                        )
                        VALUES (%s, %s, NOW(), %s, %s, %s, %s, %s, %s)
                    """, (
                        int(item_dropdown.value),
                        int(lab_tech_id),
                        result_value.value,
                        result_unit.value,
                        result_normal_range.value,
                        result_status.value,
                        result_remarks.value,
                        verified_value
                    ))

                    cursor.execute("""
                        SELECT order_id
                        FROM LabOrderItem
                        WHERE order_item_id = %s
                    """, (int(item_dropdown.value),))
                    row = cursor.fetchone()
                    if row:
                        cursor.execute("""
                            UPDATE LabOrder
                            SET status='Completed'
                            WHERE order_id=%s
                        """, (row[0],))

                    conn.commit()
                    show_snack("Lab result submitted.", ft.Colors.GREEN)
                    nav_to("lab_dashboard")
                except Exception as ex:
                    conn.rollback()
                    show_snack(f"Lab result error: {ex}", ft.Colors.RED)
                finally:
                    cursor.close()
                    conn.close()

            # -------------------- TAB 4: HISTORY --------------------
            result_cards = []
            if results:
                for r in results:
                    verifier_name = "N/A"
                    if r.get("verifier_first"):
                        verifier_name = f"Dr. {r['verifier_first']} {r['verifier_last']}"

                    result_cards.append(
                        ft.Container(
                            margin=ft.Margin.only(bottom=12),
                            padding=14,
                            border_radius=12,
                            bgcolor=ft.Colors.GREY_100,
                            content=ft.Column([
                                ft.Row(
                                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                    controls=[
                                        ft.Text(f"{r['patient_first']} {r['patient_last']}", weight="bold"),
                                        ft.Container(
                                            padding=6,
                                            border_radius=8,
                                            bgcolor=status_bg(r["status"]),
                                            content=ft.Text(r["status"], color=ft.Colors.WHITE, weight="bold")
                                        )
                                    ]
                                ),
                                ft.Text(f"Test: {r['test_name']}"),
                                ft.Text(f"Result: {r['result_value']} {r.get('unit') or ''}"),
                                ft.Text(f"Normal Range: {r.get('normal_range') or 'N/A'}"),
                                ft.Text(f"Sample Collected: {fmt_dt(r.get('sample_collected_at'))}"),
                                ft.Text(f"Reported: {fmt_dt(r.get('reported_at'))}"),
                                ft.Text(f"Verified By: {verifier_name}"),
                                ft.Text(f"Remarks: {r.get('remarks') or 'N/A'}"),
                            ])
                        )
                    )
            else:
                result_cards.append(ft.Text("No results available"))

            tabs = ft.Tabs(
                tabs=[
                    ft.Tab(
                        label="Catalog",
                        content=ft.Container(
                            padding=10,
                            content=ft.Column(catalog_sections, scroll=ft.ScrollMode.AUTO)
                        )
                    ),
                    ft.Tab(
                        label="Orders",
                        content=ft.Container(
                            padding=10,
                            content=ft.Column(order_cards, scroll=ft.ScrollMode.AUTO)
                        )
                    ),
                    ft.Tab(
                        label="Enter Result",
                        content=ft.Container(
                            padding=10,
                            content=ft.Column([
                                item_dropdown,
                                ft.Row([result_value, result_unit, result_normal_range], spacing=12),
                                ft.Row([result_status, verified_by], spacing=12),
                                result_remarks,
                                ft.FilledButton("Submit Lab Result", on_click=submit_result)
                            ], scroll=ft.ScrollMode.AUTO, spacing=12)
                        )
                    ),
                    ft.Tab(
                        label="History",
                        content=ft.Container(
                            padding=10,
                            content=ft.Column(result_cards, scroll=ft.ScrollMode.AUTO)
                        )
                    ),
                ]
            )

            content_controls.append(tabs)