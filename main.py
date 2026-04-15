import flet as ft
import mysql.connector
from mysql.connector import Error
import datetime

# =====================================================================
# 1. DATABASE CONNECTION & CORE UTILITIES
# =====================================================================
def get_db_connection():
    try:
        conn = mysql.connector.connect(
            host="localhost", 
            user="root", 
            password="root", 
            database="hospital"
        )
        return conn
    except Error as e:
        print(f"CRITICAL: Database Connection Failed: {e}")
        return None

def get_query_data(query, params=None):
    conn = get_db_connection()
    if not conn: 
        return []
    
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(query, params or ())
        data = cursor.fetchall()
        return data
    except Error as e:
        print(f"SQL Read Error: {e}")
        return []
    finally:
        cursor.close()
        conn.close()

def execute_query(query, params):
    conn = get_db_connection()
    if not conn: 
        return False
    
    cursor = conn.cursor()
    try:
        cursor.execute(query, params)
        conn.commit()
        return True
    except Error as e:
        print(f"SQL Write Error: {e}")
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()

def execute_transaction(queries_with_params):
    """Executes multiple queries safely in one transactional block."""
    conn = get_db_connection()
    if not conn: 
        return False
    
    cursor = conn.cursor()
    try:
        for query, params in queries_with_params:
            cursor.execute(query, params)
        conn.commit()
        return True
    except Error as e:
        print(f"Transaction Error: {e}")
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()

# =====================================================================
# 2. MAIN APPLICATION ARCHITECTURE
# =====================================================================
def main(page: ft.Page):
    # App Configuration
    page.title = "Apollo HMS | Enterprise Command Center"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.window_full_screen = True
    page.update()
    page.padding = 0
    page.spacing = 0

    # Universal UI Button Styles
    admin_btn_style = ft.ButtonStyle(
        color=ft.Colors.WHITE, 
        bgcolor="#1E3A8A", 
        shape=ft.RoundedRectangleBorder(radius=8)
    )
    
    rec_btn_style = ft.ButtonStyle(
        color=ft.Colors.WHITE, 
        bgcolor=ft.Colors.TEAL_700, 
        shape=ft.RoundedRectangleBorder(radius=8)
    )

    # Universal Navigation & Feedback Helpers
    def nav_to(tab_name):
        page.session.store.set("active_tab", tab_name)
        page.views.clear()
        page.views.append(dashboard_view())
        page.update()

    def logout_action(e):
        page.session.store.clear()
        page.views.clear()
        page.views.append(login_view())
        page.update()

    def show_snack(message, color):
        page.snack_bar = ft.SnackBar(
            content=ft.Text(message, color=ft.Colors.WHITE), 
            bgcolor=color
        )
        page.snack_bar.open = True
        page.update()

    # =====================================================================
    # 3. DYNAMIC STAFF HIRING LOGIC (WITH AUTO EMP-ID)
    # =====================================================================
    def hire_staff_db(data):
        conn = get_db_connection()
        if not conn: 
            return False
        
        cursor = conn.cursor()
        try:
            # Step A: Map Role ID securely
            cursor.execute("SELECT role_id FROM Role WHERE role_name = %s", (data['role'],))
            role_record = cursor.fetchone()
            if not role_record: 
                return False
            role_id = role_record[0]

            # Step B: Insert into Base Users Table to generate system UID
            user_query = """
                INSERT INTO Users (username, u_password, email, role_id, is_active) 
                VALUES (%s, %s, %s, %s, TRUE)
            """
            cursor.execute(user_query, (data['user'], data['pass'], data['email'], role_id))
            uid = cursor.lastrowid
            
            # Step C: AUTO-GENERATE ENTERPRISE EMPLOYEE ID
            emp_id = f"EMP-{data['role'][:3].upper()}-{uid:04d}"

            # Step D: Dynamic Schema Injection based on Role
            if data['role'] == "Admin":
                admin_query = """
                    INSERT INTO Admin (user_id, first_name, last_name, phone, employee_id, access_level) 
                    VALUES (%s, %s, %s, %s, %s, %s)
                """
                cursor.execute(admin_query, (uid, data['fname'], data['lname'], data['phone'], emp_id, data['access']))
            
            elif data['role'] == "Doctor":
                # Safe type casting for numerics
                dept = int(data['dept']) if data['dept'].strip().isdigit() else None
                exp = int(data['exp']) if data['exp'].strip().isdigit() else None
                fee = float(data['fee']) if data['fee'].strip() else None
                
                doc_query = """
                    INSERT INTO Doctor (
                        user_id, first_name, last_name, gender, date_of_birth, phone, email, 
                        specialization, qualification, license_number, experience_years, 
                        dept_id, consultation_fee, shift, joining_date, blood_group, address
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                cursor.execute(doc_query, (
                    uid, data['fname'], data['lname'], data['gender'], data['dob'], data['phone'], 
                    data['email'], data['spec'], data['qual'], data['lic'], exp, dept, fee, 
                    data['shift'], data['join'], data['bg'], data['addr']
                ))
            
            elif data['role'] == "Receptionist":
                counter = int(data['counter']) if data['counter'].strip().isdigit() else None
                rec_query = """
                    INSERT INTO Receptionist (
                        user_id, first_name, last_name, gender, phone, employee_id, 
                        shift, counter_number, joining_date
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                cursor.execute(rec_query, (uid, data['fname'], data['lname'], data['gender'], data['phone'], emp_id, data['shift'], counter, data['join']))
            
            elif data['role'] == "Lab Technician":
                lab_query = """
                    INSERT INTO LabTechnician (
                        user_id, first_name, last_name, gender, phone, employee_id, 
                        qualification, specialization, shift, joining_date
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                cursor.execute(lab_query, (uid, data['fname'], data['lname'], data['gender'], data['phone'], emp_id, data['qual'], data['spec'], data['shift'], data['join']))
            
            elif data['role'] == "Pharmacist":
                pharm_query = """
                    INSERT INTO Pharmacist (
                        user_id, first_name, last_name, phone, license_number, shift
                    ) VALUES (%s, %s, %s, %s, %s, %s)
                """
                cursor.execute(pharm_query, (uid, data['fname'], data['lname'], data['phone'], data['lic'], data['shift']))

            conn.commit()
            return True

        except Exception as e:
            print(f"Hire Error DB: {e}")
            conn.rollback()
            return False
        finally:
            cursor.close()
            conn.close()

    # =====================================================================
    # 4. VIEW: SECURE LOGIN GATEKEEPER
    # =====================================================================
    def login_view():
        username_input = ft.TextField(
            label="Username", 
            width=320, 
            border_radius=10, 
            prefix_icon=ft.Icons.PERSON,
            filled=True,
            bgcolor="#EDF2F7"
        )
        
        password_input = ft.TextField(
            label="Password", 
            password=True, 
            width=320, 
            border_radius=10, 
            can_reveal_password=True, 
            prefix_icon=ft.Icons.LOCK,
            filled=True,
            bgcolor="#EDF2F7"
        )
        
        error_msg = ft.Text("", color=ft.Colors.RED)

        def handle_login(e):
            query = """
                SELECT u.user_id, u.username, r.role_name 
                FROM Users u 
                JOIN Role r ON u.role_id = r.role_id 
                WHERE u.username=%s AND u.u_password=%s AND u.is_active=TRUE
            """
            data = get_query_data(query, (username_input.value, password_input.value))
            
            if data:
                user = data[0]
                page.session.store.set("user_id", user['user_id'])
                page.session.store.set("username", user['username'])
                page.session.store.set("role", user['role_name'])
                
                # Role-Based Context Setup
                if user['role_name'] == "Admin": 
                    page.session.store.set("active_tab", "admin_overview")
                
                elif user['role_name'] == "Receptionist": 
                    rec_query = "SELECT receptionist_id FROM Receptionist WHERE user_id=%s"
                    rec_data = get_query_data(rec_query, (user['user_id'],))
                    if rec_data: 
                        page.session.store.set("rec_id", rec_data[0]['receptionist_id'])
                    page.session.store.set("active_tab", "rec_overview")
                
                else: 
                    page.session.store.set("active_tab", "unauthorized")
                
                # Execute Route
                page.views.clear()
                page.views.append(dashboard_view())
                page.update()
            else:
                error_msg.value = "Authentication Failed. Check credentials."
                page.update()

        # ---------------- LEFT SIDE (IMAGE + BRANDING) ----------------
        left_section = ft.Container(
            expand=True,
            margin=0,
            padding=0,
            content=ft.Stack(
                expand=True,   # 🔥 IMPORTANT
                controls=[
                    # ✅ FULL IMAGE (fills complete left side)
                    ft.Image(
                        src="image.jpeg",
                        fit="cover",
                        expand=True,
                    ),

                    # ✅ DARK OVERLAY
                    ft.Container(
                        expand=True,
                        bgcolor="#000000",
                        opacity=0.35
                    ),

                    # ✅ TEXT (LEFT SIDE POSITIONED LIKE YOUR IMAGE)
                    ft.Container(
                        expand=True,
                        padding=40,
                        alignment=ft.alignment.Alignment(-1,1),  # 🔥 FIX POSITION
                        content=ft.Column(
                            alignment=ft.MainAxisAlignment.END,
                            horizontal_alignment=ft.CrossAxisAlignment.START,
                            spacing=5,
                            controls=[
                                ft.Text(
                                    "Welcome to",
                                    size=20,
                                    color="white"
                                ),
                                ft.Text(
                                    "APOLLO HOSPITALS",
                                    size=40,
                                    weight="bold",
                                    color="white"
                                ),
                                ft.Text(
                                    "EHR & HMS",
                                    size=16,
                                    color="#E2E8F0"
                                ),
                            ]
                        )
                    )
                ]
            )
        )

        # ---------------- RIGHT SIDE (LOGIN FORM) ----------------
        login_section = ft.Container(
            expand=True,
            bgcolor="#FFFFFF",
            content=ft.Column(
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Icon(
                        ft.Icons.LOCAL_HOSPITAL_ROUNDED, 
                        size=60, 
                        color="#38A169"
                    ),

                    ft.Text(
                        "APOLLO HOSPITAL", 
                        size=30, 
                        weight="bold", 
                        color="#38A169"
                    ),

                    ft.Text(
                        "Login to continue",
                        size=14,
                        color="#718096"
                    ),

                    ft.Container(height=20),

                    username_input,
                    password_input,
                    error_msg,

                    ft.Container(height=10),

                    ft.FilledButton(
                        "Login", 
                        color="#FFFFFF",
                        bgcolor="#1A202C",
                        on_click=handle_login, 
                        width=320, 
                        height=50, 
                        style=admin_btn_style
                    )
                ]
            )
        )

        # ---------------- FINAL VIEW ----------------
        return ft.View(
            route="/login",
            controls=[
                ft.Row(
                    expand=True,
                    spacing=0,
                    controls=[
                        left_section,
                        login_section
                    ]
                )
            ]
        )

    # =====================================================================
    # 5. VIEW: MASTER DASHBOARD ENGINE
    # =====================================================================
    def dashboard_view():
        uid = page.session.store.get("user_id")
        user_name = page.session.store.get("username")
        role = page.session.store.get("role")
        tab = page.session.store.get("active_tab")

        # -------------------------------------------------------------
        # 5.1. DYNAMIC ROLE-BASED SIDEBAR
        # -------------------------------------------------------------
        sidebar_controls = []
        sidebar_bg = "#004D40"

        if role == "Admin":
            level_data = get_query_data("SELECT access_level FROM Admin WHERE user_id = %s", (uid,))
            level = level_data[0]['access_level'] if level_data else "standard"
            
            sidebar_controls = [
                ft.Text("COMMAND CENTER", color="white", weight="bold", size=20), 
                ft.Divider(color="white24"),
                ft.ListTile(
                    leading=ft.Icon(ft.Icons.ANALYTICS, color="white"), 
                    title=ft.Text("Overview", color="white"), 
                    on_click=lambda _: nav_to("admin_overview")
                ),
                ft.ListTile(
                    leading=ft.Icon(ft.Icons.PEOPLE_ALT, color="white"), 
                    title=ft.Text("Manage Staff", color="white"), 
                    on_click=lambda _: nav_to("staff")
                ),
                ft.ListTile(
                    leading=ft.Icon(ft.Icons.SCHEDULE, color="white"), 
                    title=ft.Text("Staff Schedules", color="white"), 
                    on_click=lambda _: nav_to("schedules")
                ),
                ft.ListTile(
                    leading=ft.Icon(ft.Icons.PERSON_SEARCH, color="white"), 
                    title=ft.Text("Patients Directory", color="white"), 
                    on_click=lambda _: nav_to("patients")
                ),
                ft.ListTile(
                    leading=ft.Icon(ft.Icons.MEDICATION, color="white"), 
                    title=ft.Text("Pharmacy Inventory", color="white"), 
                    on_click=lambda _: nav_to("meds")
                ),
                ft.ListTile(
                    leading=ft.Icon(ft.Icons.DOMAIN, color="white"), 
                    title=ft.Text("Facility Management", color="white"), 
                    on_click=lambda _: nav_to("rooms")
                ),
                ft.ListTile(
                    leading=ft.Icon(ft.Icons.ATTACH_MONEY, color="white"), 
                    title=ft.Text("Revenue Overview", color="white"), 
                    on_click=lambda _: nav_to("billing")
                ),
                ft.Container(expand=True),
                ft.Container(
                    bgcolor="white10", 
                    padding=15, 
                    border_radius=10, 
                    content=ft.Text(f"Admin: {user_name}\nAccess: {level.upper()}", color="white", size=12)
                ),
                ft.TextButton(
                    "Secure Logout", 
                    icon=ft.Icons.LOGOUT, 
                    on_click=logout_action, 
                    style=ft.ButtonStyle(color="white70")
                )
            ]
            
        elif role == "Receptionist":
            sidebar_bg = ft.Colors.TEAL_900
            sidebar_controls = [
                ft.Text("FRONT DESK", color="white", weight="bold", size=20), 
                ft.Divider(color="white24"),
                ft.ListTile(
                    leading=ft.Icon(ft.Icons.HOME, color="white"), 
                    title=ft.Text("Desk Overview", color="white"), 
                    on_click=lambda _: nav_to("rec_overview")
                ),
                ft.ListTile(
                    leading=ft.Icon(ft.Icons.PERSON_ADD, color="white"), 
                    title=ft.Text("Register Patient", color="white"), 
                    on_click=lambda _: nav_to("reg_patient")
                ),
                ft.ListTile(
                    leading=ft.Icon(ft.Icons.CALENDAR_MONTH, color="white"), 
                    title=ft.Text("Appointments Desk", color="white"), 
                    on_click=lambda _: nav_to("book_appt")
                ),
                ft.ListTile(
                    leading=ft.Icon(ft.Icons.BED, color="white"), 
                    title=ft.Text("IPD Admissions", color="white"), 
                    on_click=lambda _: nav_to("admissions")
                ),
                ft.ListTile(
                    leading=ft.Icon(ft.Icons.PAYMENT, color="white"), 
                    title=ft.Text("Process Billing", color="white"), 
                    on_click=lambda _: nav_to("rec_billing")
                ),
                ft.ListTile(
                    leading=ft.Icon(ft.Icons.FORMAT_LIST_BULLETED, color="white"), 
                    title=ft.Text("All Patients", color="white"), 
                    on_click=lambda _: nav_to("patients")
                ),
                ft.Container(expand=True),
                ft.Container(
                    bgcolor="white10", 
                    padding=15, 
                    border_radius=10, 
                    content=ft.Text(f"Staff: {user_name}\nRole: Receptionist", color="white", size=12)
                ),
                ft.TextButton(
                    "Secure Logout", 
                    icon=ft.Icons.LOGOUT, 
                    on_click=logout_action, 
                    style=ft.ButtonStyle(color="white70")
                )
            ]

        sidebar = ft.Container(
            width=280, 
            bgcolor=sidebar_bg, 
            padding=20, 
            content=ft.Column(controls=sidebar_controls)
        )

        # -------------------------------------------------------------
        # 5.2. MAIN WORKSPACE HEADER & ROUTING TITLES
        # -------------------------------------------------------------
        nice_titles = {
            "admin_overview": "Enterprise Dashboard", 
            "rec_overview": "Front Desk Operations",
            "reg_patient": "Comprehensive Patient Registration", 
            "book_appt": "Appointment Scheduling & Queue",
            "admissions": "IPD Admissions & Bed Allocation", 
            "rec_billing": "Patient Billing & Invoicing",
            "staff": "Human Resources & Staff Directory", 
            "schedules": "Enterprise Staff Schedules",
            "patients": "Global Patient Directory",
            "meds": "Pharmacy Inventory Control", 
            "rooms": "Wards, Rooms & Bed Configuration", 
            "billing": "Enterprise Revenue Overview"
        }

        header_banner = ft.Container(
            padding=ft.padding.only(bottom=20),
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN, 
                controls=[
                    ft.Row(
                        controls=[
                            ft.Icon(
                                ft.Icons.LOCAL_HOSPITAL, 
                                size=45, 
                                color=ft.Colors.BLUE_900 if role == "Admin" else ft.Colors.TEAL_700
                            ),
                            ft.Text(
                                "APOLLO HOSPITALS", 
                                size=32, 
                                weight="w900", 
                                color=ft.Colors.BLUE_900 if role == "Admin" else ft.Colors.TEAL_900
                            )
                        ]
                    ),
                    ft.FilledButton(
                        "Export Report PDF", 
                        icon=ft.Icons.PICTURE_AS_PDF, 
                        style=admin_btn_style if role == "Admin" else rec_btn_style
                    )
                ]
            )
        )

        content_controls = [
            header_banner, 
            ft.Text(
                nice_titles.get(tab, tab), 
                size=28, 
                weight="bold", 
                color=ft.Colors.GREY_800
            ), 
            ft.Divider(height=30)
        ]

        # =====================================================================
        # 5.3. MODULE: OVERVIEW DASHBOARDS
        # =====================================================================
        if tab == "admin_overview":
            banner = ft.Container(
                bgcolor=ft.Colors.BLUE_900, 
                padding=40, 
                border_radius=15, 
                margin=ft.margin.only(bottom=20),
                content=ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN, 
                    controls=[
                        ft.Column(
                            controls=[
                                ft.Text("Apollo Command Center", size=32, weight="bold", color=ft.Colors.WHITE), 
                                ft.Text("Enterprise Operations & Resource Management", size=16, color=ft.Colors.WHITE70)
                            ]
                        ), 
                        ft.Icon(ft.Icons.ADMIN_PANEL_SETTINGS, size=100, color=ft.Colors.WHITE24)
                    ]
                )
            )
            content_controls.append(banner)
            
            revenue_card = ft.Card(
                ft.Container(
                    padding=25, 
                    width=320, 
                    content=ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN, 
                        controls=[
                            ft.Column(
                                controls=[
                                    ft.Text("REVENUE YTD", color=ft.Colors.GREY_600), 
                                    ft.Text("₹4,50,000", size=26, weight="bold")
                                ]
                            ), 
                            ft.Icon(ft.Icons.TRENDING_UP, color=ft.Colors.GREEN, size=40)
                        ]
                    )
                )
            )
            
            ward_card = ft.Card(
                ft.Container(
                    padding=25, 
                    width=320, 
                    content=ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN, 
                        controls=[
                            ft.Column(
                                controls=[
                                    ft.Text("WARD OCCUPANCY", color=ft.Colors.GREY_600), 
                                    ft.Text("85%", size=26, weight="bold")
                                ]
                            ), 
                            ft.Stack(
                                controls=[
                                    ft.ProgressRing(value=0.85, color=ft.Colors.ORANGE, bgcolor=ft.Colors.GREY_200, width=50, height=50), 
                                    ft.Container(padding=15, content=ft.Icon(ft.Icons.BED, size=20, color=ft.Colors.ORANGE))
                                ]
                            )
                        ]
                    )
                )
            )
            
            content_controls.append(
                ft.Row(
                    controls=[revenue_card, ward_card]
                )
            )

        elif tab == "rec_overview":
            banner = ft.Container(
                bgcolor=ft.Colors.TEAL_700, 
                padding=40, 
                border_radius=15, 
                margin=ft.margin.only(bottom=20),
                content=ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN, 
                    controls=[
                        ft.Column(
                            controls=[
                                ft.Text("Front Desk Operations", size=32, weight="bold", color=ft.Colors.WHITE), 
                                ft.Text("Manage patient flow, appointments, and billing efficiently.", size=16, color=ft.Colors.WHITE70)
                            ]
                        ), 
                        ft.Icon(ft.Icons.SUPPORT_AGENT, size=100, color=ft.Colors.WHITE24)
                    ]
                )
            )
            content_controls.append(banner)
            
            appt_card = ft.Card(
                ft.Container(
                    padding=25, 
                    width=320, 
                    content=ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN, 
                        controls=[
                            ft.Column(
                                controls=[
                                    ft.Text("TODAY'S APPOINTMENTS", color=ft.Colors.GREY_600), 
                                    ft.Text("24 / 30", size=26, weight="bold")
                                ]
                            ), 
                            ft.ProgressRing(value=24/30, color=ft.Colors.TEAL, bgcolor=ft.Colors.GREY_200, width=50, height=50)
                        ]
                    )
                )
            )
            
            bill_card = ft.Card(
                ft.Container(
                    padding=25, 
                    width=320, 
                    content=ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN, 
                        controls=[
                            ft.Column(
                                controls=[
                                    ft.Text("PENDING BILLS", color=ft.Colors.GREY_600), 
                                    ft.Text("5", size=26, weight="bold")
                                ]
                            ), 
                            ft.Icon(ft.Icons.WARNING_ROUNDED, color=ft.Colors.RED_400, size=40)
                        ]
                    )
                )
            )
            
            content_controls.append(
                ft.Row(
                    controls=[appt_card, bill_card]
                )
            )

        # =====================================================================
        # 5.4. MODULE: STAFF MANAGEMENT (THE BULLETPROOF UI FIX)
        # =====================================================================
        elif tab == "staff":
            level_data = get_query_data("SELECT access_level FROM Admin WHERE user_id = %s", (uid,))
            level = level_data[0]['access_level'] if level_data else "standard"

            # Shared Form Inputs
            us_in = ft.TextField(label="System Username", width=250)
            pa_in = ft.TextField(label="System Password", password=True, width=250)
            em_in = ft.TextField(label="System Email Address", width=250)
            fn_in = ft.TextField(label="First Name", width=250)
            ln_in = ft.TextField(label="Last Name", width=250)
            ph_in = ft.TextField(label="Phone Number", width=250)
            
            ro_drop = ft.Dropdown(
                label="Assign Role", 
                width=250, 
                options=[
                    ft.dropdown.Option("Doctor"), 
                    ft.dropdown.Option("Receptionist"), 
                    ft.dropdown.Option("Admin"), 
                    ft.dropdown.Option("Lab Technician"), 
                    ft.dropdown.Option("Pharmacist")
                ]
            )
            
            # --- DYNAMIC FIELD DEFINITIONS ---
            acc_drop = ft.Dropdown(label="Admin Access Level", width=250, options=[ft.dropdown.Option("super"), ft.dropdown.Option("standard")])
            gen_drop = ft.Dropdown(label="Gender", width=250, options=[ft.dropdown.Option("Male"), ft.dropdown.Option("Female"), ft.dropdown.Option("Other")])
            dob_in = ft.TextField(label="DOB (YYYY-MM-DD)", width=250)
            spec_in = ft.TextField(label="Specialization", width=250)
            qual_in = ft.TextField(label="Qualifications", width=250)
            lic_in = ft.TextField(label="License Number", width=250)
            exp_in = ft.TextField(label="Years of Experience", width=250)
            dept_in = ft.TextField(label="Department ID", width=250)
            fee_in = ft.TextField(label="Consultation Fee (₹)", width=250)
            shift_drop = ft.Dropdown(label="Assigned Shift", width=250, options=[ft.dropdown.Option("Morning"), ft.dropdown.Option("Evening"), ft.dropdown.Option("Night"), ft.dropdown.Option("Rotating")])
            join_in = ft.TextField(label="Joining Date (YYYY-MM-DD)", width=250)
            bg_drop = ft.Dropdown(label="Blood Group", width=250, options=[ft.dropdown.Option("A+"), ft.dropdown.Option("O+"), ft.dropdown.Option("B+"), ft.dropdown.Option("AB+"), ft.dropdown.Option("O-")])
            addr_in = ft.TextField(label="Full Residential Address", width=520)
            counter_in = ft.TextField(label="Desk/Counter Number", width=250)

            # This is the crucial container. We call .update() on THIS container.
            dynamic_fields = ft.Column(controls=[])

            def build_dynamic_form(e):
                # 1. Clear existing controls
                dynamic_fields.controls.clear()
                
                # 2. Check if a role is actually selected
                if not ro_drop.value:
                    dynamic_fields.update()
                    return

                # 3. Add Header and Note
                dynamic_fields.controls.append(
                    ft.Text(f"Required Schema Attributes for {ro_drop.value}", weight="bold", color=ft.Colors.BLUE_900)
                )
                dynamic_fields.controls.append(
                    ft.Text("Note: Employee ID will be auto-generated upon save.", italic=True, color=ft.Colors.GREY)
                )
                
                # 4. Inject specific rows based on exact schema
                if ro_drop.value == "Admin":
                    dynamic_fields.controls.append(
                        ft.Row(controls=[acc_drop])
                    )
                
                elif ro_drop.value == "Doctor":
                    dynamic_fields.controls.extend([
                        ft.Row(controls=[gen_drop, dob_in]),
                        ft.Row(controls=[spec_in, qual_in]),
                        ft.Row(controls=[lic_in, exp_in]),
                        ft.Row(controls=[dept_in, fee_in]),
                        ft.Row(controls=[shift_drop, join_in]),
                        ft.Row(controls=[bg_drop]),
                        addr_in
                    ])
                
                elif ro_drop.value == "Receptionist":
                    dynamic_fields.controls.extend([
                        ft.Row(controls=[gen_drop, shift_drop]),
                        ft.Row(controls=[counter_in, join_in])
                    ])
                
                elif ro_drop.value == "Lab Technician":
                    dynamic_fields.controls.extend([
                        ft.Row(controls=[gen_drop, shift_drop]),
                        ft.Row(controls=[spec_in, qual_in]),
                        ft.Row(controls=[join_in])
                    ])
                
                elif ro_drop.value == "Pharmacist":
                    dynamic_fields.controls.extend([
                        ft.Row(controls=[lic_in, shift_drop])
                    ])
                
                # 5. THE FIX: Force the specific container to redraw itself instantly
                dynamic_fields.update()

            # Attach event listener to dropdown
            ro_drop.on_change = build_dynamic_form

            def execute_hire(e):
                data_dict = {
                    "role": ro_drop.value, 
                    "user": us_in.value, 
                    "pass": pa_in.value, 
                    "email": em_in.value,
                    "fname": fn_in.value, 
                    "lname": ln_in.value, 
                    "phone": ph_in.value,
                    "access": acc_drop.value, 
                    "gender": gen_drop.value, 
                    "dob": dob_in.value,
                    "spec": spec_in.value, 
                    "qual": qual_in.value, 
                    "lic": lic_in.value,
                    "exp": exp_in.value, 
                    "dept": dept_in.value, 
                    "fee": fee_in.value,
                    "shift": shift_drop.value, 
                    "join": join_in.value, 
                    "bg": bg_drop.value,
                    "addr": addr_in.value, 
                    "counter": counter_in.value
                }
                
                if hire_staff_db(data_dict):
                    hire_dlg.open = False
                    page.update()
                    show_snack("Personnel Successfully Registered in Database!", ft.Colors.GREEN)
                    nav_to("staff")
                else:
                    show_snack("Registration Failed. Check unique constraints (e.g. Username/Email).", ft.Colors.RED)

            hire_dlg = ft.AlertDialog(
                title=ft.Text("Register New Personnel", weight="bold"),
                content=ft.Container(
                    width=570, 
                    content=ft.Column(
                        controls=[
                            ft.Text("System Access Credentials", weight="bold", color=ft.Colors.BLUE_900),
                            ft.Row(
                                controls=[us_in, pa_in]
                            ), 
                            ft.Row(
                                controls=[em_in, ro_drop]
                            ),
                            ft.Divider(),
                            ft.Text("Basic Identity", weight="bold", color=ft.Colors.BLUE_900),
                            ft.Row(
                                controls=[fn_in, ln_in]
                            ), 
                            ft.Row(
                                controls=[ph_in]
                            ),
                            ft.Divider(),
                            dynamic_fields
                        ], 
                        tight=True, 
                        scroll=ft.ScrollMode.AUTO
                    )
                ),
                actions=[
                    ft.FilledButton(
                        "Save Complete Profile to Database", 
                        on_click=execute_hire, 
                        style=admin_btn_style
                    )
                ]
            )

            # Eye Icon Logic to View Staff Database Profile
            def open_staff_profile(staff_member):
                table_map = {
                    "Admin": "Admin", 
                    "Doctor": "Doctor", 
                    "Receptionist": "Receptionist", 
                    "Lab Technician": "LabTechnician", 
                    "Pharmacist": "Pharmacist"
                }
                table_name = table_map.get(staff_member['role_name'], staff_member['role_name'].replace(" ", ""))
                
                profile_query = f"SELECT * FROM {table_name} WHERE user_id = %s"
                profile_data = get_query_data(profile_query, (staff_member['user_id'],))
                p = profile_data[0] if profile_data else {}

                extra_controls = []
                if staff_member['role_name'] == "Doctor":
                    extra_controls.append(ft.Text(f"Specialization: {p.get('specialization')} | Qualification: {p.get('qualification')}"))
                    extra_controls.append(ft.Text(f"Medical License: {p.get('license_number')} | Experience: {p.get('experience_years')} yrs"))
                    extra_controls.append(ft.Text(f"Consultation Fee: ₹{p.get('consultation_fee')} | Active Shift: {p.get('shift')}"))
                    extra_controls.append(ft.Text(f"Joining Date: {p.get('joining_date')} | Dept ID: {p.get('dept_id')}"))
                
                elif staff_member['role_name'] == "Admin":
                    extra_controls.append(ft.Text(f"Employee ID: {p.get('employee_id')} | Access Rights: {str(p.get('access_level')).upper()}"))
                
                elif staff_member['role_name'] == "Receptionist":
                    extra_controls.append(ft.Text(f"Employee ID: {p.get('employee_id')} | Active Shift: {p.get('shift')}"))
                    extra_controls.append(ft.Text(f"Counter Number: {p.get('counter_number')} | Joining Date: {p.get('joining_date')}"))
                
                elif staff_member['role_name'] == "Lab Technician":
                    extra_controls.append(ft.Text(f"Employee ID: {p.get('employee_id')} | Active Shift: {p.get('shift')}"))
                    extra_controls.append(ft.Text(f"Specialization: {p.get('specialization')} | Qualification: {p.get('qualification')}"))
                    extra_controls.append(ft.Text(f"Joining Date: {p.get('joining_date')}"))
                
                elif staff_member['role_name'] == "Pharmacist":
                    extra_controls.append(ft.Text(f"Pharmacy License: {p.get('license_number')} | Active Shift: {p.get('shift')}"))

                staff_dlg = ft.AlertDialog(
                    title=ft.Text(f"Personnel Profile: {staff_member['username']}", weight="bold", color=ft.Colors.BLUE_900),
                    content=ft.Container(
                        width=500, 
                        content=ft.Column(
                            controls=[
                                ft.Row(
                                    controls=[
                                        ft.Text(f"System ID: {staff_member['user_id']}", weight="bold"), 
                                        ft.Text(f"Role: {staff_member['role_name']}", weight="bold", color=ft.Colors.GREY_600)
                                    ], 
                                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                                ),
                                ft.Divider(),
                                ft.Text("Basic Info", weight="bold", color=ft.Colors.GREY_600),
                                ft.Text(f"Name: {p.get('first_name', 'Data Missing')} {p.get('last_name', '')}"),
                                ft.Text(f"Email: {staff_member['email']} | Phone: {p.get('phone', 'N/A')}"),
                                ft.Text(
                                    f"System Access: {'GRANTED' if staff_member['is_active'] else 'REVOKED'}", 
                                    color=ft.Colors.GREEN if staff_member['is_active'] else ft.Colors.RED, 
                                    weight="bold"
                                ),
                                ft.Divider(),
                                ft.Text("Schema & Operational Attributes", weight="bold", color=ft.Colors.GREY_600),
                                *extra_controls
                            ], 
                            tight=True, 
                            scroll=ft.ScrollMode.AUTO
                        )
                    ),
                    actions=[
                        ft.TextButton(
                            "Close Profile", 
                            on_click=lambda e: setattr(staff_dlg, 'open', False) or page.update()
                        )
                    ]
                )
                page.overlay.append(staff_dlg)
                staff_dlg.open = True
                page.update()

            staff_data = get_query_data("SELECT u.user_id, u.username, r.role_name, u.email, u.is_active FROM Users u JOIN Role r ON u.role_id = r.role_id")
            
            if not staff_data: 
                content_controls.append(ft.Text("No personnel data found in system.", color=ft.Colors.GREY))
            else:
                table_rows = []
                for s in staff_data:
                    view_btn = ft.IconButton(
                        icon=ft.Icons.VISIBILITY, 
                        icon_color=ft.Colors.BLUE_900, 
                        on_click=lambda e, data=s: open_staff_profile(data)
                    )
                    table_rows.append(
                        ft.DataRow(
                            cells=[
                                ft.DataCell(ft.Text(s['username'])), 
                                ft.DataCell(ft.Text(s['role_name'])), 
                                ft.DataCell(ft.Text(s['email'])), 
                                ft.DataCell(view_btn)
                            ]
                        )
                    )
                
                if level == "super": 
                    content_controls.append(
                        ft.FilledButton(
                            "Register New Staff Member", 
                            icon=ft.Icons.PERSON_ADD, 
                            style=admin_btn_style, 
                            on_click=lambda e: page.overlay.append(hire_dlg) or setattr(hire_dlg, 'open', True) or page.update()
                        )
                    )
                
                content_controls.extend([
                    ft.Divider(),
                    ft.Text("Click the eye icon to view comprehensive schema attributes for any staff member.", color=ft.Colors.GREY), 
                    ft.DataTable(
                        columns=[
                            ft.DataColumn(ft.Text("Username")), 
                            ft.DataColumn(ft.Text("Role")), 
                            ft.DataColumn(ft.Text("Email Address")), 
                            ft.DataColumn(ft.Text("Action"))
                        ], 
                        rows=table_rows
                    )
                ])

        # =====================================================================
        # 5.5. MODULE: STAFF SCHEDULES (RESTORED AS REQUESTED)
        # =====================================================================
        elif tab == "schedules":
            schedule_query = """
                SELECT s.schedule_id, u.username, r.role_name, s.work_date, s.shift_start, s.shift_end, s.status 
                FROM StaffSchedule s 
                JOIN Users u ON s.user_id = u.user_id 
                JOIN Role r ON s.role_id = r.role_id 
                ORDER BY s.work_date DESC, s.shift_start ASC
            """
            sched_data = get_query_data(schedule_query)

            if not sched_data:
                content_controls.append(
                    ft.Text("No staff schedules currently exist in the database.", color=ft.Colors.GREY)
                )
            else:
                s_rows = []
                for s in sched_data:
                    if s['status'] == 'Present':
                        status_color = ft.Colors.GREEN
                    elif s['status'] == 'Scheduled':
                        status_color = ft.Colors.ORANGE
                    else:
                        status_color = ft.Colors.RED
                        
                    s_rows.append(
                        ft.DataRow(
                            cells=[
                                ft.DataCell(ft.Text(str(s['schedule_id']))),
                                ft.DataCell(ft.Text(s['username'])),
                                ft.DataCell(ft.Text(s['role_name'])),
                                ft.DataCell(ft.Text(str(s['work_date']))),
                                ft.DataCell(ft.Text(f"{s['shift_start']} - {s['shift_end']}")),
                                ft.DataCell(
                                    ft.Container(
                                        content=ft.Text(s['status'].upper(), weight="bold", color=ft.Colors.WHITE, size=11), 
                                        bgcolor=status_color, 
                                        padding=5, 
                                        border_radius=5
                                    )
                                )
                            ]
                        )
                    )
                
                content_controls.extend([
                    ft.Text("Enterprise Staff Schedule Logs", weight="bold", size=20), 
                    ft.DataTable(
                        columns=[
                            ft.DataColumn(ft.Text("Schedule ID")), 
                            ft.DataColumn(ft.Text("Staff Username")), 
                            ft.DataColumn(ft.Text("Role")), 
                            ft.DataColumn(ft.Text("Work Date")), 
                            ft.DataColumn(ft.Text("Shift Time")),
                            ft.DataColumn(ft.Text("Attendance Status"))
                        ], 
                        rows=s_rows
                    )
                ])

        # =====================================================================
        # 5.6. MODULE: COMPREHENSIVE PATIENT REGISTRATION
        # =====================================================================
        elif tab == "reg_patient":
            fn = ft.TextField(label="First Name", width=250)
            ln = ft.TextField(label="Last Name", width=250)
            dob = ft.TextField(label="Date of Birth (YYYY-MM-DD)", width=250)
            gen = ft.Dropdown(label="Gender", width=250, options=[ft.dropdown.Option("Male"), ft.dropdown.Option("Female"), ft.dropdown.Option("Other")])
            bg = ft.Dropdown(label="Blood Group", width=250, options=[ft.dropdown.Option("A+"), ft.dropdown.Option("O+"), ft.dropdown.Option("B+"), ft.dropdown.Option("AB+"), ft.dropdown.Option("O-"), ft.dropdown.Option("A-"), ft.dropdown.Option("B-")])
            ph = ft.TextField(label="Phone Number", width=250)
            em = ft.TextField(label="Email Address", width=250)
            addr = ft.TextField(label="Residential Address", width=520)
            city = ft.TextField(label="City", width=160)
            st = ft.TextField(label="State", width=160)
            pin = ft.TextField(label="Postal Code", width=160)
            e_name = ft.TextField(label="Emergency Contact Name", width=250)
            e_phone = ft.TextField(label="Emergency Phone", width=250)
            e_rel = ft.TextField(label="Relationship", width=250)
            i_prov = ft.TextField(label="Insurance Provider", width=250)
            i_pol = ft.TextField(label="Policy Number", width=250)

            def save_comprehensive_patient(e):
                conn = get_db_connection()
                if not conn: return
                cursor = conn.cursor(dictionary=True)
                try:
                    # 1. AUTO-GENERATE AHL-PT-XXXX REGISTRATION NO
                    cursor.execute("SELECT MAX(patient_id) as max_id FROM Patient")
                    res = cursor.fetchone()
                    next_id = (res['max_id'] or 0) + 1 if res else 1
                    auto_reg_no = f"AHL-PT-{next_id:04d}"

                    # 2. Insert Full Schema
                    query = """
                        INSERT INTO Patient (
                            registration_no, first_name, last_name, gender, date_of_birth, blood_group, 
                            phone, email, address, city, state, pincode, 
                            emergency_contact_name, emergency_contact_phone, emergency_contact_rel, 
                            insurance_provider, insurance_policy_no, registered_by
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """
                    params = (
                        auto_reg_no, fn.value, ln.value, gen.value, dob.value, bg.value, 
                        ph.value, em.value, addr.value, city.value, st.value, pin.value, 
                        e_name.value, e_phone.value, e_rel.value, i_prov.value, i_pol.value, uid
                    )
                    cursor.execute(query, params)
                    conn.commit()
                    show_snack(f"Success! Auto-Generated Patient ID: {auto_reg_no}", ft.Colors.GREEN)
                    nav_to("reg_patient")
                except Exception as ex:
                    conn.rollback()
                    show_snack(f"Database Error: {ex}", ft.Colors.RED)
                finally:
                    cursor.close()
                    conn.close()

            content_controls.append(
                ft.Column(
                    spacing=15,
                    controls=[
                        ft.Text("General Medical Information", weight="bold", color=ft.Colors.TEAL_900),
                        ft.Text("Note: Registration Number (AHL-PT-XXXX) is generated automatically upon save.", italic=True, color=ft.Colors.GREY),
                        ft.Row(controls=[fn, ln, dob]), 
                        ft.Row(controls=[gen, bg, ph, em]),
                        ft.Divider(), 
                        ft.Text("Location & Demographics", weight="bold", color=ft.Colors.TEAL_900),
                        ft.Row(controls=[addr, city, st, pin]),
                        ft.Divider(), 
                        ft.Text("Emergency Contacts & Insurance", weight="bold", color=ft.Colors.TEAL_900),
                        ft.Row(controls=[e_name, e_phone, e_rel]), 
                        ft.Row(controls=[i_prov, i_pol]),
                        ft.FilledButton(
                            "Commit Patient to Database", 
                            icon=ft.Icons.SAVE, 
                            style=rec_btn_style, 
                            on_click=save_comprehensive_patient
                        )
                    ]
                )
            )

        # =====================================================================
        # 5.7. MODULE: PATIENT MASTER DIRECTORY
        # =====================================================================
        elif tab == "patients":
            def open_patient_profile(p):
                patient_dlg = ft.AlertDialog(
                    title=ft.Text(f"Comprehensive Profile: {p['first_name']} {p['last_name']}", weight="bold", color=ft.Colors.BLUE_900),
                    content=ft.Container(
                        width=650, 
                        content=ft.Column(
                            controls=[
                                ft.Row(
                                    controls=[
                                        ft.Text(f"Reg No: {p['registration_no']}", weight="bold"), 
                                        ft.Text(f"Database ID: {p['patient_id']}")
                                    ], 
                                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                                ), 
                                ft.Divider(),
                                ft.Text("Personal Information", weight="bold", color=ft.Colors.GREY_600), 
                                ft.Text(f"Date of Birth: {p['date_of_birth']} | Gender: {p['gender']} | Blood Group: {p['blood_group']}"), 
                                ft.Text(f"Phone: {p['phone']} | Email: {p['email']}"), 
                                ft.Divider(),
                                ft.Text("Residential Address", weight="bold", color=ft.Colors.GREY_600), 
                                ft.Text(f"{p['address']}, {p['city']}, {p['state']} - {p['pincode']}"), 
                                ft.Divider(),
                                ft.Text("Emergency Details & Health Insurance", weight="bold", color=ft.Colors.GREY_600), 
                                ft.Text(f"Contact Name: {p['emergency_contact_name']} ({p['emergency_contact_rel']}) - {p['emergency_contact_phone']}"), 
                                ft.Text(f"Provider: {p['insurance_provider']} | Policy No: {p['insurance_policy_no']}"),
                                ft.Text(f"Account Created: {p['registered_at']}", size=10, color=ft.Colors.GREY_400)
                            ], 
                            tight=True, 
                            scroll=ft.ScrollMode.AUTO
                        )
                    ),
                    actions=[
                        ft.TextButton(
                            "Close Window", 
                            on_click=lambda e: setattr(patient_dlg, 'open', False) or page.update()
                        )
                    ]
                )
                page.overlay.append(patient_dlg)
                patient_dlg.open = True
                page.update()

            patient_data = get_query_data("SELECT * FROM Patient")
            if not patient_data: 
                content_controls.append(ft.Text("No patients currently exist in the database.", color=ft.Colors.GREY))
            else:
                p_rows = []
                for p in patient_data:
                    eye_btn = ft.IconButton(
                        icon=ft.Icons.VISIBILITY, 
                        icon_color=ft.Colors.BLUE_900, 
                        on_click=lambda e, data=p: open_patient_profile(data)
                    )
                    p_rows.append(
                        ft.DataRow(
                            cells=[
                                ft.DataCell(ft.Text(f"{p['registration_no'] or 'N/A'}")), 
                                ft.DataCell(ft.Text(f"{p['first_name']} {p['last_name']}")), 
                                ft.DataCell(ft.Text(p['phone'] or 'N/A')), 
                                ft.DataCell(eye_btn)
                            ]
                        )
                    )
                
                content_controls.extend([
                    ft.Text("Patient Master Directory. Click the eye icon to retrieve full schema details.", color=ft.Colors.GREY), 
                    ft.DataTable(
                        columns=[
                            ft.DataColumn(ft.Text("Registration No.")), 
                            ft.DataColumn(ft.Text("Full Name")), 
                            ft.DataColumn(ft.Text("Contact Number")), 
                            ft.DataColumn(ft.Text("Actions"))
                        ], 
                        rows=p_rows
                    )
                ])

        # =====================================================================
        # 5.8. MODULE: APPOINTMENTS & SCHEDULING
        # =====================================================================
        elif tab == "book_appt":
            rec_id = page.session.store.get("rec_id")
            
            patient_list = get_query_data("SELECT patient_id, first_name, last_name, registration_no FROM Patient")
            doctor_list = get_query_data("SELECT doctor_id, first_name, last_name, specialization FROM Doctor")
            
            p_dropdown = ft.Dropdown(
                label="Select Registered Patient", 
                width=300, 
                options=[ft.dropdown.Option(key=str(p['patient_id']), text=f"{p['registration_no']} - {p['first_name']} {p['last_name']}") for p in patient_list]
            )
            d_dropdown = ft.Dropdown(
                label="Assign Specialist Doctor", 
                width=300, 
                options=[ft.dropdown.Option(key=str(d['doctor_id']), text=f"Dr. {d['first_name']} ({d['specialization']})") for d in doctor_list]
            )
            
            appt_date = ft.TextField(label="Date (YYYY-MM-DD)", width=200)
            appt_time = ft.TextField(label="Time (HH:MM)", width=200)
            appt_type = ft.Dropdown(label="Consultation Type", width=200, options=[ft.dropdown.Option("OPD"), ft.dropdown.Option("Follow-up"), ft.dropdown.Option("Emergency"), ft.dropdown.Option("Online")])
            
            token_num = ft.TextField(label="Token / Queue Number", width=200)
            visit_reason = ft.TextField(label="Primary Reason for Visit", width=450)
            internal_notes = ft.TextField(label="Internal Desk Notes", width=450)

            def execute_booking(e):
                try:
                    # Validate Date and extract Day of Week
                    date_obj = datetime.datetime.strptime(appt_date.value, "%Y-%m-%d")
                    day_of_week_str = date_obj.strftime("%a")
                    
                    # Logic Check: Doctor Availability Validation
                    avail_check = get_query_data("SELECT * FROM DoctorAvailability WHERE doctor_id=%s AND day_of_week=%s", (d_dropdown.value, day_of_week_str))
                    if not avail_check:
                        show_snack(f"Validation Failed: Doctor is NOT scheduled to work on {day_of_week_str}.", ft.Colors.RED)
                        return

                    query = """
                        INSERT INTO Appointment 
                        (patient_id, doctor_id, receptionist_id, appointment_date, appointment_time, token_number, reason, type, status, notes) 
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'Scheduled', %s)
                    """
                    params = (p_dropdown.value, d_dropdown.value, rec_id, appt_date.value, appt_time.value, token_num.value, visit_reason.value, appt_type.value, internal_notes.value)
                    
                    if execute_query(query, params):
                        show_snack("Appointment Successfully Added to Queue!", ft.Colors.GREEN)
                        nav_to("book_appt")
                    else: 
                        show_snack("Database Transaction Failed. Verify inputs.", ft.Colors.RED)

                except ValueError:
                    show_snack("Format Error: Date must be YYYY-MM-DD.", ft.Colors.RED)

            queue_data = get_query_data("""
                SELECT a.appointment_id, p.first_name, d.first_name as d_name, a.appointment_date, a.appointment_time, a.type, a.status 
                FROM Appointment a 
                JOIN Patient p ON a.patient_id = p.patient_id 
                JOIN Doctor d ON a.doctor_id = d.doctor_id 
                ORDER BY a.appointment_date DESC, a.appointment_time DESC
            """)
            
            q_rows = []
            for q in queue_data:
                status_val = q.get('status') or "Scheduled"
                type_val = q.get('type') or "OPD"
                status_color = ft.Colors.GREEN if status_val.lower() == 'completed' else ft.Colors.ORANGE
                
                q_rows.append(
                    ft.DataRow(
                        cells=[
                            ft.DataCell(ft.Text(str(q['appointment_id']))), 
                            ft.DataCell(ft.Text(q['first_name'])), 
                            ft.DataCell(ft.Text(f"Dr. {q['d_name']}")), 
                            ft.DataCell(ft.Text(f"{q['appointment_date']} {q['appointment_time']}")),
                            ft.DataCell(ft.Text(type_val, weight="bold", color=ft.Colors.TEAL_700)),
                            ft.DataCell(
                                ft.Container(
                                    content=ft.Text(status_val.upper(), weight="bold", color=ft.Colors.WHITE, size=11), 
                                    bgcolor=status_color, 
                                    padding=5, 
                                    border_radius=5
                                )
                            )
                        ]
                    )
                )

            content_controls.append(
                ft.Column(
                    controls=[
                        ft.Text("Step 1: Patient Identification", weight="bold", color=ft.Colors.TEAL_900), 
                        ft.Row(controls=[p_dropdown, d_dropdown]),
                        ft.Text("Step 2: Scheduling Parameters", weight="bold", color=ft.Colors.TEAL_900), 
                        ft.Row(controls=[appt_date, appt_time, appt_type, token_num]), 
                        ft.Text("Step 3: Clinical Context", weight="bold", color=ft.Colors.TEAL_900),
                        ft.Row(controls=[visit_reason, internal_notes]),
                        ft.FilledButton(
                            "Verify Schedule & Commit Appointment", 
                            icon=ft.Icons.EVENT_AVAILABLE, 
                            style=rec_btn_style, 
                            on_click=execute_booking
                        ),
                        ft.Divider(height=40), 
                        ft.Text("Live Consultation Queue", weight="bold", size=20),
                        ft.DataTable(
                            columns=[
                                ft.DataColumn(ft.Text("Appt ID")), 
                                ft.DataColumn(ft.Text("Patient Name")), 
                                ft.DataColumn(ft.Text("Doctor Assigned")), 
                                ft.DataColumn(ft.Text("Date & Time")), 
                                ft.DataColumn(ft.Text("Type")), 
                                ft.DataColumn(ft.Text("Current Status"))
                            ], 
                            rows=q_rows
                        )
                    ]
                )
            )

        # =====================================================================
        # 5.9. MODULE: IPD ADMISSIONS & BED MANAGEMENT
        # =====================================================================
        elif tab == "admissions":
            patient_list = get_query_data("SELECT patient_id, first_name, last_name, registration_no FROM Patient")
            doctor_list = get_query_data("SELECT doctor_id, first_name, last_name FROM Doctor")
            
            # Complex Query: Only fetch beds that are physically Available
            bed_list = get_query_data("""
                SELECT b.bed_id, b.bed_number, r.room_number, w.ward_name 
                FROM Bed b 
                JOIN Room r ON b.room_id=r.room_id 
                JOIN Ward w ON r.ward_id = w.ward_id
                WHERE b.status='Available'
            """)
            
            p_dropdown = ft.Dropdown(
                label="Select Patient", 
                width=300, 
                options=[ft.dropdown.Option(key=str(p['patient_id']), text=f"{p['registration_no']} - {p['first_name']} {p['last_name']}") for p in patient_list]
            )
            d_dropdown = ft.Dropdown(
                label="Attending Physician", 
                width=300, 
                options=[ft.dropdown.Option(key=str(d['doctor_id']), text=f"Dr. {d['first_name']} {d['last_name']}") for d in doctor_list]
            )
            b_dropdown = ft.Dropdown(
                label="Assign Available Bed", 
                width=400, 
                options=[ft.dropdown.Option(key=str(b['bed_id']), text=f"Bed {b['bed_number']} | Room {b['room_number']} | {b['ward_name']}") for b in bed_list]
            )
            
            adm_date = ft.TextField(label="Admission Datestamp (YYYY-MM-DD HH:MM:SS)", width=350)
            adm_reason = ft.TextField(label="Medical Reason for Admission", width=550)

            def execute_admission(e):
                query1 = "INSERT INTO Admission (patient_id, doctor_id, bed_id, admission_date, reason, status) VALUES (%s, %s, %s, %s, %s, 'Admitted')"
                params1 = (p_dropdown.value, d_dropdown.value, b_dropdown.value, adm_date.value, adm_reason.value)
                
                query2 = "UPDATE Bed SET status = 'Occupied' WHERE bed_id = %s"
                params2 = (b_dropdown.value,)

                if execute_transaction([(query1, params1), (query2, params2)]):
                    show_snack("IPD Admission processed and Bed marked Occupied.", ft.Colors.GREEN)
                    nav_to("admissions")
                else: 
                    show_snack("Transaction Failed. Check Data Constraints.", ft.Colors.RED)

            adm_data = get_query_data("""
                SELECT a.admission_id, p.first_name, d.first_name as doc, b.bed_number, w.ward_name, a.admission_date, a.status 
                FROM Admission a 
                JOIN Patient p ON a.patient_id = p.patient_id 
                JOIN Doctor d ON a.doctor_id = d.doctor_id 
                JOIN Bed b ON a.bed_id = b.bed_id
                JOIN Room r ON b.room_id = r.room_id
                JOIN Ward w ON r.ward_id = w.ward_id
            """)
            
            if not adm_data: 
                content_controls.append(ft.Text("No active inpatient admissions found.", color=ft.Colors.GREY))
            else:
                a_rows = []
                for a in adm_data:
                    status_color = ft.Colors.ORANGE if a['status'] == 'Admitted' else ft.Colors.GREEN
                    a_rows.append(
                        ft.DataRow(
                            cells=[
                                ft.DataCell(ft.Text(str(a['admission_id']))), 
                                ft.DataCell(ft.Text(a['first_name'])), 
                                ft.DataCell(ft.Text(f"Dr. {a['doc']}")), 
                                ft.DataCell(ft.Text(f"{a['ward_name']} / {a['bed_number']}")), 
                                ft.DataCell(ft.Text(str(a['admission_date']))), 
                                ft.DataCell(ft.Text(a['status'].upper(), color=status_color, weight="bold"))
                            ]
                        )
                    )
                
                content_controls.append(
                    ft.Column(
                        controls=[
                            ft.Text("Admit New Patient to Ward", weight="bold", color=ft.Colors.TEAL_900),
                            ft.Row(controls=[p_dropdown, d_dropdown, b_dropdown]), 
                            ft.Row(controls=[adm_date, adm_reason]),
                            ft.FilledButton(
                                "Process Inpatient Admission", 
                                icon=ft.Icons.BED, 
                                style=rec_btn_style, 
                                on_click=execute_admission
                            ), 
                            ft.Divider(height=40),
                            ft.Text("Active Inpatient Directory", weight="bold", size=20),
                            ft.DataTable(
                                columns=[
                                    ft.DataColumn(ft.Text("Adm ID")), 
                                    ft.DataColumn(ft.Text("Patient Name")), 
                                    ft.DataColumn(ft.Text("Attending Doctor")), 
                                    ft.DataColumn(ft.Text("Location")), 
                                    ft.DataColumn(ft.Text("Date Admitted")), 
                                    ft.DataColumn(ft.Text("Status"))
                                ], 
                                rows=a_rows
                            )
                        ]
                    )
                )

        # =====================================================================
        # 5.10. MODULE: FACILITY CONFIGURATION (Wards / Rooms / Beds)
        # =====================================================================
        elif tab == "rooms":
            # Ward Inputs
            w_name = ft.TextField(label="Ward Name", width=200)
            w_type = ft.Dropdown(
                label="Ward Type", 
                width=200, 
                options=[
                    ft.dropdown.Option("General"), ft.dropdown.Option("ICU"), 
                    ft.dropdown.Option("NICU"), ft.dropdown.Option("Private"), 
                    ft.dropdown.Option("Emergency")
                ]
            )
            w_dept = ft.TextField(label="Dept ID", width=100)
            w_floor = ft.TextField(label="Floor", width=100)
            w_cap = ft.TextField(label="Capacity", width=100)
            
            def save_ward(e):
                query = "INSERT INTO Ward (ward_name, ward_type, dept_id, floor, capacity) VALUES (%s, %s, %s, %s, %s)"
                if execute_query(query, (w_name.value, w_type.value, w_dept.value, w_floor.value, w_cap.value)):
                    show_snack("Ward Generated Successfully!", ft.Colors.GREEN)
                    nav_to("rooms")
                else: 
                    show_snack("Error: Verify Department ID exists.", ft.Colors.RED)

            # Room Inputs
            r_num = ft.TextField(label="Room Number", width=200)
            r_ward_drop = ft.Dropdown(label="Select Existing Ward", width=250)
            r_type = ft.Dropdown(
                label="Room Configuration", 
                width=200, 
                options=[
                    ft.dropdown.Option("Single"), ft.dropdown.Option("Double"), ft.dropdown.Option("Multi")
                ]
            )
            r_charge = ft.TextField(label="Daily Charge (₹)", width=150)

            def save_room(e):
                query = "INSERT INTO Room (room_number, ward_id, room_type, daily_charge) VALUES (%s, %s, %s, %s)"
                if execute_query(query, (r_num.value, r_ward_drop.value, r_type.value, r_charge.value)):
                    show_snack("Room Attached to Ward Successfully!", ft.Colors.GREEN)
                    nav_to("rooms")
                else: 
                    show_snack("Error: Valid Ward must be selected.", ft.Colors.RED)

            # Bed Inputs
            b_num = ft.TextField(label="Bed Designation (e.g. B-01)", width=250)
            b_room_drop = ft.Dropdown(label="Select Existing Room", width=250)

            def save_bed(e):
                query = "INSERT INTO Bed (bed_number, room_id, status) VALUES (%s, %s, 'Available')"
                if execute_query(query, (b_num.value, b_room_drop.value)):
                    show_snack("Bed Deployed Successfully!", ft.Colors.GREEN)
                    nav_to("rooms")
                else: 
                    show_snack("Error: Valid Room must be selected.", ft.Colors.RED)

            facility_dlg = ft.AlertDialog(
                title=ft.Text("Facility Architecture Configuration", weight="bold"),
                content=ft.Container(
                    width=750, 
                    content=ft.Column(
                        controls=[
                            ft.Text("Step 1: Construct a Ward", weight="bold", color=ft.Colors.BLUE_900), 
                            ft.Row(controls=[w_name, w_type, w_dept, w_floor, w_cap]), 
                            ft.FilledButton("Construct Ward", style=admin_btn_style, on_click=save_ward), 
                            ft.Divider(),
                            
                            ft.Text("Step 2: Add Rooms to Ward", weight="bold", color=ft.Colors.BLUE_900), 
                            ft.Row(controls=[r_num, r_ward_drop, r_type, r_charge]), 
                            ft.FilledButton("Attach Room", style=admin_btn_style, on_click=save_room), 
                            ft.Divider(),
                            
                            ft.Text("Step 3: Deploy Beds to Room", weight="bold", color=ft.Colors.BLUE_900), 
                            ft.Row(controls=[b_num, b_room_drop]), 
                            ft.FilledButton("Deploy Bed", style=admin_btn_style, on_click=save_bed)
                        ], 
                        tight=True, 
                        scroll=ft.ScrollMode.AUTO
                    )
                ),
                actions=[
                    ft.TextButton(
                        "Close Architect", 
                        on_click=lambda e: setattr(facility_dlg, 'open', False) or page.update()
                    )
                ]
            )

            # Function to populate dropdowns dynamically
            def open_facility_architect(e):
                wards = get_query_data("SELECT ward_id, ward_name FROM Ward")
                r_ward_drop.options = [ft.dropdown.Option(key=str(w['ward_id']), text=f"ID: {w['ward_id']} - {w['ward_name']}") for w in wards]

                rooms = get_query_data("SELECT room_id, room_number FROM Room")
                b_room_drop.options = [ft.dropdown.Option(key=str(r['room_id']), text=f"ID: {r['room_id']} - Room {r['room_number']}") for r in rooms]

                page.overlay.append(facility_dlg)
                facility_dlg.open = True
                page.update()

            content_controls.append(
                ft.FilledButton(
                    "Open Architecture Configurator", 
                    icon=ft.Icons.DOMAIN_ADD, 
                    style=admin_btn_style, 
                    on_click=open_facility_architect
                )
            )
            content_controls.append(ft.Divider())

            # Data Tables for Facilities
            ward_data = get_query_data("SELECT ward_id, ward_name, ward_type, capacity FROM Ward")
            if ward_data:
                w_rows = []
                for w in ward_data:
                    w_rows.append(
                        ft.DataRow(
                            cells=[
                                ft.DataCell(ft.Text(str(w['ward_id']))), 
                                ft.DataCell(ft.Text(w['ward_name'])), 
                                ft.DataCell(ft.Text(w['ward_type'])), 
                                ft.DataCell(ft.Text(str(w['capacity'])))
                            ]
                        )
                    )
                
                content_controls.extend([
                    ft.Text("Constructed Wards Overview", weight="bold", size=20), 
                    ft.DataTable(
                        columns=[
                            ft.DataColumn(ft.Text("Ward ID")), 
                            ft.DataColumn(ft.Text("Ward Name")), 
                            ft.DataColumn(ft.Text("Classification")), 
                            ft.DataColumn(ft.Text("Total Capacity"))
                        ], 
                        rows=w_rows
                    ),
                    ft.Divider(height=30)
                ])

            bed_data = get_query_data("SELECT b.bed_id, b.bed_number, r.room_number, b.status FROM Bed b JOIN Room r ON b.room_id = r.room_id")
            if bed_data:
                b_rows = []
                for b in bed_data:
                    b_rows.append(
                        ft.DataRow(
                            cells=[
                                ft.DataCell(ft.Text(str(b['bed_id']))), 
                                ft.DataCell(ft.Text(b['bed_number'])), 
                                ft.DataCell(ft.Text(b['room_number'])), 
                                ft.DataCell(ft.Text(b['status'], color=ft.Colors.GREEN if b['status']=='Available' else ft.Colors.RED, weight="bold"))
                            ]
                        )
                    )

                content_controls.extend([
                    ft.Text("Real-Time Bed Matrix", weight="bold", size=20), 
                    ft.DataTable(
                        columns=[
                            ft.DataColumn(ft.Text("Bed Database ID")), 
                            ft.DataColumn(ft.Text("Bed Designation")), 
                            ft.DataColumn(ft.Text("Assigned Room")), 
                            ft.DataColumn(ft.Text("Occupancy Status"))
                        ], 
                        rows=b_rows
                    )
                ])
            else:
                content_controls.append(ft.Text("No beds currently exist in the database architecture.", color=ft.Colors.GREY))

        # =====================================================================
        # 5.11. MODULE: PHARMACY INVENTORY & BILLING (Dashboards)
        # =====================================================================
        elif tab == "meds":
            med_data = get_query_data("SELECT medicine_id, medicine_name, stock_quantity, unit_price, generic_name FROM Medicine")
            if not med_data: 
                content_controls.append(ft.Text("No medicines configured in Pharmacy Schema.", color=ft.Colors.GREY))
            else:
                m_rows = []
                for m in med_data:
                    stock_color = ft.Colors.RED if m['stock_quantity'] < 10 else ft.Colors.BLACK
                    m_rows.append(
                        ft.DataRow(
                            cells=[
                                ft.DataCell(ft.Text(str(m['medicine_id']))), 
                                ft.DataCell(ft.Text(m['medicine_name'], weight="bold")), 
                                ft.DataCell(ft.Text(m['generic_name'] or "N/A")),
                                ft.DataCell(ft.Text(str(m['stock_quantity']), color=stock_color)), 
                                ft.DataCell(ft.Text(f"₹{m['unit_price']}"))
                            ]
                        )
                    )
                
                content_controls.extend([
                    ft.Text("Central Pharmacy Repository", weight="bold", size=20),
                    ft.DataTable(
                        columns=[
                            ft.DataColumn(ft.Text("ID")), 
                            ft.DataColumn(ft.Text("Medicine Brand Name")), 
                            ft.DataColumn(ft.Text("Generic Name")), 
                            ft.DataColumn(ft.Text("Available Stock")), 
                            ft.DataColumn(ft.Text("Unit Price"))
                        ], 
                        rows=m_rows
                    )
                ])

        elif tab in ["billing", "rec_billing"]:
            bill_data = get_query_data("SELECT i.invoice_id, i.invoice_number, p.first_name, p.last_name, i.total_amount, i.payment_status, i.invoice_date FROM Invoice i JOIN Patient p ON i.patient_id = p.patient_id")
            if not bill_data: 
                content_controls.append(ft.Text("No financial invoices found in the database.", color=ft.Colors.GREY))
            else:
                bill_rows = []
                for b in bill_data:
                    status_color = ft.Colors.GREEN if b['payment_status'] == 'Paid' else ft.Colors.RED
                    bill_rows.append(
                        ft.DataRow(
                            cells=[
                                ft.DataCell(ft.Text(str(b['invoice_number']))), 
                                ft.DataCell(ft.Text(f"{b['first_name']} {b['last_name']}")), 
                                ft.DataCell(ft.Text(str(b['invoice_date']).split()[0])),
                                ft.DataCell(ft.Text(f"₹{b['total_amount']}")), 
                                ft.DataCell(ft.Text(b['payment_status'].upper(), weight="bold", color=status_color))
                            ]
                        )
                    )
                
                content_controls.extend([
                    ft.Text("Global Financial Transactions", weight="bold", size=20),
                    ft.DataTable(
                        columns=[
                            ft.DataColumn(ft.Text("Invoice Num")), 
                            ft.DataColumn(ft.Text("Patient Name")), 
                            ft.DataColumn(ft.Text("Generated Date")), 
                            ft.DataColumn(ft.Text("Total Due")), 
                            ft.DataColumn(ft.Text("Settlement Status"))
                        ], 
                        rows=bill_rows
                    )
                ])

        # Return the entirely assembled View structure
        return ft.View(
            route="/dashboard",
            bgcolor=ft.Colors.GREY_50,
            controls=[
                ft.Row(
                    expand=True, 
                    spacing=0,
                    controls=[
                        sidebar, 
                        ft.Container(
                            expand=True, 
                            padding=40, 
                            content=ft.Column(
                                controls=content_controls, 
                                scroll=ft.ScrollMode.AUTO
                            )
                        )
                    ]
                )
            ]
        )

    # =====================================================================
    # 6. STARTUP EXECUTION ENGINE
    # =====================================================================
    page.views.clear()
    page.views.append(login_view())
    page.update()

if __name__ == "__main__":
    ft.run(main)